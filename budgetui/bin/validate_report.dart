import 'dart:io';
import 'dart:convert';
import 'package:csv/csv.dart';

// Lightweight validator that mirrors the UI parsing + vendor rules
// Usage: dart run bin/validate_report.dart /path/to/csv/dir

final vendorPatterns = <Map<String, String>>[
  {'pattern': r'TMOBILE.*', 'vendor': 'TMOBILE'},
  {'pattern': r'COMCAST.*', 'vendor': 'COMCAST'},
  {'pattern': r'ATGPAY.*', 'vendor': 'ATGPAY'},
  {'pattern': r'NSM DBAMR.*COOPER.*', 'vendor': 'NSM DBAMR.COOPER'},
  {'pattern': r'WESTERN UNION.*|WESTERN .*', 'vendor': 'WESTERN UNION'},
  {'pattern': r'CITI AUTOPAY.*', 'vendor': 'CITI AUTOPAY'},
  {'pattern': r'CASH APP.*|CASHAPP.*', 'vendor': 'CASH APP'},
  {'pattern': r'REVERSAL.*', 'vendor': 'REVERSAL'},
  {'pattern': r'Subscription.*', 'vendor': 'SUBSCRIPTION'},
  {'pattern': r'CITGO.*', 'vendor': 'CITGO'},
  {'pattern': r'KROGER.*', 'vendor': 'KROGER'},
  {'pattern': r'CHERIANS.*', 'vendor': 'CHERIANS INTERNATIONAL'},
  {'pattern': r'PATEL BROTHERS.*', 'vendor': 'PATEL'},
  {'pattern': r'PATEL.*', 'vendor': 'PATEL'},
  {'pattern': r'INDIFRESH.*|TST\*INDI.*', 'vendor': 'INDIFRESH'},
  {'pattern': r'FRESH MEAT IN MART.*', 'vendor': 'FRESH MEAT IN MART'},
  {'pattern': r'WEGMANS.*', 'vendor': 'WEGMANS'},
  {'pattern': r'PUBLIX.*', 'vendor': 'PUBLIX'},
  {'pattern': r'FCS FOOD AND NUTRITION.*', 'vendor': 'FCS FOOD AND NUTRITION'},
  {'pattern': r'AMAZON.*', 'vendor': 'AMAZON'},
  {'pattern': r'COSTCO WHSE.*', 'vendor': 'COSTCO'},
  {'pattern': r'COSTCO GAS.*', 'vendor': 'COSTCO GAS'},
  {'pattern': r'KROGER FUEL.*', 'vendor': 'KROGER FUEL'},
  {'pattern': r'SQ \*NALAN INDIAN CUISINE.*', 'vendor': 'NALAN INDIAN CUISINE'},
  {'pattern': r'TACO BELL.*', 'vendor': 'TACO BELL'},
  {'pattern': r"DOMINO'S.*", 'vendor': 'DOMINOS'},
  {'pattern': r'TARGET.*', 'vendor': 'TARGET'},
  {'pattern': r'WAL-?MART.*', 'vendor': 'WALMART'},
  {'pattern': r'DOLLAR TREE.*', 'vendor': 'DOLLAR TREE'},
  {'pattern': r'SHELL OIL.*', 'vendor': 'SHELL'},
  {'pattern': r"MCDONALD'S.*", 'vendor': 'MCDONALDS'},
  {'pattern': r'DUNKIN.*', 'vendor': 'DUNKIN'},
  {'pattern': r'CHIPOTLE.*', 'vendor': 'CHIPOTLE'},
  {'pattern': r'SUBWAY.*', 'vendor': 'SUBWAY'},
  {'pattern': r'LEAGUE TENNIS.*', 'vendor': 'LEAGUE TENNIS'},
  {'pattern': r'TELLO US.*', 'vendor': 'TELLO'},
  {'pattern': r'TMOBILE\*AUTO PAY.*', 'vendor': 'TMOBILE'},
  {'pattern': r'COMCAST-XFINITY.*', 'vendor': 'COMCAST'},
  {'pattern': r'SAWNEE ELECTRIC MEMBERSH.*', 'vendor': 'SAWNEE ELECTRIC'},
  {'pattern': r'CONSTELLATION NEW ENERGY.*', 'vendor': 'CONSTELLATION ENERGY'},
  {'pattern': r'FC WATER&SEWER.*', 'vendor': 'FC WATER&SEWER'},
  {'pattern': r'RED OAK SANITATION.*', 'vendor': 'RED OAK SANITATION'},
  {'pattern': r'WWP\*GOT BUGS INC.*', 'vendor': 'WWP GOT BUGS'},
  {'pattern': r'TRAVELERS-GEICO AGENCY.*', 'vendor': 'TRAVELERS-GEICO'},
  {'pattern': r'AAA LIFE INSURANCE.*', 'vendor': 'AAA LIFE INSURANCE'},
  {'pattern': r'THE EMORY CLINIC, INC.*', 'vendor': 'EMORY CLINIC'},
  {'pattern': r'TELADOC.*', 'vendor': 'TELADOC'},
  {'pattern': r'HAWKMUSICACADEMY.*', 'vendor': 'HAWKMUSIC ACADEMY'},
  {'pattern': r'JFI\*URBAN AIR.*', 'vendor': 'URBAN AIR'},
  {'pattern': r'AMC .*|AMC \d+ ONLINE.*', 'vendor': 'AMC'},
  {'pattern': r'TJ MAXX.*', 'vendor': 'TJ MAXX'},
  {'pattern': r'TST\* DESI DISTRICT.*', 'vendor': 'DESI DISTRICT'},
  {'pattern': r'SQ \*BEAUTY AMBASSADORS.*', 'vendor': 'BEAUTY AMBASSADORS'},
  {'pattern': r'TANISHQ - ATLANTA.*', 'vendor': 'TANISHQ'},
  {'pattern': r'THE HOME DEPOT .*', 'vendor': 'HOME DEPOT'},
  {'pattern': r'WAWA 118.*', 'vendor': 'WAWA'},
  {'pattern': r'ATGPAY ONLINE PA.*', 'vendor': 'ATGPAY'},
  {'pattern': r'NSM DBAMR\\.COOPER.*', 'vendor': 'NSM DBAMR.COOPER'},
  {'pattern': r'HOMEDEPOT.*', 'vendor': 'HOME DEPOT'},
  {'pattern': r'DOLLAR-GENERAL.*', 'vendor': 'DOLLAR TREE'},
  {'pattern': r'PAYPAL.*', 'vendor': 'PAYPAL'},
  {'pattern': r'ROSS STORE.*', 'vendor': 'ROSS'},
  {'pattern': r'FORSYTH COUNTY.*', 'vendor': 'FORSYTH COUNTY'},
];


