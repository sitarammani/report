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

class SpendingLM:
    """Local LLM interface for spending data analysis"""
    
    def __init__(self, model="llama2", ollama_host="http://localhost:11434"):
        """
        Initialize LLM interface
        
        Args:
            model: Model name (default: llama2, options: mistral, neural-chat, dolphin-mixtral)
            ollama_host: Ollama server URL
        """
        self.model = model
        self.ollama_host = ollama_host
        self.available_models = []
        self.spending_data = None
        self.categories = None
        self.rules = None
        
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
    
    def pull_model(self, model_name: str = "llama2") -> bool:
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
    
    def query(self, question: str) -> str:
        """
        Ask natural language question about spending
        
        Args:
            question: Natural language query
            
        Returns:
            LLM response
        """
        if not self.is_ollama_running():
            return "❌ Ollama is not running. Start it with: ollama serve"
        
        # Build context from spending data
        context = self._build_context()
        
        # Create prompt
        prompt = f"""You are a helpful financial assistant analyzing spending data.

SPENDING DATA CONTEXT:
{context}

USER QUESTION:
{question}

Please provide a clear, concise answer based on the spending data provided. If asked about amounts, be specific with dollar signs and percentages."""
        
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
                return result.get("response", "No response generated")
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "⏱️  Request timed out. Try a simpler question."
        except Exception as e:
            return f"❌ Error querying LLM: {e}"
    
    def analyze_spending_patterns(self) -> str:
        """Generate automatic spending analysis and insights"""
        if not self.is_ollama_running():
            return "❌ Ollama is not running. Start it with: ollama serve"
        
        context = self._build_context()
        prompt = f"""You are a financial advisor analyzing spending patterns.

SPENDING DATA:
{context}

Please provide:
1. Key spending insights (2-3 bullet points)
2. Highest spending categories
3. Areas for potential savings
4. Overall financial observations

Be concise and actionable."""
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,  # Lower for more focused analysis
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No analysis generated")
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error generating analysis: {e}"
    
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
            print("\nNo models available. Downloading llama2...")
            if not self.pull_model("llama2"):
                print("Failed to download model. Please install manually:")
                print("  ollama pull mistral  (recommended, faster)")
                print("  ollama pull llama2")
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
        
        while True:
            try:
                question = input("\n🤔 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                if not question:
                    continue
                
                print("\n🔍 Analyzing...\n")
                response = self.query(question)
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
        default="llama2",
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
