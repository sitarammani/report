import pandas as pd
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# -------------------------------------------------------------------
# 1. File names
# -------------------------------------------------------------------
FILE_STMT = "stmt.csv"
FILE_DEC_1004 = "December2025_1004.csv"
FILE_CURRENT_1004 = "currentTransaction_1004.csv"
FILE_CLOSED_DEC15 = "Statement closed Dec 15, 2025.CSV"
FILE_SINCE_DEC16 = "Since Dec 16, 2025.CSV"
OUTPUT_FILE = "December_2025_Spending_Report.xlsx"

# -------------------------------------------------------------------
# 2. Vendor normalization
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
    ]

    for pattern, vendor in patterns:
        if re.match(pattern, d):
            return vendor

    return d.split()[0] if d else ""

# -------------------------------------------------------------------
# 3. Category mapping
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
        "TJ MAXX", "BEAUTY AMBASSADORS", "TANISHQ"
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
# 4. Income/transfer exclusion
# -------------------------------------------------------------------
INCOME_TRANSFER_KEYWORDS = [
    "PAYROLL", "ZELLE PAYMENT FROM", "TRANSFER",
    "OVERDRAFT PROTECTION", "DEPOSIT",
    "CREDIT CARD BILL PAYMENT", "CITI AUTOPAY",
    "AUTOPAY", "ONLINE BANKING PAYMENT",
    "ONLINE BANKING PAYMENT TO CRD",
    "BANK OF AMERICA CREDIT CARD BILL PAYMENT",
    "BA ELECTRONIC PAYMENT", "FID BKG SVC",
    "BEGINNING BALANCE"
]

def is_income_or_transfer(desc: str) -> bool:
    d = (desc or "").upper()
    return any(k in d for k in INCOME_TRANSFER_KEYWORDS)

# -------------------------------------------------------------------
# 5. Loaders
# -------------------------------------------------------------------
def load_stmt():
    df = pd.read_csv(FILE_STMT, skiprows=5)
    df = df[df["Date"].astype(str).str.startswith("12/")]
    df = df[~df["Description"].apply(is_income_or_transfer)]
    df["Amount"] = (
        df["Amount"].astype(str)
        .str.replace(",", "")
        .replace("", "0")
        .astype(float)
    )
    df["Vendor"] = df["Description"].apply(normalize_vendor)
    df["Category"] = df["Vendor"].apply(categorize_vendor)
    return df[["Date", "Vendor", "Category", "Amount"]]

def load_cc_basic(path, date_col, desc_col, amt_col):
    df = pd.read_csv(path)
    df = df[df[date_col].astype(str).str.startswith("12/")]
    df = df[[date_col, desc_col, amt_col]].copy()
    df.columns = ["Date", "Description", "Amount"]
    df["Amount"] = (
        df["Amount"].astype(str)
        .str.replace(",", "")
        .replace("", "0")
        .astype(float)
    )
    df["Vendor"] = df["Description"].apply(normalize_vendor)
    df["Category"] = df["Vendor"].apply(categorize_vendor)
    return df[["Date", "Vendor", "Category", "Amount"]]

def load_closed_dec15():
    raw = pd.read_csv(FILE_CLOSED_DEC15)
    raw = raw[raw["Date"].astype(str).str.startswith("12/")]

    credit = (
        raw["Credit"].astype(str)
        .str.replace(",", "")
        .replace("", "0")
    )
    debit = (
        raw["Debit"].astype(str)
        .str.replace(",", "")
        .replace("", "0")
    )

    credit = pd.to_numeric(credit, errors="coerce").fillna(0)
    debit = pd.to_numeric(debit, errors="coerce").fillna(0)

    amount = credit - debit

    df = pd.DataFrame({
        "Date": raw["Date"],
        "Vendor": raw["Description"].apply(normalize_vendor),
        "Category": raw["Description"].apply(
            lambda x: categorize_vendor(normalize_vendor(x))
        ),
        "Amount": amount
    })
    return df

def load_since_dec16():
    raw = pd.read_csv(FILE_SINCE_DEC16)
    raw = raw[raw["Date"].astype(str).str.startswith("12/")]

    credit = (
        raw["Credit"].astype(str)
        .str.replace(",", "")
        .replace("", "0")
    )
    debit = (
        raw["Debit"].astype(str)
        .str.replace(",", "")
        .replace("", "0")
    )

    credit = pd.to_numeric(credit, errors="coerce").fillna(0)
    debit = pd.to_numeric(debit, errors="coerce").fillna(0)

    amount = credit - debit

    df = pd.DataFrame({
        "Date": raw["Date"],
        "Vendor": raw["Description"].apply(normalize_vendor),
        "Category": raw["Description"].apply(
            lambda x: categorize_vendor(normalize_vendor(x))
        ),
        "Amount": amount
    })
    return df

# -------------------------------------------------------------------
# 6. Combine all transactions
# -------------------------------------------------------------------
bank_df = load_stmt()
dec_1004_df = load_cc_basic(FILE_DEC_1004, "Posted Date", "Payee", "Amount")
current_1004_df = load_cc_basic(FILE_CURRENT_1004, "Posted Date", "Payee", "Amount")
closed_dec15_df = load_closed_dec15()
since_dec16_df = load_since_dec16()

