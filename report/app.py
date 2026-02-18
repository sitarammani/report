#!/usr/bin/env python3
"""
Main Application Menu
Central hub for all spending management features
"""

import sys
import os
import time
import json
from pathlib import Path
from metrics_logger import get_metrics_logger, init_metrics_logger

from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Determine base path for resources and support files.
# - When PyInstaller-bundled, use sys._MEIPASS
# - When packaged as a macOS .app bundle, place support files in Contents/Resources
# - Otherwise, use the script directory
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundled executable
    BASE_PATH = sys._MEIPASS
else:
    # If running from inside a .app bundle (Contents/MacOS), point to Resources
    exe_path = Path(sys.executable)
    if '.app/Contents/MacOS' in str(exe_path):
        BASE_PATH = str((exe_path.parent.parent / 'Resources').resolve())
    else:
        # Running as script
        BASE_PATH = os.path.dirname(__file__)

def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print("💰 SPENDING REPORT & ANALYSIS SYSTEM")
    print("="*70)
    print("Manage your finances with AI-powered insights\n")

def print_menu():
    """Print main menu options"""
    print("\n" + "─"*70)
    print("📋 MAIN MENU - SELECT AN OPTION")
    print("─"*70 + "\n")
    
    options = [
        ("1", "📊 Generate Spending Report", 
         "Create Excel report from bank statements"),
        ("2", "🤖 AI Assistant & Analysis",
         "Ask about spending, query logs, view history"),
        ("3", "⚙️  Manage Categories & Rules",
         "Customize categories and categorization rules"),
        ("4", "📈 View Category Hierarchy",
         "See parent-child category relationships"),
        ("5", "📤 Export Custom Rules",
         "Export your custom categories and rules"),
        ("6", "ℹ️  Help & Documentation", 
         "View help and feature guides"),
        ("7", "📈 Performance Summary",
         "View system performance metrics"),
        ("0", "❌ Exit",
         "Close the application"),
    ]
    
    for num, title, desc in options:
        print(f"  {num}  {title}")
        print(f"     {desc}\n")
    
    print("─"*70)

