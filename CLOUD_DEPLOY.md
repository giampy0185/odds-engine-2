# Odds Engine — Cloud Deploy

This package is prepared for a Render Web Service.

Build command:
`pip install -r requirements.txt`

Start command:
`uvicorn cloud_app:app --host 0.0.0.0 --port $PORT`

Required secret:
`ODDS_API_KEY`

The API key is intentionally NOT included in this package.

Safety:
- PAPER_ONLY=true
- No real betting execution is implemented.

Quota:
The current configuration uses 1 region (`eu`) and 1 market (`h2h`).
With a 500-credit monthly plan, a 90-minute polling interval is about
480 scheduled requests/month if every request returns data. Increase polling
frequency only after confirming the account quota/plan.

Endpoints:
- `/health`
- `/mobile/dashboard`
- `/mobile/signals`
- `/mobile/history`
