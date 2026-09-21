# Odds Engine v3

Motore di ricerca e paper trading per quote calcistiche. **Nessuna esecuzione reale** è inclusa.

## 1) Installazione

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## 2) API live
Copia `.env.example` in `.env` e inserisci `ODDS_API_KEY`. Il collector usa un adapter per The Odds API e salva ogni polling come snapshot SQLite.

## 3) Avvio

```bash
python -m pytest -q
python -m odds_engine.cli poll
python -m odds_engine.cli signals
streamlit run app.py
```

Per polling continuo:

```bash
python scheduler.py
```

## Architettura
- `api.py`: adapter quote live
- `collector.py`: acquisizione e snapshot
- `market.py`: probabilità, fair odds, EV, score, stake
- `signals.py`: generazione segnali pre-match
- `regime.py`: stato NORMAL/YELLOW/RED
- `paper.py`: settlement paper trading
- `backtest.py`: benchmark storico
- `db.py`: SQLite/time series
- `app.py`: dashboard

## Sicurezza metodologica
La chiusura non viene usata per creare un segnale storico pre-match. Il movimento viene calcolato solo quando esistono snapshot realmente osservati nel tempo. Il sistema non piazza scommesse reali.

## Nota
Lo Score v3 è un motore di ricerca iniziale, non una garanzia di profitto e non un modello ML validato. I pesi devono essere congelati prima dei test out-of-sample.

## Test finale
- `pytest -q` esegue i test del motore.
- `python -m odds_engine.cli import-csv data/I1_2023_24.csv` importa lo storico nel DB.
- `python -m odds_engine.cli status` mostra i contatori del database.
- `streamlit run app.py` avvia la dashboard interattiva.
- `dashboard_preview.html` è una preview statica generata dal DB e può essere aperta localmente anche senza Streamlit.
