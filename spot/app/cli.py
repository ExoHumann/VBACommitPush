#!/usr/bin/env python3
"""SpotViso CLI module."""

import sys


def main():
    """Main CLI entry point that prints help information."""
    help_text = """
SpotViso - A data visualization tool

Usage:
    spotviso [options]

Options:
    --help, -h    Show this help message and exit
    --version     Show version information

Description:
    SpotViso is a tool for visualizing and analyzing data.
    This is currently a stub implementation.
    """
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print(help_text.strip())
        return 0
    elif len(sys.argv) > 1 and sys.argv[1] == '--version':
        from spot import __version__
        print(f"SpotViso version {__version__}")
        return 0
    else:
        print(help_text.strip())
        return 0


if __name__ == "__main__":
    sys.exit(main())