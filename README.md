# 💰 Budget App

Track and analyze your expenses with ease. Upload CSV statements, get detailed reports by category, and manage your finances.

## Features

✅ **CSV Import** - Upload bank statements in various formats
✅ **Smart Categorization** - Automatically categorizes expenses
✅ **Category Analytics** - View spending by category with percentages
✅ **Expandable Reports** - Click categories to see individual transactions
✅ **Data Export** - Export reports as CSV
✅ **Local Storage** - All data stored securely on your device

## Supported Platforms

- 🌐 Web (Mac, Windows, Linux, Mobile Browser)
- 🍎 macOS (coming soon)
- 🤖 Android (coming soon)

## Getting Started

### Web Version
Simply visit: [Budget App](https://yourusername.github.io/budget-app)

### For Developers

```bash
# Clone repository
git clone https://github.com/yourusername/budget-app.git
cd budget-app/budgetui

# Install dependencies
flutter pub get

# Run web version
flutter run -d chrome

# Build for production
flutter build web --release
```

## CSV Import Format

Supports bank statement formats with:
- Date column
- Description/Payee column
- Amount column
- Optional payment method column

### Supported Columns:
- Date (various formats)
- Description / Payee / Merchant
- Amount / Debit / Credit
- Payment Method / Account
- Status (for cleared transactions)

### Auto-Filters:
- Income/Payroll entries
- Transfers between accounts
- Balance rows
- Summary rows

## Expense Categories

- 🛒 Shopping & Retail
- 🍔 Restaurants & Food
- ⛽ Auto & Gas
- 🏠 Home & Services
- 🎮 Entertainment
- 💳 Utilities Bills & Insurance
- 🛒 Groceries & Markets

## Report Features

- **Total Amount** - Sum of all expenses in period
- **Average Daily** - Calculate daily spending average
- **Highest Category** - Identify top spending category
- **Category Breakdown** - Visualize spending distribution
- **Expense Details** - Expand categories to see individual transactions

## CSV Export

Export reports in CSV format for use in Excel, Google Sheets, or other analysis tools.

## Privacy

✅ **All data is stored locally** on your device  
✅ **No data sent to servers**  
✅ **100% private and secure**  

## Screenshots

[Add screenshots here after deployment]

## Tech Stack

- **Frontend:** Flutter/Dart
- **Language Support:** English
- **Data Storage:** Browser LocalStorage
- **CSV Parsing:** Custom RFC 4180 compliant parser

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Support

For bugs or feature requests, please open an GitHub issue.

---

**Made with ❤️ for better expense tracking**
