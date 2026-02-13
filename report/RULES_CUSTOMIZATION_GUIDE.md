# Category Rules Customization Guide

## Overview
The **Category Rules Manager** (`manage_rules.py`) is an interactive command-line tool that allows you to customize how transactions are categorized without touching any code.

## How It Works
- **Rules-based system**: Each vendor is categorized based on matching rules
- **Priority-driven**: Rules with higher priority are evaluated first
- **Easy management**: Add, edit, delete, or search rules through a simple CLI menu

## Getting Started

### Launch the Manager
```bash
python3 manage_rules.py
```

You'll see the main menu with 10 options:
```
  1. View all rules (by priority)
  2. View rules by category
  3. Search rules
  4. Add new rule
  5. Edit rule
  6. Delete rule
  7. Duplicate rule
  8. Export rules
  9. Restore from backup
  0. Exit
```

---

## Menu Options

### 1️⃣ View All Rules (By Priority)
Displays all 52+ rules sorted by priority (highest first).

**Example:**
```
Priority   ID       Pattern                        Category                  
110        A002     KROGER FUEL                    Auto & Gas                
110        A003     SHELL                          Auto & Gas                
100        G001     KROGER                         Groceries & Markets       
```

### 2️⃣ View Rules by Category
Groups rules by spending category for easier browsing.

**Example:**
```
Groceries & Markets (9 rules)
─────────────────────────────
  G001     [P:100] KROGER                 | Kroger grocery stores
  G002     [P:100] INDIFRESH              | Indian grocery store
  ...
```

### 3️⃣ Search Rules
Search for rules by vendor pattern or category name.

**Usage:**
```
Enter search term: KROGER
✓ Found 2 matching rule(s):
  G001  | KROGER              | Groceries & Markets
  A002  | KROGER FUEL         | Auto & Gas
```

### 4️⃣ Add New Rule
Create a new categorization rule.

**Interactive prompt:**
```
Rule ID:        G010
Priority:       100
Pattern:        NEW VENDOR
Category:       (Select from list or custom)
Explanation:    My custom vendor
```

**What is Priority?**
- **Higher priority (100-110)** → Checked first
- **Lower priority (1-75)** → Checked later
- **Default catch-all (1)** → Used if nothing matches

### 5️⃣ Edit Rule
Modify an existing rule without recreating it.

**Example:**
```
Current rule: R001
  Priority:  90
  Pattern:   TACO BELL
  Category:  Restaurants & Food

New Priority: 95
New Pattern:  TACO BELL FAST FOOD
```

### 6️⃣ Delete Rule
Permanently remove a rule (with confirmation).

```
Rule to delete:
  ID:       R001
  Pattern:  TACO BELL → Restaurants & Food

Confirm deletion? (yes/no): yes
✓ Rule 'R001' deleted successfully!
```

### 7️⃣ Duplicate Rule
Copy an existing rule with a new Rule ID (great for similar vendors).

**Example:**
```
Rule to duplicate: G001 (KROGER)
New Rule ID:       G010
→ Creates a copy of KROGER rule as G010
```

### 8️⃣ Export Rules
Save your rules to a separate CSV file for backup or sharing.

```
Export filename: my_custom_rules.csv
✓ Rules exported to my_custom_rules.csv
```

### 9️⃣ Restore from Backup
Recover your previous rules (auto-backup created when rules are saved).

```
Backup file: category_rules.csv.backup
Restore? (yes/no): yes
✓ Rules restored from backup
```

### 0️⃣ Exit
Close the manager.

---

## Real-World Examples

### Example 1: Add a New Vendor Rule
You notice transactions from "STARBUCKS" aren't being categorized correctly.

**Steps:**
```
1. Select: 4 (Add new rule)
2. Rule ID: R009
3. Priority: 90 (same as other restaurants)
4. Pattern: STARBUCKS
5. Category: Restaurants & Food (select from list)
6. Explanation: Coffee and pastries
```

**Result:**
- All "STARBUCKS" transactions → **Restaurants & Food**

### Example 2: Change Priority (More Specific Match First)
You want "KROGER FUEL" checked BEFORE general "KROGER".

**Current:**
```
Priority 110: KROGER FUEL  → Auto & Gas
Priority 100: KROGER      → Groceries & Markets
✓ Already correct (specific rule has higher priority)
```

If it weren't, you'd:
```
1. Select: 5 (Edit rule)
2. Rule ID: A002
3. New Priority: 110
```

### Example 3: Add a Custom Category
You want to track "Subscriptions" separately.

**Steps:**
```
1. Select: 4 (Add new rule)
2. Rule ID: SUB001
3. Priority: 85
4. Pattern: NETFLIX
5. Category: Subscriptions (custom - type it)
6. Explanation: Streaming service
```

