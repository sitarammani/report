#!/usr/bin/env python3
"""
Category Rules Manager (Enhanced)
Interactive CLI tool to customize spending categories and rules with:
- User-defined categories
- Rule overrides
- Category hierarchy
"""

import pandas as pd
import os
import sys
from datetime import datetime

RULES_FILE = os.path.join(os.path.dirname(__file__), "category_rules.csv")
CATEGORIES_FILE = os.path.join(os.path.dirname(__file__), "categories.csv")
BACKUP_EXT = ".backup"

def load_rules():
    """Load rules from CSV file."""
    if not os.path.exists(RULES_FILE):
        print(f"Error: {RULES_FILE} not found!")
        sys.exit(1)
    return pd.read_csv(RULES_FILE)

def load_categories():
    """Load categories from CSV file."""
    if not os.path.exists(CATEGORIES_FILE):
        print(f"Creating {CATEGORIES_FILE}...")
        # Create default categories
        categories = pd.DataFrame({
            'CategoryName': ['Groceries & Markets', 'Restaurants & Food', 'Shopping & Retail',
                            'Auto & Gas', 'Utilities Bills & Insurance', 'Entertainment',
                            'Health', 'Home & Services'],
            'ParentCategory': [''] * 8,
            'Description': ['Fresh food and grocery shopping', 'Dining out and food delivery',
                           'General shopping and retail stores', 'Vehicle fuel and gas stations',
                           'Monthly bills and insurance payments', 'Movies, shows, and entertainment',
                           'Healthcare and medical services', 'Home improvement and services'],
            'IsUserDefined': ['No'] * 8,
            'CreatedDate': ['2026-01-01'] * 8
        })
        categories.to_csv(CATEGORIES_FILE, index=False)
        return categories
    return pd.read_csv(CATEGORIES_FILE)

def save_rules(df):
    """Save rules to CSV and create backup."""
    if os.path.exists(RULES_FILE):
        backup_file = f"{RULES_FILE}{BACKUP_EXT}"
        df_old = pd.read_csv(RULES_FILE)
        df_old.to_csv(backup_file, index=False)
        print(f"  ✓ Backup created: {backup_file}")
    
    df.to_csv(RULES_FILE, index=False)
    print(f"  ✓ Rules saved to {RULES_FILE}")

def save_categories(df):
    """Save categories to CSV."""
    df.to_csv(CATEGORIES_FILE, index=False)
    print(f"  ✓ Categories saved to {CATEGORIES_FILE}")

