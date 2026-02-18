#!/usr/bin/env python3
"""
Natural Language Query Tool for Spending Data
Uses local LLM (Ollama) - no API required
"""

from spending_lm import SpendingLM
import sys
import os

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("💰 NATURAL LANGUAGE SPENDING ANALYZER")
    print("="*70)
    print("Query your spending data using plain English!")
    print("Running completely locally - no external APIs needed")
    print("="*70 + "\n")

def quick_start():
    """Print quick start instructions"""
    print("""
QUICK START:
───────────────────────────────────────────────────────────────────────

1. FIRST TIME SETUP:
   
   # Download a model (one-time, takes 5-10 minutes)
   python3 natural_language_query.py --download

2. START OLLAMA SERVER:
   
   # In a new terminal:
   ollama serve

3. INTERACTIVE QUERIES:
   
   # Ask questions about your spending
   python3 natural_language_query.py

EXAMPLES OF QUESTIONS YOU CAN ASK:
───────────────────────────────────────────────────────────────────────
  ✓ "How much did I spend on education?"
  ✓ "What was my highest spending category last month?"
  ✓ "How many transactions were over $200?"
  ✓ "Compare my shopping vs restaurant spending"
  ✓ "What percentage of my budget went to utilities?"
  ✓ "Show me all transactions categorized as entertainment"
  ✓ "Analyze my spending patterns and suggest areas to save"

COMMAND LINE OPTIONS:
───────────────────────────────────────────────────────────────────────
  python3 natural_language_query.py
    └─ Interactive mode (ask multiple questions)
  
  python3 natural_language_query.py "How much on groceries?"
    └─ Single query mode
  
  python3 natural_language_query.py --analyze
    └─ Generate automatic spending analysis
  
  python3 natural_language_query.py --download
    └─ Download the Mistral model
  
  python3 natural_language_query.py --list-models
    └─ Show installed models
  
  python3 natural_language_query.py --model llama2 "question"
    └─ Use a different model

MODELS AVAILABLE:
───────────────────────────────────────────────────────────────────────
  • mistral (4GB, fast, recommended) ⭐
  • llama2 (7GB, slower, more powerful)
  • neural-chat (4GB, optimized for chat)
  • dolphin-mixtral (26GB, very powerful)

REQUIREMENTS:
───────────────────────────────────────────────────────────────────────
  ✓ Ollama installed (via: brew install ollama)
  ✓ Python 3.7+
  ✓ requests library (auto-installed)
  ✓ spending data files in current directory

GETTING HELP:
───────────────────────────────────────────────────────────────────────
  python3 natural_language_query.py --help
    └─ Show all options

""")

def main():
    print_banner()
    
    # Check if this is first time
    if len(sys.argv) == 1:
        print("ℹ️  Starting in interactive mode...")
        print("(For help, run: python3 natural_language_query.py --help)\n")
        
        lm = SpendingLM()
        lm.load_spending_data()
        lm.interactive_session()
    else:
        # Pass through to spending_lm
        from spending_lm import main
        main()

if __name__ == "__main__":
    main()
