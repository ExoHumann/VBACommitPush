#!/usr/bin/env python3
"""Spotviso test runner command."""
import sys
import subprocess
import argparse


def main():
    """Main entry point for spotviso command."""
    parser = argparse.ArgumentParser(description="Spotviso test runner")
    parser.add_argument("command", nargs="?", default="help", 
                       help="Command to run (test, help)")
    parser.add_argument("-m", "--marker", help="Run tests with specific marker")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.command == "help" or args.command is None:
        print("Spotviso test runner")
        print("Usage: spotviso test [-m marker] [--verbose]")
        print("Example: spotviso test -m smoke")
        return 0
    
    elif args.command == "test":
        # Build pytest command
        pytest_cmd = ["python", "-m", "pytest"]
        
        if args.verbose:
            pytest_cmd.append("-v")
        else:
            pytest_cmd.append("-q")
            
        if args.marker:
            pytest_cmd.extend(["-m", args.marker])
            
        # Add test path
        pytest_cmd.append("tests")
        
        print(f"Running: {' '.join(pytest_cmd)}")
        
        # Execute pytest
        try:
            result = subprocess.run(pytest_cmd, check=False)
            return result.returncode
        except FileNotFoundError:
            print("Error: pytest not found. Please install pytest.")
            return 1
            
    else:
        print(f"Unknown command: {args.command}")
        print("Use 'spotviso help' for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())