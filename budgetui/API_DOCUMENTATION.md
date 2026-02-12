# API Documentation - Expense Report App

## 📚 Developer Reference

### Models API

#### Expense Model

```dart
class Expense {
  final String id;
  final String description;
  final double amount;
  final String category;
  final DateTime date;
  final String? notes;
  final String paymentMethod;

  // Constructor
  Expense({
    required this.id,
    required this.description,
    required this.amount,
    required this.category,
    required this.date,
    this.notes,
    required this.paymentMethod,
  });

  // JSON Methods
  Map<String, dynamic> toJson()
  factory Expense.fromJson(Map<String, dynamic> json)

  // Utilities
  Expense copyWith({...})
  String toString()
}
```

**Example Usage:**
```dart
final expense = Expense(
  id: DatabaseService.generateId(),
  description: 'Grocery shopping',
  amount: 45.50,
  category: ExpenseCategory.shopping,
  date: DateTime.now(),
  paymentMethod: PaymentMethod.creditCard,
  notes: 'Weekly groceries',
);

// JSON serialization
final json = expense.toJson();
final expenseFromJson = Expense.fromJson(json);

// Copy with modifications
final updated = expense.copyWith(amount: 50.00);
```

#### ExpenseReport Model

```dart
class ExpenseReport {
  final String id;
  final String title;
  final DateTime createdDate;
  final DateTime startDate;
  final DateTime endDate;
  final List<Expense> expenses;
  final String reportType; // 'daily', 'weekly', 'monthly', 'yearly'

  // Constructor
  ExpenseReport({
    required this.id,
    required this.title,
    required this.createdDate,
    required this.startDate,
    required this.endDate,
    required this.expenses,
    required this.reportType,
  });

  // Analytics Methods
  double getTotalAmount()
  Map<String, double> getCategoryTotals()
  Map<String, double> getPaymentMethodTotals()
  Map<DateTime, double> getDailyTotals()
  double getAverageDailySpending()
  String? getHighestCategory()

  // JSON Methods
  Map<String, dynamic> toJson()
  factory ExpenseReport.fromJson(Map<String, dynamic> json)
}
```

**Example Usage:**
```dart
final report = ExpenseReport(
  id: DatabaseService.generateId(),
  title: 'Monthly Report - January 2024',
  createdDate: DateTime.now(),
  startDate: DateTime(2024, 1, 1),
  endDate: DateTime(2024, 1, 31),
  expenses: [expense1, expense2, expense3],
  reportType: 'monthly',
);

// Analytics
final total = report.getTotalAmount();        // 150.50
final categories = report.getCategoryTotals(); // {'Food': 45.50, ...}
final avgDaily = report.getAverageDailySpending(); // 4.85
final highest = report.getHighestCategory();  // 'Food & Dining'
```

---

### DatabaseService API

Singleton pattern for local data persistence.

```dart
class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  
  factory DatabaseService() => _instance;
  
  DatabaseService._internal();

  // Initialization
  Future<void> init()

  // Expense Operations
  Future<void> addExpense(Expense expense)
  Future<void> updateExpense(Expense expense)
  Future<void> deleteExpense(String id)
  Future<List<Expense>> getAllExpenses()
  Future<List<Expense>> getExpensesByDateRange(DateTime start, DateTime end)
  Future<List<Expense>> getExpensesByCategory(String category)

  // Report Operations
  Future<void> saveReport(ExpenseReport report)
  Future<List<ExpenseReport>> getAllReports()
  Future<void> deleteReport(String reportId)

  // Utility
  static String generateId()
}
```

**Example Usage:**
```dart
// Initialize (in main())
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final db = DatabaseService();
  await db.init();
  runApp(const MainApp());
}

// Add expense
final db = DatabaseService();
await db.addExpense(expense);

// Get expenses
final allExpenses = await db.getAllExpenses();
final janExpenses = await db.getExpensesByDateRange(
  DateTime(2024, 1, 1),
  DateTime(2024, 1, 31),
);

// Generate ID
final id = DatabaseService.generateId();
```

