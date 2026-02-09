import pandas as pd

# Check the Statement closed Jan 15, 2026.CSV file
csv_path = "/Users/janani/Desktop/sitapp/jan/Statement closed Jan 15, 2026.CSV"

df = pd.read_csv(csv_path)
print("Columns:", df.columns.tolist())
print(f"\nTotal rows: {len(df)}\n")

# Look for AUTOPAY or similar transactions
autopay_rows = df[df.iloc[:, 1].astype(str).str.contains('AUTOPAY|autopay', case=False, na=False)]

print("AUTOPAY/AutoPay transactions found:")
print("-" * 100)
for idx, row in autopay_rows.iterrows():
    print(row.tolist())