all_txns = pd.concat(
    [
        bank_df,
        dec_1004_df,
        current_1004_df,
        closed_dec15_df,
        since_dec16_df
    ],
    ignore_index=True
)

# -------------------------------------------------------------------
# 7. Build Excel with formatting
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

    # -----------------------------
    # Report 1
    # -----------------------------
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

    report1_df = pd.DataFrame(
        report1_rows,
        columns=["Category", "Vendor", "Total"]
    )

    ws1 = workbook.add_worksheet("Report_1")
    writer.sheets["Report_1"] = ws1

    headers = list(report1_df.columns)
    for col, h in enumerate(headers):
        ws1.write(0, col, h, header_fmt)

    for r in range(len(report1_df)):
        row_values = report1_df.iloc[r]
        is_total = "total" in str(row_values.values).lower()
        fmt = total_green_fmt if is_total else wrap_fmt

        for c in range(len(headers)):
            ws1.write(r + 1, c, row_values.iloc[c], fmt)

    ws1.set_column("A:C", 25, wrap_fmt)

    # -----------------------------
    # Report 2
    # -----------------------------
    cat_totals = []
    for cat in category_order:
        cat_df = all_txns[all_txns["Category"] == cat]
        if not cat_df.empty:
            cat_totals.append((cat, cat_df["Amount"].sum()))

    grand_total = sum(t for _, t in cat_totals)

    report2_rows = [["Category", "Total", "Percent"]]

    for cat, total in cat_totals:
        pct = (
            abs(total) / abs(grand_total) * 100
            if grand_total != 0 else 0
        )
        report2_rows.append([cat, f"{total:.2f}", f"{pct:.2f}%"])

    report2_rows.append(["Total", f"{grand_total:.2f}", "100.00%"])

    report2_df = pd.DataFrame(
        report2_rows[1:],
        columns=report2_rows[0]
    )

    report2_html_table = report2_df.to_html(index=False, border=1)

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

    # -----------------------------
    # Report 3 — Transactions > $200
    # -----------------------------
    report3_df = all_txns[all_txns["Amount"].abs() > 200].copy()
    report3_df = report3_df.sort_values("Date")

    # Convert Report 3 into an HTML table for email
    report3_html_table = report3_df.to_html(index=False, border=1)

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

    # -----------------------------
    # Detailed category sheets
    # -----------------------------
    for cat in category_order:
        cat_df = all_txns[all_txns["Category"] == cat].copy()
        if cat_df.empty:
            continue

        output_rows = []

        for vendor, vdf in cat_df.groupby("Vendor"):
            output_rows.append([f"Vendor: {vendor}", ""])
            vdf = vdf.sort_values("Date")

            for _, row in vdf.iterrows():
                output_rows.append([row["Date"], f"{row['Amount']:.2f}"])

            vendor_total = vdf["Amount"].sum()
            output_rows.append(["Vendor Total", f"{vendor_total:.2f}"])
            output_rows.append(["", ""])

        category_total = cat_df["Amount"].sum()
        output_rows.append(["Category Total", f"{category_total:.2f}"])

        detail_df = pd.DataFrame(
            output_rows,
            columns=["Date", "Amount"]
        )
        detail_df.to_excel(
            writer,
            sheet_name=cat[:31],
            index=False
        )

        ws = writer.sheets[cat[:31]]
        ws.set_column("A:B", 25, wrap_fmt)

        for i, row in enumerate(output_rows):
            if "total" in str(row[0]).lower():
                ws.set_row(i + 1, None, total_green_fmt)
                print("Excel report generated:", OUTPUT_FILE)

# -------------------------------------------------------------------
# 8. Email the generated file (HTML tables for Report 2 & 3)
# -------------------------------------------------------------------

SENDER_EMAIL = "ssram.chn@gmail.com"
RECIPIENT_EMAIL = "jega.itcontact@gmail.com"
EMAIL_APP_PASSWORD = "dkao jbhl iwfk cjoz"  # <-- replace locally

subject = "December 2025 Spending Report – Summary Included"

# Build HTML email body with both tables
body_html = f"""
<html>
<body>
<p>Hello,</p>

<p>Your December 2025 Spending Report is attached.</p>

<h3>Report 2 – Category Summary</h3>
{report2_html_table}

<h3>Report 3 – Transactions Over $200</h3>
{report3_html_table}

<p>Regards,<br>
Automated Report System</p>

</body>
</html>
"""

# Build email message
msg = MIMEMultipart("alternative")
msg["From"] = SENDER_EMAIL
msg["To"] = RECIPIENT_EMAIL
msg["Subject"] = subject

# Attach HTML body
msg.attach(MIMEText(body_html, "html"))

# Attach the Excel file
with open(OUTPUT_FILE, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

encoders.encode_base64(part)
part.add_header(
    "Content-Disposition",
    f"attachment; filename={OUTPUT_FILE}"
)

msg.attach(part)

# Send email via Gmail SMTP
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
    server.send_message(msg)

print("Email sent to", RECIPIENT_EMAIL)