**Result:**
- New category "Subscriptions" automatically appears in reports
- Future "NETFLIX" transactions → **Subscriptions**

### Example 4: Search and Edit
You want to boost priority of all "Health" vendors.

**Steps:**
```
1. Select: 3 (Search rules)
2. Search term: HEALTH
   → Shows: H001, H002
3. Select: 5 (Edit rule)
4. Rule ID: H001
5. New Priority: 100
6. Repeat for H002
```

---

## Rule Structure

Each rule has 5 components:

| Field | Example | Purpose |
|-------|---------|---------|
| **RuleID** | G001 | Unique identifier (prefix = category, number = sequence) |
| **Priority** | 100 | 1-110. Higher = evaluated first |
| **VendorPattern** | KROGER | Text to match in vendor name |
| **Category** | Groceries & Markets | Output category for reports |
| **Explanation** | Kroger grocery stores | Description for documentation |

---

## Auto Backup System

Every time you save changes, the manager:
1. ✅ Creates a timestamped backup (`category_rules.csv.backup`)
2. ✅ Saves your new rules
3. ✅ Allows you to restore anytime with option 9

**To restore:**
```
Select: 9 (Restore from backup)
Confirm: yes
→ Your previous rules are restored
```

---

## Tips & Best Practices

### ✅ DO:
- **Use descriptive Rule IDs**: G001, R001, S001 (prefix hints the category)
- **Set priorities logically**: More specific patterns get higher priority
- **Use backup before major changes**: Export rules before bulk edits
- **Test categorization**: Run `python3 generate_reports_email.py` to see results

### ❌ DON'T:
- **Manually edit CSV**: Use the manager instead (prevents errors)
- **Leave patterns too generic**: "BANK" will match everything
- **Forget to test**: Verify with test_rules.py after major changes
- **Delete DEFAULT rule**: It's the fallback for unmapped vendors

---

## Command-Line Examples

### Quick View (Non-interactive)
```bash
# Just view rules
python3 manage_rules.py --view

# View a specific category
python3 manage_rules.py --category "Restaurants & Food"
```

### Batch Operations
```bash
# Export all rules
python3 manage_rules.py --export custom_rules.csv

# Import rules
python3 manage_rules.py --import custom_rules.csv
```

---

## Troubleshooting

### Issue: Rule not working
**Check:**
1. Pattern spelling matches your vendor names
2. Priority is higher than conflicting rules
3. Run: `python3 test_rules.py` to verify

### Issue: Backup missing
**Solution:**
1. Open `category_rules.csv` (current rules)
2. Manually save a copy
3. Select "Add new rule" to create new backup

### Issue: Confused about priority
**Remember:**
- Priority 110 (highest) → Checked FIRST
- Priority 1 (lowest) → Checked LAST
- More specific patterns should have higher priority

---

## Integration with Reports

Once you customize rules:

1. **Categorization automatically updates**:
   - Rules manager loads rules from CSV
   - Report generator uses same rules
   - No code changes needed

2. **Immediate effect**:
   ```bash
   python3 manage_rules.py  # Customize
   
   python3 generate_reports_email.py  # Uses new rules
   ```

3. **Works with existing data**:
   - Old reports use old rules
   - New reports use new rules
   - No re-processing needed

---

## Advanced: Understanding Rule Priority

### Priority Order (What Gets Checked First)

```
210 ─► SPECIFIC PATTERNS (fuel stations, fast food variants) [if added]
110 ─► SPECIFIC + QUALIFIER (KROGER FUEL, COSTCO GAS) [checked first]
100 ─► MAIN VENDORS (KROGER, WEGMANS, PUBLIX)
 95 ─► HEALTH (TELADOC, EMORY CLINIC)
 90 ─► RESTAURANTS (TACO BELL, DOMINOS)
 88 ─► ENTERTAINMENT (AMC, URBAN AIR)
 85 ─► AUTO & GAS (SHELL, WAWA)
 82 ─► HOME & SERVICES (HOME DEPOT)
 80 ─► SHOPPING & RETAIL (AMAZON, TARGET)
 75 ─► UTILITIES (COMCAST, TMOBILE, INSURANCE)
  1 ─► DEFAULT CATCH-ALL (matches anything)
```

**Why priorities matter:**
- Without priority, "KROGER FUEL" would match "KROGER" first
- With priority, more specific rules match first
- Prevents wrong categorization

---

## Questions?

The rules manager is designed to be self-explanatory. If you're unsure:

1. **Try option 3 (Search)** to explore existing rules
2. **Try option 2 (View by category)** to understand the structure
3. **Use option 9 (Restore)** to undo any changes
4. **Create a test rule** with a unique pattern to experiment

**Your custom categories are saved forever** until you delete them manually. Enjoy! 🎉
