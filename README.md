# Spending Report Generator — Email with Gmail OAuth2

This folder contains `generate_reports_email.py` which generates spending reports (CSV/PDF inputs) and can email the report. Below are simple steps so any user can run the program with their own Google account (no app password required).

1) Install dependencies (use a virtualenv):

```bash
pip install -r requirements.txt
```

2) Create Google OAuth client credentials (one-time per user):
- Visit https://console.cloud.google.com/
- Create or select a project and enable the Gmail API
- Create OAuth 2.0 Client ID credentials → Application type: "Desktop app"
- Download the JSON and save it as `credentials.json` in this `report/` folder

3) Run the script and choose Gmail OAuth2 when prompted:

```bash
cd report
python generate_reports_email.py
```

- When asked to send the report via email, enter `y`.
- When asked "Use Gmail OAuth2 (recommended)?", enter `y`.
- A browser window will open to complete Google sign-in and consent; after that a `token.json` file will be saved for reuse.

Notes
- Each user should create or reuse their own `credentials.json` and will receive their own `token.json` after the OAuth flow.
- If you prefer not to use OAuth, choose `n` to use the SMTP fallback (requires SMTP credentials).
- Keep `credentials.json` and `token.json` private.

If you'd like, I can also:
- Add a helper script that checks for `credentials.json` in common locations, or
- Add a small `setup_oauth.sh` with step-by-step commands to help create the OAuth client.
