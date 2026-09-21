import os
import threading
import time
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from odds_engine.collector import poll
from odds_engine.signals import generate
from odds_engine.paper import settle
from odds_engine.db import connect

DB_PATH = os.getenv("ODDS_DB_PATH", "/var/data/odds_engine.sqlite")
SPORT = os.getenv("ODDS_SPORT", "soccer_italy_serie_a")
REGIONS = os.getenv("ODDS_REGIONS", "eu")
MARKETS = os.getenv("ODDS_MARKETS", "h2h")
# Starter quota: 500 credits/month. With 1 market x 1 region,
# 90 minutes gives about 480 scheduled calls/month.
POLL_MINUTES = int(os.getenv("POLL_MINUTES", "90"))
PAPER_ONLY = os.getenv("PAPER_ONLY", "true").lower() == "true"

state = {
    "started_at": datetime.now(timezone.utc).isoformat(),
    "last_run": None,
    "last_success": None,
    "last_error": None,
    "events": 0,
    "snapshots": 0,
    "signals": 0,
    "settled": 0,
    "running": False,
}

app = FastAPI(title="Odds Engine Cloud API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_once():
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state["running"] = True
    try:
        events, snapshots = poll(
            db=DB_PATH,
            sport=SPORT,
            regions=REGIONS,
            markets=MARKETS,
        )
        signals = generate(db=DB_PATH)
        settled = settle(db=DB_PATH)
        state.update({
            "last_success": datetime.now(timezone.utc).isoformat(),
            "last_error": None,
            "events": events,
            "snapshots": snapshots,
            "signals": signals,
            "settled": settled,
        })
        print(
            f"[collector] OK events={events} snapshots={snapshots} "
            f"signals={signals} settled={settled}",
            flush=True,
        )
    except Exception as exc:
        state["last_error"] = str(exc)
        print(f"[collector] ERROR {exc}", flush=True)
    finally:
        state["running"] = False

def collector_loop():
    # Do one collection shortly after startup, then follow the configured interval.
    while True:
        run_once()
        time.sleep(max(15, POLL_MINUTES * 60))

@app.on_event("startup")
def startup():
    threading.Thread(target=collector_loop, name="collector", daemon=True).start()

@app.get("/")
def root():
    return {
        "service": "Odds Engine",
        "status": "ok",
        "mode": "PAPER_TRADING" if PAPER_ONLY else "UNSAFE_CONFIG",
        "sport": SPORT,
        "poll_minutes": POLL_MINUTES,
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "collector": {
            "running": state["running"],
            "last_run": state["last_run"],
            "last_success": state["last_success"],
            "last_error": state["last_error"],
        },
        "paper_trading": PAPER_ONLY,
        "sport": SPORT,
        "poll_minutes": POLL_MINUTES,
    }

@app.get("/mobile/dashboard")
def dashboard():
    con = connect(DB_PATH)
    matches = con.execute("SELECT COUNT(*) AS n FROM matches").fetchone()["n"]
    snapshots = con.execute("SELECT COUNT(*) AS n FROM snapshots").fetchone()["n"]
    signals = con.execute("SELECT COUNT(*) AS n FROM signals").fetchone()["n"]
    bets = con.execute(
        "SELECT COUNT(*) AS n FROM paper_bets WHERE status='OPEN'"
    ).fetchone()["n"]
    con.close()
    return {
        "matches": matches,
        "snapshots": snapshots,
        "signals": signals,
        "open_paper_bets": bets,
        "collector": state,
    }

@app.get("/mobile/signals")
def mobile_signals(limit: int = 50):
    limit = max(1, min(limit, 200))
    con = connect(DB_PATH)
    rows = con.execute(
        """SELECT s.*, m.home_team, m.away_team, m.commence_time
           FROM signals s JOIN matches m ON m.id=s.match_id
           ORDER BY s.id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.get("/mobile/history")
def mobile_history(limit: int = 100):
    limit = max(1, min(limit, 500))
    con = connect(DB_PATH)
    rows = con.execute(
        """SELECT pb.*, s.score, s.ev, s.odds_gap,
                  m.home_team, m.away_team, m.commence_time
           FROM paper_bets pb
           JOIN signals s ON s.id=pb.signal_id
           JOIN matches m ON m.id=s.match_id
           ORDER BY pb.id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]
