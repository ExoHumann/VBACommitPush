"""Command line interface for spotviso."""

import argparse
import sys
from spot.logging import get_logger, configure_logging


"""Command line interface for spotviso."""

import argparse
import sys
import os
from spot.logging import get_logger, configure_logging
from spot.context import build_processing_context, validate_context
from spot.embedding import embed_data_structure, analyze_embedding_quality


def check_command(args):
    """Handle the check command."""
    logger = get_logger(__name__)
    
    logger.debug("Starting check command")
    logger.info("Running spotviso check")
    
    # Get VBA data files from current directory
    current_dir = os.getcwd()
    data_files = []
    
    logger.debug(f"Scanning directory: {current_dir}")
    
    for filename in os.listdir(current_dir):
        if filename.endswith('.txt') and 'Excel' in filename:
            data_files.append(filename)
    
    if not data_files:
        logger.warning("No VBA data files found in current directory")
        logger.info("Looking for files with pattern: *Excel.txt")
    else:
        logger.info(f"Found {len(data_files)} VBA data files")
        logger.debug(f"Files: {', '.join(data_files[:5])}{'...' if len(data_files) > 5 else ''}")
    
    # Build processing context
    logger.debug("Building processing context...")
    try:
        context = build_processing_context(data_files)
        
        # Validate context
        if not validate_context(context):
            logger.error("Context validation failed")
            return 1
        
        # Embed data structure
        logger.debug("Embedding data structure...")
        embedded_data = embed_data_structure(context)
        
        # Analyze embedding quality
        quality_metrics = analyze_embedding_quality(embedded_data)
        
        if quality_metrics['completeness'] >= 0.7:
            logger.info("Check command completed successfully")
            return 0
        else:
            logger.error("Check command completed with quality issues")
            return 1
            
    except Exception as e:
        logger.error(f"Check command failed: {e}")
        return 1


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='spotviso',
        description='VBA data processing tool with logging support'
    )
    
    # Global verbosity options
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose (DEBUG) logging'
    )
    verbosity_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Enable quiet (ERROR only) logging'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check and validate VBA data')
    check_parser.set_defaults(func=check_command)
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging based on verbosity flags
    configure_logging(verbose=args.verbose, quiet=args.quiet)
    
    # If no command specified, show help
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    # Execute the command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        logger = get_logger(__name__)
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())