def display_header(title):
    """Display section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def view_category_hierarchy():
    """View category hierarchy."""
    display_header("CATEGORY HIERARCHY")
    
    categories = load_categories()
    rules_df = load_rules()
    
    print(f"\n{'Category':<35} {'Status':<15} {'Rules':<8} {'Parent':<30}")
    print("-" * 90)
    
    for _, cat in categories.iterrows():
        cat_name = cat['CategoryName']
        parent = cat['ParentCategory'] if cat['ParentCategory'] else '(Root)'
        status = "User-Defined" if cat['IsUserDefined'] == 'Yes' else "Built-in"
        rule_count = len(rules_df[rules_df['Category'] == cat_name])
        
        print(f"{cat_name:<35} {status:<15} {rule_count:<8} {parent:<30}")

def view_all_rules():
    """View all rules sorted by priority."""
    display_header("VIEW ALL RULES (By Priority)")
    
    df = load_rules()
    df_sorted = df.sort_values('Priority', ascending=False)
    
    print(f"\n{'Priority':<10} {'ID':<8} {'Pattern':<25} {'Category':<25} {'Custom':<7} {'Override'}")
    print("-" * 100)
    
    for _, row in df_sorted.iterrows():
        pattern = row['VendorPattern'][:23]
        category = row['Category'][:23]
        override = row['OverrideRuleID'] if pd.notna(row['OverrideRuleID']) and row['OverrideRuleID'] != '' else '-'
        print(f"{row['Priority']:<10} {row['RuleID']:<8} {pattern:<25} {category:<25} {row['IsCustom']:<7} {override}")
    
    print(f"\nTotal Rules: {len(df)}")

def view_custom_rules():
    """View only user-defined rules."""
    display_header("USER-DEFINED RULES")
    
    df = load_rules()
    custom_rules = df[df['IsCustom'] == 'Yes'].sort_values('Priority', ascending=False)
    
    if len(custom_rules) == 0:
        print("\nNo user-defined rules yet.")
        return
    
    print(f"\n{'ID':<8} {'Priority':<10} {'Pattern':<25} {'Category':<25}")
    print("-" * 70)
    
    for _, row in custom_rules.iterrows():
        print(f"{row['RuleID']:<8} {row['Priority']:<10} {row['VendorPattern']:<25} {row['Category']:<25}")
    
    print(f"\nTotal Custom Rules: {len(custom_rules)}")

def add_user_category():
    """Create a new user-defined category."""
    display_header("ADD USER-DEFINED CATEGORY")
    
    categories = load_categories()
    
    category_name = input("\nEnter new category name (e.g., Subscriptions): ").strip()
    
    if not category_name:
        print("✗ Category name cannot be empty")
        return
    
    if category_name in categories['CategoryName'].values:
        print(f"✗ Category '{category_name}' already exists")
        return
    
    print("\nAvailable parent categories (or press Enter for none):")
    for i, cat_name in enumerate(categories['CategoryName'].unique(), 1):
        print(f"  {i}. {cat_name}")
    
    parent_input = input("\nSelect parent category (number or leave empty): ").strip()
    parent_category = ''
    
    if parent_input:
        try:
            parent_idx = int(parent_input) - 1
            cat_list = list(categories['CategoryName'].unique())
            if 0 <= parent_idx < len(cat_list):
                parent_category = cat_list[parent_idx]
        except ValueError:
            pass
    
    description = input("Description: ").strip()
    
    new_category = pd.DataFrame({
        'CategoryName': [category_name],
        'ParentCategory': [parent_category],
        'Description': [description if description else f"{category_name} transactions"],
        'IsUserDefined': ['Yes'],
        'CreatedDate': [datetime.now().strftime('%Y-%m-%d')]
    })
    
    categories = pd.concat([categories, new_category], ignore_index=True)
    save_categories(categories)
    
    print(f"\n✓ Category '{category_name}' created successfully!")
    if parent_category:
        print(f"  Parent: {parent_category}")

def add_custom_rule():
    """Add a custom rule that can override existing rules."""
    display_header("ADD CUSTOM RULE")
    
    df = load_rules()
    categories = load_categories()
    
    print("\nEnter rule details:")
    rule_id = input("  Rule ID (e.g., C001, CUSTOM-NETFLIX): ").strip().upper()
    
    if rule_id in df['RuleID'].values:
        print(f"  ✗ Rule ID '{rule_id}' already exists!")
        return
    
    priority = input("  Priority (1-110, higher = checked first): ").strip()
    try:
        priority = int(priority)
        if not (1 <= priority <= 150):
            print("  ✗ Priority must be between 1 and 150")
            return
    except ValueError:
        print("  ✗ Priority must be a number")
        return
    
    pattern = input("  Vendor Pattern (e.g., NETFLIX): ").strip().upper()
    if not pattern:
        print("  ✗ Pattern cannot be empty")
        return
    
    print("\n  Available Categories:")
    cat_names = sorted(categories['CategoryName'].unique())
    for i, cat in enumerate(cat_names, 1):
        print(f"    {i}. {cat}")
    
    category_input = input("  Select category (number or custom name): ").strip()
    try:
        cat_idx = int(category_input) - 1
        if 0 <= cat_idx < len(cat_names):
            category = cat_names[cat_idx]
        else:
            category = category_input
    except ValueError:
        category = category_input
    
    if not category:
        print("  ✗ Category cannot be empty")
        return
    
    print("\n  Override an existing rule? (press Enter to skip)")
    override_id = input("  Rule ID to override (e.g., G001): ").strip().upper()
    
    if override_id and override_id not in df['RuleID'].values:
        print(f"    ✗ Rule '{override_id}' not found")
        return
    
    explanation = input("  Explanation: ").strip()
    
    new_rule = pd.DataFrame({
        'RuleID': [rule_id],
        'Priority': [priority],
        'VendorPattern': [pattern],
        'Category': [category],
        'Explanation': [explanation if explanation else f"{pattern} transaction"],
        'OverrideRuleID': [override_id if override_id else ''],
        'IsCustom': ['Yes'],
        'CreatedDate': [datetime.now().strftime('%Y-%m-%d')]
    })
    
    df = pd.concat([df, new_rule], ignore_index=True)
    save_rules(df)
    
    print(f"\n✓ Custom rule '{rule_id}' added successfully!")
    print(f"  Pattern: {pattern} → {category} (Priority: {priority})")
    if override_id:
        print(f"  Overrides: {override_id}")

def view_rule_overrides():
    """View rules that override other rules."""
    display_header("RULE OVERRIDES")
    
    df = load_rules()
    overrides = df[df['OverrideRuleID'].notna() & (df['OverrideRuleID'] != '')].sort_values('Priority', ascending=False)
    
    if len(overrides) == 0:
        print("\nNo rule overrides defined.")
        return
    
    print(f"\n{'ID':<8} {'Priority':<10} {'Overrides':<10} {'Pattern':<20} {'Category':<25}")
    print("-" * 75)
    
    for _, row in overrides.iterrows():
        print(f"{row['RuleID']:<8} {row['Priority']:<10} {row['OverrideRuleID']:<10} {row['VendorPattern']:<20} {row['Category']:<25}")

def delete_user_category():
    """Delete a user-defined category."""
    display_header("DELETE USER-DEFINED CATEGORY")
    
    categories = load_categories()
    user_cats = categories[categories['IsUserDefined'] == 'Yes']
    
    if len(user_cats) == 0:
        print("\nNo user-defined categories to delete.")
        return
    
    print("\nUser-defined categories:")
    for i, (_, cat) in enumerate(user_cats.iterrows(), 1):
        print(f"  {i}. {cat['CategoryName']}")
    
    choice = input("\nEnter category number to delete: ").strip()
    
    try:
        idx = int(choice) - 1
        cat_to_delete = user_cats.iloc[idx]['CategoryName']
    except (ValueError, IndexError):
        print("✗ Invalid selection")
        return
    
    confirm = input(f"\nDelete '{cat_to_delete}'? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Deletion cancelled.")
        return
    
    categories = categories[categories['CategoryName'] != cat_to_delete]
    save_categories(categories)
    print(f"✓ Category '{cat_to_delete}' deleted!")

def manage_rule_overrides():
    """Manage which rules override which."""
    display_header("MANAGE RULE OVERRIDES")
    
    df = load_rules()
    
    rule_id = input("\nEnter Rule ID to modify: ").strip().upper()
    
    if rule_id not in df['RuleID'].values:
        print(f"✗ Rule '{rule_id}' not found")
        return
    
    print(f"\nOther rules that could be overridden:")
    other_rules = df[df['RuleID'] != rule_id].sort_values('Priority', ascending=False)
    
    for i, (_, row) in enumerate(other_rules.iterrows(), 1):
        print(f"  {i}. {row['RuleID']:<8} [{row['Priority']:3}] {row['VendorPattern']:<20} → {row['Category']}")
    
    override_input = input("\nEnter Rule ID to override (or press Enter for none): ").strip().upper()
    
    if override_input and override_input not in df['RuleID'].values:
        print(f"✗ Rule '{override_input}' not found")
        return
    
    df.loc[df['RuleID'] == rule_id, 'OverrideRuleID'] = override_input if override_input else ''
    save_rules(df)
    
    if override_input:
        print(f"\n✓ Rule '{rule_id}' now overrides '{override_input}'")
    else:
        print(f"\n✓ Override removed from '{rule_id}'")

def export_custom_rules():
    """Export only custom rules."""
    display_header("EXPORT CUSTOM RULES")
    
    df = load_rules()
    custom = df[df['IsCustom'] == 'Yes']
    
    if len(custom) == 0:
        print("\nNo custom rules to export.")
        return
    
    filename = input("Enter export filename (default: custom_rules.csv): ").strip()
    if not filename:
        filename = "custom_rules.csv"
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    custom.to_csv(filename, index=False)
    print(f"✓ {len(custom)} custom rule(s) exported to {filename}")

def main():
    """Main menu."""
    while True:
        display_header("ADVANCED CATEGORY RULES MANAGER")
        print("""
  === CATEGORIES ===
  1. View category hierarchy
  2. Add user-defined category
  3. Delete user-defined category
  
  === RULES & OVERRIDES ===
  4. View all rules (with override info)
  5. View only custom rules
  6. View rule overrides
  7. Add custom rule (with override option)
  8. Manage rule overrides
  
  === UTILITIES ===
  9. Export custom rules
  0. Exit
        """)
        
        choice = input("Select option (0-9): ").strip()
        
        if choice == '1':
            view_category_hierarchy()
        elif choice == '2':
            add_user_category()
        elif choice == '3':
            delete_user_category()
        elif choice == '4':
            view_all_rules()
        elif choice == '5':
            view_custom_rules()
        elif choice == '6':
            view_rule_overrides()
        elif choice == '7':
            add_custom_rule()
        elif choice == '8':
            manage_rule_overrides()
        elif choice == '9':
            export_custom_rules()
        elif choice == '0':
            print("\nExiting Rules Manager. Goodbye!")
            break
        else:
            print("✗ Invalid option. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting Rules Manager.")
        sys.exit(0)
