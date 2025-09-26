"""CLI interface for SPOT_VISO."""
import click
import logging
from pathlib import Path
import sys


def setup_logging(verbose: int = 0) -> None:
    """Setup logging with appropriate verbosity."""
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(verbose, len(levels) - 1)]
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.group()
@click.option('-v', '--verbose', count=True, help='Increase verbosity')
@click.pass_context
def cli(ctx, verbose):
    """SPOT_VISO bridge geometry and visualization system."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.pass_context
def check(ctx):
    """Check system integrity and data validation."""
    logging.info("Running system checks...")
    
    # Check for data files
    data_files = [
        "CrossSection_Points_Excel.txt",
        "CrossSection_Variables_Excel.txt", 
        "CrossSection_Excel.txt",
        "MainStation_Excel.txt",
        "DeckObject_Excel.txt"
    ]
    
    missing_files = []
    for file in data_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logging.error(f"Missing data files: {missing_files}")
        click.echo("❌ Check failed - missing data files", err=True)
        sys.exit(1)
    else:
        logging.info("All required data files found")
        click.echo("✅ System check passed")


@cli.command()
@click.option('-m', '--mode', default='all', 
              type=click.Choice(['smoke', 'all']), 
              help='Test mode to run')
@click.pass_context
def test(ctx, mode):
    """Run tests with specified mode."""
    logging.info(f"Running tests in {mode} mode...")
    
    if mode == 'smoke':
        click.echo("🧪 Running smoke tests...")
        # Import here to avoid circular imports and dependencies
        try:
            import pytest
            result = pytest.main(['-v', 'tests/', '-k', 'smoke'])
            sys.exit(result)
        except ImportError:
            logging.error("pytest not installed. Run: pip install pytest")
            click.echo("❌ pytest not available", err=True)
            sys.exit(1)
    else:
        click.echo("🧪 Running all tests...")
        try:
            import pytest
            result = pytest.main(['-v', 'tests/'])
            sys.exit(result)
        except ImportError:
            logging.error("pytest not installed. Run: pip install pytest")
            click.echo("❌ pytest not available", err=True)
            sys.exit(1)


@cli.command()
@click.option('--case', required=True, help='Case ID to visualize')
@click.pass_context
def viz(ctx, case):
    """Visualize bridge geometry for specified case."""
    logging.info(f"Visualizing case: {case}")
    click.echo(f"🎨 Visualizing case {case}...")
    
    # Placeholder for visualization logic
    click.echo(f"Visualization for case '{case}' would be displayed here.")
    click.echo("(Visualization system not yet implemented)")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()