String normalizeVendor(String desc) {
  final d = desc.toUpperCase();
  for (final p in vendorPatterns) {
    final regex = RegExp('^' + p['pattern']!, caseSensitive: false);
    if (regex.hasMatch(d)) return p['vendor']!;
  }
  return d.split(' ').first;
}

String categorizeVendor(String vendor) {
  final v = vendor.toUpperCase();
  final groceries = {
    'KROGER', 'INDIFRESH', 'CHERIANS INTERNATIONAL', 'FRESH MEAT IN MART', 'WEGMANS', 'PUBLIX', 'FCS FOOD AND NUTRITION', 'COSTCO'
  };
  final restaurants = {'TACO BELL', 'DOMINOS', 'SUBWAY', 'CHIPOTLE', 'MCDONALDS', 'DESI DISTRICT', 'NALAN INDIAN CUISINE', 'DUNKIN'};
  final shopping = {'AMAZON', 'BESTBUY', 'TARGET', 'WALMART', 'TJ MAXX', 'BEAUTY AMBASSADORS', 'TANISHQ', 'ROSS', 'DOLLAR TREE', 'OPTICONTACTS', 'FCPL', 'SCHLPAY', 'PAYPAL', 'REVERSAL', 'CASH APP', 'CITGO', 'SUBSCRIPTION', 'CITI AUTOPAY', 'FORSYTH COUNTY', 'PATEL', 'WESTERN UNION'};
  final autoGas = {'COSTCO GAS', 'KROGER FUEL', 'SHELL', 'WAWA'};
  final utilities = {'COMCAST', 'TMOBILE', 'SAWNEE ELECTRIC', 'CONSTELLATION ENERGY', 'TELLO', 'TRAVELERS-GEICO', 'AAA LIFE INSURANCE', 'FC WATER&SEWER', 'RED OAK SANITATION', 'ATGPAY', 'NSM DBAMR.COOPER'};
  final health = {'TELADOC', 'EMORY CLINIC'};
  final entertainment = {'AMC', 'URBAN AIR', 'HAWKMUSIC ACADEMY', 'LEAGUE TENNIS'};
  final homeServices = {'HOME DEPOT', 'WWP GOT BUGS'};

  if (groceries.contains(v)) return 'Groceries & Markets';
  if (restaurants.contains(v)) return 'Restaurants & Food';
  if (autoGas.contains(v)) return 'Auto & Gas';
  if (utilities.contains(v)) return 'Utilities Bills & Insurance';
  if (health.contains(v)) return 'Health';
  if (entertainment.contains(v)) return 'Entertainment';
  if (homeServices.contains(v)) return 'Home & Services';
  if (shopping.contains(v)) return 'Shopping & Retail';
  return 'Shopping & Retail';
}

