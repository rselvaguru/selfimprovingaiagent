#!/usr/bin/env python3
"""
Setup and testing utility for Self-Improving AI Agent Framework

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    This script helps with:
    1. Verifying dependencies
    2. Testing Ollama connectivity
    3. Running basic validation tests
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    print("[*] Checking Python version...")
    
    if sys.version_info < (3, 8):
        print(f"  ✗ Python 3.8+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        return False
    
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor} OK")
    return True


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n[*] Checking Python dependencies...")
    
    required = [
        "requests",
        "pydantic",
    ]
    
    optional = [
        "chromadb",
        "fastapi",
        "uvicorn",
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing_required.append(package)
    
    for package in optional:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ⚠ {package} (optional)")
            missing_optional.append(package)
    
    if missing_required:
        print(f"\n  Missing required: {', '.join(missing_required)}")
        print("  Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_ollama():
    """Check if Ollama is running and accessible."""
    print("\n[*] Checking Ollama connectivity...")
    
    try:
        import requests
        
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            if models:
                print(f"  ✓ Ollama is running")
                print(f"  ✓ Available models: {len(models)}")
                for model in models[:3]:
                    print(f"    - {model.get('name', 'unknown')}")
                if len(models) > 3:
                    print(f"    ... and {len(models) - 3} more")
                return True
            else:
                print(f"  ⚠ Ollama is running but no models found")
                print(f"  Pull a model with: ollama pull llama2")
                return False
        else:
            print(f"  ✗ Ollama returned status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ✗ Cannot connect to Ollama at http://localhost:11434")
        print(f"  Error: {str(e)}")
        print(f"  Make sure Ollama is running: ollama serve")
        return False


def check_project_structure():
    """Check if project structure is correct."""
    print("\n[*] Checking project structure...")
    
    required_dirs = [
        "agents",
        "memory",
        "prompts",
        "api",
        "utils",
    ]
    
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "README.md",
    ]
    
    all_ok = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_ok = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} (missing)")
            all_ok = False
    
    return all_ok


def test_basic_import():
    """Test if main modules can be imported."""
    print("\n[*] Testing module imports...")
    
    try:
        from agents import ExecutorAgent, EvaluatorAgent, OptimizerAgent
        print(f"  ✓ Agents imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import agents: {str(e)}")
        return False
    
    try:
        from memory import MemoryManager
        print(f"  ✓ Memory manager imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import memory manager: {str(e)}")
        return False
    
    try:
        from main import SelfImprovingAIAgent
        print(f"  ✓ Self-improving agent imported successfully")
    except Exception as e:
        print(f"  ✗ Failed to import agent: {str(e)}")
        return False
    
    return True


def test_agent_initialization():
    """Test if agent can be initialized."""
    print("\n[*] Testing agent initialization...")
    
    try:
        from main import SelfImprovingAIAgent
        
        agent = SelfImprovingAIAgent()
        print(f"  ✓ Agent initialized successfully")
        
        stats = agent.get_statistics()
        print(f"  ✓ Statistics accessible")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed to initialize agent: {str(e)}")
        return False


def run_full_setup():
    """Run all setup checks."""
    print("\n" + "="*60)
    print("Self-Improving AI Agent - Setup Verification")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Module Imports", test_basic_import),
        ("Agent Initialization", test_agent_initialization),
        ("Ollama Service", check_ollama),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ✗ Error during {name}: {str(e)}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("Setup Verification Summary")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All checks passed! You're ready to use the framework.")
        print("\nQuick Start:")
        print("  1. Single task: python main.py \"Your task here\"")
        print("  2. Interactive:  python main.py --interactive")
        print("  3. API server:   python -m api.fastapi_server")
        print("  4. Examples:     python examples.py 1")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Start Ollama: ollama serve")
        print("  - Check Ollama models: ollama list")
    
    return all_passed


if __name__ == "__main__":
    success = run_full_setup()
    sys.exit(0 if success else 1)
