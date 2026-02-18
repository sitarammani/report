import subprocess
import sys
import os

def install_ollama():
    if sys.platform == 'darwin':
        print('Checking for Ollama on macOS...')
        if subprocess.run(['which', 'ollama'], capture_output=True).returncode != 0:
            print('Installing Ollama via Homebrew...')
            subprocess.run(['brew', 'install', 'ollama'], check=True)
    elif sys.platform.startswith('win'):
        print('Checking for Ollama on Windows...')
        # Windows install instructions placeholder
        print('Please install Ollama manually from https://ollama.ai/download')
    else:
        print('Checking for Ollama on Linux...')
        if subprocess.run(['which', 'ollama'], capture_output=True).returncode != 0:
            print('Installing Ollama via script...')
            subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'], shell=True)

def pull_model(model='mistral'):
    print(f'Pulling LLM model: {model}...')
    subprocess.run(['ollama', 'pull', model], check=True)

def main():
    install_ollama()
    pull_model()
    print('Ollama and model setup complete.')

if __name__ == '__main__':
    main()
