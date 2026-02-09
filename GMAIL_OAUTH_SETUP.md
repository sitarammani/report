# Gmail OAuth2 Setup Guide

The app needs OAuth2 credentials to send emails via Gmail API. Here's how to set it up:

## Step 1: Create OAuth Credentials in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create an OAuth 2.0 Client ID:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application"
   - Download the JSON file
5. Rename the downloaded file to `credentials.json` and place it in this folder (`C:\Users\jegas\Downloads\report\`)

## Step 2: Run OAuth Setup

Once `credentials.json` is in place, run:

```powershell
python oauth_setup.py
```

This will:
- Open a browser window for Google login
- Ask for permission to send emails
- Save your token as `token.json` (for future use)

## Step 3: Run the App

Now you can run the app and choose Gmail OAuth2 when prompted:

```powershell
python generate_reports_email.py
```

## Troubleshooting

- **"credentials.json not found"**: Make sure the file is in the same folder as the scripts
- **"Invalid client"**: Check that the credentials.json file is correct and not corrupted
- **"Invalid scope"**: Make sure the Gmail API is enabled in Google Cloud Console
