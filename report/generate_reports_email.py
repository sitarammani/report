#!/usr/bin/env python3
"""
Spending Report Generator - Command Line Version
Processes CSV and PDF bank/credit card statements and generates spending reports
"""

import pandas as pd
import re
import os
import getpass
from datetime import datetime
from pathlib import Path

# -------------------------------------------------------------------
# Security & Validation Functions
# -------------------------------------------------------------------
def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_directory_path(dir_path: str) -> bool:
    """Validate that directory path exists and is safe (no path traversal)."""
    if '..' in dir_path:
        return False
    return os.path.isdir(dir_path)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
print("\n" + "="*70)
print("SPENDING REPORT GENERATOR")
print("="*70)

# Ask for directory
print("\nEnter the directory path containing CSV/PDF statement files:")
print("  (e.g., /Users/janani/Desktop/sitapp/jan)")
dir_path = input("> ").strip()

if not dir_path:
    print("No directory specified. Using current directory.")
    dir_path = "."

# Validate directory path
if not validate_directory_path(dir_path):
    print(f"Error: Directory '{dir_path}' not found or invalid!")
    exit(1)

# Get files from specified directory
print(f"\nScanning directory: {dir_path}")
available_files = []
for f in Path(dir_path).glob("*.[cC][sS][vV]"):
    available_files.append(str(f))
    print(f"  - {f.name}")
for f in Path(dir_path).glob("*.[pP][dD][fF]"):
    available_files.append(str(f))
    print(f"  - {f.name}")

if not available_files:
    print("  No CSV or PDF files found in this directory!")
    exit(1)

# Ask user which files to process
print(f"\nFound {len(available_files)} file(s).")
print("Enter file numbers to process (comma-separated), or press Enter for all:")
for i, f in enumerate(available_files, 1):
    print(f"  {i}. {Path(f).name}")
file_input = input("> ").strip()

if file_input:
    try:
        indices = [int(x.strip()) - 1 for x in file_input.split(",")]
        file_paths = [available_files[i] for i in indices if 0 <= i < len(available_files)]
    except ValueError:
        print("Invalid input. Processing all files.")
        file_paths = available_files
else:
    file_paths = available_files

print(f"\nFiles to process:")
for f in file_paths:
    print(f"  - {f}")

# Ask for month
month_input = input("\nEnter the month for the report (MM/YYYY): ").strip()

parts = month_input.split("/")
if len(parts) != 2:
    print("Invalid format. Please enter as MM/YYYY.")
    exit(1)

mm, yyyy = parts
mm = mm.zfill(2)
target_month = int(mm)
target_year = int(yyyy)

print(f"\nGenerating report for: {mm}/{yyyy}")