---

### CsvExportService API

Static methods for CSV operations.

```dart
class CsvExportService {
  // Export
  static Future<File> exportExpensesToCsv(List<Expense> expenses)
  static Future<File> exportReportToCsv(ExpenseReport report)

  // Import
  static Future<List<Expense>> importFromCsv(File csvFile)

  // Share
  static Future<void> shareReportAsCsv(ExpenseReport report)
}
```

**Example Usage:**
```dart
// Export expenses
final csvFile = await CsvExportService.exportExpensesToCsv(expenses);

// Export report
final reportCsv = await CsvExportService.exportReportToCsv(report);

// Import from CSV
final importedExpenses = await CsvExportService.importFromCsv(file);

// Share report
await CsvExportService.shareReportAsCsv(report);
```

---

### Constants

#### ExpenseCategory

```dart
class ExpenseCategory {
  static const String food = 'Food & Dining';
  static const String transportation = 'Transportation';
  static const String utilities = 'Utilities';
  static const String entertainment = 'Entertainment';
  static const String shopping = 'Shopping';
  static const String health = 'Health & Medical';
  static const String education = 'Education';
  static const String work = 'Work Related';
  static const String personal = 'Personal';
  static const String other = 'Other';

  static const List<String> all = [
    food, transportation, utilities, entertainment, shopping,
    health, education, work, personal, other,
  ];
}
```

#### PaymentMethod

```dart
class PaymentMethod {
  static const String cash = 'Cash';
  static const String creditCard = 'Credit Card';
  static const String debitCard = 'Debit Card';
  static const String bankTransfer = 'Bank Transfer';
  static const String mobile = 'Mobile Payment';
  static const String other = 'Other';

  static const List<String> all = [
    cash, creditCard, debitCard, bankTransfer, mobile, other,
  ];
}
```

---

### Utility Functions

#### DateUtils

```dart
class DateUtils {
  static String formatDate(DateTime date)           // 'Jan 31, 2024'
  static String formatDateShort(DateTime date)      // 'Jan 31'
  static String formatDateISO(DateTime date)        // '2024-01-31'
  static String formatDateLong(DateTime date)       // 'Wednesday, January 31, 2024'
  static String formatDateRange(DateTime start, DateTime end)
  static bool isToday(DateTime date)
  static bool isYesterday(DateTime date)
  static int daysBetween(DateTime start, DateTime end)
  static DateTime startOfMonth(DateTime date)
  static DateTime endOfMonth(DateTime date)
  static DateTime startOfYear(DateTime date)
  static DateTime endOfYear(DateTime date)
  static DateTime startOfWeek(DateTime date)
  static DateTime endOfWeek(DateTime date)
}
```

**Example:**
```dart
final formatted = DateUtils.formatDate(DateTime.now()); // 'Jan 31, 2024'
final range = DateUtils.formatDateRange(start, end);    // 'Jan 01, 2024 - Jan 31, 2024'
```

#### CurrencyUtils

```dart
class CurrencyUtils {
  static String formatCurrency(double amount)         // '\$1,234.56'
  static String formatCurrencyAmount(double amount)   // '1,234.56'
  static double? parseCurrency(String value)
}
```

**Example:**
```dart
final formatted = CurrencyUtils.formatCurrency(1234.56); // '\$1,234.56'
```

#### ValidationUtils

```dart
class ValidationUtils {
  static bool isValidAmount(String value)
  static bool isValidDescription(String value)
  static bool isValidNotes(String value)
  static String? getAmountError(String value)
  static String? getDescriptionError(String value)
}
```

#### StatisticsUtils

```dart
class StatisticsUtils {
  static double calculatePercentage(double value, double total)
  static double roundTo2Decimals(double value)
  static String formatPercentage(double percentage)
  static double getPercentageChange(double old, double current)
  static String getChangeIndicator(double change)
}
```

