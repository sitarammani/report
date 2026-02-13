# Gmail OAuth2 Setup Guide for End Users

This guide shows how to set up secure Gmail OAuth2 for the Spending Report Generator.

## ✅ Why OAuth2?

- **No passwords stored in the app**
- **Most secure method**
- **Easy one-time setup**
- **Full control in your Google Account**

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create OAuth Credentials

1. Go to: https://console.cloud.google.com/
2. **Create a new project** (or use existing):
   - Click dropdown at top → "NEW PROJECT"
   - Name: "Spending Report" (or any name)
   - Click "CREATE"

3. **Enable Gmail API**:
   - Search for "Gmail API" in the search box
   - Click "Gmail API"
   - Click "ENABLE"

4. **Create OAuth Client ID**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: **"Desktop application"**
   - Click "CREATE"

5. **Download JSON File**:
   - You'll see your new credential
   - Click the download icon (⬇️)
   - Save the JSON file

### Step 2: Place Credentials File

1. Extract the `Spending_Report_Generator` folder (from ZIP if applicable)
2. Rename the JSON file to: `credentials.json`
3. Place `credentials.json` in the same folder as `Spending_Report_Generator`

**Folder should look like:**
```
Spending_Report_Generator/
├── Spending_Report_Generator (executable)
├── credentials.json ← Place your file here
└── category_map.csv
```

### Step 3: Use the App

1. Run: `Spending_Report_Generator`
2. When asked about email, enter: `y`
3. Input sender and recipient emails
4. When prompted for authentication, select: **OAuth2**
5. A browser window opens
6. Click **"Allow"** to authorize
7. Done! ✅

## 🔐 Security Notes

✅ **Your credentials file**:
- Contains only your app ID (credentials)
- Does NOT contain your password
- Safe to keep in the app folder

✅ **Tokens (auto-generated)**:
- First run creates `token.json` (secure!)
- This is the actual authorization
- Only works for this app
- Can be revoked anytime

❌ **DO NOT**:
- Share `credentials.json` with others
- Commit to version control (it's in .gitignore)
- Post credentials online

## 🔄 How to Revoke Access

If you want to stop the app from accessing Gmail:

1. Go to: https://myaccount.google.com/permissions
2. Find "Spending Report" (your app name)
3. Click it → "Remove"
4. Done! The app can no longer send emails

## ❓ Troubleshooting

**"credentials.json not found"**
- Make sure file is named exactly: `credentials.json`
- Check it's in the same folder as the executable
- Ensure it's the OAuth 2.0 file from Google Cloud Console

**"Invalid credentials"**
- Download a fresh credentials.json file
- Make sure Application Type was "Desktop application"
- Delete `token.json` (if it exists) and try again

**"Authorization denied"**
- Click "Allow" when the browser opens
- Make sure you're logged into the correct Google account
- Try creating new credentials

**Still not working?**
- Delete `token.json` file
- Run the app again
- The browser should open for fresh authorization

## 📚 Learn More

- [Google Cloud Console](https://console.cloud.google.com/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth2 Overview](https://developers.google.com/identity/protocols/oauth2)
