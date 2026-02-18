#!/usr/bin/env python3
"""
Spending Report System - Quick Launcher
Simple entry point that checks requirements and launches the main app
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path

class ProgressBar:
    """Simple progress bar for startup sequence"""
    def __init__(self, total_steps=10):
        self.total_steps = total_steps
        self.current_step = 0
    
    def update(self, step_name=""):
        """Update progress bar"""
        self.current_step += 1
        percent = int((self.current_step / self.total_steps) * 100)
        filled = int(percent / 5)
        bar = "█" * filled + "░" * (20 - filled)
        
        if step_name:
            print(f"⏳ {bar} {percent:3d}% | {step_name}", flush=True)
        else:
            print(f"\r⏳ {bar} {percent:3d}%", end="", flush=True)
    
    def complete(self):
        """Show completion"""
        print(f"\r✅ {chr(9608)*20} 100% | All systems ready!", flush=True)
        print()

def check_python_version():
    """Check if Python version is 3.7+"""
    if sys.version_info < (3, 7):
        return False
    return True

def check_required_files():
    """Check if required files exist"""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(__file__)
    required_files = [
        "categories.csv",
        "category_rules.csv",
    ]
    
    # For frozen, the py files are bundled, so don't check
    if not getattr(sys, 'frozen', False):
        required_files.extend([
            "generate_reports_email.py",
            "natural_language_query.py",
            "manage_rules.py",
            "spending_lm.py",
        ])
    
    missing = []
    for f in required_files:
        filepath = os.path.join(base_dir, f)
        if not os.path.exists(filepath):
            missing.append(f)
    
    return len(missing) == 0

def check_dependencies():
    """Check if required Python packages are installed"""
    if getattr(sys, 'frozen', False):
        # In frozen app, assume packages are bundled
        return True
    
    required = ["pandas", "openpyxl", "xlsxwriter", "requests"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing, 
                         check=True, capture_output=True)
            return True
        except Exception:
            return False
    
    return True

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def is_ollama_running():
    """Check if Ollama server is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Start Ollama server in background"""
    try:
        if not check_ollama_installed():
            print("\n⚠️  Ollama is not installed")
            print("   Install from: https://ollama.ai")
            print("   Features requiring Ollama will be unavailable\n")
            return False
        
        print("🚀 Starting Ollama server...")
        # Start ollama serve in background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid if sys.platform != "win32" else None
        )
        
        # Wait for server to start
        max_retries = 10
        for i in range(max_retries):
            time.sleep(0.5)
            if is_ollama_running():
                print("✅ Ollama server started successfully")
                return True
        
        print("⚠️  Ollama server may be starting (taking longer than expected)")
        return True
    except Exception as e:
        print(f"⚠️  Could not start Ollama: {e}")
        return False

def check_first_time_install():
    """Check if this is first time install and ask for configuration"""
    config_dir = Path.home() / '.config' / 'SpendingApp'
    config_file = config_dir / 'config.json'
    
    if config_file.exists():
        return False  # Not first time
    
    # First time install
    print("\n" + "="*70)
    print("🎉 WELCOME TO SPENDING REPORT SYSTEM - FIRST TIME SETUP")
    print("="*70)
    
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Ask for log location
    print("\n📁 LOG FILE LOCATION")
    print("─"*70)
    print("\nWhere would you like to store application logs and transaction data?")
    print(f"\nDefault location: {config_dir}")
    
    try:
        response = input("\nUse default location? (y/n): ").strip().lower()
    except EOFError:
        response = 'y'
    
    if response == 'y' or response == '':
        log_location = str(config_dir)
    else:
        try:
            custom_path = input("Enter custom path: ").strip()
            if custom_path:
                log_location = custom_path
            else:
                log_location = str(config_dir)
        except EOFError:
            log_location = str(config_dir)
    
    # Create config file
    config = {
        'version': '1.0',
        'log_location': log_location,
        'created_at': str(Path(config_file).stat().st_mtime if config_file.exists() else time.time()),
        'first_time_setup_complete': True
    }
    
    try:
        # Create log directory
        Path(log_location).mkdir(parents=True, exist_ok=True)
        
        # Save config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration saved")
        print(f"   Logs location: {log_location}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ Error creating configuration: {e}")
        print(f"   Using default: {config_dir}\n")
        return True

def main():
    """Main launcher with progress bar"""
    
    # Check for first time install BEFORE progress bar (needs user interaction)
    config_dir = Path.home() / '.config' / 'SpendingApp'
    config_file = config_dir / 'config.json'
    is_first_time = not config_file.exists()
    
    if is_first_time:
        # Show first-time setup
        check_first_time_install()
    
    # Now show progress bar for background startup tasks
    sys.stdout.write("\n")
    sys.stdout.flush()
    print("╔" + "═"*68 + "╗", flush=True)
    print("║  🚀 SPENDING REPORT SYSTEM - INITIALIZING" + " "*24 + "║", flush=True)
    print("╚" + "═"*68 + "╝", flush=True)
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    # Initialize progress bar
    progress = ProgressBar(total_steps=10)
    
    try:
        # Step 1: Check Python version
        progress.update("Checking Python version...")
        time.sleep(0.1)
        if not check_python_version():
            print("❌ Python 3.7+ required", flush=True)
            sys.exit(1)
        
        # Step 2: Check required files
        progress.update("Verifying application files...")
        time.sleep(0.1)
        if not check_required_files():
            print("❌ Missing required files", flush=True)
            sys.exit(1)
        
        # Step 3: Check dependencies
        progress.update("Checking Python dependencies...")
        time.sleep(0.1)
        if not check_dependencies():
            print("⚠️  Some dependencies missing. Continuing...", flush=True)
        
        # Step 4: Load configuration
        progress.update("Loading configuration...")
        time.sleep(0.1)
        
        # Step 5: Check Ollama installation
        progress.update("Detecting Ollama installation...")
        time.sleep(0.1)
        ollama_installed = check_ollama_installed()
        
        # Step 6-7: Start Ollama if available
        if ollama_installed:
            progress.update("Starting Ollama AI server...")
            time.sleep(0.2)
            start_ollama()
        else:
            progress.update("Ollama not available (AI features disabled)...")
            time.sleep(0.1)
        
        # Step 8: Final preparations
        progress.update("Preparing application environment...")
        time.sleep(0.2)
        
        # Step 9: Loading resources
        progress.update("Loading application resources...")
        time.sleep(0.1)
        
        # Step 10: Complete
        progress.update("Finalizing startup sequence...")
        time.sleep(0.1)
        
        # Show completion
        progress.complete()
        
        # Show "Application started" only after all background work is done
        print("="*70, flush=True)
        print("✨ APPLICATION STARTED - ALL SYSTEMS READY", flush=True)
        print("="*70, flush=True)
        print()
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Run bootstrap script for Ollama/model install
        bootstrap_path = os.path.join(os.path.dirname(__file__), "bootstrap_ollama.py")
        if os.path.exists(bootstrap_path):
            progress.update("Setting up Ollama and LLM model...")
            try:
                if getattr(sys, 'frozen', False):
                    import bootstrap_ollama
                    bootstrap_ollama.main()
                else:
                    result_bootstrap = subprocess.run([sys.executable, bootstrap_path], check=True)
                print("✅ Ollama/model setup complete.")
            except Exception as e:
                print(f"⚠️  Ollama/model setup failed: {e}")
        else:
            print("⚠️  bootstrap_ollama.py not found, skipping Ollama/model setup.")

        # Launch main app
        if getattr(sys, 'frozen', False):
            # In frozen app, import and run app
            import app
            app.main()
        else:
            app_path = os.path.join(os.path.dirname(__file__), "app.py")
            result = subprocess.run([sys.executable, app_path])
            sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\n\n👋 Startup cancelled by user", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Startup error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
