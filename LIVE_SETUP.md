# Odds Engine — Live configuration

The Odds API credentials have been placed in `.env` and are intentionally not printed in documentation.

Configured:
- Sport: soccer_italy_serie_a
- Region: eu
- Market: h2h (1X2)
- Odds format: decimal
- Polling: 5 minutes
- Paper trading: ON
- Real-money execution: OFF

Start scheduler:

```bash
python scheduler.py
```

Start dashboard:

```bash
streamlit run app.py
```

Keep `.env` private. If the package is ever shared, remove `.env` first.
