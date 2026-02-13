#!/usr/bin/env python3
"""
Setup script for Local LLM Natural Language Query System
Installs and configures Ollama + Mistral model
"""

import subprocess
import os
import sys
import time
from pathlib import Path

def run_command(cmd, description=""):
    """Run shell command and return result"""
    try:
        if description:
            print(f"\n{'='*70}")
            print(f"⏳ {description}")
            print('='*70)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_ollama():
    """Check if Ollama is installed"""
    success, stdout, _ = run_command("which ollama")
    return success

def check_ollama_server():
    """Check if Ollama server is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("\n" + "="*70)
    print("🤖 LOCAL LLM SETUP WIZARD")
    print("="*70)
    print("\nThis script will set up everything needed for natural language")
    print("queries on your spending data using a local LLM.\n")
    
    # Check Python version
    print("📋 Checking requirements...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]}")
    
    # Check Ollama
    if not check_ollama():
        print("\n❌ Ollama not found!")
        print("\nInstall Ollama:")
        print("  macOS: brew install ollama")
        print("  Linux: curl https://ollama.ai/install.sh | sh")
        print("  Windows: Download from https://ollama.ai")
        sys.exit(1)
    print("✓ Ollama installed")
    
    # Check Ollama server
    if not check_ollama_server():
        print("\n⚠️  Ollama server not running")
        print("\nStart Ollama in a new terminal:")
        print("  ollama serve")
        print("\nThen run this script again.")
        return
    print("✓ Ollama server running")
    
    # Check for requests library
    try:
        import requests
        print("✓ requests library installed")
    except ImportError:
        print("\n📦 Installing requests library...")
        success, _, _ = run_command("pip3 install requests", "Installing Python dependencies")
        if success:
            print("✓ requests library installed")
        else:
            print("❌ Failed to install requests")
            sys.exit(1)
    
    # List models
    print("\n📊 Checking available models...")
    success, stdout, _ = run_command("ollama list", "Listing models")
    
    models = []
    for line in stdout.split('\n'):
        if ':' in line and 'NAME' not in line:
            model = line.split()[0]
            if model:
                models.append(model)
    
    if models:
        print(f"✓ Models available: {', '.join(models)}")
    else:
        print("⚠️  No models installed yet")
    
    # Download Mistral if not present
    if 'mistral' not in models and 'mistral:latest' not in models:
        print("\n📥 Downloading Mistral model (this may take 5-10 minutes)...")
        print("   Size: 4GB | Speed: Fast | Quality: Excellent")
        
        # Download with progress
        process = subprocess.Popen(
            ["ollama", "pull", "mistral"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        for line in process.stdout:
            if "pulling" in line.lower():
                # Extract percentage if possible
                if "%" in line:
                    print(f"   {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print("✓ Mistral model ready!")
        else:
            print("❌ Failed to download Mistral")
            print("   Try manually: ollama pull mistral")
            sys.exit(1)
    else:
        print("✓ Mistral model already installed")
    
    # Test LLM connection
    print("\n🧪 Testing LLM connection...")
    from spending_lm import SpendingLM
    
    lm = SpendingLM(model="mistral")
    
    if lm.is_ollama_running():
        print("✓ LLM service connected")
        
        # Quick test query
        print("\n⚡ Running quick test query...")
        response = lm.query("What is the capital of France?")
        if response and "Ollama" not in response and "Error" not in response:
            print("✓ LLM working correctly")
            print(f"  Test response: {response[:100]}...")
        else:
            print("⚠️  LLM returned unexpected response")
    else:
        print("❌ Cannot connect to LLM service")
        print("   Make sure Ollama server is running: ollama serve")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE!")
    print("="*70)
    print("\n🚀 Ready to use! Start with:")
    print("\n  python3 natural_language_query.py")
    print("\nExample questions:")
    print('  • "How much did I spend on education?"')
    print('  • "What\'s my highest spending category?"')
    print('  • "Analyze my spending patterns"')
    print("\nFor more info, see: LLM_NATURAL_LANGUAGE_GUIDE.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