# -------------------------------------------------------------------
# 1. Vendor normalization
# -------------------------------------------------------------------
def normalize_vendor(desc: str) -> str:
    d = (desc or "").upper()

    patterns = [
        (r"KROGER.*", "KROGER"),
        (r"INDIFRESH.*|TST\*INDI FRESH.*", "INDIFRESH"),
        (r"CHERIANS INTERNATIONAL.*", "CHERIANS INTERNATIONAL"),
        (r"FRESH MEAT IN MART.*", "FRESH MEAT IN MART"),
        (r"WEGMANS.*", "WEGMANS"),
        (r"PUBLIX.*", "PUBLIX"),
        (r"FCS FOOD AND NUTRITION.*", "FCS FOOD AND NUTRITION"),
        (r"AMAZON.*", "AMAZON"),
        (r"COSTCO WHSE.*", "COSTCO"),
        (r"COSTCO GAS.*", "COSTCO GAS"),
        (r"KROGER FUEL.*", "KROGER FUEL"),
        (r"SQ \*NALAN INDIAN CUISINE.*", "NALAN INDIAN CUISINE"),
        (r"TACO BELL.*", "TACO BELL"),
        (r"DOMINO'S.*", "DOMINOS"),
        (r"TARGET.*", "TARGET"),
        (r"WAL-?MART.*", "WALMART"),
        (r"DOLLAR TREE.*", "DOLLAR TREE"),
        (r"SHELL OIL.*", "SHELL"),
        (r"MCDONALD'S.*", "MCDONALDS"),
        (r"DUNKIN.*", "DUNKIN"),
        (r"CHIPOTLE.*", "CHIPOTLE"),
        (r"SUBWAY.*", "SUBWAY"),
        (r"LEAGUE TENNIS.*", "LEAGUE TENNIS"),
        (r"TELLO US.*", "TELLO"),
        (r"TMOBILE\*AUTO PAY.*", "TMOBILE"),
        (r"COMCAST-XFINITY.*", "COMCAST"),
        (r"SAWNEE ELECTRIC MEMBERSH.*", "SAWNEE ELECTRIC"),
        (r"CONSTELLATION NEW ENERGY.*", "CONSTELLATION ENERGY"),
        (r"FC WATER&SEWER.*", "FC WATER&SEWER"),
        (r"RED OAK SANITATION.*", "RED OAK SANITATION"),
        (r"WWP\*GOT BUGS INC.*", "WWP GOT BUGS"),
        (r"TRAVELERS-GEICO AGENCY.*", "TRAVELERS-GEICO"),
        (r"AAA LIFE INSURANCE.*", "AAA LIFE INSURANCE"),
        (r"THE EMORY CLINIC, INC.*", "EMORY CLINIC"),
        (r"TELADOC.*", "TELADOC"),
        (r"HAWKMUSICACADEMY.*", "HAWKMUSIC ACADEMY"),
        (r"JFI\*URBAN AIR.*", "URBAN AIR"),
        (r"AMC .*|AMC \d+ ONLINE.*", "AMC"),
        (r"TJ MAXX.*", "TJ MAXX"),
        (r"TST\* DESI DISTRICT.*", "DESI DISTRICT"),
        (r"TST\*DESI.*|SQ \*DESI.*", "DESI DISTRICT"),
        (r"SQ \*BEAUTY AMBASSADORS.*", "BEAUTY AMBASSADORS"),
        (r"TANISHQ - ATLANTA.*", "TANISHQ"),
        (r"THE HOME DEPOT .*", "HOME DEPOT"),
        (r"WAWA 118.*", "WAWA"),
        (r"ATGPAY ONLINE PA.*", "ATGPAY"),
        (r"NSM DBAMR\.COOPER.*", "NSM DBAMR.COOPER"),
        (r"HOMEDEPOT.*", "HOME DEPOT"),
        (r"DOLLAR-GENERAL.*", "DOLLAR TREE"),
        (r"PAYPAL.*", "PAYPAL"),
        (r"ROSS STORE.*", "ROSS"),
        (r"FORSYTH COUNTY.*", "FORSYTH COUNTY"),
        (r"PATEL BROTHERS.*", "PATEL BROTHERS"),
    ]

    for pattern, vendor in patterns:
        if re.match(pattern, d):
            return vendor

    return d.split()[0] if d else ""

# -------------------------------------------------------------------
# 2. Rule-based category mapping with override support
# -------------------------------------------------------------------
# Cache for category rules (loaded once on first use)
_category_rules_cache = None

