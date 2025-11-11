#!/usr/bin/env python3
"""
Repository Readiness Check
Verifies that all files are in place for GitHub repository creation
"""

import os
import sys
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_file(filepath, required=True):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"{GREEN}✓{RESET} {filepath}")
        return True
    else:
        status = f"{RED}✗{RESET}" if required else f"{YELLOW}⚠{RESET}"
        req_text = "(required)" if required else "(optional)"
        print(f"{status} {filepath} {req_text}")
        return not required

def check_directory(dirpath, required=True):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"{GREEN}✓{RESET} {dirpath}/")
        return True
    else:
        status = f"{RED}✗{RESET}" if required else f"{YELLOW}⚠{RESET}"
        req_text = "(required)" if required else "(optional)"
        print(f"{status} {dirpath}/ {req_text}")
        return not required

def main():
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}Repository Readiness Check{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    all_good = True
    
    # Documentation files
    print(f"\n{BOLD}📄 Documentation Files:{RESET}")
    all_good &= check_file("README.md")
    all_good &= check_file("TECHNICAL_REPORT.md")
    all_good &= check_file("LICENSE")
    all_good &= check_file("CONTRIBUTING.md")
    all_good &= check_file("CHANGELOG.md")
    all_good &= check_file("GITHUB_SETUP.md")
    all_good &= check_file("REPOSITORY_SUMMARY.md", required=False)
    
    # Configuration files
    print(f"\n{BOLD}⚙️  Configuration Files:{RESET}")
    all_good &= check_file("requirements.txt")
    all_good &= check_file("pyproject.toml")
    all_good &= check_file(".gitignore")
    
    # Source code files
    print(f"\n{BOLD}🔬 Source Code Files:{RESET}")
    all_good &= check_file("lab_qc_analysis.py")
    all_good &= check_file("lab_qc_demo.py")
    all_good &= check_file("realtime_qc_monitor.py")
    all_good &= check_file("realtime_qc_desktop.py")
    all_good &= check_file("advanced_fault_detection.py")
    all_good &= check_file("start_realtime_monitor.py", required=False)
    all_good &= check_file("quick_reference.py", required=False)
    all_good &= check_file("test_dual_monitor.py", required=False)
    all_good &= check_file("validate_fix.py", required=False)
    
    # Directories
    print(f"\n{BOLD}📁 Directories:{RESET}")
    check_directory("data", required=False)
    check_directory("results", required=False)
    check_directory("docs", required=False)
    
    # Check for sensitive information
    print(f"\n{BOLD}🔒 Security Checks:{RESET}")
    sensitive_patterns = ['.env', 'password', 'secret', 'api_key', '.pem', '.key']
    sensitive_found = []
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and cache directories
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git']]
        
        for file in files:
            file_lower = file.lower()
            if any(pattern in file_lower for pattern in sensitive_patterns):
                sensitive_found.append(os.path.join(root, file))
    
    if sensitive_found:
        print(f"{YELLOW}⚠{RESET} Potential sensitive files found:")
        for f in sensitive_found:
            print(f"  - {f}")
        print(f"{YELLOW}  Please review before committing to GitHub{RESET}")
    else:
        print(f"{GREEN}✓{RESET} No obvious sensitive files detected")
    
    # Check file sizes
    print(f"\n{BOLD}📊 Large Files Check:{RESET}")
    large_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git']]
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                if size > 10 * 1024 * 1024:  # 10 MB
                    large_files.append((filepath, size / (1024*1024)))
            except:
                pass
    
    if large_files:
        print(f"{YELLOW}⚠{RESET} Large files found (>10MB):")
        for f, size in large_files:
            print(f"  - {f} ({size:.1f} MB)")
        print(f"{YELLOW}  GitHub has a 100MB file size limit{RESET}")
    else:
        print(f"{GREEN}✓{RESET} No large files detected")
    
    # Git status
    print(f"\n{BOLD}🔧 Git Status:{RESET}")
    if os.path.exists('.git'):
        print(f"{GREEN}✓{RESET} Git repository initialized")
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--short'], 
                                  capture_output=True, text=True)
            if result.stdout:
                print(f"{YELLOW}  Uncommitted changes detected{RESET}")
            else:
                print(f"{GREEN}  Working directory clean{RESET}")
        except:
            print(f"{YELLOW}  Could not check git status{RESET}")
    else:
        print(f"{YELLOW}⚠{RESET} Git not yet initialized")
        print(f"  Run: git init")
    
    # Python dependencies check
    print(f"\n{BOLD}📦 Dependencies Check:{RESET}")
    required_packages = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy', 'plotly', 'dash']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"{GREEN}✓{RESET} {package}")
        except ImportError:
            print(f"{RED}✗{RESET} {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n{YELLOW}Install missing packages with:{RESET}")
        print(f"  pip install {' '.join(missing_packages)}")
    
    # Quick test
    print(f"\n{BOLD}🧪 Quick Code Test:{RESET}")
    try:
        from lab_qc_analysis import LabQCAnalysis
        qc = LabQCAnalysis(seed=42)
        data = qc.generate_qc_data('creatinine', n_days=1, measurements_per_day=3)
        if len(data) == 3:
            print(f"{GREEN}✓{RESET} Code imports and runs successfully")
        else:
            print(f"{YELLOW}⚠{RESET} Code runs but unexpected output")
    except Exception as e:
        print(f"{RED}✗{RESET} Code test failed: {str(e)}")
        all_good = False
    
    # README customization check
    print(f"\n{BOLD}✏️  Customization Needed:{RESET}")
    with open('README.md', 'r') as f:
        readme_content = f.read()
    
    if 'yourusername' in readme_content.lower():
        print(f"{YELLOW}⚠{RESET} Update 'yourusername' in README.md with your GitHub username")
    else:
        print(f"{GREEN}✓{RESET} README appears customized")
    
    # Summary
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    if all_good and not missing_packages:
        print(f"{BOLD}{GREEN}✅ Repository is ready for GitHub!{RESET}")
        print(f"\n{BOLD}Next steps:{RESET}")
        print(f"1. Review GITHUB_SETUP.md for detailed instructions")
        print(f"2. Create repository on GitHub.com")
        print(f"3. Push your code:")
        print(f"   {BLUE}git init{RESET}")
        print(f"   {BLUE}git add .{RESET}")
        print(f"   {BLUE}git commit -m 'Initial commit: v1.0.0'{RESET}")
        print(f"   {BLUE}git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git{RESET}")
        print(f"   {BLUE}git push -u origin main{RESET}")
    else:
        print(f"{BOLD}{YELLOW}⚠️  Please address the issues above before publishing{RESET}")
    
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

if __name__ == '__main__':
    main()
