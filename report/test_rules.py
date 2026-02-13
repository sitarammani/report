#!/usr/bin/env python3
"""Test the rule-based categorization system"""

import pandas as pd
import re
import os

# Load rules
rules_df = pd.read_csv('category_rules.csv')
rules = []

for _, row in rules_df.iterrows():
    rules.append({
        'rule_id': row['RuleID'],
        'priority': int(row['Priority']),
        'vendor_pattern': row['VendorPattern'].upper(),
        'category': row['Category'],
        'explanation': row['Explanation']
    })

# Sort by priority (descending)
rules.sort(key=lambda x: x['priority'], reverse=True)

def categorize_vendor(vendor: str) -> str:
    """Categorize vendor using rule-based system."""
    v = vendor.upper()
    
    for rule in rules:
        pattern = rule['vendor_pattern']
        if re.match(f".*{re.escape(pattern)}.*", v):
            return rule['category']
    
    return "Shopping & Retail"

# Test cases
test_cases = [
    ("KROGER", "Groceries & Markets"),
    ("KROGER FUEL CENTER", "Auto & Gas"),
    ("AMAZON.COM", "Shopping & Retail"),
    ("COMCAST XFINITY", "Utilities Bills & Insurance"),
    ("EMORY CLINIC", "Health"),
    ("TACO BELL", "Restaurants & Food"),
    ("RANDOM VENDOR", "Shopping & Retail"),
]

print("\n" + "="*70)
print("RULE-BASED CATEGORIZATION SYSTEM TEST")
print("="*70)
print(f"\nTotal Rules Loaded: {len(rules)}\n")

print("Testing Categorization:")
print("-" * 70)

all_pass = True
for vendor, expected_category in test_cases:
    actual_category = categorize_vendor(vendor)
    status = "✅ PASS" if actual_category == expected_category else "❌ FAIL"
    
    if actual_category != expected_category:
        all_pass = False
    
    print(f"{status} | {vendor:30} → {actual_category:30}")
    if actual_category != expected_category:
        print(f"      Expected: {expected_category}")

print("-" * 70)
print(f"\nResult: {'✅ All tests passed!' if all_pass else '❌ Some tests failed'}")
print("\nRule structure example:")
print("-" * 70)
for rule in rules[:3]:
    print(f"Rule ID:     {rule['rule_id']}")
    print(f"Priority:    {rule['priority']}")
    print(f"Pattern:     {rule['vendor_pattern']}")
    print(f"Category:    {rule['category']}")
    print(f"Explanation: {rule['explanation']}")
    print()