DateTime? parseDate(String s) {
  final trimmed = s.trim();
  if (trimmed.isEmpty) return null;
  final mmddyyyy = RegExp(r'^(\d{1,2})/(\d{1,2})/(\d{4})$');
  final mmddyy = RegExp(r'^(\d{1,2})/(\d{1,2})/(\d{2})$');
  final ymd = RegExp(r'^(\d{4})-(\d{1,2})-(\d{1,2})$');
  var m = mmddyyyy.firstMatch(trimmed);
  if (m != null) return DateTime(int.parse(m.group(3)!), int.parse(m.group(1)!), int.parse(m.group(2)!));
  m = mmddyy.firstMatch(trimmed);
  if (m != null) { var y = int.parse(m.group(3)!); if (y < 100) y += 2000; return DateTime(y, int.parse(m.group(1)!), int.parse(m.group(2)!)); }
  m = ymd.firstMatch(trimmed);
  if (m != null) return DateTime(int.parse(m.group(1)!), int.parse(m.group(2)!), int.parse(m.group(3)!));
  return null;
}

bool isIncomeOrTransfer(String s) {
  final kws = ['PAYROLL', 'ZELLE PAYMENT FROM', 'TRANSFER', 'OVERDRAFT PROTECTION', 'DEPOSIT', 'CREDIT CARD BILL PAYMENT', 'ONLINE BANKING PAYMENT', 'ONLINE PAYMENT', 'BA ELECTRONIC PAYMENT', 'BEGINNING BALANCE', 'FID BKG SVC', 'KEEP THE CHANGE'];
  final d = s.toUpperCase();
  return kws.any((k) => d.contains(k));
}

double? parseAmount(String s) {
  if (s == null) return null;
  final cleaned = s.replaceAll(RegExp(r'[\$,]'), '').trim();
  if (cleaned.isEmpty) return null;
  return double.tryParse(cleaned);
}

List<List<String>> parseWithDelimiterDetection(String content) {
  // Normalize line endings to \n
  final normalized = content.replaceAll('\r\n', '\n').replaceAll('\r', '\n');
  final lines = normalized.split('\n').where((l) => l.trim().isNotEmpty).toList();
  if (lines.isEmpty) return [];
  int pipeCount = 0, commaCount = 0;
  for (final line in lines.take(3)) { pipeCount += '|'.allMatches(line).length; commaCount += ','.allMatches(line).length; }
  if (pipeCount > commaCount && pipeCount > 0) {
    return lines.map((l) => l.split('|').map((f) => f.trim()).toList()).toList();
  }
  final conv = CsvToListConverter(eol: '\n');
  final rows = conv.convert(normalized);
  return rows.map((r) => r.map((c) => c?.toString() ?? '').toList()).toList();
}

int findHeaderRow(List<List<String>> rows) {
  final scan = rows.length < 10 ? rows.length : 10;
  for (int i = 0; i < scan; i++) {
    final joined = rows[i].map((c) => c.toLowerCase()).join(' ');
    if (joined.contains('date') && joined.contains('amount') && (joined.contains('description') || joined.contains('payee') || joined.contains('merchant') || joined.contains('vendor') || joined.contains('desc'))) {
      return i;
    }
  }
  return 0;
}

Map<String, int?> detectHeaders(List<String> headerRow) {
  final Map<String, int?> headers = {
    'date': null,
    'description': null,
    'amount': null,
    'debit': null,
    'credit': null,
    'paymentMethod': null,
    'notes': null,
    'category': null,
  };
  for (int i = 0; i < headerRow.length; i++) {
    final h = headerRow[i].toLowerCase();
    if (h.contains('date') && headers['date'] == null) headers['date'] = i;
    if ((h.contains('payee') || h.contains('description') || h.contains('desc') || h.contains('merchant') || h.contains('vendor')) && headers['description'] == null) headers['description'] = i;
    if ((h.contains('amount') || h.contains('debit') || h.contains('credit') || h.contains('total')) && headers['amount'] == null) { headers['amount'] = i; if (h.contains('debit')) headers['debit'] = i; if (h.contains('credit')) headers['credit'] = i; }
    if ((h.contains('payment') || h.contains('method')) && headers['paymentMethod'] == null) headers['paymentMethod'] = i;
    if ((h.contains('note') || h.contains('memo') || h.contains('reference')) && headers['notes'] == null) headers['notes'] = i;
  }
  if (headers['date'] == null) headers['date'] = 0;
  if (headers['description'] == null) headers['description'] = 2;
  if (headers['amount'] == null) headers['amount'] = 4;
  if (headers['paymentMethod'] == null) headers['paymentMethod'] = 3;
  if (headers['notes'] == null) headers['notes'] = 1;
  return headers;
}

