# Spending Report Generator — Email with Gmail OAuth2

This folder contains `generate_reports_email.py` which generates spending reports (CSV/PDF inputs) and can email the report. 

## Quick Start - Using the EXE (Easiest)

**For Windows users:**
1. Double-click `build.bat` to build the executable
2. Navigate to `dist/Spending_Report_Generator/` folder
3. Double-click `Spending_Report_Generator.exe` to run

**For macOS/Linux users:**
```bash
chmod +x build.sh
./build.sh
# Then run: ./dist/Spending_Report_Generator/Spending_Report_Generator
```

The executable includes all dependencies and doesn't require Python to be installed!

## Alternative - Running Python Script Directly

If you prefer running the Python script directly:

1) Install dependencies (use a virtualenv):

```bash
pip install -r requirements.txt
```

2) Run the script:

```bash
cd report
python generate_reports_email.py
```

## 📧 Email Authentication

The app uses **Gmail OAuth2 (recommended)** for secure email delivery.

### Option 1: OAuth2 (RECOMMENDED - Secure & Easy)

**Setup (One-Time Only):**

1. Visit: https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable Gmail API: Search "Gmail API" → Enable
4. Create OAuth credentials:
   - Click "Create Credentials"
   - Select "OAuth 2.0 Client ID"
   - Application type: "Desktop application"
5. Download the JSON file
6. Save as `credentials.json` in the app folder

**When You Run the App:**
- When asked about email, select "oauth"
- A browser window opens automatically
- Click "Allow" to authorize
- Done! No passwords stored ✅

**Benefits:**
- ✅ No passwords in the app
- ✅ Full app control in Google Account
- ✅ Secure OAuth tokens
- ✅ Can revoke access anytime

### Option 2: Gmail App Password (Fallback)

If you don't want to set up OAuth2, use an app-specific password:

1. Go to: https://myaccount.google.com/apppasswords
2. Select: Mail → Your Device Type
3. Google generates a 16-character password
4. Copy and paste into the app when prompted

**Note:** OAuth2 is more secure, but this works if you prefer simplicity.

## Security Best Practices

⚠️ **IMPORTANT:** Keep your credentials secure!

- **Never commit** `credentials.json` or `token.json` to version control
- **Keep OAuth tokens private** - anyone with them can send emails on your behalf
- **Use OAuth2 (recommended)** instead of storing passwords
- **Delete old tokens** if they are compromised
- A browser window will open to complete Google sign-in and consent; after that a `token.json` file will be saved for reuse.

## Security Best Practices

⚠️ **IMPORTANT:** Keep your credentials secure!

- **Never commit** `credentials.json` or `token.json` to version control (see `.gitignore`)
- **Passwords are hidden** when entered - they will not appear on screen
- **Keep OAuth tokens private** - anyone with `token.json` can send emails on your behalf
- **Use Gmail OAuth2 (recommended)** instead of storing passwords
- **Use app-specific passwords** if using SMTP (not your main account password)

### If Using SMTP:
- Use an **App Password**, not your main account password
- Never share your email credentials
- For Gmail: [Enable "Less secure app access"](https://support.google.com/accounts/answer/6010255) or use an [App Password](https://support.google.com/accounts/answer/185833)

## Notes

- Each user should create or reuse their own `credentials.json` and will receive their own `token.json` after the OAuth flow.
- If you prefer not to use OAuth, choose `n` to use the SMTP fallback (requires SMTP credentials).
- Keep `credentials.json` and `token.json` private.
- The application validates email addresses and file paths to prevent errors
