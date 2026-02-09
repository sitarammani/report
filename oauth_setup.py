#!/usr/bin/env python3
"""
OAuth setup helper — performs Google OAuth flow and saves token.json
Place `credentials.json` (OAuth client) in this folder, then run:

  python oauth_setup.py

This will open a browser for sign-in and save `token.json` for future runs.
"""
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def main():
    if not os.path.exists('credentials.json'):
        print('credentials.json not found. Create OAuth client credentials in Google Cloud Console and save as credentials.json in this folder.')
        return

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except Exception as e:
        print('Missing required packages. Run: pip install -r requirements.txt')
        raise

    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as f:
        f.write(creds.to_json())

    print('Saved token.json — you can now run generate_reports_email.py and choose Gmail OAuth2')


if __name__ == '__main__':
    main()