---

### Screen Components

#### ExpensesScreen

Main expenses management screen with list and add functionality.

**Features:**
- Display all expenses
- Add new expense
- Delete existing expense
- Sorted by date (newest first)

**Usage:**
```dart
const ExpensesScreen()
```

#### ReportsScreen

Display generated reports with detailed analytics.

**Features:**
- List all reports
- View report details
- Delete reports
- Analytics visualization

**Usage:**
```dart
const ReportsScreen()
```

#### GenerateReportScreen

Create new expense reports with customizable parameters.

**Features:**
- Select report type (daily/weekly/monthly/yearly)
- Custom date range
- Generate report

**Usage:**
```dart
const GenerateReportScreen()
```

---

### Custom Widgets

#### AddExpenseSheet

Modal bottom sheet for adding new expenses.

```dart
AddExpenseSheet(
  onSave: (expense) {
    // Handle saved expense
  }
)
```

#### ReportDetailsSheet

Draggable bottom sheet displaying report analytics.

```dart
ReportDetailsSheet(report: report)
```

---

## 🔄 Complete Workflow Example

```dart
// 1. Initialize app
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final db = DatabaseService();
  await db.init();
  runApp(const MainApp());
}

// 2. Add expense
Future<void> addUserExpense() async {
  final db = DatabaseService();
  final expense = Expense(
    id: DatabaseService.generateId(),
    description: 'Coffee',
    amount: 5.50,
    category: ExpenseCategory.food,
    date: DateTime.now(),
    paymentMethod: PaymentMethod.cash,
  );
  await db.addExpense(expense);
}

// 3. Generate report
Future<void> generateMonthlyReport() async {
  final db = DatabaseService();
  final now = DateTime.now();
  final start = DateTime(now.year, now.month, 1);
  final end = DateTime(now.year, now.month + 1, 0);
  
  final expenses = await db.getExpensesByDateRange(start, end);
  final report = ExpenseReport(
    id: DatabaseService.generateId(),
    title: 'Monthly Report',
    createdDate: DateTime.now(),
    startDate: start,
    endDate: end,
    expenses: expenses,
    reportType: 'monthly',
  );
  await db.saveReport(report);
}

// 4. Export report
Future<void> exportReport(ExpenseReport report) async {
  final csvFile = await CsvExportService.exportReportToCsv(report);
  print('Exported to: ${csvFile.path}');
}
```

---

## 📊 Data Flow Diagram

```
User Input
    ↓
AddExpenseSheet → Expense Model → DatabaseService → JSON File
                                        ↓
                                  getAllExpenses()
                                        ↓
                                  ExpensesScreen displays
                                        ↓
    GenerateReportScreen → ExpenseReport Model → DatabaseService → JSON File
                                                        ↓
                                                 getAllReports()
                                                        ↓
                                                 ReportsScreen displays
                                                        ↓
                                            CsvExportService → CSV File
```

---

## 🐛 Error Handling

All services include try-catch blocks. Check logs for errors:

```bash
flutter logs
```

---

## 📱 Platform-Specific Considerations

### iOS
- Documents directory accessible via `path_provider`
- No special permissions needed

### Android
- Documents directory accessible via `path_provider`
- Storage permissions handled by `share_plus`

---

## 🔍 Debugging Tips

```dart
// Print all expenses
final expenses = await DatabaseService().getAllExpenses();
print(expenses);

// Print all reports
final reports = await DatabaseService().getAllReports();
print(reports);

// Check report analytics
print('Total: ${report.getTotalAmount()}');
print('Categories: ${report.getCategoryTotals()}');
print('Avg Daily: ${report.getAverageDailySpending()}');
```

---

**Last Updated**: January 31, 2024
**API Version**: 1.0
**Flutter**: 3.10.8+
