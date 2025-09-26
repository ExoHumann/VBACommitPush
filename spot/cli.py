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
@click.option('--output', help='Output directory for saved plots')
@click.option('--save', is_flag=True, help='Save plots instead of displaying')
@click.pass_context
def viz(ctx, case, output, save):
    """Visualize bridge geometry for specified case."""
    logging.info(f"Visualizing case: {case}")
    click.echo(f"🎨 Visualizing case {case}...")
    
    try:
        from spot.data import DataLoader, GeometryProcessor
        from spot.vis import BridgePlotter
        from pathlib import Path
        
        # Initialize components
        data_loader = DataLoader()
        processor = GeometryProcessor(data_loader)
        plotter = BridgePlotter()
        
        # Set output directory
        output_dir = Path(output) if output else Path.cwd() / "plots"
        
        # Generate visualizations based on case type
        if case.lower() == 'axis':
            # Visualize axis frames
            axis_frames = processor.get_axis_frames()
            plotter.plot_axis_frames(axis_frames, f"Axis Frames - Case: {case}")
            
            if save:
                saved_path = plotter.save_plot(f"axis_frames_{case}", output_dir)
                click.echo(f"✅ Axis frames plot saved to: {saved_path}")
            else:
                plotter.show_plot()
                
        elif case.lower().startswith('section'):
            # Extract section name (e.g., 'section_Pyl_CSB' -> 'Pyl_CSB')
            section_name = case.split('_', 1)[1] if '_' in case else 'Pyl_CSB'
            
            # Visualize cross-section points
            local_data = processor.embed_section_points_basic(section_name)
            world_data = processor.embed_section_points_world_symmetric(section_name)
            
            # Plot comparison
            plotter.compare_coordinate_systems(
                local_data, world_data, 
                f"Section Points - Case: {case}"
            )
            
            if save:
                saved_path = plotter.save_plot(f"section_{section_name}_{case}", output_dir)
                click.echo(f"✅ Section plot saved to: {saved_path}")
            else:
                plotter.show_plot()
                
        else:
            # Default: try to use as section name
            local_data = processor.embed_section_points_basic(case)
            if local_data['points']:
                plotter.plot_cross_section_points(
                    local_data, f"Cross Section Points - Case: {case}"
                )
                
                if save:
                    saved_path = plotter.save_plot(f"cross_section_{case}", output_dir)
                    click.echo(f"✅ Cross section plot saved to: {saved_path}")
                else:
                    plotter.show_plot()
            else:
                click.echo(f"❌ No data found for case: {case}", err=True)
                click.echo("Available cases: 'axis', 'section_Pyl_CSB', 'Pyl_CSB'")
                
        plotter.close_plot()
        
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        click.echo("❌ Visualization dependencies not available", err=True)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Visualization error: {e}")
        click.echo(f"❌ Visualization failed: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()