#!/usr/bin/env python3
"""
Automated Gmail OAuth2 Setup
Opens browser to create OAuth credentials, stores them locally.
No manual file downloads needed.
"""

import os
import json
import webbrowser
from pathlib import Path

CONFIG_FILE = '.gmail_oauth_config'

def setup_oauth():
    """Interactive setup for Gmail OAuth2."""
    
    print("\n" + "="*70)
    print("GMAIL OAUTH2 SETUP (One-Time Only)")
    print("="*70)
    
    if os.path.exists(CONFIG_FILE):
        print("\n✅ OAuth2 already configured!")
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"   Client ID: {config['client_id'][:20]}...")
        return
    
    print("""
📋 Setup Instructions (2 minutes):

1. Click the link below to open Google Cloud Console
2. Follow the automated steps to create an OAuth Desktop app
3. Copy the Client ID
4. Copy the Client Secret  
5. Paste them back here

Let's get started!
""")
    
    # Open Google Cloud Console
    console_url = "https://console.cloud.google.com/apis/credentials"
    print("Opening Google Cloud Console in your browser...")
    webbrowser.open(console_url)
    
    print("\n" + "-"*70)
    print("""
Quick Setup Steps:
  1. Create a NEW PROJECT (name: "Spending Report")
  2. Search for "Gmail API" and ENABLE it
  3. Go to: Credentials → Create Credentials → OAuth Client ID
  4. Choose: Desktop Application
  5. Download the JSON (contains client_id and client_secret)
  6. Come back here and paste the values below
""")
    print("-"*70)
    
    # Get credentials from user
    print("\nPaste your OAuth credentials below:")
    print("(You can paste the entire JSON or individual values)\n")
    
    client_id = input("Enter Client ID: ").strip()
    client_secret = input("Enter Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("\n❌ Both Client ID and Secret are required!")
        return False
    
    # Store configuration
    config = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scopes': ['https://www.googleapis.com/auth/gmail.send']
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    os.chmod(CONFIG_FILE, 0o600)  # Restrict permissions
    
    print("\n✅ OAuth2 configured successfully!")
    print("   You can now run: python3 generate_reports_email.py")
    print("   Browser will open for Google login\n")
    return True


if __name__ == '__main__':
    try:
        setup_oauth()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.")
