#!/usr/bin/env python3
"""
Gmail OAuth2 Setup Script
Helps users set up OAuth2 credentials for Gmail authentication.
Run this once to configure OAuth2, then use generate_reports_email.py normally.
"""

import os
import json
import sys

print("\n" + "="*70)
print("GMAIL OAUTH2 SETUP")
print("="*70)

# Check if credentials.json already exists
if os.path.exists('credentials.json'):
    print("\n✅ credentials.json already exists!")
    print("   OAuth2 is already set up.")
    print("   You can now run: python3 generate_reports_email.py")
    sys.exit(0)

print("\n📋 OAuth2 Setup Instructions")
print("-"*70)
print("""
Follow these steps to set up Gmail OAuth2:

1. Go to: https://console.cloud.google.com/

2. Create a new project (or use existing):
   - Click "Select a Project" → "New Project"
   - Enter project name (e.g., "Spending Report")
   - Click "Create"

3. Enable Gmail API:
   - Search for "Gmail API"
   - Click on it → "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to: APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted: Click "Configure Consent Screen"
   - Select "External" user type → "Create"
   - Fill in:
     * App name: "Spending Report"
     * User support email: (your email)
     * Developer contact: (your email)
     * Scroll down → "Save and Continue"
   - Skip scopes (click "Save and Continue")
   - Skip test users → "Save and Continue"
   - Go back to Credentials

5. Create OAuth Client:
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop application"
   - Name it: "Spending Report"
   - Click "Create"

6. Download the JSON:
   - Click the download icon (↓)
   - A JSON file will download

7. Place the file:
   - Move it to this folder
   - Rename it to: credentials.json
   - OR just drop it here if download prompts for name

8. Verify setup:
   - Type: python3 generate_reports_email.py
   - When asked, select OAuth2
   - Browser will open for login
   - Approve the Gmail access
   - Done! 🎉
""")

print("-"*70)
print("\n📝 Next Steps:")
print("  1. Follow the instructions above to get credentials.json")
print("  2. Place credentials.json in this folder")
print("  3. Run: python3 generate_reports_email.py")
print("  4. Select OAuth2 when prompted")
print("  5. Approve Gmail access in your browser")
print("\n⚠️  Already have credentials.json?")
print("  Just run: python3 generate_reports_email.py\n")

# Optional: Check if credentials.json exists after giving user time
print("Checking for credentials.json...")
for i in range(5):
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found! Setup complete.")
        print("\nYou can now run: python3 generate_reports_email.py")
        sys.exit(0)
    elif i < 4:
        print("   (waiting for file...)")
        import time
        time.sleep(1)

print("\n⏳ Waiting for credentials.json...")
print("   Place the downloaded file in this folder and name it 'credentials.json'")
print("   This script will detect it automatically.\n")

# Continue polling
try:
    while True:
        import time
        time.sleep(1)
        if os.path.exists('credentials.json'):
            print("✅ credentials.json detected! Setup complete.")
            print("\nYou can now run: python3 generate_reports_email.py\n")
            sys.exit(0)
except KeyboardInterrupt:
    print("\n\n❌ Setup cancelled.")
    print("   To try again, place credentials.json in this folder and run:")
    print("   python3 generate_reports_email.py\n")
    sys.exit(1)
