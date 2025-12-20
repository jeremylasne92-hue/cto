#!/usr/bin/env python3
"""
Check if all system requirements are met for the Universal Content Ingestion Pipeline
"""

import sys
import subprocess
import shutil

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (required: 3.10+)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (required: 3.10+)")
        return False

def check_command(command, name, version_flag='--version'):
    """Check if a command is available"""
    if shutil.which(command):
        try:
            result = subprocess.run([command, version_flag], 
                                    capture_output=True, text=True, timeout=5)
            version = result.stdout.split('\n')[0] if result.stdout else result.stderr.split('\n')[0]
            print(f"✓ {name} is installed: {version.strip()}")
            return True
        except:
            print(f"✓ {name} is installed")
            return True
    else:
        print(f"✗ {name} is not installed")
        return False

def main():
    print("=" * 60)
    print("Universal Content Ingestion Pipeline - Requirements Check")
    print("=" * 60)
    print()
    
    checks = []
    
    # Python version
    checks.append(check_python_version())
    
    # Python tools
    checks.append(check_command('pip', 'pip'))
    
    # Node.js
    checks.append(check_command('node', 'Node.js'))
    checks.append(check_command('npm', 'npm'))
    
    # Optional but recommended
    print("\nOptional tools:")
    check_command('git', 'Git')
    check_command('docker', 'Docker')
    check_command('docker-compose', 'Docker Compose', '--version')
    
    print()
    print("=" * 60)
    
    if all(checks):
        print("✓ All required dependencies are installed!")
        print("You can proceed with the setup.")
        return 0
    else:
        print("✗ Some required dependencies are missing.")
        print("Please install the missing dependencies and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
