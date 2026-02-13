#!/usr/bin/env python3
import pandas as pd
import re

# Load rules
rules_df = pd.read_csv('category_rules.csv')
rules_df_sorted = rules_df.sort_values('Priority', ascending=False)

# Check matching
vendor = "HAWKMUSIC ACADEMY"
v = vendor.upper()

print(f"Testing vendor: {vendor}\n")
print("Rules by priority (TOP 20):\n")
print(f"{'Pri':<4} | {'ID':<10} | {'Pattern':<25} | {'Category':<30} | Match")
print("-" * 95)

count = 0
for _, row in rules_df_sorted.iterrows():
    if count >= 20:
        break
    pattern = row['VendorPattern'].upper()
    matches = re.match(f".*{re.escape(pattern)}.*", v)
    status = "✓" if matches else ""
    print(f"{row['Priority']:<4} | {row['RuleID']:<10} | {pattern:<25} | {row['Category']:<30} | {status}")
    count += 1

print("\n" + "="*95)

# Find which rule actually matches
rules = []
for _, row in rules_df.iterrows():
    rules.append({
        'rule_id': row['RuleID'],
        'priority': int(row['Priority']),
        'vendor_pattern': row['VendorPattern'].upper(),
        'category': row['Category'],
    })
rules.sort(key=lambda x: x['priority'], reverse=True)

for rule in rules:
    pattern = rule['vendor_pattern']
    if re.match(f".*{re.escape(pattern)}.*", v):
        print(f"\n✓ FIRST MATCH FOUND:")
        print(f"  Rule ID: {rule['rule_id']}")
        print(f"  Priority: {rule['priority']}")
        print(f"  Pattern: {pattern}")
        print(f"  Category: {rule['category']}")
        break
