#!/usr/bin/env python3
"""
Gmail Authentication Module
Handles OAuth2 and SMTP authentication for sending emails via Gmail.
"""

import os
import smtplib
import ssl
import base64
import getpass
import certifi

# Optional Gmail API imports (for OAuth2)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_API_AVAILABLE = True
except Exception:
    GMAIL_API_AVAILABLE = False


class GmailAuth:
    """Handles Gmail authentication via OAuth2 or SMTP."""

    CONFIG_FILE = os.path.join(os.path.dirname(__file__), '.gmail_oauth_config')

    def __init__(self):
        self.gmail_api_available = GMAIL_API_AVAILABLE

    @staticmethod
    def _load_oauth_config():
        """Load OAuth config from stored file."""
        import json
        if not os.path.exists(GmailAuth.CONFIG_FILE):
            raise FileNotFoundError(
                f'{GmailAuth.CONFIG_FILE} not found. Run: python3 setup_gmail_oauth.py'
            )
        with open(GmailAuth.CONFIG_FILE, 'r') as f:
            return json.load(f)

    # ========================================================
    # OAuth2 Authentication
    # ========================================================
    def get_oauth2_credentials(self, scope='gmail_api'):
        """Get OAuth2 credentials for Gmail API.
        
        Args:
            scope: 'gmail_api' for Gmail API
        
        Returns:
            Credentials object
        """
        if not self.gmail_api_available:
            raise RuntimeError('Gmail API libraries not available. Install: google-auth-oauthlib')

        scopes = ['https://www.googleapis.com/auth/gmail.send']
        token_path = 'token.json'

        # Try to load existing token
        creds = None
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, scopes)
            except Exception:
                creds = None

        # Check if token is still valid
        if creds and not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
            else:
                creds = None

        # If no valid token, run OAuth flow
        if not creds:
            config = self._load_oauth_config()
            
            try:
                # Create flow from config (no need for credentials.json file)
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": config['client_id'],
                            "client_secret": config['client_secret'],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                    },
                    scopes
                )
                creds = flow.run_local_server(port=0)
                # Save token for future use
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
            except Exception as e:
                raise RuntimeError(f'OAuth2 authentication failed: {e}')

        return creds

    # ========================================================
    # Gmail API Send
    # ========================================================
    def send_via_gmail_api(self, sender_email, recipient_email, msg):
        """Send email via Gmail API."""
        if not self.gmail_api_available:
            raise RuntimeError('Gmail API not available')

        creds = self.get_oauth2_credentials(scope='gmail_api')
        service = build('gmail', 'v1', credentials=creds)
        
        import email.mime.base
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        body = {'raw': raw}
        return service.users().messages().send(userId='me', body=body).execute()

    # ========================================================
    # SMTP Authentication (OAuth2 XOAUTH2)
    # ========================================================
    def send_via_smtp_oauth2(self, sender_email, recipient_email, msg):
        """Send email via SMTP using OAuth2 XOAUTH2."""
        creds = self.get_oauth2_credentials(scope='smtp')

        # Ensure token is valid
        if not creds.valid:
            try:
                creds.refresh(Request())
            except Exception:
                pass

        access_token = creds.token
        if not access_token:
            raise ValueError('No access token available')

        auth_string = f'user={sender_email}\x01auth=Bearer {access_token}\x01\x01'
        auth_b64 = base64.b64encode(auth_string.encode()).decode()

        context = ssl.create_default_context(cafile=certifi.where())
        
        try:
            # Try STARTTLS first
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                code, resp = server.docmd('AUTH', 'XOAUTH2 ' + auth_b64)
                if code != 235:
                    raise RuntimeError(f'SMTP XOAUTH2 auth failed: {code} {resp}')
                server.send_message(msg)
                return
        except Exception as e:
            # Fallback to SMTPS
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=60) as server:
                    code, resp = server.docmd('AUTH', 'XOAUTH2 ' + auth_b64)
                    if code != 235:
                        raise RuntimeError(f'SMTP XOAUTH2 auth failed (SSL): {code} {resp}')
                    server.send_message(msg)
                    return
            except Exception:
                raise

    # ========================================================
    # SMTP Login (Email + Password)
    # ========================================================
    def send_via_smtp_login(self, sender_email, recipient_email, msg, password=None):
        """Send email via SMTP using email + password login."""
        if not password:
            password = getpass.getpass("Enter your Gmail password: ").strip()

        context = ssl.create_default_context(cafile=certifi.where())

        try:
            # Try STARTTLS first
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(sender_email, password)
                server.send_message(msg)
                return True
        except smtplib.SMTPAuthenticationError as e:
            # Check if error is due to 2-Step Verification
            if self._is_app_password_required(e):
                self._show_app_password_instructions()
                return False
            else:
                raise
        except Exception as e:
            # Try SMTPS fallback
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=60) as server:
                    server.login(sender_email, password)
                    server.send_message(msg)
                    return True
            except smtplib.SMTPAuthenticationError as e2:
                if self._is_app_password_required(e2):
                    self._show_app_password_instructions()
                    return False
                else:
                    raise
            except Exception:
                raise

    # ========================================================
    # Helper Methods
    # ========================================================
    def _is_app_password_required(self, error):
        """Check if error indicates App Password is required."""
        error_str = str(error)
        return "534" in error_str or "Application-specific password" in error_str

    def _show_app_password_instructions(self):
        """Display instructions for generating an App Password."""
        print("\n" + "="*70)
        print("❌ Gmail requires an App Password")
        print("="*70)
        print("\nYour account has 2-Step Verification enabled.")
        print("Gmail blocks direct password login for security reasons.\n")
        print("📱 To generate an App Password:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Sign in with your Google account")
        print("  3. Select 'Mail' and 'Windows Computer' (or your device type)")
        print("  4. Google will generate a 16-character password")
        print("  5. Copy that password and use it instead of your account password\n")
        print("Then run this script again and enter the App Password when prompted.")
        print("="*70 + "\n")

    def prompt_authentication_method(self):
        """Automatically use OAuth2 (no user choice needed).
        
        Returns:
            'oauth' tuple
        """
        if not self.gmail_api_available:
            raise RuntimeError(
                'Gmail API libraries not available.\n'
                'Install: pip install google-auth-oauthlib'
            )

        if not os.path.exists(self.CONFIG_FILE):
            print("\n" + "="*70)
            print("⚠️  Gmail OAuth2 Not Configured")
            print("="*70)
            print("""
Please set up Gmail OAuth2 first:
  Run: python3 setup_gmail_oauth.py

This will:
  1. Guide you through creating OAuth credentials
  2. You just paste the Client ID and Secret
  3. Everything else is automatic!

Takes 2 minutes, done once.
""")
            print("="*70 + "\n")
            raise FileNotFoundError('OAuth2 not configured. Run: python3 setup_gmail_oauth.py')
        else:
            return ('oauth', None)


# Convenience functions for backward compatibility
def send_email(sender_email, recipient_email, msg, method='oauth', password=None):
    """Send email using the specified authentication method.
    
    Args:
        sender_email: Gmail address
        recipient_email: Recipient email address
        msg: MIMEMultipart message object
        method: 'oauth', 'smtp_oauth', or 'smtp_login'
        password: Password (for smtp_login method)
    """
    auth = GmailAuth()

    if method == 'oauth':
        return auth.send_via_gmail_api(sender_email, recipient_email, msg)
    elif method == 'smtp_oauth':
        return auth.send_via_smtp_oauth2(sender_email, recipient_email, msg)
    elif method == 'smtp_login':
        return auth.send_via_smtp_login(sender_email, recipient_email, msg, password)
    else:
        raise ValueError(f'Invalid method: {method}')


if __name__ == '__main__':
    print("Gmail Auth module - use in your scripts")
    auth = GmailAuth()
    print(f"Gmail API available: {auth.gmail_api_available}")
