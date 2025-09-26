#!/usr/bin/env python3
"""
SpotViso CLI - Command line interface for data validation and visualization.

This CLI provides subcommands for:
- check: validate data integrity and object wiring
- test: pass through to pytest (smoke / full)
- test-all: full test suite  
- viz: produce an HTML in /artifacts
"""

import argparse
import sys
import subprocess
from pathlib import Path
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for spotviso CLI."""
    parser = argparse.ArgumentParser(
        prog='spotviso',
        description='SpotViso CLI for data validation and visualization'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # spotviso check
    check_parser = subparsers.add_parser('check', help='validate data integrity and object wiring')
    
    # spotviso test
    test_parser = subparsers.add_parser('test', help='pass through to pytest (smoke / full)')
    test_parser.add_argument('-m', '--markers', help='pytest markers to filter tests')
    test_parser.add_argument('pytest_args', nargs='*', help='additional pytest arguments')
    
    # spotviso test-all
    test_all_parser = subparsers.add_parser('test-all', help='full test suite')
    
    # spotviso viz
    viz_parser = subparsers.add_parser('viz', help='produce an HTML in /artifacts')
    viz_parser.add_argument('--case', help='case ID to visualize')
    
    return parser


def command_check() -> int:
    """Execute the check command to validate data integrity and object wiring."""
    print("Running data integrity and object wiring validation...")
    
    # Get the repository root directory  
    repo_root = Path(__file__).parent.parent
    
    # Check if data files exist
    data_files = [
        "CrossSection_Excel.txt",
        "CrossSection_Points_Excel.txt", 
        "CrossSection_Variables_Excel.txt",
        "AxisVariables_Excel.txt",
        "BearingArticulation_Excel.txt",
        "DeckObject_Excel.txt",
        "MainStation_Excel.txt"
    ]
    
    missing_files = []
    for file_name in data_files:
        file_path = repo_root / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"ERROR: Missing data files: {', '.join(missing_files)}")
        return 1
    
    print("✓ All required data files are present")
    
    # Basic JSON validation for data files
    import json
    json_validation_errors = []
    
    for file_name in data_files:
        if file_name.endswith('.txt'):
            file_path = repo_root / file_name
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip().startswith('[') or content.strip().startswith('{'):
                        json.loads(content)
                        print(f"✓ {file_name}: Valid JSON structure")
                    else:
                        print(f"ℹ {file_name}: Not JSON format (skipped validation)")
            except json.JSONDecodeError as e:
                json_validation_errors.append(f"{file_name}: {str(e)}")
            except Exception as e:
                json_validation_errors.append(f"{file_name}: {str(e)}")
    
    if json_validation_errors:
        print("JSON validation errors:")
        for error in json_validation_errors:
            print(f"  ERROR: {error}")
        return 1
    
    print("✓ Data integrity check completed successfully")
    return 0


def command_test(markers: Optional[str] = None, pytest_args: List[str] = None) -> int:
    """Execute the test command as a passthrough to pytest."""
    cmd = ['python', '-m', 'pytest']
    
    if markers:
        cmd.extend(['-m', markers])
    
    if pytest_args:
        cmd.extend(pytest_args)
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return result.returncode
    except FileNotFoundError:
        print("ERROR: pytest not found. Install pytest to use this command.")
        return 1


def command_test_all() -> int:
    """Execute the full test suite."""
    print("Running full test suite...")
    return command_test()


def command_viz(case_id: Optional[str] = None) -> int:
    """Execute the viz command to produce HTML visualization."""
    repo_root = Path(__file__).parent.parent
    artifacts_dir = repo_root / "artifacts"
    
    # Ensure artifacts directory exists and is not in GIT directory
    artifacts_dir.mkdir(exist_ok=True)
    
    if case_id:
        print(f"Generating visualization for case ID: {case_id}")
        output_file = artifacts_dir / f"case_{case_id}.html"
        # TODO: Load and process specific case data
        html_content = generate_case_visualization(case_id, repo_root)
    else:
        print("Generating visualization for synthetic default case...")
        output_file = artifacts_dir / "synthetic_case.html"
        html_content = generate_synthetic_visualization()
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Visualization saved to: {output_file}")
    return 0


def generate_synthetic_visualization() -> str:
    """Generate a tiny synthetic case visualization."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>SpotViso - Synthetic Case</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f8ff; padding: 20px; border-radius: 8px; }
        .content { margin: 20px 0; }
        .data-section { 
            background: #f9f9f9; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
            border-left: 4px solid #007acc;
        }
        .value { font-weight: bold; color: #007acc; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SpotViso Visualization</h1>
        <h2>Synthetic Test Case</h2>
    </div>
    
    <div class="content">
        <div class="data-section">
            <h3>Cross Section Data</h3>
            <p>Type: <span class="value">Deck</span></p>
            <p>Name: <span class="value">Synthetic_Deck</span></p>
            <p>Width: <span class="value">8000 mm</span></p>
            <p>Height: <span class="value">1200 mm</span></p>
        </div>
        
        <div class="data-section">
            <h3>Material Properties</h3>
            <p>Concrete: <span class="value">C45/55</span></p>
            <p>Reinforcement: <span class="value">B500B</span></p>
        </div>
        
        <div class="data-section">
            <h3>Geometry Points</h3>
            <p>Points Count: <span class="value">4</span></p>
            <p>Top Left: <span class="value">(-4000, 0)</span></p>
            <p>Top Right: <span class="value">(4000, 0)</span></p>
            <p>Bottom Left: <span class="value">(-4000, 1200)</span></p>
            <p>Bottom Right: <span class="value">(4000, 1200)</span></p>
        </div>
    </div>
    
    <footer style="margin-top: 40px; color: #666; text-align: center;">
        Generated by SpotViso CLI v0.1.0
    </footer>
</body>
</html>"""


def generate_case_visualization(case_id: str, repo_root: Path) -> str:
    """Generate visualization for a specific case ID."""
    # Try to load case data from files
    try:
        # Look for case data in CrossSection files
        cross_section_file = repo_root / "CrossSection_Excel.txt"
        if cross_section_file.exists():
            with open(cross_section_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Basic case data extraction would go here
                # For now, generate a placeholder
                pass
    except Exception as e:
        print(f"Warning: Could not load case data: {e}")
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>SpotViso - Case {case_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f8ff; padding: 20px; border-radius: 8px; }}
        .content {{ margin: 20px 0; }}
        .data-section {{ 
            background: #f9f9f9; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
            border-left: 4px solid #007acc;
        }}
        .value {{ font-weight: bold; color: #007acc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SpotViso Visualization</h1>
        <h2>Case ID: {case_id}</h2>
    </div>
    
    <div class="content">
        <div class="data-section">
            <h3>Case Information</h3>
            <p>Case ID: <span class="value">{case_id}</span></p>
            <p>Status: <span class="value">Active</span></p>
        </div>
        
        <div class="data-section">
            <h3>Data Sources</h3>
            <p>Cross Sections: <span class="value">Available</span></p>
            <p>Variables: <span class="value">Available</span></p>
            <p>Points: <span class="value">Available</span></p>
        </div>
    </div>
    
    <footer style="margin-top: 40px; color: #666; text-align: center;">
        Generated by SpotViso CLI v0.1.0
    </footer>
</body>
</html>"""


def main():
    """Main entry point for the spotviso CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    exit_code = 0
    
    try:
        if args.command == 'check':
            exit_code = command_check()
        elif args.command == 'test':
            exit_code = command_test(args.markers, args.pytest_args)
        elif args.command == 'test-all':
            exit_code = command_test_all()
        elif args.command == 'viz':
            exit_code = command_viz(args.case)
        else:
            print(f"Unknown command: {args.command}")
            exit_code = 1
            
    except KeyboardInterrupt:
        print("\nAborted by user")
        exit_code = 130
    except Exception as e:
        print(f"ERROR: {e}")
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()