def menu_reports():
    """Generate spending reports"""
    print("\n" + "="*70)
    print("📊 SPENDING REPORT GENERATOR")
    print("="*70)
    print("\nStarting report generation...\n")
    
    try:
        import subprocess
        # Collect inputs here and pass as CLI args to avoid nested interactive prompts
        try:
            dir_path = input("\nEnter the directory path containing CSV/PDF statement files (press Enter for current dir):\n> ").strip()
        except EOFError:
            dir_path = ""

        if not dir_path:
            dir_path = os.getcwd()

        try:
            month_input = input("\nEnter the month for the report (MM/YYYY): ").strip()
        except EOFError:
            month_input = ""

        cli_args = [sys.executable, "generate_reports_email.py", "--dir", dir_path, "--files", "all"]
        if month_input:
            cli_args += ["--month", month_input]

        # Record timestamp to find child metrics file after subprocess completes
        start_ts = time.time()

        if getattr(sys, 'frozen', False):
            # For frozen app, set sys.argv and import the module
            original_argv = sys.argv
            sys.argv = cli_args
            try:
                import generate_reports_email
                result = 0  # Assume success
            except SystemExit as e:
                result = e.code
            except Exception as e:
                print(f"Error running report generator: {e}")
                result = 1
            finally:
                sys.argv = original_argv
        else:
            result = subprocess.run(
                cli_args,
                cwd=BASE_PATH,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
                bufsize=0
            ).returncode

        # After the generator subprocess finishes, attempt to locate its metrics JSON
        try:
            home = Path.home()
            metrics_dir = home / '.config' / 'SpendingApp' / 'logs'
            if metrics_dir.exists():
                # Find newest metrics file modified after we started the subprocess
                candidates = sorted(metrics_dir.glob('metrics_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
                child_metrics = None
                for p in candidates:
                    if p.stat().st_mtime >= start_ts - 1:
                        try:
                            with open(p, 'r') as f:
                                child_metrics = json.load(f)
                            # Merge child metrics into parent metrics logger
                            metrics = get_metrics_logger()
                            # Merge categorization details
                            for d in child_metrics.get('categorization_metrics', {}).get('details', []):
                                metrics.categorization_times.append(d)
                            # Merge hashes
                            hashes = child_metrics.get('hash_stability', {}).get('hashes', {})
                            metrics.hash_values.update(hashes)
                            # Merge llm inferences
                            for i in child_metrics.get('llm_metrics', {}).get('details', []):
                                metrics.llm_inferences.append(i)
                            # Merge conflicts
                            for c in child_metrics.get('conflicts', {}).get('details', []):
                                metrics.conflicts.append(c)

                            metrics.logger.debug(f"Merged metrics from subprocess: {p}")
                            break
                        except Exception:
                            continue
        except Exception:
            pass
        return result == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def menu_ai_assistant():
    """Unified AI Assistant submenu - combining NLQ, log queries, and history"""
    while True:
        print("\n" + "="*70)
        print("🤖 AI ASSISTANT & ANALYSIS HUB")
        print("="*70)
        print("\nWhat would you like to do?\n")
        
        ai_options = [
            ("1", "💬 Ask about your spending", "Natural language queries about transactions"),
            ("2", "📊 Query logs & performance", "Ask AI about application metrics and logs"),
            ("3", "� Compare monthly expenses", "Analyze spending trends between months"),
            ("4", "📜 View query history", "Browse past AI responses and queries"),
            ("0", "⬅️  Back to main menu", "Return to main menu"),
        ]
        
        for num, title, desc in ai_options:
            print(f"  {num}  {title}")
            print(f"     {desc}\n")
        
        try:
            choice = input("👉 Select option (0-4): ").strip()
        except EOFError:
            return False
        
        if choice == "1":
            menu_nlq()
        elif choice == "2":
            menu_query_logs()
        elif choice == "3":
            menu_compare_months()
        elif choice == "4":
            menu_query_history()
        elif choice == "0":
            return True
        else:
            print("\n❌ Invalid choice. Please select 0-4\n")

def menu_nlq():
    """Natural language queries"""
    print("\n" + "="*70)
    print("🤖 NATURAL LANGUAGE ANALYZER")
    print("="*70)
    print("\nStarting natural language query tool...\n")
    
    try:
        if getattr(sys, 'frozen', False):
            import natural_language_query
            try:
                natural_language_query.main()
                result = 0
            except SystemExit as e:
                result = e.code if e.code is not None else 0
            except Exception as e:
                print(f"Error running NLQ: {e}")
                result = 1
        else:
            result = subprocess.run(
                [sys.executable, "natural_language_query.py"],
                cwd=BASE_PATH
            ).returncode
        return result == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def menu_compare_months():
    """Compare monthly expenses with AI-powered analysis"""
    print("\n" + "="*70)
    print("📊 MONTHLY EXPENSE COMPARISON & ANALYSIS")
    print("="*70)
    print("\nAnalyzing spending trends across months...\n")
    
    try:
        from spending_lm import SpendingLM
        from transaction_logger import get_transaction_logger
        
        # Initialize LLM
        lm = SpendingLM()
        lm.load_spending_data(BASE_PATH)
        
        # Get transaction logger
        tx_logger = get_transaction_logger()
        tx_logger.load_monthly_logs()
        
        # Check if Ollama is running
        if not lm.is_ollama_running():
            print("❌ Ollama server is not running!")
            print("\nTo use this feature, start Ollama with:")
            print("  ollama serve")
            print("\nThen try again.")
            input("\n👉 Press Enter to continue...")
            return False
        
        # Get available months
        months = tx_logger.get_available_months()
        
        if len(months) < 2:
            print("⚠️  Not enough transaction data to compare.")
            print(f"   Available months: {months if months else 'None'}")
            print("\nYou need at least 2 months of data to compare expenses.")
            input("\n👉 Press Enter to continue...")
            return False
        
        # Display available months
        print(f"📅 Available months: {', '.join(months)}\n")
        
        # Default comparison (latest vs previous)
        month1 = months[-1]
        month2 = months[-2] if len(months) >= 2 else months[-1]
        
        print(f"📍 Comparing {month1} (latest) vs {month2} (previous)\n")
        print("🤖 Analyzing spending patterns with AI...\n")
        
        # Get AI analysis
        analysis = lm.compare_months_with_llm(month1, month2)
        
        print("─" * 70)
        print(f"\n💡 AI INSIGHTS:\n{analysis}\n")
        print("─" * 70)
        
        # Offer further comparison options
        while True:
            print("\n\nOptions:")
            print("  1. Compare different months")
            print("  2. Return to main menu")
            
            try:
                choice = input("\n👉 Select option (1-2): ").strip()
            except EOFError:
                return False
            
            if choice == "1":
                # Let user select months
                print("\nEnter month indices to compare (space-separated):")
                for i, m in enumerate(months):
                    print(f"  {i}: {m}")
                
                try:
                    indices_input = input("\n👉 Select two months (e.g., '0 1'): ").strip()
                    indices = [int(x) for x in indices_input.split()]
                    
                    if len(indices) == 2:
                        m1, m2 = months[indices[0]], months[indices[1]]
                        if m1 != m2:
                            print(f"\n🤖 Analyzing {m1} vs {m2}...\n")
                            analysis = lm.compare_months_with_llm(m1, m2)
                            print("─" * 70)
                            print(f"\n💡 AI INSIGHTS:\n{analysis}\n")
                            print("─" * 70)
                        else:
                            print("\n❌ Please select two different months\n")
                    else:
                        print("\n❌ Please enter exactly two month indices\n")
                except (ValueError, IndexError):
                    print("\n❌ Invalid input. Please try again.\n")
            elif choice == "2":
                return True
            else:
                print("\n❌ Invalid choice\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\n👉 Press Enter to continue...")
        return False

def menu_manage_rules():
    """Manage categories and rules"""
    print("\n" + "="*70)
    print("⚙️  CATEGORY & RULE MANAGER")
    print("="*70)
    print("\nStarting rule manager...\n")
    
    try:
        if getattr(sys, 'frozen', False):
            import manage_rules
            try:
                manage_rules.main()
                result = 0
            except SystemExit as e:
                result = e.code if e.code is not None else 0
            except Exception as e:
                print(f"Error running rule manager: {e}")
                result = 1
        else:
            result = subprocess.run(
                [sys.executable, "manage_rules.py"],
                cwd=BASE_PATH
            ).returncode
        return result == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def menu_hierarchy():
    """View category hierarchy"""
    print("\n" + "="*70)
    print("📈 CATEGORY HIERARCHY")
    print("="*70 + "\n")
    
    try:
        import pandas as pd
        
        categories_file = os.path.join(os.path.dirname(__file__), "categories.csv")
        if not os.path.exists(categories_file):
            print("❌ categories.csv not found")
            return False
        
        df = pd.read_csv(categories_file)
        
        # Print root categories (no parent)
        print("📂 ROOT CATEGORIES:")
        print("─"*70)
        root_cats = df[df['ParentCategory'].isna()]
        for _, row in root_cats.iterrows():
            print(f"  • {row['CategoryName']}")
            
            # Print sub-categories
            sub_cats = df[df['ParentCategory'] == row['CategoryName']]
            if not sub_cats.empty:
                for _, sub_row in sub_cats.iterrows():
                    marker = "✨" if sub_row.get('IsUserDefined') == 'Yes' else "  "
                    print(f"    {marker} ↳ {sub_row['CategoryName']}")
        
        print("\n✨ = Custom user-defined category")
        print("\nTotal categories: " + str(len(df)))
        print("User-defined: " + str(len(df[df.get('IsUserDefined') == 'Yes'])))
        
        return True
        
    except ImportError:
        print("❌ pandas not installed. Install with: pip3 install pandas")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def menu_export():
    """Export custom rules"""
    print("\n" + "="*70)
    print("📤 EXPORT CUSTOM RULES")
    print("="*70 + "\n")
    
    try:
        import pandas as pd
        
        rules_file = os.path.join(os.path.dirname(__file__), "category_rules.csv")
        if not os.path.exists(rules_file):
            print("❌ category_rules.csv not found")
            return False
        
        df = pd.read_csv(rules_file)
        custom_rules = df[df.get('IsCustom', 'No') == 'Yes']
        
        if custom_rules.empty:
            print("ℹ️  No custom rules found")
            return True
        
        print(f"📋 CUSTOM RULES ({len(custom_rules)} total)\n")
        print("─"*70)
        
        for _, row in custom_rules.iterrows():
            print(f"\nRule ID: {row['RuleID']}")
            print(f"  Category: {row['Category']}")
            print(f"  Pattern: {row['VendorPattern']}")
            print(f"  Priority: {row['Priority']}")
            print(f"  Created: {row.get('CreatedDate', 'Unknown')}")
            if pd.notna(row.get('Explanation')):
                print(f"  Note: {row['Explanation']}")
        
        # Ask to export
        print("\n" + "─"*70)
        export = input("\n📥 Export to CSV file? (y/n): ").strip().lower()
        
        if export == 'y':
            filename = input("Enter filename (default: custom_rules_export.csv): ").strip()
            if not filename:
                filename = "custom_rules_export.csv"
            
            filepath = os.path.join(os.path.dirname(__file__), filename)
            custom_rules.to_csv(filepath, index=False)
            print(f"✅ Exported to: {filename}")
            return True
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def menu_help():
    """Show help and documentation"""
    print("\n" + "="*70)
    print("ℹ️  HELP & DOCUMENTATION")
    print("="*70 + "\n")
    
    help_options = [
        ("1", "Quick Start Guide", "README.md"),
        ("2", "Spending Report Guide", "README.md"),
        ("3", "Natural Language Query Guide", "LLM_NATURAL_LANGUAGE_GUIDE.md"),
        ("4", "Custom Categories Guide", "ADVANCED_CUSTOMIZATION_GUIDE.md"),
        ("5", "LLM Setup & Troubleshooting", "LLM_README.md"),
        ("0", "Back to main menu", None),
    ]
    
    print("Available documentation:\n")
    for num, title, _ in help_options:
        print(f"  {num}  {title}")
    
    print("\n" + "─"*70)
    choice = input("Select option (0-5): ").strip()
    
    if choice == "0":
        return True
    
    doc_map = {
        "1": "README.md",
        "2": "README.md",
        "3": "LLM_NATURAL_LANGUAGE_GUIDE.md",
        "4": "ADVANCED_CUSTOMIZATION_GUIDE.md",
        "5": "LLM_README.md",
    }
    
    doc_file = doc_map.get(choice)
    if not doc_file:
        print("❌ Invalid option")
        return False
    
    filepath = os.path.join(os.path.dirname(__file__), doc_file)
    if not os.path.exists(filepath):
        print(f"❌ File not found: {doc_file}")
        return False
    
    try:
        import subprocess
        subprocess.run(["less", filepath])
    except:
        # Fallback to cat if less not available
        try:
            with open(filepath, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    return True

def menu_query_logs():
    """Query logs via LLM"""
    print("\n" + "="*70)
    print("📋 QUERY PERFORMANCE LOGS WITH AI")
    print("="*70)
    print("\nAsk questions about application logs and performance metrics")
    print("(powered by local LLM - no API keys needed)\n")
    
    try:
        from spending_lm import SpendingLM
        
        lm = SpendingLM()
        
        if not lm.is_ollama_running():
            print("❌ Ollama server is not running")
            print("\nStart Ollama with: ollama serve")
            return False
        
        print("📊 Example queries:")
        print("  • 'summarize performance'")
        print("  • 'were there any conflicts?'")
        print("  • 'how long did categorization take?'\n")
        
        question = input("🤔 Your question (or press Enter for summary): ").strip()
        
        if not question:
            question = None
        
        print("\n🔍 Analyzing logs...\n")
        response = lm.query_logs(question)
        
        print(f"💡 Response:\n{response}\n")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def menu_query_history():
    """View history of LLM queries and responses"""
    print("\n" + "="*70)
    print("📜 LLM QUERY HISTORY")
    print("="*70)
    
    from metrics_logger import get_metrics_logger
    
    metrics = get_metrics_logger()
    history = metrics.get_llm_query_history()
    
    if not history:
        print("\n❌ No LLM queries yet\n")
        try:
            input(" Press Enter to return to menu...")
        except EOFError:
            pass
        return False
    
    print(f"\n✅ Found {len(history)} queries:\n")
    
    for item in history:
        print(f"{item['index']}. [{item['timestamp']}]")
        print(f"   Q: {item['question']}")
        print(f"   A: {item['response_preview']}")
        print(f"   ⏱️  {item['inference_time']:.2f}s | 💾 {item['response_length']} chars")
        print()
    
    selection = input("View full response? (enter number or press Enter to skip): ").strip()
    if selection.isdigit():
        query_idx = int(selection) - 1
        full_query = metrics.get_llm_query_full(query_idx)
        if full_query:
            print(f"\n{'='*70}")
            print(f"FULL RESPONSE TO: {full_query['question']}")
            print(f"{'='*70}")
            print(full_query['response'])
            print(f"\n⏱️  Inference time: {full_query['inference_time_seconds']:.2f}s")
            print(f"💾 Response length: {full_query['response_length']} characters")
            print(f"🧠 Peak memory: {full_query['memory_peak_mb']:.1f} MB\n")
        else:
            print("❌ Invalid selection\n")
    
    try:
        input(" Press Enter to return to menu...")
    except EOFError:
        pass
    
    return True

def interactive_menu():
    """Main interactive menu loop"""
    # Initialize metrics logger
    init_metrics_logger()
    metrics = get_metrics_logger()
    metrics_logger_info = "ℹ️  Metrics logging enabled - tracking performance and usage patterns"
    print(f"\n{metrics_logger_info}")
    
    print_banner()
    
    menu_actions = {
        "1": ("Reports", menu_reports),
        "2": ("AI Assistant", menu_ai_assistant),
        "3": ("Manage Rules", menu_manage_rules),
        "4": ("View Hierarchy", menu_hierarchy),
        "5": ("Export Rules", menu_export),
        "6": ("Help", menu_help),
        "7": ("Performance Summary", lambda: (metrics.display_summary(), True)[1]),
        "0": ("Exit", None),
    }
    
    while True:
        print_menu()
        try:
            choice = input("👉 Enter your choice (0-7): ").strip()
        except EOFError:
            # If running interactively, re-display the menu; if stdin is not a TTY
            # (non-interactive run or piped input) then exit gracefully and save metrics.
            if sys.stdin.isatty():
                print("\n\nInput closed unexpectedly — re-displaying menu.")
                continue

            print("\n\n" + "="*70)
            print("👋 Thank you for using Spending Report System!")
            print("="*70 + "\n")

            # Save metrics summary on exit (silent)
            try:
                metrics.save_metrics_summary()
            except Exception as e:
                pass
            break
        
        if choice not in menu_actions:
            print("\n❌ Invalid choice. Please select 0-7")
            continue
        
        title, action = menu_actions[choice]
        
        # Log menu selection
        metrics.logger.info(f"User selected menu option: {choice} ({title})")
        
        if choice == "0":
            print("\n" + "="*70)
            print("👋 Thank you for using Spending Report System!")
            print("="*70 + "\n")
            
            # Save metrics summary on exit (silent)
            try:
                metrics.save_metrics_summary()
            except Exception as e:
                pass
            
            break
        
        if action:
            try:
                success = action()
                if success:
                    print("\n✅ Operation completed successfully")
                try:
                    input("\n Press Enter to return to menu...")
                except EOFError:
                    pass
            except KeyboardInterrupt:
                print("\n\n⏹️  Operation cancelled")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                try:
                    input("\n Press Enter to return to menu...")
                except EOFError:
                    pass

def main():
    """Main entry point"""
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
