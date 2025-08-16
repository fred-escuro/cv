#!/usr/bin/env python3
"""
Batch CV Processor Launcher

This script launches the batch processor from the backend directory.
It automatically navigates to the batch_process folder and runs the processor.
Supports .env configuration with command line overrides.
"""

import os
import sys
import subprocess
from pathlib import Path

def show_help():
    """Display comprehensive help information"""
    print("🚀 Batch CV Processor Launcher")
    print("=" * 50)
    print("This launcher provides easy access to the batch CV processor")
    print("with full .env configuration support and command line overrides.")
    print()
    
    print("📋 USAGE:")
    print("  python run_batch_processor.py [<folder_path>] [options]")
    print()
    
    print("🔧 CONFIGURATION OPTIONS:")
    print("  --show-config              # Display current .env configuration")
    print("  --create-env               # Create .env template file")
    print("  --help                     # Show this help message")
    print()
    
    print("📁 PROCESSING OPTIONS:")
    print("  <folder_path>              # Override CV folder from .env")
    print("  --limit <number>           # Maximum files to process")
    print("  --file-types <types>       # Comma-separated file extensions")
    print("  --log-file <name>          # Custom log file name")
    print("  --error-log-file <name>    # Custom error log file name")
    print()
    
    print("📊 EXAMPLES:")
    print("  # Use .env configuration")
    print("  python run_batch_processor.py")
    print()
    print("  # Override folder from .env")
    print("  python run_batch_processor.py \"C:/CVs\"")
    print()
    print("  # Override multiple settings")
    print("  python run_batch_processor.py \"C:/CVs\" --limit 50 --file-types \"pdf,docx\"")
    print()
    print("  # Configuration management")
    print("  python run_batch_processor.py --show-config")
    print("  python run_batch_processor.py --create-env")
    print()
    
    print("⚙️  CONFIGURATION FILES:")
    print("  .env                       # Main configuration (create from env_example.txt)")
    print("  env_example.txt            # Configuration template")
    print("  setup_config.py            # Interactive configuration setup")
    print("  config_manager.py          # Configuration management module")
    print()
    
    print("🛠️  ALTERNATIVE RUNNERS:")
    print("  # Windows Batch File (interactive)")
    print("  cd batch_process && run_batch_processor.bat")
    print()
    print("  # PowerShell Script (advanced)")
    print("  cd batch_process && .\\run_batch_processor.ps1")
    print()
    print("  # Quick Configuration")
    print("  cd batch_process && config.bat")
    print()
    
    print("📖 FOR MORE INFORMATION:")
    print("  cd batch_process && python batch_cv_processor.py --help")
    print("  cd batch_process && python setup_config.py")
    print()

def check_env_file(batch_process_dir):
    """Check if .env file exists and provide guidance"""
    env_file = batch_process_dir / ".env"
    env_example = batch_process_dir / "env_example.txt"
    
    if env_file.exists():
        print("✅ .env configuration file found")
        return True
    else:
        print("⚠️  No .env file found. Using default configuration.")
        print()
        if env_example.exists():
            print("📝 To create a .env file:")
            print("   1. Copy env_example.txt to .env")
            print("   2. Edit .env with your preferences")
            print("   3. Or run: python setup_config.py")
        else:
            print("📝 To create a .env file:")
            print("   1. Run: python setup_config.py")
            print("   2. Or create manually based on documentation")
        print()
        return False

def main():
    """Main launcher function"""
    
    # Get the backend directory
    backend_dir = Path(__file__).parent.absolute()
    batch_process_dir = backend_dir / "batch_process"
    
    # Check if batch_process directory exists
    if not batch_process_dir.exists():
        print("❌ Error: batch_process directory not found!")
        print(f"Expected location: {batch_process_dir}")
        return 1
    
    # Check if the main script exists
    main_script = batch_process_dir / "batch_cv_processor.py"
    if not main_script.exists():
        print("❌ Error: batch_cv_processor.py not found!")
        print(f"Expected location: {main_script}")
        return 1
    
    # Get command line arguments
    args = sys.argv[1:]
    
    # Handle help and configuration commands
    if "--help" in args or "-h" in args:
        show_help()
        return 0
    
    if not args:
        print("🚀 Batch CV Processor Launcher")
        print("=" * 50)
        print("Configuration: .env file in batch_process directory")
        print("Command line arguments override .env settings")
        print()
        
        # Check .env status
        check_env_file(batch_process_dir)
        
        print("📋 Quick Start:")
        print("  1. python run_batch_processor.py                    # Use .env settings")
        print("  2. python run_batch_processor.py \"C:/CVs\"         # Override folder")
        print("  3. python run_batch_processor.py --show-config     # Show configuration")
        print("  4. python run_batch_processor.py --create-env      # Create .env template")
        print()
        print("💡 For interactive setup: cd batch_process && python setup_config.py")
        print("💡 For full help: python run_batch_processor.py --help")
        print()
        
        # Ask user if they want to run the processor now
        try:
            user_input = input("🚀 Would you like to run the batch processor now? (y/n, default: y): ").strip().lower()
            if user_input in ['', 'y', 'yes']:
                print()
                print("🚀 Running batch processor with .env settings...")
                print("=" * 50)
                
                # Build the command to run with .env settings
                cmd = [sys.executable, str(main_script)]
                
                print(f"📁 Working directory: {batch_process_dir}")
                print(f"🔧 Command: {' '.join(cmd)}")
                print("=" * 50)
                
                try:
                    # Change to batch_process directory and run the processor
                    result = subprocess.run(cmd, cwd=batch_process_dir)
                    return result.returncode
                except KeyboardInterrupt:
                    print("\n⚠️ Processing interrupted by user")
                    return 1
                except Exception as e:
                    print(f"❌ Error launching batch processor: {e}")
                    return 1
            else:
                print("ℹ️  Batch processor not launched. Use one of the commands above when ready.")
                return 0
        except KeyboardInterrupt:
            print("\n⚠️ Operation cancelled by user")
            return 1
        
        return 0
    
    # Build the command
    cmd = [sys.executable, str(main_script)] + args
    
    print(f"🚀 Launching Batch CV Processor...")
    print(f"📁 Working directory: {batch_process_dir}")
    print(f"🔧 Command: {' '.join(cmd)}")
    print("=" * 50)
    
    # Show .env status before running
    check_env_file(batch_process_dir)
    
    try:
        # Change to batch_process directory and run the processor
        result = subprocess.run(cmd, cwd=batch_process_dir)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error launching batch processor: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