void main(List<String> args) async {
  if (args.isEmpty) {
    print('Usage: dart run bin/validate_report.dart /path/to/csv/dir [MM/YYYY]');
    exit(1);
  }
  final dir = Directory(args[0]);
  // Optional month/year arg to filter transactions (MM/YYYY)
  int targetMonth = DateTime.now().month;
  int targetYear = DateTime.now().year;
  if (args.length > 1) {
    final parts = args[1].split('/');
    if (parts.length == 2) {
      targetMonth = int.tryParse(parts[0]) ?? targetMonth;
      targetYear = int.tryParse(parts[1]) ?? targetYear;
    }
  }
  if (!await dir.exists()) { print('Directory not found: ${args[0]}'); exit(1); }

  final categoryTotals = <String, double>{};
  final vendorTotals = <String, Map<String, double>>{}; // vendor -> {category: total}

  await for (final file in dir.list()) {
    if (file is! File) continue;
    final path = file.path;
    if (!path.toLowerCase().endsWith('.csv')) continue;
    final content = await file.readAsString();
    final rows = parseWithDelimiterDetection(content);
    if (rows.isEmpty) continue;
    final headerRowIndex = findHeaderRow(rows);
    final headers = detectHeaders(rows[headerRowIndex]);

    for (int i = headerRowIndex + 1; i < rows.length; i++) {
      final row = rows[i];
      String? date = (headers['date']! < row.length) ? row[headers['date']!].trim() : '';
      String? desc = (headers['description']! < row.length) ? row[headers['description']!].trim() : '';
      String? amountStr;
      if (headers['debit'] != null || headers['credit'] != null) {
        final debit = (headers['debit'] != null && headers['debit']! < row.length) ? row[headers['debit']!].trim() : '';
        final credit = (headers['credit'] != null && headers['credit']! < row.length) ? row[headers['credit']!].trim() : '';
        if (debit.isNotEmpty) amountStr = '-$debit'; else if (credit.isNotEmpty) amountStr = credit; else amountStr = (headers['amount']! < row.length) ? row[headers['amount']!].trim() : '';
      } else {
        amountStr = (headers['amount']! < row.length) ? row[headers['amount']!].trim() : '';
      }
      if (date == null || desc == null || amountStr == null) continue;
      if (date.isEmpty || desc.isEmpty || amountStr.isEmpty) continue;
      final parsedDate = parseDate(date);
      if (parsedDate == null) continue;
      // Filter to target month/year to match Python behavior
      if (parsedDate.month != targetMonth || parsedDate.year != targetYear) continue;
      if (isIncomeOrTransfer(desc)) continue;
      final parsedAmount = parseAmount(amountStr);
      if (parsedAmount == null || parsedAmount == 0) continue;
      final norm = normalizeVendor(desc);
      final category = categorizeVendor(norm);
      categoryTotals[category] = (categoryTotals[category] ?? 0) + parsedAmount;
      vendorTotals.putIfAbsent(norm, () => {});
      vendorTotals[norm]![category] = (vendorTotals[norm]![category] ?? 0) + parsedAmount;
    }
  }

  print('\n=== Category Totals ===');
  final ordered = categoryTotals.entries.toList()..sort((a,b) => b.value.abs().compareTo(a.value.abs()));
  for (final e in ordered) {
    print('${e.key}: ${e.value.toStringAsFixed(2)}');
  }

  print('\n=== Groceries Vendor Breakdown ===');
  final groceriesVendors = vendorTotals.entries.where((v) => v.value.keys.contains('Groceries & Markets'));
  for (final v in groceriesVendors) {
    final amt = v.value['Groceries & Markets'] ?? 0.0;
    print('${v.key}: ${amt.toStringAsFixed(2)}');
  }

  print('\n=== Shopping & Retail Vendor Breakdown ===');
  final shoppingVendors = vendorTotals.entries.where((v) => v.value.keys.contains('Shopping & Retail'));
  for (final v in shoppingVendors) {
    final amt = v.value['Shopping & Retail'] ?? 0.0;
    print('${v.key}: ${amt.toStringAsFixed(2)}');
  }

  print('\n=== Utilities Vendor Breakdown ===');
  final utilitiesVendors = vendorTotals.entries.where((v) => v.value.keys.contains('Utilities Bills & Insurance'));
  for (final v in utilitiesVendors) {
    final amt = v.value['Utilities Bills & Insurance'] ?? 0.0;
    print('${v.key}: ${amt.toStringAsFixed(2)}');
  }

  print('\nDone.');
}
