#!/usr/bin/env python3
"""
Spending Report Generator - Command Line Version
Processes CSV and PDF bank/credit card statements and generates spending reports
"""

import pandas as pd
import re
import os
from datetime import datetime
from pathlib import Path

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

# Check if directory exists
if not os.path.isdir(dir_path):
    print(f"Error: Directory '{dir_path}' not found!")
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
    ]

    for pattern, vendor in patterns:
        if re.match(pattern, d):
            return vendor

    return d.split()[0] if d else ""

# -------------------------------------------------------------------
# 2. Category mapping
# -------------------------------------------------------------------
def categorize_vendor(vendor: str) -> str:
    v = vendor.upper()

    groceries = {
        "KROGER", "INDIFRESH", "CHERIANS INTERNATIONAL",
        "FRESH MEAT IN MART", "WEGMANS", "PUBLIX",
        "FCS FOOD AND NUTRITION", "COSTCO"
    }

    restaurants = {
        "TACO BELL", "DOMINOS", "SUBWAY", "CHIPOTLE",
        "MCDONALDS", "DESI DISTRICT", "NALAN INDIAN CUISINE",
        "DUNKIN"
    }

    shopping = {
        "AMAZON", "BESTBUY", "TARGET", "WALMART",
        "TJ MAXX", "BEAUTY AMBASSADORS", "TANISHQ", "ROSS", "DOLLAR TREE"
    }

    auto_gas = {"COSTCO GAS", "KROGER FUEL", "SHELL", "WAWA"}

    utilities = {
        "COMCAST", "TMOBILE", "SAWNEE ELECTRIC",
        "CONSTELLATION ENERGY", "TELLO", "TRAVELERS-GEICO",
        "AAA LIFE INSURANCE", "FC WATER&SEWER",
        "RED OAK SANITATION", "ATGPAY", "NSM DBAMR.COOPER"
    }

    health = {"TELADOC", "EMORY CLINIC"}

    entertainment = {
        "AMC", "URBAN AIR", "HAWKMUSIC ACADEMY", "LEAGUE TENNIS"
    }

    home_services = {"HOME DEPOT", "WWP GOT BUGS"}

    if v in groceries:
        return "Groceries & Markets"
    if v in restaurants:
        return "Restaurants & Food"
    if v in auto_gas:
        return "Auto & Gas"
    if v in utilities:
        return "Utilities Bills & Insurance"
    if v in health:
        return "Health"
    if v in entertainment:
        return "Entertainment"
    if v in home_services:
        return "Home & Services"
    if v in shopping:
        return "Shopping & Retail"

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
    "BEGINNING BALANCE"
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

print("\nWould you like to send this report via email? (y/n): ", end="")
send_email = input().strip().lower() == 'y'

if send_email:
    print("\nEmail Configuration:")
    sender_email = input("  Sender email: ").strip()
    sender_password = input("  Sender password (or app password): ").strip()
    recipient_email = input("  Recipient email: ").strip()
    smtp_host = input("  SMTP host (e.g., smtp.gmail.com) [default: smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    smtp_port = input("  SMTP port [default: 465]: ").strip() or "465"
    
    try:
        smtp_port = int(smtp_port)
        
        # Build email
        subject = f"Spending Report for {mm}/{yyyy}"
        
        # Create HTML email body
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
        
        <p>Best regards,<br>
        Automated Report System</p>
        
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
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {OUTPUT_FILE}"
        )
        
        msg.attach(part)
        
        # Send email
        print(f"\nConnecting to {smtp_host}:{smtp_port}...")
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"✓ Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"✗ Error sending email: {e}")

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