def load_category_rules():
    """Load categorization rules from CSV file with override support."""
    global _category_rules_cache
    
    if _category_rules_cache is not None:
        return _category_rules_cache
    
    rules_file = "category_rules.csv"
    
    # Try to find rules file in multiple locations
    if not os.path.exists(rules_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rules_file = os.path.join(script_dir, "category_rules.csv")
    
    rules = []
    try:
        rules_df = pd.read_csv(rules_file)
        for _, row in rules_df.iterrows():
            # Handle optional fields
            override_id = row.get('OverrideRuleID', '') if 'OverrideRuleID' in row else ''
            is_custom = row.get('IsCustom', 'No') if 'IsCustom' in row else 'No'
            
            override_id = '' if pd.isna(override_id) else override_id
            
            rules.append({
                'rule_id': row['RuleID'],
                'priority': int(row['Priority']),
                'vendor_pattern': row['VendorPattern'].upper(),
                'category': row['Category'],
                'explanation': row['Explanation'],
                'override_rule_id': override_id,
                'is_custom': is_custom
            })
        # Sort by priority (descending) so highest priority rules are evaluated first
        rules.sort(key=lambda x: x['priority'], reverse=True)
        _category_rules_cache = rules
        return rules
    except Exception as e:
        print(f"Warning: Could not load category rules: {e}")
        return []

def categorize_vendor(vendor: str) -> str:
    """Categorize vendor using rule-based system with override support.
    
    Rules are evaluated in priority order:
    1. Higher priority rules are checked first
    2. User-defined (custom) rules with overrides take precedence
    3. Returns category from first matching rule
    """
    v = vendor.upper()
    rules = load_category_rules()
    
    # Evaluate each rule in priority order
    for rule in rules:
        pattern = rule['vendor_pattern']
        # Use regex matching for flexibility
        if re.match(f".*{re.escape(pattern)}.*", v):
            # Rule matched! Return its category
            # (If this rule overrides another, it was given higher priority)
            return rule['category']
    
    # Fallback to "Shopping & Retail" if no rules match
    return "Shopping & Retail"

# -------------------------------------------------------------------
# 3. Income/transfer exclusion
# -------------------------------------------------------------------
INCOME_TRANSFER_KEYWORDS = [
    "PAYROLL", "ZELLE PAYMENT FROM", "TRANSFER",
    "OVERDRAFT PROTECTION", "DEPOSIT",
    "CREDIT CARD BILL PAYMENT", "CITI AUTOPAY",
    "AUTOPAY", "ONLINE BANKING PAYMENT", "ONLINE PAYMENT",
    "ONLINE BANKING PAYMENT TO CRD",
    "BANK OF AMERICA CREDIT CARD BILL PAYMENT",
    "BA ELECTRONIC PAYMENT", "FID BKG SVC",
    "BEGINNING BALANCE", "FORSYTH COUNTY PARKS"
]

def is_income_or_transfer(desc: str) -> bool:
    d = (desc or "").upper()
    return any(k in d for k in INCOME_TRANSFER_KEYWORDS)

# -------------------------------------------------------------------
# 4. Safe date parsing + month filter helper
# -------------------------------------------------------------------
def parse_date_safe(x):
    x = str(x).strip()
    if not x:
        return None
    # Try with year first, then without year (add current target year)
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%m/%d"):
        try:
            dt = datetime.strptime(x, fmt)
            # If no year was parsed, use target year
            if dt.year == 1900:
                dt = dt.replace(year=target_year)
            return dt
        except ValueError:
            continue
    return None

def filter_to_month(df, date_col_name: str):
    df["parsed_date"] = df[date_col_name].astype(str).apply(parse_date_safe)
    df = df[df["parsed_date"].notna()]
    df = df[
        (df["parsed_date"].dt.month == target_month) &
        (df["parsed_date"].dt.year == target_year)
    ]
    return df

# -------------------------------------------------------------------
# 5. PDF extraction
# -------------------------------------------------------------------
def extract_from_pdf(path):
    """Extract transaction data from PDF credit card statement"""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            transactions = []
            in_transaction_section = False
            
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')
                
                for line in lines:
                    # Look for the start of transaction sections
                    if 'standard purchases' in line.lower() or ('year to date' in line.lower() and ':' in line):
                        in_transaction_section = True
                        continue
                    
                    if in_transaction_section:
                        # Stop at specific keywords indicating end of transaction list
                        if any(x in line.lower() for x in ['fees charged', 'interest charged', 'earned this period', 'cardholder summary']):
                            in_transaction_section = False
                            continue
                        
                        # Skip lines that don't look like transactions
                        if not line.strip() or 'date' in line.lower() or '%' in line:
                            continue
                        
                        # Parse transaction lines using regex
                        match = re.search(r'(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.+?)\s+(\$[\d,\.]+)', line)
                        if match:
                            post_date = match.group(2)
                            description = match.group(3).strip()
                            amount_str = match.group(4).strip()
                            
                            try:
                                amount = float(amount_str.replace('$', '').replace(',', ''))
                                amount = -abs(amount)
                                
                                transactions.append({
                                    'date': post_date,
                                    'description': description,
                                    'amount': amount
                                })
                            except:
                                continue
            
            if not transactions:
                raise ValueError("No transactions found in PDF")
            
            df = pd.DataFrame(transactions)
            df.columns = df.columns.str.strip().str.lower()
            return df
    except Exception as e:
        raise ValueError(f"Failed to extract PDF: {e}")

# -------------------------------------------------------------------
# 6. Smart loader
# -------------------------------------------------------------------
def load_any_statement(path):
    # Check if it's a PDF
    if path.lower().endswith('.pdf'):
        try:
            df = extract_from_pdf(path)
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            raise
    else:
        # Try reading CSV normally; fallback for stmt.csv
        try:
            df = pd.read_csv(path)
        except:
            df = pd.read_csv(path, skiprows=5)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # FORMAT 1: Bank stmt.csv (Date, Description, Amount, Running Bal.)
    if any("bal" in c for c in df.columns) and "amount" in df.columns and "description" in df.columns:
        df = df[["date", "description", "amount"]]
        df["amount"] = (
            df["amount"].astype(str)
            .str.replace(",", "")
            .astype(float)
        )
        df = df[~df["description"].apply(is_income_or_transfer)]
        df = filter_to_month(df, "date")
        df["vendor"] = df["description"].apply(normalize_vendor)
        df["category"] = df["vendor"].apply(categorize_vendor)
        return df[["date", "vendor", "category", "amount"]]

    # FORMAT 2: Credit Card Type A (Posted Date, Payee, Amount)
    if "posted date" in df.columns and "payee" in df.columns and "amount" in df.columns:
        df = df[["posted date", "payee", "amount"]]
        df.columns = ["date", "description", "amount"]
        df["amount"] = (
            df["amount"].astype(str)
            .str.replace(",", "")
            .astype(float)
        )
        df = df[~df["description"].apply(is_income_or_transfer)]
        df = filter_to_month(df, "date")
        df["vendor"] = df["description"].apply(normalize_vendor)
        df["category"] = df["vendor"].apply(categorize_vendor)
        return df[["date", "vendor", "category", "amount"]]

    # FORMAT 3: Credit Card Type B (Date, Description, Credit, Debit)
    if "credit" in df.columns and "debit" in df.columns and "description" in df.columns and "date" in df.columns:
        credit = pd.to_numeric(df["credit"].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
        debit = pd.to_numeric(df["debit"].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
        df["amount"] = credit - debit
        # Exclude income/transfer-like descriptions (AUTOPAY, ONLINE PAYMENT, ZELLE, etc.)
        df = df[~df["description"].apply(is_income_or_transfer)]
        df = filter_to_month(df, "date")
        df["vendor"] = df["description"].apply(normalize_vendor)
        df["category"] = df["vendor"].apply(categorize_vendor)
        return df[["date", "vendor", "category", "amount"]]

    # FORMAT 4: PDF extraction (Date, Description, Amount)
    if "date" in df.columns and "description" in df.columns and "amount" in df.columns:
        df = df[["date", "description", "amount"]]
        df["amount"] = (
            df["amount"].astype(str)
            .str.replace(",", "")
            .astype(float)
        )
        df = df[~df["description"].apply(is_income_or_transfer)]
        df = filter_to_month(df, "date")
        df["vendor"] = df["description"].apply(normalize_vendor)
        df["category"] = df["vendor"].apply(categorize_vendor)
        return df[["date", "vendor", "category", "amount"]]

    raise ValueError(f"Unrecognized format in file: {path}")

# -------------------------------------------------------------------
# 7. Load all selected files
# -------------------------------------------------------------------
all_dfs = []

for path in file_paths:
    try:
        print(f"Processing: {path}")
        df = load_any_statement(path)
        all_dfs.append(df)
        print(f"  ✓ Loaded {len(df)} transactions")
    except Exception as e:
        print(f"  ✗ Skipping: {e}")

if not all_dfs:
    print("No valid files found for that month. Exiting.")
    exit(1)

all_txns = pd.concat(all_dfs, ignore_index=True)
all_txns.columns = ["Date", "Vendor", "Category", "Amount"]
all_txns["ParsedDate"] = all_txns["Date"].astype(str).apply(parse_date_safe)

print(f"\n✓ Total transactions loaded: {len(all_txns)}")

# -------------------------------------------------------------------
# 8. Build Reports
# -------------------------------------------------------------------

# Load category order dynamically from categories.csv
try:
    categories_file = os.path.join(os.path.dirname(__file__), "categories.csv")
    if os.path.exists(categories_file):
        cats_df = pd.read_csv(categories_file)
        category_order = cats_df["CategoryName"].tolist()
    else:
        # Fallback if categories.csv doesn't exist
        category_order = [
            "Groceries & Markets",
            "Restaurants & Food",
            "Shopping & Retail",
            "Auto & Gas",
            "Utilities Bills & Insurance",
            "Health",
            "Entertainment",
            "Home & Services"
        ]
except:
    # Fallback on any error
    category_order = [
        "Groceries & Markets",
        "Restaurants & Food",
        "Shopping & Retail",
        "Auto & Gas",
        "Utilities Bills & Insurance",
        "Health",
        "Entertainment",
        "Home & Services"
    ]

# Report 1: Category → Vendor totals
report1_rows = []
for cat in category_order:
    cat_df = all_txns[all_txns["Category"] == cat]
    if cat_df.empty:
        continue

    report1_rows.append([cat, "", ""])
    vendor_totals = (
        cat_df.groupby("Vendor")["Amount"]
        .sum()
        .reset_index()
    )
    for _, row in vendor_totals.iterrows():
        report1_rows.append(["", row["Vendor"], f"{row['Amount']:.2f}"])

    category_total = vendor_totals["Amount"].sum()
    report1_rows.append(["", "Category Total", f"{category_total:.2f}"])
    report1_rows.append(["", "", ""])

report1_df = pd.DataFrame(report1_rows, columns=["Category", "Vendor", "Total"])

# Report 2: Category totals + percent
cat_totals = []
for cat in category_order:
    cat_df = all_txns[all_txns["Category"] == cat]
    if not cat_df.empty:
        cat_totals.append((cat, cat_df["Amount"].sum()))

grand_total = sum(t for _, t in cat_totals)

report2_rows = [["Category", "Total", "Percent"]]
for cat, total in cat_totals:
    pct = abs(total) / abs(grand_total) * 100 if grand_total != 0 else 0
    report2_rows.append([cat, f"{total:.2f}", f"{pct:.2f}%"])
report2_rows.append(["Total", f"{grand_total:.2f}", "100.00%"])

report2_df = pd.DataFrame(report2_rows[1:], columns=report2_rows[0])

# Report 3: Transactions > $200
report3_df = all_txns[all_txns["Amount"].abs() > 200].copy()
report3_df = report3_df.sort_values("ParsedDate")

# -------------------------------------------------------------------
# 9. Write Excel
# -------------------------------------------------------------------
OUTPUT_FILE = f"Spending_Report_{mm}_{yyyy}.xlsx"

try:
    with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
        workbook = writer.book

        header_fmt = workbook.add_format({
            "bold": True,
            "font_color": "white",
            "bg_color": "#4F81BD",
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True
        })

        total_green_fmt = workbook.add_format({
            "bg_color": "#C6EFCE",
            "bold": True,
            "text_wrap": True
        })

        wrap_fmt = workbook.add_format({"text_wrap": True})

        # Report 1
        ws1 = workbook.add_worksheet("Report_1")
        writer.sheets["Report_1"] = ws1

        headers1 = list(report1_df.columns)
        for col, h in enumerate(headers1):
            ws1.write(0, col, h, header_fmt)

        for r in range(len(report1_df)):
            row_values = report1_df.iloc[r]
            is_total = "total" in str(row_values.values).lower()
            fmt = total_green_fmt if is_total else wrap_fmt
            for c in range(len(headers1)):
                ws1.write(r + 1, c, row_values.iloc[c], fmt)

        ws1.set_column("A:C", 25, wrap_fmt)

        # Report 2
        ws2 = workbook.add_worksheet("Report_2")
        writer.sheets["Report_2"] = ws2

        headers2 = list(report2_df.columns)
        for col, h in enumerate(headers2):
            ws2.write(0, col, h, header_fmt)

        for r in range(len(report2_df)):
            row_values = report2_df.iloc[r]
            is_total = "total" in str(row_values.values).lower()
            fmt = total_green_fmt if is_total else wrap_fmt
            for c in range(len(headers2)):
                ws2.write(r + 1, c, row_values.iloc[c], fmt)

        ws2.set_column("A:C", 25, wrap_fmt)

        # Report 3
        ws3 = workbook.add_worksheet("Report_3")
        writer.sheets["Report_3"] = ws3

        headers3 = ["Date", "Category", "Vendor", "Amount"]
        for col, h in enumerate(headers3):
            ws3.write(0, col, h, header_fmt)

        for r in range(len(report3_df)):
            row = report3_df.iloc[r]
            for c, colname in enumerate(headers3):
                ws3.write(r + 1, c, row[colname], wrap_fmt)

        ws3.set_column("A:D", 25, wrap_fmt)

    print(f"\n✓ Excel report generated: {OUTPUT_FILE}")
except Exception as e:
    print(f"\n✗ Error generating Excel: {e}")

# -------------------------------------------------------------------
# 10. Email sending (optional)
# -------------------------------------------------------------------
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import base64

# Optional Gmail API imports (for OAuth2)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_API_AVAILABLE = True
except Exception:
    GMAIL_API_AVAILABLE = False

print("\nWould you like to send this report via email? (y/n): ", end="")
send_email = input().strip().lower() == 'y'

def get_gmail_credentials():
    """Load or run OAuth flow to obtain Gmail API credentials.
    Requires `credentials.json` (OAuth client) in the working directory.
    Stores user token in `token.json` for reuse.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    token_path = 'token.json'
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

    if not creds:
        if not os.path.exists('credentials.json'):
            raise FileNotFoundError(
                '\n❌ credentials.json not found.\n\n'
                'To set up Gmail OAuth2:\n'
                '1. Create OAuth credentials in Google Cloud Console\n'
                '2. Download the JSON file and save it as "credentials.json" in this folder\n'
                '3. Run: python oauth_setup.py\n\n'
                'See GMAIL_OAUTH_SETUP.md for detailed instructions.\n'
                'Or use SMTP with your email password as an alternative.'
            )
        try:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for next run
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            raise RuntimeError(
                f'Failed to authenticate with Gmail OAuth:\n{e}\n\n'
                'Make sure credentials.json is a valid OAuth client credentials file.'
            )
    return creds

def get_gmail_credentials_for_smtp():
    """Get OAuth2 credentials with full mail scope usable for SMTP XOAUTH2."""
    SCOPES = ['https://mail.google.com/']
    token_path = 'token_smtp.json'
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

    if not creds:
        if not os.path.exists('credentials.json'):
            raise FileNotFoundError('credentials.json not found. Create OAuth credentials in Google Cloud Console and save as credentials.json')
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
    return creds

def send_via_smtp_xoauth2(creds, sender, recipient, msg, smtp_host='smtp.gmail.com', smtp_port=587):
    """Authenticate to SMTP using XOAUTH2 and send message."""
    # Ensure token is valid
    if not creds.valid:
        try:
            creds.refresh(Request())
        except Exception:
            pass

    access_token = creds.token
    if not access_token:
        raise ValueError('No access token available')

    auth_string = f'user={sender}\x01auth=Bearer {access_token}\x01\x01'
    auth_b64 = base64.b64encode(auth_string.encode()).decode()

    # Use STARTTLS on port 587
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    code, resp = server.docmd('AUTH', 'XOAUTH2 ' + auth_b64)
    if code != 235:
        server.quit()
        raise RuntimeError(f'SMTP XOAUTH2 authentication failed: {code} {resp}')
    server.send_message(msg)
    server.quit()

def send_via_gmail_api(creds, sender, recipient, msg):
    """Send MIMEMultipart `msg` via Gmail API using `creds`."""
    service = build('gmail', 'v1', credentials=creds)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {'raw': raw}
    return service.users().messages().send(userId='me', body=body).execute()

if send_email:
    print("\n" + "="*70)
    print("EMAIL CONFIGURATION")
    print("="*70)
    sender_email = input("\nSender email: ").strip()
    if not validate_email(sender_email):
        print(f"❌ Invalid email format: {sender_email}")
        send_email = False
    else:
        recipient_email = input("Recipient email: ").strip()
        if not validate_email(recipient_email):
            print(f"❌ Invalid email format: {recipient_email}")
            send_email = False
    
    if not send_email:
        print("Skipping email delivery.")

if send_email:
    # Build email content
    subject = f"Spending Report for {mm}/{yyyy}"
    report2_html_table = report2_df.to_html(index=False, border=1)
    report3_html_table = report3_df[["Date", "Category", "Vendor", "Amount"]].to_html(index=False, border=1)
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
    <p>Hello,</p>
    <p>Your spending report for <strong>{mm}/{yyyy}</strong> is attached.</p>
    <h3>Category Summary</h3>
    {report2_html_table}
    <h3>Large Transactions (> $200)</h3>
    {report3_html_table}
    <p>Best regards,<br>Automated Report System</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))

    # Attach Excel file
    with open(OUTPUT_FILE, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {OUTPUT_FILE}")
    msg.attach(part)

    # ========================================================
    # AUTHENTICATION METHOD SELECTION
    # ========================================================
    print("\n" + "-"*70)
    print("Authentication Method (RECOMMENDED: OAuth2)")
    print("-"*70)
    
    use_oauth = True
    auth_method = "oauth"
    
    if not GMAIL_API_AVAILABLE:
        print("⚠️  Gmail OAuth2 not available (missing dependencies)")
        print("Falling back to SMTP email...")
        use_oauth = False
    elif not os.path.exists('credentials.json'):
        print("\n📝 OAuth2 Requires Setup (First Time Only)")
        print("\nTo use OAuth2, place 'credentials.json' in this folder:")
        print("  1. Go to: https://console.cloud.google.com/")
        print("  2. Create OAuth 2.0 Client ID (Desktop app)")
        print("  3. Download JSON file → save as 'credentials.json'")
        print("\nUse SMTP instead? (Gmail App Password - simpler)")
        choice = input("\nUse OAuth2 (requires setup) or SMTP? [oauth/smtp]: ").strip().lower()
        
        if choice in ['oauth', 'o']:
            print("❌ Cannot proceed without credentials.json")
            print("   Please set up OAuth credentials and try again.")
            send_email = False
            use_oauth = False
        else:
            use_oauth = False
            auth_method = "smtp"
    else:
        print("✅ OAuth2 credentials found")
        print("\n🔐 Secure Email Authentication")
        print("A browser window will open for you to authorize Gmail access.")
        print("No passwords will be stored or transmitted unsecurely.\n")

    # ========================================================
    # OAUTH2 METHOD (RECOMMENDED)
    # ========================================================
    if send_email and use_oauth:
        try:
            print("⏳ Authenticating with Gmail OAuth2...")
            creds = get_gmail_credentials()
            print("✓ Authentication successful!")
            
            print(f"📧 Sending email to {recipient_email}...")
            send_via_gmail_api(creds, sender_email, recipient_email, msg)
            print(f"✅ Email sent successfully!\n")
            
        except Exception as e:
            print(f"❌ OAuth2 failed: {e}")
            print("\n⚠️  Falling back to SMTP (App Password)...")
            use_oauth = False
            auth_method = "smtp"
    
    # ========================================================
    # SMTP FALLBACK (App Password)
    # ========================================================
    if send_email and not use_oauth:
        print("\n" + "-"*70)
        print("Gmail SMTP Configuration (Using App Password)")
        print("-"*70)
        print("\n📝 Setup Instructions (First Time Only):")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Select: Mail → Your Device Type")
        print("  3. Google generates a 16-character password")
        print("  4. Copy and paste it below (won't display on screen)")
        print("\n🔒 Security Note: This password only works for email")
        
        try:
            sender_password = getpass.getpass("\nPaste your Gmail App Password: ").strip()
            
            if not sender_password:
                print("❌ No password provided")
                send_email = False
            else:
                smtp_host = "smtp.gmail.com"
                smtp_port = 587
                
                print(f"\n⏳ Connecting to {smtp_host}:{smtp_port}...")
                with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                print(f"✅ Email sent successfully to {recipient_email}!\n")
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            print("\n💡 Troubleshooting:")
            print("   - Is the App Password correct? (16 characters)")
            print("   - Did you enable 2-Step Verification on Google Account?")
            print("   - Try creating a new App Password")
            print("   - Check your internet connection")

# -------------------------------------------------------------------
# 11. Print Summary
# -------------------------------------------------------------------
print("\n" + "="*70)
print(f"SPENDING SUMMARY FOR {mm}/{yyyy}")
print("="*70)
print("\nCategory Breakdown:")
print("-"*70)
for cat, total in cat_totals:
    pct = abs(total) / abs(grand_total) * 100 if grand_total != 0 else 0
    print(f"  {cat:40s} ${abs(total):>10.2f} ({pct:5.1f}%)")
print("-"*70)
print(f"  {'TOTAL':40s} ${abs(grand_total):>10.2f} (100.0%)")
print("="*70)

if len(report3_df) > 0:
    print(f"\nLarge Transactions (> $200): {len(report3_df)}")
    print("-"*70)
    for _, row in report3_df.head(10).iterrows():
        print(f"  {row['Date']} | {row['Vendor']:40s} ${abs(row['Amount']):>10.2f}")
    if len(report3_df) > 10:
        print(f"  ... and {len(report3_df) - 10} more")
else:
    print("\nNo transactions over $200")

print("\n")

# -------------------------------------------------------------------
# 12. Suggest Using LLM for Natural Language Analysis
# -------------------------------------------------------------------
print("="*70)
print("💡 TIP: Ask questions about your spending with AI!")
print("="*70)
print("\nUse Natural Language Query to analyze your data:")
print("\n  python3 natural_language_query.py")
print("\nExample questions:")
print('  • "How much did I spend on education?"')
print('  • "What\'s my highest spending category?"')
print('  • "Analyze my spending patterns and suggest savings"')
print("\nRuns completely locally - no API keys or internet needed!")
print("="*70 + "\n")
