# Flutter Expense Report App - Setup Guide

## Project Overview

This is a complete Flutter mobile application for financial report generation with:
- **Offline-first architecture** - All data stored locally
- **CSV processing** - Export/import expense data
- **iOS & Android support** - Cross-platform compatibility
- **Spending reports** - Generate and analyze financial reports in Dart

## Quick Start

### 1. Prerequisites
- Install [Flutter SDK](https://flutter.dev/docs/get-started/install)
- Install [Dart SDK](https://dart.dev/get-dart) (comes with Flutter)
- IDE: VS Code, Android Studio, or IntelliJ IDEA

### 2. Setup Flutter Environment
```bash
# Verify Flutter installation
flutter doctor

# This should show:
# [✓] Flutter (Channel stable)
# [✓] Android toolchain
# [✓] Xcode (for iOS)
# [✓] VS Code
```

### 3. Install Dependencies
```bash
# Navigate to project
cd pythonexpenseapp

# Get all dependencies
flutter pub get

# Check for any issues
flutter analyze
```

### 4. Run the App

**On Android Emulator:**
```bash
flutter run
```

**On iOS Simulator:**
```bash
flutter run -d ios
```

**On Physical Device:**
```bash
flutter run
```

## App Architecture

### Models (`lib/models/`)
- **expense.dart**: Expense model with categories and payment methods
- **report.dart**: ExpenseReport model with analytics functions

### Services (`lib/services/`)
- **database_service.dart**: Local JSON-based offline storage
  - Add, update, delete expenses
  - Generate date-range queries
  - Save and retrieve reports
  
- **csv_export_service.dart**: CSV export/import functionality
  - Export expenses to CSV
  - Export reports with summaries
  - Import CSV data
  - Share reports via email/messaging

### Screens (`lib/screens/`)
- **main.dart**: App entry point with bottom navigation
- **expenses_screen.dart**: List and add expenses
- **reports_screen.dart**: View generated reports with details
- **generate_report_screen.dart**: Create new reports by date range

## Key Features Implemented

### 1. Expense Management
```dart
Expense(
  id: 'unique-id',
  description: 'Coffee',
  amount: 5.50,
  category: 'Food & Dining',
  date: DateTime.now(),
  paymentMethod: 'Cash',
  notes: 'Morning coffee'
)
```

### 2. Report Analytics
- Total spending calculation
- Category-wise breakdown
- Payment method analysis
- Daily average spending
- Highest spending category identification

### 3. CSV Processing
- Export expenses to spreadsheet format
- Export reports with summaries
- Import CSV data
- Share via email/messaging apps

### 4. Offline Storage
- JSON-based local storage
- No internet required
- Data persists between sessions
- Located in app documents directory

## Data Structure

```json
// expenses.json
[
  {
    "id": "uuid",
    "description": "Coffee",
    "amount": 5.50,
    "category": "Food & Dining",
    "date": "2024-01-31T10:30:00.000Z",
    "notes": "Morning coffee",
    "paymentMethod": "Cash"
  }
]

// reports.json
[
  {
    "id": "uuid",
    "title": "Monthly Report - January 31, 2024",
    "createdDate": "2024-01-31T10:30:00.000Z",
    "startDate": "2024-01-01T00:00:00.000Z",
    "endDate": "2024-01-31T23:59:59.999Z",
    "reportType": "monthly",
    "expenses": [...]
  }
]
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| intl | ^0.19.0 | Date/time formatting |
| path_provider | ^2.1.0 | Access documents directory |
| uuid | ^4.0.0 | Generate unique IDs |
| csv | ^6.0.0 | CSV parsing/writing |
| share_plus | ^7.2.0 | Share files |
| provider | ^6.1.0 | State management |

## Platform Configuration

### Android Setup
No additional setup required. Permissions are handled by Flutter.

### iOS Setup
No additional setup required. The app works on all iOS versions supported by Flutter.

## Building for Distribution

### Android APK
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (Recommended for Play Store)
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS
```bash
flutter build ios --release
# Then use Xcode to upload to App Store Connect
```

## Testing

Run the app and:

1. **Add expenses**
   - Navigate to Expenses tab
   - Tap + button
   - Fill all fields
   - Verify saved

2. **View expenses**
   - Check if expenses appear in list
   - Verify date ordering (newest first)

3. **Generate reports**
   - Navigate to Reports tab
   - Tap + button
   - Select report type
   - Verify report generates with correct data

4. **Test CSV export**
   - View a report
   - Export as CSV
   - Check CSV file format

## Troubleshooting

### "Flutter not found"
```bash
# Add Flutter to PATH
# Windows: Add Flutter/bin to System Environment Variables
# Mac/Linux: export PATH="$PATH:$(pwd)/flutter/bin"
```

### Dependencies won't install
```bash
flutter clean
flutter pub get
```

### App crashes on startup
```bash
flutter clean
flutter pub get
flutter run
# Check logs: flutter logs
```

### CSV export permission denied
- Check storage permissions in app settings
- Ensure device has available storage

## Future Enhancements

- [ ] Cloud backup (Firebase/AWS)
- [ ] Multi-currency support
- [ ] Budget alerts & notifications
- [ ] Receipt image attachment
- [ ] Advanced charts & visualization
- [ ] Recurring expenses
- [ ] Mobile payment integration
- [ ] Expense categorization rules
- [ ] Data encryption
- [ ] Multi-user support

## File Organization

```
pythonexpenseapp/
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── expense.dart
│   │   └── report.dart
│   ├── services/
│   │   ├── database_service.dart
│   │   └── csv_export_service.dart
│   ├── screens/
│   │   ├── expenses_screen.dart
│   │   ├── reports_screen.dart
│   │   └── generate_report_screen.dart
│   ├── widgets/
│   └── utils/
├── ios/              # iOS-specific code
├── android/          # Android-specific code
├── pubspec.yaml      # Dependencies
└── README.md
```

## Support & Documentation

- [Flutter Documentation](https://flutter.dev/docs)
- [Dart Language Guide](https://dart.dev/guides)
- [Material Design](https://material.io/design)

## License

MIT License - See LICENSE file for details
