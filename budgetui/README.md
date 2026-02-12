# Expense Report App

A powerful Flutter mobile application for managing expenses and generating financial reports. Features offline-first architecture with CSV export/import capabilities.

## Features

- **Expense Tracking**: Add, edit, and delete expenses with detailed information
- **Offline Storage**: All data stored locally using JSON files
- **Report Generation**: Generate daily, weekly, monthly, and yearly expense reports
- **CSV Export/Import**: Export reports and expenses as CSV files for spreadsheet analysis
- **Financial Analytics**: 
  - Category-wise spending breakdown
  - Payment method analysis
  - Daily average spending calculation
  - Highest spending category identification
- **Cross-Platform**: Works on iOS and Android

## Project Structure

```
lib/
├── models/
│   ├── expense.dart          # Expense model with categories and payment methods
│   └── report.dart           # ExpenseReport model with analytics
├── services/
│   ├── database_service.dart # Local JSON-based database
│   └── csv_export_service.dart # CSV export/import functionality
├── screens/
│   ├── expenses_screen.dart  # Main expenses list and add expense
│   ├── reports_screen.dart   # View generated reports
│   └── generate_report_screen.dart # Report generation interface
├── widgets/                  # Reusable UI components
├── utils/                    # Utility functions
└── main.dart                 # Application entry point
```

## Getting Started

### Prerequisites

- Flutter SDK (3.10.8+)
- Dart SDK (3.10.8+)

### Installation

1. Navigate to project folder:
```bash
cd pythonexpenseapp
```

2. Install dependencies:
```bash
flutter pub get
```

3. Run the app:
```bash
flutter run
```

## Dependencies

- **intl**: Date and time formatting
- **path_provider**: Access app documents directory
- **uuid**: Generate unique IDs
- **csv**: CSV parsing and conversion
- **share_plus**: Share files and data
- **provider**: State management (optional enhancement)

## Usage

### Adding Expenses

1. Go to the "Expenses" tab
2. Tap the floating action button (+)
3. Fill in the expense details:
   - Description
   - Amount
   - Category
   - Payment Method
   - Date (optional)
   - Notes (optional)
4. Save the expense

### Generating Reports

1. Go to the "Reports" tab
2. Tap the floating action button (+)
3. Select report type (Daily, Weekly, Monthly, Yearly)
4. Adjust date range if needed
5. Generate report

### Viewing Report Details

1. Tap on any report to view:
   - Total spending
   - Average daily spending
   - Highest spending category
   - Category breakdown with percentages
   - Payment method breakdown
   - List of all expenses in the report

### Exporting Data

Reports and expenses can be exported as CSV files for:
- Spreadsheet analysis
- Budget planning
- Record keeping
- Sharing with accountants or financial advisors

## Data Storage

Data is stored locally in the application's documents directory:
- `expenses.json`: All recorded expenses
- `reports.json`: Generated reports

All data is stored offline and encrypted locally on the device.

## Supported Categories

- Food & Dining
- Transportation
- Utilities
- Entertainment
- Shopping
- Health & Medical
- Education
- Work Related
- Personal
- Other

## Supported Payment Methods

- Cash
- Credit Card
- Debit Card
- Bank Transfer
- Mobile Payment
- Other

## Troubleshooting

### App fails to launch
- Ensure Flutter SDK is properly installed: `flutter doctor`
- Delete build folder: `flutter clean`
- Reinstall dependencies: `flutter pub get`

### CSV export not working
- Ensure storage permissions are granted
- Check available disk space

### Data not persisting
- Verify app has write permissions
- Check device storage space

## Platform-Specific Setup

### iOS

1. Update `ios/Podfile` if needed
2. Run `flutter pub get`
3. Run `flutter run -d ios`

### Android

1. Ensure Android SDK is installed
2. Run `flutter pub get`
3. Run `flutter run -d android`

## Building for Production

### iOS
```bash
flutter build ios --release
```

### Android
```bash
flutter build apk --release
# or for App Bundle (recommended)
flutter build appbundle --release
```

## License

MIT License - feel free to use this for personal or commercial projects
