#!/usr/bin/env python3
"""
Spending Data LLM Integration
Query spending data using natural language with local LLM (Ollama)
No API required - everything runs locally
"""

import pandas as pd
import subprocess
import json
import re
import os
from pathlib import Path
from typing import Optional, Dict, List
import requests
from datetime import datetime
from metrics_logger import get_metrics_logger
from transaction_logger import get_transaction_logger, init_transaction_logger

class SpendingLM:
    """Local LLM interface for spending data analysis"""
    
    def __init__(self, model="mistral", ollama_host="http://localhost:11434"):
        """
        Initialize LLM interface
        
        Args:
            model: Model name (default: mistral, options: mistral, llama2, neural-chat, dolphin-mixtral)
            ollama_host: Ollama server URL
        """
        self.model = model
        self.ollama_host = ollama_host
        self.available_models = []
        self.spending_data = None
        self.categories = None
        self.rules = None
        self.transaction_logger = get_transaction_logger()  # Initialize transaction logger
        
    def is_ollama_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def list_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            data = response.json()
            models = [m["name"].split(":")[0] for m in data.get("models", [])]
            self.available_models = list(set(models))  # Remove duplicates
            return self.available_models
        except Exception as e:
            print(f"⚠️  Could not list models: {e}")
            return []
    
    def pull_model(self, model_name: str = "mistral") -> bool:
        """
        Download and install a model
        Note: Mistral is smaller, faster (4GB vs 7GB for llama2)
        """
        if self.model in self.list_available_models():
            print(f"✓ Model '{self.model}' already available")
            return True
        
        print(f"Downloading {model_name} model (this may take a few minutes)...")
        try:
            # Show progress
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                if "pulling" in line.lower() or "%" in line:
                    print(f"  {line.strip()}")
            
            process.wait()
            if process.returncode == 0:
                self.model = model_name
                print(f"✓ Model '{model_name}' ready")
                return True
            else:
                print(f"✗ Failed to download model")
                return False
        except Exception as e:
            print(f"✗ Error downloading model: {e}")
            return False
    
    def load_spending_data(self, data_dir: str = "."):
        """Load spending data from CSV files"""
        try:
            # Load categories
            categories_file = os.path.join(data_dir, "categories.csv")
            if os.path.exists(categories_file):
                self.categories = pd.read_csv(categories_file)
            
            # Load rules
            rules_file = os.path.join(data_dir, "category_rules.csv")
            if os.path.exists(rules_file):
                self.rules = pd.read_csv(rules_file)
            
            print("✓ Spending data loaded")
            return True
        except Exception as e:
            print(f"✗ Error loading spending data: {e}")
            return False
    
    def log_transactions_to_archive(self, df: pd.DataFrame, 
                                   date_column: str = 'Date',
                                   vendor_column: str = 'Vendor',
                                   amount_column: str = 'Amount',
                                   category_column: str = 'Category') -> int:
        """
        Log transactions to monthly archive
        
        Args:
            df: DataFrame with transaction data
            date_column: Column name for date
            vendor_column: Column name for vendor
            amount_column: Column name for amount
            category_column: Column name for category
            
        Returns:
            Number of transactions logged
        """
        logged_count = self.transaction_logger.log_transactions_batch(
            df, 
            date_column=date_column,
            vendor_column=vendor_column,
            amount_column=amount_column,
            category_column=category_column
        )
        return logged_count
    
    def save_transaction_logs(self) -> Dict:
        """Save transaction logs to JSON files by month"""
        return self.transaction_logger.save_monthly_logs()
    
    def get_available_months(self) -> List[str]:
        """Get list of months with transaction data"""
        return self.transaction_logger.get_available_months()
    
    def compare_months_with_llm(self, month1: str = None, month2: str = None) -> str:
        """
        Compare spending between two months using LLM analysis
        
        Args:
            month1: First month (YYYY-MM), latest if None
            month2: Second month (YYYY-MM), previous if None
            
        Returns:
            LLM analysis of month-to-month comparison
        """
        if not self.is_ollama_running():
            return "❌ Ollama is not running. Start it with: ollama serve"
        
        # Build comparison context
        context = self.transaction_logger.build_comparison_context(month1, month2)
        
        if "No transaction data" in context or "Error" in context:
            return context
        
        # Log LLM query start
        metrics = get_metrics_logger()
        question = f"Compare spending for {month1 or 'latest'} vs {month2 or 'previous'} months"
        metrics.log_llm_query_start(question)
        
        # Create comparison analysis prompt
        prompt = f"""{context}

Based on this spending data comparison, please provide:
1. Overall spending trend (increased/decreased/stable)
2. Top 3 categories with biggest changes
3. Key insights and patterns
4. Specific recommendations based on the changes

Be concise and actionable with specific dollar amounts."""

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "No response generated")
                
                # Log LLM inference complete
                metrics.log_llm_inference_complete(
                    response_text, 
                    len(response_text.split())
                )
                
                return response_text
            else:
                error_msg = f"Error: {response.status_code}"
                metrics.log_potential_hallucination(question, error_msg, severity="ERROR")
                return error_msg
                
        except requests.exceptions.Timeout:
            timeout_msg = "⏱️  Request timed out. Try again."
            metrics.log_potential_hallucination(question, timeout_msg, severity="TIMEOUT")
            return timeout_msg
        except Exception as e:
            error_msg = f"❌ Error: {e}"
            metrics.log_potential_hallucination(question, error_msg, severity="EXCEPTION")
            return error_msg
    
    def query(self, question: str, context: str = None) -> str:
        """
        Ask natural language question about spending
        
        Args:
            question: Natural language query
            context: Optional pre-built context (if None, builds from data)
            
        Returns:
            LLM response
        """
        if not self.is_ollama_running():
            return "❌ Ollama is not running. Start it with: ollama serve"
        
        # Build context from spending data if not provided
        if context is None:
            context = self._build_context()
        
        # Create prompt
        prompt = f"""You are a helpful financial assistant analyzing spending data.

SPENDING DATA CONTEXT:
{context}

USER QUESTION:
{question}

Please provide a clear, concise answer based on the spending data provided. If asked about amounts, be specific with dollar signs and percentages."""
        
        # Log LLM query start
        metrics = get_metrics_logger()
        metrics.log_llm_query_start(question)
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "No response generated")
                
                # Log LLM inference complete
                metrics.log_llm_inference_complete(
                    response_text, 
                    len(response_text.split())
                )
                
                return response_text
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                metrics.log_potential_hallucination(
                    question, 
                    error_msg, 
                    severity="ERROR"
                )
                return error_msg
                
        except requests.exceptions.Timeout:
            timeout_msg = "⏱️  Request timed out. Try a simpler question."
            metrics.log_potential_hallucination(
                question, 
                timeout_msg, 
                severity="TIMEOUT"
            )
            return timeout_msg
        except Exception as e:
            error_msg = f"❌ Error querying LLM: {e}"
            metrics.log_potential_hallucination(
                question, 
                error_msg, 
                severity="EXCEPTION"
            )
            return error_msg
    
    def _build_context_with_transactions(self) -> str:
        """Build context including actual transaction data with vendors and amounts"""
        context = []
        
        # Add categories
        if self.categories is not None:
            context.append("AVAILABLE CATEGORIES:")
            for _, row in self.categories.iterrows():
                cat_name = row.get("CategoryName", "Unknown")
                context.append(f"  - {cat_name}")
            context.append("")
        
        # Add rules
        if self.rules is not None:
            context.append("CATEGORIZATION RULES:")
            top_rules = self.rules.head(10)
            for _, row in top_rules.iterrows():
                rule_id = row.get("RuleID", "?")
                category = row.get("Category", "?")
                pattern = row.get("VendorPattern", "?")
                context.append(f"  - {rule_id}: {category} (matches {pattern})")
            context.append("")
        
        # Load and add actual transaction data
        transaction_data = []
        try:
            import glob
            csv_files = glob.glob('*.csv')
            statement_files = [f for f in csv_files if 'statement' in f.lower() or 'transaction' in f.lower()]
            if not statement_files:
                statement_files = [f for f in csv_files if f.endswith('.csv') and f not in ['categories.csv', 'category_rules.csv', 'category_map.csv']]
            
            vendor_amounts = {}  # {vendor: {'amount': total, 'category': cat, 'count': count}}
            
            for stmt_file in statement_files[:5]:
                try:
                    df = pd.read_csv(stmt_file)
                    if len(df) > 0:
                        # Find vendor column
                        vendor_cols = [c for c in df.columns if any(x in c.lower() for x in ['vendor', 'description', 'merchant', 'name'])]
                        amount_cols = [c for c in df.columns if any(x in c.lower() for x in ['amount', 'debit', 'credit', 'transaction'])]
                        cat_cols = [c for c in df.columns if 'category' in c.lower()]
                        
                        vendor_col = vendor_cols[0] if vendor_cols else None
                        amount_col = amount_cols[0] if amount_cols else None
                        cat_col = cat_cols[0] if cat_cols else None
                        
                        if vendor_col and amount_col:
                            for _, row in df.iterrows():
                                vendor = str(row[vendor_col]).strip() if pd.notna(row[vendor_col]) else "Unknown"
                                try:
                                    amount = float(row[amount_col])
                                except:
                                    amount = 0
                                
                                category = str(row[cat_col]).strip() if cat_col and pd.notna(row[cat_col]) else "Uncategorized"
                                
                                if vendor not in vendor_amounts:
                                    vendor_amounts[vendor] = {'amount': 0, 'category': category, 'count': 0}
                                
                                vendor_amounts[vendor]['amount'] += abs(amount)
                                vendor_amounts[vendor]['count'] += 1
                                vendor_amounts[vendor]['category'] = category
                except:
                    pass
            
            if vendor_amounts:
                context.append("TRANSACTION DATA - TOP VENDORS BY SPENDING:")
                sorted_vendors = sorted(vendor_amounts.items(), key=lambda x: x[1]['amount'], reverse=True)[:30]
                for vendor, data in sorted_vendors:
                    context.append(f"  - {vendor}: ${data['amount']:.2f} ({data['count']} transactions, Category: {data['category']})")
                context.append("")
        except:
            pass
        
        context.append("INSTRUCTIONS:")
        context.append("- Reference specific vendors and amounts when answering questions")
        context.append("- Provide dollar amounts with the $ symbol")
        context.append("- Use actual transaction data to answer vendor-specific questions")
        context.append("- If asked about a specific vendor, look it up in the transaction data")
        
        return "\n".join(context)
    
    def analyze_spending_patterns(self) -> str:
        """Generate automatic spending analysis and insights"""
        if not self.is_ollama_running():
            return "❌ Ollama is not running. Start it with: ollama serve"
        
        context = self._build_context_with_transactions()
        
        # Log LLM query start
        metrics = get_metrics_logger()
        metrics.log_llm_query_start("analyze_spending_patterns")
        
        prompt = """Please analyze the spending data provided and give:
1. Key spending insights (2-3 bullet points)
2. Highest spending categories
3. Areas for potential savings
4. Overall financial observations

Be concise and actionable."""
        
        try:
            response = self.query(prompt, context=context)
            
            # Log LLM inference complete
            metrics.log_llm_inference_complete(
                response, 
                len(response.split())
            )
            
            return response
                
        except Exception as e:
            error_msg = f"Error generating analysis: {e}"
            metrics.log_potential_hallucination(
                "analyze_spending_patterns",
                error_msg,
                severity="EXCEPTION"
            )
            return error_msg
    
    def _build_context(self) -> str:
        """Build context string from available data"""
        context = []
        
        if self.categories is not None:
            context.append("AVAILABLE CATEGORIES:")
            for _, row in self.categories.iterrows():
                cat_name = row.get("CategoryName", "Unknown")
                context.append(f"  - {cat_name}")
            context.append("")
        
        if self.rules is not None:
            context.append("CATEGORIZATION RULES:")
            top_rules = self.rules.head(5)
            for _, row in top_rules.iterrows():
                rule_id = row.get("RuleID", "?")
                category = row.get("Category", "?")
                pattern = row.get("VendorPattern", "?")
                context.append(f"  - {rule_id}: {category} (matches {pattern})")
            context.append("")
        
        context.append("INSTRUCTIONS:")
        context.append("- Use categories and patterns when answering questions")
        context.append("- Provide specific amounts when possible")
        context.append("- Reference category names when discussing spending")
        
        return "\n".join(context)
    
    def query_logs(self, question: str = None) -> str:
        """Query application logs and metrics with natural language"""
        try:
            home = Path.home()
            logs_dir = home / '.config' / 'SpendingApp' / 'logs'
            
            if not logs_dir.exists():
                return "❌ No logs found yet. Run the application first."
            
            # Get metrics from memory (more current than JSON)
            metrics = get_metrics_logger()
            
            # Load latest application log (last 100 lines)
            log_files = sorted(logs_dir.glob('spending_app_*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
            log_content = ""
            if log_files:
                try:
                    with open(log_files[0], 'r') as f:
                        lines = f.readlines()
                        log_content = "".join(lines[-100:])  # Last 100 lines
                except:
                    pass
            
            # Load transaction data from CSV files for context
            transaction_summary = ""
            try:
                import glob
                csv_files = glob.glob('*.csv')
                # Look for common statement files
                statement_files = [f for f in csv_files if 'statement' in f.lower() or 'transaction' in f.lower()]
                if not statement_files:
                    statement_files = [f for f in csv_files if f.endswith('.csv') and f not in ['categories.csv', 'category_rules.csv', 'category_map.csv']]
                
                total_transactions = 0
                categories_found = {}
                vendors_found = {}
                
                for stmt_file in statement_files[:5]:  # Check first 5 CSV files
                    try:
                        df = pd.read_csv(stmt_file)
                        if len(df) > 0:
                            total_transactions += len(df)
                            
                            # Try to find category column
                            cat_cols = [c for c in df.columns if 'category' in c.lower()]
                            if cat_cols:
                                cat_col = cat_cols[0]
                                for cat in df[cat_col].dropna().unique():
                                    cat_count = len(df[df[cat_col] == cat])
                                    categories_found[cat] = categories_found.get(cat, 0) + cat_count
                            
                            # Try to find vendor/description column
                            vendor_cols = [c for c in df.columns if any(x in c.lower() for x in ['vendor', 'description', 'merchant', 'name'])]
                            if vendor_cols:
                                vendor_col = vendor_cols[0]
                                for vendor in df[vendor_col].dropna().unique()[:20]:  # Top 20 vendors
                                    vendors_found[str(vendor)[:40]] = vendors_found.get(str(vendor)[:40], 0) + 1
                    except:
                        pass
                
                if total_transactions > 0:
                    cat_summary = "\\n".join([f"  - {cat}: {count} transactions" for cat, count in sorted(categories_found.items(), key=lambda x: x[1], reverse=True)[:15]])
                    vendor_list = "\\n".join([f"  - {vendor}: {count}x" for vendor, count in sorted(vendors_found.items(), key=lambda x: x[1], reverse=True)[:10]])
                    transaction_summary = f"\\n\\nTRANSACTION DATA AVAILABLE:\\n- Total transactions in system: {total_transactions}\\n\\nTop spending categories:\\n{cat_summary}\\n\\nFrequent merchants/vendors:\\n{vendor_list}"
            except:
                pass
            
            # If no question provided, summarize logs
            if not question:
                question = "Summarize the performance metrics and recent activity"
            
            # Build context from metrics logger using in-memory data
            avg_latency = sum(c['total_time_seconds'] for c in metrics.categorization_times) / len(metrics.categorization_times) if metrics.categorization_times else 0
            avg_conflict = sum(c['conflict_rate_percent'] for c in metrics.categorization_times) / len(metrics.categorization_times) if metrics.categorization_times else 0
            total_tx = sum(c['transaction_count'] for c in metrics.categorization_times)
            
            context = f"""You are analyzing an expense tracking application. Here's the current system data:

PERFORMANCE METRICS (Current Session):
- Categorization Batches Processed: {len(metrics.categorization_times)}
- Total Transactions Categorized: {total_tx}
- Average Categorization Speed: {avg_latency:.3f}s
- Rule Conflict Rate: {avg_conflict:.1f}%
- Unique Vendors Tracked: {len(metrics.hash_values)}
- LLM Queries Made This Session: {len(metrics.llm_inferences)}
{transaction_summary}

RECENT ACTIVITY LOG (Last 100 lines):
{log_content}

User Question: {question}

Based on the application metrics and transaction data available, provide a helpful and concise answer to the user's question."""
            
            metrics.log_llm_query_start(question)
            
            response = self.query(question, context=context)
            
            metrics.log_llm_inference_complete(response)
            
            return response
            
        except Exception as e:
            return f"❌ Error querying logs: {e}"
    
    def interactive_session(self):
        """Start interactive Q&A session"""
        print("\n" + "="*70)
        print("SPENDING DATA NATURAL LANGUAGE QUERY")
        print("="*70)
        
        # Check Ollama
        if not self.is_ollama_running():
            print("\n⚠️  Ollama server is not running!")
            print("\nStart Ollama with:")
            print("  ollama serve")
            print("\nThen come back to this tool.")
            return
        
        # Ensure model is available
        available = self.list_available_models()
        if not available:
            print("\nNo models available. Downloading mistral...")
            if not self.pull_model("mistral"):
                print("Failed to download model. Please install manually:")
                print("  ollama pull mistral  (recommended, faster)")
                print("  ollama pull mistral")
                return
        
        if self.model not in available:
            print(f"\n✓ Using model: {self.model}")
        else:
            print(f"✓ Model loaded: {self.model}")
        
        print("\n" + "-"*70)
        print("Ask questions about your spending data (type 'quit' to exit):")
        print("Examples:")
        print("  - How much did I spend on education?")
        print("  - What's my highest spending category?")
        print("  - Show me all shopping purchases")
        print("  - Analyze my spending patterns")
        print("  - Compare groceries vs dining")
        print("-"*70 + "\n")
        
        # Build transaction context once for all queries
        transaction_context = self._build_context_with_transactions()
        
        while True:
            try:
                question = input("\n🤔 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                if not question:
                    continue
                
                print("\n🔍 Analyzing...\n")
                response = self.query(question, context=transaction_context)
                print(f"💡 Response:\n{response}")
                print("\n" + "-"*70)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Natural language queries for spending data using local LLM"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask (omit for interactive mode)"
    )
    parser.add_argument(
        "--model",
        default="mistral",
        help="LLM model to use (mistral, llama2, neural-chat, etc.)"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Generate automatic spending analysis"
    )
    parser.add_argument(
        "--data-dir",
        default=".",
        help="Directory with spending data"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download the specified model"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models"
    )
    
    args = parser.parse_args()
    
    # Initialize
    lm = SpendingLM(model=args.model)
    lm.load_spending_data(args.data_dir)
    
    # List models
    if args.list_models:
        print("Available models:")
        models = lm.list_available_models()
        if models:
            for m in models:
                print(f"  - {m}")
        else:
            print("  No models installed. Run with --download to get started.")
        return
    
    # Download model
    if args.download:
        lm.pull_model(args.model)
        return
    
    # Single query
    if args.query:
        if not lm.is_ollama_running():
            print("❌ Ollama is not running!")
            print("\nStart Ollama with:")
            print("  ollama serve")
            return
        
        print(f"\n🤔 Query: {args.query}\n")
        print("🔍 Analyzing...\n")
        
        if args.analyze:
            response = lm.analyze_spending_patterns()
        else:
            response = lm.query(args.query)
        
        print(f"💡 Response:\n{response}\n")
        return
    
    # Interactive mode
    lm.interactive_session()


if __name__ == "__main__":
    main()
