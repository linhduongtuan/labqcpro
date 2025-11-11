#!/usr/bin/env python3
"""
Quick Start - Real-Time QC Monitoring
Automatically detects and runs the best monitoring option
"""

import sys
import subprocess

def check_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("\n" + "="*80)
    print("🔬 REAL-TIME QC MONITORING - QUICK START")
    print("="*80)
    
    # Check what's available
    has_dash = check_package('dash')
    has_matplotlib = check_package('matplotlib')
    
    print("\n📦 Checking dependencies...")
    print(f"   Dash (Web Dashboard): {'✅ Installed' if has_dash else '❌ Not installed'}")
    print(f"   Matplotlib (Desktop):  {'✅ Installed' if has_matplotlib else '❌ Not installed'}")
    
    if not has_dash and not has_matplotlib:
        print("\n⚠️  No visualization packages found!")
        print("\nInstall options:")
        print("   1. Web Dashboard:  uv add dash plotly")
        print("   2. Desktop App:    uv add matplotlib")
        print("\nRun this script again after installation.")
        sys.exit(1)
    
    # Decide what to offer
    options = []
    if has_dash:
        options.append(('web', 'Web Dashboard (Recommended)', 'realtime_qc_monitor.py'))
    if has_matplotlib:
        options.append(('desktop', 'Desktop Application', 'realtime_qc_desktop.py'))
    
    if len(options) == 1:
        # Only one option available, use it
        opt_type, opt_name, opt_file = options[0]
        print(f"\n🚀 Starting {opt_name}...")
        
        if opt_type == 'web':
            print("\n" + "="*80)
            print("📊 WEB DASHBOARD STARTING")
            print("="*80)
            print("\n⏳ Please wait while the server starts...")
            print("🌐 Your browser will show: http://127.0.0.1:8050")
            print("⚠️  Press Ctrl+C to stop the server\n")
            subprocess.run([sys.executable, opt_file])
        else:
            print("\n" + "="*80)
            print("🖥️  DESKTOP APPLICATION STARTING")
            print("="*80)
            print("\n⚠️  Close the window to stop monitoring\n")
            subprocess.run([sys.executable, opt_file])
    
    else:
        # Multiple options, let user choose
        print("\n📋 Select monitoring method:")
        for i, (opt_type, opt_name, opt_file) in enumerate(options, 1):
            print(f"   {i}. {opt_name}")
        
        while True:
            try:
                choice = input(f"\nEnter choice (1-{len(options)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    break
                print("❌ Invalid choice. Try again.")
            except (ValueError, KeyboardInterrupt):
                print("\n\nExiting.")
                sys.exit(0)
        
        opt_type, opt_name, opt_file = options[idx]
        print(f"\n🚀 Starting {opt_name}...")
        
        if opt_type == 'web':
            print("\n" + "="*80)
            print("📊 WEB DASHBOARD STARTING")
            print("="*80)
            print("\n⏳ Please wait while the server starts...")
            print("🌐 Open your browser to: http://127.0.0.1:8050")
            print("\n✨ Features:")
            print("   • Live Levey-Jennings charts")
            print("   • Automatic Westgard rule checking")
            print("   • Real-time statistics (Mean, SD, CV, Bias, Sigma)")
            print("   • Alert notifications")
            print("   • Data export to CSV")
            print("\n⚠️  Press Ctrl+C to stop the server\n")
            print("="*80 + "\n")
            subprocess.run([sys.executable, opt_file])
        else:
            print("\n" + "="*80)
            print("🖥️  DESKTOP APPLICATION STARTING")
            print("="*80)
            print("\n⚠️  Close the window to stop monitoring\n")
            subprocess.run([sys.executable, opt_file])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped. Goodbye!")
        sys.exit(0)
