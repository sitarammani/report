# Advanced Category Customization Guide

## New Features Overview

The enhanced Category Rules Manager now supports:

### 1. **User-Defined Categories** 🎨
Create your own spending categories beyond the pre-defined ones.

### 2. **Rule Overrides** 🔄
User-defined rules can override built-in rules for specific vendors.

### 3. **Category Hierarchy** 🌳
Organize categories with parent-child relationships for better organization.

### 4. **Rule Tracking** 📝
Track which rules are user-defined (custom) and which override other rules.

---

## Launch the Advanced Manager

```bash
python3 manage_rules.py
```

### New Menu Structure

```
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
```

---

## Feature 1: User-Defined Categories 🎨

### What It Does
Create custom spending categories tailored to your needs.

### Examples
- **Subscriptions**: Netflix, Hulu, Spotify, etc.
- **Pet Care**: Vet bills, pet food, grooming
- **Education**: Tuition, courses, books
- **Fitness**: Gym, yoga, fitness equipment
- **Travel**: Flights, hotels, car rentals

### How to Use

**Step 1: Launch Manager**
```bash
python3 manage_rules.py
```

**Step 2: Select Option 2 (Add user-defined category)**
```
Select option: 2
```

**Step 3: Enter Details**
```
Enter new category name: Subscriptions
Description: Monthly subscription services and memberships
Select parent category (optional): (press Enter)
```

**Step 4: Verify**
Manager will display:
```
✓ Category 'Subscriptions' created successfully!
```

### View All Categories (Option 1)
```
Category                            Status          Rules    Parent
────────────────────────────────────────────────────────────────────
Groceries & Markets                 Built-in        9        
Restaurants & Food                  Built-in        8        
Subscriptions                       User-Defined    0        
...
```

---

## Feature 2: Rule Overrides 🔄

### What It Does
Override how built-in rules categorize vendors using higher-priority custom rules.

### Example: Redirect Shopping Category

**Scenario:** You want "BESTBUY" to be categorized as "Technology" (custom) instead of "Shopping & Retail" (built-in).

**Steps:**
```
1. Select: 7 (Add custom rule)
2. Rule ID: T001
3. Priority: 85 (higher than S002 "BESTBUY" which has 80)
4. Pattern: BESTBUY
5. Category: Technology
6. Override rule: S002
```

**Result:**
- BESTBUY now categorizes as **Technology** (instead of Shopping & Retail)
- The override is tracked in `OverrideRuleID` column

### View All Overrides (Option 6)

```
ID       Priority   Overrides   Pattern              Category
─────────────────────────────────────────────────────────────
T001     85         S002        BESTBUY              Technology
MUSIC001 92         R008        SPOTIFY              Subscriptions
```

### How Overrides Work

The priority system automatically handles overrides:

```
Priority 110 ─► Specific patterns (KROGER FUEL)
Priority 85  ─► Your custom rule (BESTBUY override)
Priority 80  ─► Original rule (BESTBUY built-in)
              (your rule matches first because higher priority!)
```

---

## Feature 3: Category Hierarchy 🌳

### What It Does
Organize categories in parent-child relationships.

### Example Hierarchies

```
Entertainment (parent)
├── Movies
├── Sports
└── Music
```

```
Shopping (parent)
├── Clothing
├── Electronics
└── Home Goods
```

### Setup Example

**Create a child category:**
```
Select: 2 (Add user-defined category)
Category name: Electronics
Description: Electronics and tech purchases
Parent category: Shopping & Retail
```

**View the hierarchy:**
```
Select: 1 (View category hierarchy)

Result:
Category                    Status          Rules    Parent
──────────────────────────────────────────────────────────────
Shopping & Retail           Built-in        11       (Root)
Electronics                 User-Defined    0        Shopping & Retail
Clothing                    User-Defined    0        Shopping & Retail
```

---

## Feature 4: Custom Rules

### Advanced Options

When adding a custom rule (Option 7), you can:

1. **Set Custom Priority**
   - Higher than built-in rules to override them
   - Lower to be secondary fallback

2. **Specify Override Target**
   - Link to the rule being overridden
   - For documentation and tracking

3. **Use Custom Categories**
   - Reference existing custom categories
   - Or create new ones on the fly

### Example: Netflix Override

```
Add Custom Rule:
  Rule ID: SUBS001
  Priority: 95 (higher than restaurants 90)
  Pattern: NETFLIX
  Category: Subscriptions (custom category)
  Override: R008 (DUNKIN - because Netflix is NOT a restaurant!)
  Explanation: Streaming video subscription service
```

---

## Feature 5: View Custom Rules (Option 5)

See only the rules YOU created, not the 50+ built-in ones.

```
Select: 5

Result:
ID          Priority    Pattern              Category
──────────────────────────────────────────────────────
SUBS001     95          NETFLIX              Subscriptions
T001        85          BESTBUY              Technology
MUSIC001    92          SPOTIFY              Subscriptions
```

---

## File Structure

### New Files Created

| File | Purpose | Tracks |
|------|---------|--------|
| `categories.csv` | All categories with hierarchy | Parent relationships, User-defined flag |
| `category_rules.csv` | *Enhanced* with new columns | `OverrideRuleID`, `IsCustom`, `CreatedDate` |
| `manage_rules.py` | *Enhanced* manager tool | All advanced features |

### Categories File Format

