#!/usr/bin/env python3
"""
Monthly Transaction Logger & Analytics
Maintains separate logs of transactions by month for historical comparison
Enables month-to-month spending analysis
"""

import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

class TransactionLogger:
    """
    Logs and archives transactions by month
    Enables historical comparison and trend analysis
    """
    
    def __init__(self, log_dir: str = None):
        """Initialize transaction logger"""
        
        # Set up log directory
        if log_dir is None:
            home = Path.home()
            log_dir = home / '.config' / 'SpendingApp' / 'transaction_logs'
        else:
            log_dir = Path(log_dir)
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Monthly transaction storage
        self.current_month_key = None
        self.transactions_by_month = {}
        self.monthly_summaries = {}
    
    def _get_month_key(self, date_obj: datetime) -> str:
        """Generate month key in format YYYY-MM"""
        return date_obj.strftime('%Y-%m')
    
    def log_transaction(self, 
                       date: str, 
                       vendor: str, 
                       amount: float, 
                       category: str,
                       description: str = "",
                       transaction_id: str = None) -> str:
        """
        Log individual transaction
        
        Args:
            date: Transaction date (YYYY-MM-DD or similar)
            vendor: Vendor name
            amount: Transaction amount
            category: Category assigned
            description: Optional description
            transaction_id: Optional unique ID
            
        Returns:
            Transaction ID
        """
        
        try:
            # Parse date
            date_obj = pd.to_datetime(date)
            month_key = self._get_month_key(date_obj)
            
            # Generate transaction ID if not provided
            if transaction_id is None:
                hash_input = f"{date}|{vendor}|{amount}|{category}".encode()
                transaction_id = hashlib.md5(hash_input).hexdigest()[:12]
            
            # Initialize month storage if needed
            if month_key not in self.transactions_by_month:
                self.transactions_by_month[month_key] = []
            
            # Create transaction record
            transaction = {
                'id': transaction_id,
                'date': date,
                'vendor': vendor,
                'amount': float(amount),
                'category': category,
                'description': description,
                'logged_at': datetime.now().isoformat()
            }
            
            # Add to monthly log
            self.transactions_by_month[month_key].append(transaction)
            self.current_month_key = month_key
            
            return transaction_id
            
        except Exception as e:
            print(f"❌ Error logging transaction: {e}")
            return None
    
    def log_transactions_batch(self, transactions_df: pd.DataFrame, 
                               date_column: str = 'Date',
                               vendor_column: str = 'Vendor',
                               amount_column: str = 'Amount',
                               category_column: str = 'Category') -> int:
        """
        Log multiple transactions from DataFrame
        
        Args:
            transactions_df: DataFrame with transaction data
            date_column: Column name for date
            vendor_column: Column name for vendor
            amount_column: Column name for amount
            category_column: Column name for category
            
        Returns:
            Number of transactions logged
        """
        
        logged_count = 0
        
        for idx, row in transactions_df.iterrows():
            try:
                self.log_transaction(
                    date=row[date_column],
                    vendor=row[vendor_column],
                    amount=row[amount_column],
                    category=row[category_column],
                    description=row.get('Description', '')
                )
                logged_count += 1
            except Exception as e:
                print(f"⚠️  Skipped transaction at row {idx}: {e}")
        
        return logged_count
    
    def get_month_transactions(self, month_key: str) -> List[Dict]:
        """Get all transactions for a specific month"""
        return self.transactions_by_month.get(month_key, [])
    
    def get_available_months(self) -> List[str]:
        """Get list of months with transaction data (sorted)"""
        months = sorted(self.transactions_by_month.keys())
        return months
    
    def calculate_monthly_summary(self, month_key: str) -> Dict:
        """
        Calculate spending summary for a month
        
        Args:
            month_key: Month in format YYYY-MM
            
        Returns:
            Dictionary with summary statistics
        """
        
        transactions = self.get_month_transactions(month_key)
        
        if not transactions:
            return {
                'month': month_key,
                'total_transactions': 0,
                'total_amount': 0,
                'average_spending': 0,
                'by_category': {},
                'top_vendors': [],
                'available': False
            }
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(transactions)
        
        # Category breakdown
        category_summary = df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).to_dict('index')
        category_breakdown = {}
        for cat, stats in category_summary.items():
            category_breakdown[cat] = {
                'total': float(stats['sum']),
                'count': int(stats['count']),
                'average': float(stats['mean'])
            }
        
        # Top vendors
        top_vendors = df.groupby('vendor')['amount'].sum().sort_values(ascending=False).head(10)
        top_vendors_dict = {vendor: float(amount) for vendor, amount in top_vendors.items()}
        
        summary = {
            'month': month_key,
            'total_transactions': len(transactions),
            'total_amount': float(df['amount'].sum()),
            'average_spending': float(df['amount'].mean()),
            'max_transaction': float(df['amount'].max()),
            'min_transaction': float(df['amount'].min()),
            'by_category': category_breakdown,
            'top_vendors': top_vendors_dict,
            'available': True
        }
        
        self.monthly_summaries[month_key] = summary
        return summary
    
    def compare_months(self, month1: str, month2: str) -> Dict:
        """
        Compare spending between two months
        
        Args:
            month1: First month (YYYY-MM)
            month2: Second month (YYYY-MM)
            
        Returns:
            Comparison dictionary
        """
        
        summary1 = self.calculate_monthly_summary(month1)
        summary2 = self.calculate_monthly_summary(month2)
        
        if not summary1['available'] or not summary2['available']:
            return {
                'error': 'One or both months have no transaction data',
                'month1': month1,
                'month2': month2
            }
        
        # Calculate differences
        total_diff = summary2['total_amount'] - summary1['total_amount']
        total_diff_percent = (total_diff / summary1['total_amount'] * 100) if summary1['total_amount'] > 0 else 0
        
        # Category comparison
        category_comparison = {}
        all_categories = set(summary1['by_category'].keys()) | set(summary2['by_category'].keys())
        
        for cat in all_categories:
            cat1 = summary1['by_category'].get(cat, {'total': 0, 'count': 0})
            cat2 = summary2['by_category'].get(cat, {'total': 0, 'count': 0})
            
            cat_diff = cat2['total'] - cat1['total']
            cat_diff_percent = (cat_diff / cat1['total'] * 100) if cat1['total'] > 0 else 0
            
            category_comparison[cat] = {
                'month1_total': cat1['total'],
                'month2_total': cat2['total'],
                'difference': cat_diff,
                'percent_change': cat_diff_percent,
                'month1_count': cat1['count'],
                'month2_count': cat2['count']
            }
        
        return {
            'month1': month1,
            'month2': month2,
            'month1_summary': summary1,
            'month2_summary': summary2,
            'total_difference': total_diff,
            'total_percent_change': total_diff_percent,
            'categories': category_comparison,
            'increased_categories': [cat for cat, comp in category_comparison.items() 
                                    if comp['difference'] > 0],
            'decreased_categories': [cat for cat, comp in category_comparison.items() 
                                    if comp['difference'] < 0]
        }
    
    def save_monthly_logs(self) -> Dict[str, Path]:
        """
        Save all transaction logs to JSON files
        
        Returns:
            Dictionary of month -> file path
        """
        
        saved_files = {}
        
        for month_key, transactions in self.transactions_by_month.items():
            # Create JSON file for the month
            file_path = self.log_dir / f"transactions_{month_key}.json"
            
            log_data = {
                'month': month_key,
                'generated_at': datetime.now().isoformat(),
                'transaction_count': len(transactions),
                'transactions': transactions
            }
            
            with open(file_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            saved_files[month_key] = file_path
            print(f"✓ Saved {len(transactions)} transactions for {month_key} → {file_path}")
        
        return saved_files
    
    def load_monthly_logs(self, month_key: str = None) -> int:
        """
        Load transaction logs from JSON files
        
        Args:
            month_key: Specific month to load (YYYY-MM), or None for all
            
        Returns:
            Number of transactions loaded
        """
        
        total_loaded = 0
        
        if month_key:
            # Load specific month
            file_path = self.log_dir / f"transactions_{month_key}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.transactions_by_month[month_key] = data['transactions']
                    total_loaded = len(data['transactions'])
                    print(f"✓ Loaded {total_loaded} transactions for {month_key}")
        else:
            # Load all months
            for file_path in self.log_dir.glob("transactions_*.json"):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    month = data['month']
                    self.transactions_by_month[month] = data['transactions']
                    total_loaded += len(data['transactions'])
                    print(f"✓ Loaded {len(data['transactions'])} transactions for {month}")
        
        return total_loaded
    
    def build_comparison_context(self, month1: str = None, month2: str = None) -> str:
        """
        Build context for LLM comparing two months
        
        Args:
            month1: First month (latest if None)
            month2: Second month (previous if None)
            
        Returns:
            Formatted context string for LLM
        """
        
        months = self.get_available_months()
        
        if not months:
            return "No transaction data available for comparison."
        
        # Default to latest two months
        if month2 is None:
            month2 = months[-2] if len(months) >= 2 else months[-1]
        if month1 is None:
            month1 = months[-1]
        
        comparison = self.compare_months(month2, month1)
        
        if 'error' in comparison:
            return f"Error: {comparison['error']}"
        
        context = f"""
MONTHLY SPENDING COMPARISON

Current Month: {month1}
Previous Month: {month2}

=== OVERVIEW ===
{month1} Total Spending: ${comparison['month1_summary']['total_amount']:.2f}
{month2} Total Spending: ${comparison['month2_summary']['total_amount']:.2f}
Difference: ${comparison['total_difference']:+.2f} ({comparison['total_percent_change']:+.1f}%)
Transaction Count: {comparison['month1_summary']['total_transactions']} (current) vs {comparison['month2_summary']['total_transactions']} (previous)

=== CATEGORY BREAKDOWN FOR {month1} ===
"""
        
        for cat, stats in comparison['month1_summary']['by_category'].items():
            context += f"{cat}: ${stats['total']:.2f} ({stats['count']} transactions, avg: ${stats['average']:.2f})\n"
        
        context += f"\n=== CATEGORY INCREASES (vs {month2}) ===\n"
        for cat in comparison['increased_categories']:
            comp = comparison['categories'][cat]
            context += f"{cat}: +${comp['difference']:.2f} ({comp['percent_change']:+.1f}%)\n"
        
        context += f"\n=== CATEGORY DECREASES (vs {month2}) ===\n"
        for cat in comparison['decreased_categories']:
            comp = comparison['categories'][cat]
            context += f"{cat}: -${abs(comp['difference']):.2f} ({comp['percent_change']:.1f}%)\n"
        
        context += f"\n=== TOP 10 VENDORS ({month1}) ===\n"
        for vendor, amount in list(comparison['month1_summary']['top_vendors'].items())[:10]:
            context += f"{vendor}: ${amount:.2f}\n"
        
        return context


# Global transaction logger instance
_transaction_logger = None

def get_transaction_logger() -> TransactionLogger:
    """Get or create global transaction logger"""
    global _transaction_logger
    if _transaction_logger is None:
        _transaction_logger = TransactionLogger()
    return _transaction_logger

def init_transaction_logger(log_dir: str = None) -> TransactionLogger:
    """Initialize transaction logger"""
    global _transaction_logger
    _transaction_logger = TransactionLogger(log_dir)
    return _transaction_logger
