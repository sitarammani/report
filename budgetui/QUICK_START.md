# Quick Start Guide - Expense Report App

## 🚀 Get Running in 5 Minutes

### Step 1: Prerequisites Check
Ensure you have Flutter installed:
```bash
flutter --version
# Should output: Flutter 3.10.8 or higher
```

If not installed, visit: https://flutter.dev/docs/get-started/install

### Step 2: Navigate to Project
```bash
cd pythonexpenseapp
```

### Step 3: Get Dependencies
```bash
flutter pub get
```

### Step 4: Run App
```bash
# On Android emulator or iOS simulator
flutter run

# Or specify device
flutter run -d "device-id"
```

## 📱 App Navigation

### Main Screens

**1. Expenses Tab**
- View all your expenses
- Add new expense (+ button)
- Delete expenses (menu)
- Sorted by newest first

**2. Reports Tab**
- View generated reports
- Generate new report (+ button)
- View detailed analytics

## ➕ Adding Your First Expense

1. Tap **Expenses** tab
2. Tap **+ (plus)** button
3. Fill in:
   - **Description**: What did you spend on?
   - **Amount**: How much? ($)
   - **Category**: Type of expense
   - **Payment Method**: How did you pay?
   - **Date**: When? (Today by default)
   - **Notes**: Optional extra info
4. Tap **Save Expense**

## 📊 Generating Your First Report

1. Tap **Reports** tab
2. Tap **+ (plus)** button
3. Choose report type:
   - **Daily**: Today's expenses
   - **Weekly**: Last 7 days
   - **Monthly**: This month
   - **Yearly**: This year
   - **Custom**: Select your own dates
4. Tap **Generate Report**

## 📈 View Report Details

1. From Reports tab, tap any report
2. See analytics:
   - **Total** spending
   - **Average Daily** spending
   - **Highest Category** (most spent)
   - **Category Breakdown**: % breakdown by type
   - **Payment Methods**: By payment method
   - **All Expenses**: List of expenses in report

## 💾 Data Storage

- All data stored **locally** on your device
- No internet required
- Data persists between app sessions
- Stored in: `documents/expenses.json` and `documents/reports.json`

## 🎨 Categories

Choose from these expense categories:
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

## 💳 Payment Methods

Select from these payment methods:
- Cash
- Credit Card
- Debit Card
- Bank Transfer
- Mobile Payment
- Other

## 🐛 Common Issues

**Q: App won't open?**
```bash
flutter clean
flutter pub get
flutter run
```

**Q: Expenses not saving?**
- Check device storage space
- Restart app

**Q: Want to export data?**
- Share reports as CSV
- Use reports with spreadsheet apps

## 📚 Full Documentation

- **README.md**: Project overview
- **SETUP_GUIDE.md**: Detailed setup instructions

## ⚙️ Build for Devices

**Android (.apk)**
```bash
flutter build apk --release
```

**iOS**
```bash
flutter build ios --release
```

## 🎓 Learning Resources

- [Flutter Docs](https://flutter.dev/docs)
- [Dart Language Guide](https://dart.dev/guides)
- [Material Design](https://material.io/design)

## ✨ Next Steps

After getting comfortable with the app:
1. Add multiple expenses
2. Generate reports for different periods
3. Explore category and payment method analytics
4. Export reports for record keeping

Happy tracking! 💰