```csv
CategoryName,ParentCategory,Description,IsUserDefined,CreatedDate
"Groceries & Markets",,Fresh food shopping,No,2026-01-01
Subscriptions,,Subscription services,Yes,2026-02-12
```

### Expanded Rules File Format

```csv
RuleID,Priority,VendorPattern,Category,Explanation,OverrideRuleID,IsCustom,CreatedDate
G001,100,KROGER,Groceries & Markets,Kroger stores,,No,2026-01-01
SUBS001,95,NETFLIX,Subscriptions,Streaming service,R008,Yes,2026-02-12
```

---

## Practical Workflows

### Workflow 1: Add a New Category with Custom Rules

```
1. Add Category (Option 2)
   → "Subscriptions"

2. Add Custom Rules (Option 7)
   → NETFLIX → Subscriptions
   → SPOTIFY → Subscriptions
   → HULU → Subscriptions

3. View Custom Rules (Option 5)
   → See all 3 rules you created
```

### Workflow 2: Override a Built-in Rule

```
1. View Rules (Option 4)
   → Find the rule to override (e.g., S002 for BESTBUY)

2. Add Custom Rule (Option 7)
   → Set HIGHER priority (85 vs 80)
   → Set override to S002
   → Point to custom category

3. View Overrides (Option 6)
   → Confirm the override is tracked
```

### Workflow 3: Organize Categories Hierarchically

```
1. View Hierarchy (Option 1)
   → See current structure

2. Add Category (Option 2)
   → Select parent category
   → Creates child relationship

3. View Hierarchy (Option 1)
   → See updated tree structure
```

---

## Data Integrity

### Auto-Backup System
Every change creates an automatic backup:
- `category_rules.csv.backup`

### Restore (old manager option)
```
python3 manage_rules.py
(original manager still has restore option)
```

### Export Custom Rules
```
Select: 9 (Export custom rules)
Filename: my_custom_rules.csv
→ Creates CSV with only YOUR rules
```

---

## Integration with Report Generator

### Automatic Updates
```
├─ Customize categories/rules (manage_rules.py)
│
├─ Rules saved to category_rules.csv
│
├─ Run report generator (generate_reports_email.py)
│
└─ Reports use your custom categories immediately! ✨
```

### No Code Changes Needed
1. Manager updates CSV files
2. Report generator loads CSV files
3. Your customizations are applied
4. No restart or recompilation required

---

## Advanced Topics

### Rule Priority Scoring

When deciding rule priority, consider:
- **110+**: Extremely specific patterns (KROGER FUEL vs KROGER)
- **90-95**: Common categories (restaurants, health)
- **80-85**: General shopping categories
- **75-80**: Utilities, recurring services
- **1-50**: Fallback/default rules

### Override Best Practices

✅ **DO:**
- Override to more specific categories for YOUR use case
- Document why you're overriding (explanation field)
- Test with multiple vendor names

❌ **DON'T:**
- Override all shopping categories indiscriminately
- Delete built-in rules (mark as disabled instead)
- Create duplicate rules with same pattern

### Hierarchy Design

✅ **Good Design:**
```
Shopping & Retail (root)
├── Clothing (seasonal)
├── Electronics (tech items)
└── Home Goods (furniture/decor)
```

❌ **Avoid:**
```
Electronics (root)
├── AMAZON
├── TARGET
└── BESTBUY
(this is vendor-based, not category-based)
```

---

## Troubleshooting

### Issue: Custom rules not working
**Check:**
1. Rule ID is unique (`manage_rules.py` checks this)
2. Pattern matches vendor name exactly (case-insensitive)
3. Priority is higher than conflicting rules (Option 6 to view)
4. Category name is spelled correctly

### Issue: Can't override a rule
**Solution:**
```
1. Find target rule (Option 4)
2. Note its priority (e.g., S002 = 80)
3. Create custom with HIGHER priority (e.g., 85)
4. Should work immediately
```

### Issue: Lost track of overrides
**Solution:**
```
View all overrides anytime:
Select: 6 (View rule overrides)
Shows ALL rules with OverrideRuleID set
```

---

## Examples Walkthrough

### Example 1: Fitness Buff's Setup

```
Step 1: Add Fitness category
Step 2: Create rules
  - PLANET FITNESS → Fitness
  - APPLE HEALTH+ → Fitness (overrides Entertainment)
  - FITBIT → Fitness (overrides Shopping)
Step 3: Run report
  → All fitness expenses grouped together!
```

### Example 2: Business Owner's Setup

```
Step 1: Add "Business Expenses" category
Step 2: Add rules for business vendors
  - OFFICE DEPOT → Business Expenses
  - AWS → Business Expenses
  - GEN BUSINESS SERVICES → Business Expenses
Step 3: Track business spending separately
```

### Example 3: Tax Preparation Setup

```
Step 1: Create "Tax Deductible" category
Step 2: Mark which purchases are deductible
  - HOME OFFICE SUPPLIES → Tax Deductible
  - PROFESSIONAL SERVICES → Tax Deductible
Step 3: Generate reports by deductibility
```

---

## Summary

| Feature | Benefit | How to Use |
|---------|---------|-----------|
| User-Defined Categories | Match your spending | Option 2 |
| Rule Overrides | Correct misclassifications | Option 7 + priority |
| Category Hierarchy | Organize categories | Option 1 view, Option 2 with parent |
| Rule Tracking | See what's custom | Option 5 (view custom) |
| Auto-Backup | Never lose changes | Automatic on save |

**Your spending categorization now fully matches your needs!** 🎉
