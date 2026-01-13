#!/usr/bin/env python3
"""
Run React frontend for HH Resume Analyzer
"""

import sys
import os
import subprocess

def run_frontend():
    """Run the React frontend"""
    print("🎨 Starting React Frontend...")
    print("📍 Frontend will be available at: http://localhost:3000")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    # Change to frontend directory
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
    
    if not os.path.exists(frontend_path):
        print("❌ Frontend directory not found!")
        return 1
    
    os.chdir(frontend_path)
    
    # Check if node_modules exists
    if not os.path.exists('node_modules'):
        print("📦 Installing dependencies...")
        try:
            subprocess.run(['npm', 'install'], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return 1
    
    try:
        # Run the frontend
        subprocess.run(['npm', 'start'])
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped")
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js")
        return 1

def main():
    print("🎯 HH Resume Analyzer - Frontend")
    print("=" * 40)
    print("Starting React frontend with JSX components")
    print("Make sure backend is running on http://localhost:8000")
    print("=" * 40)
    print()
    
    return run_frontend()

if __name__ == "__main__":
    sys.exit(main())