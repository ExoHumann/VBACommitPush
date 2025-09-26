#!/usr/bin/env python3
"""
SPOTVISO - Cross-platform SPOT data visualization and checking tool.

This tool provides commands for checking data integrity and visualizing
structural engineering data with cross-platform path handling.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from SPOT_Filters import SPOTFilters


class SpotViso:
    """Main SPOTVISO application class."""
    
    def __init__(self):
        """Initialize SPOTVISO with cross-platform path support."""
        self.filters = SPOTFilters()
        self.demo_data = self._create_demo_data()
    
    def _create_demo_data(self) -> Dict:
        """Create synthetic demo data for testing."""
        return {
            "case_name": "demo",
            "cross_sections": [
                {
                    "name": "Deck_Demo",
                    "type": "Deck",
                    "material": {"concrete": 100, "reinforcement": 200},
                    "geometry": {
                        "width": 3000,
                        "height": 250,
                        "thickness_top": 40,
                        "thickness_bottom": 60
                    }
                },
                {
                    "name": "Pylon_Demo", 
                    "type": "Pylon",
                    "material": {"concrete": 100, "reinforcement": 200},
                    "geometry": {
                        "height": 4000,
                        "width_top": 3000,
                        "width_bottom": 6000,
                        "cantilever_length": 2000
                    }
                }
            ],
            "stations": [
                {"id": "ST_001", "position": 0.0, "section": "Deck_Demo"},
                {"id": "ST_002", "position": 50.0, "section": "Deck_Demo"},
                {"id": "ST_003", "position": 100.0, "section": "Pylon_Demo"}
            ],
            "bearings": [
                {
                    "name": "Bearing_01",
                    "type": "Fixed",
                    "station": "ST_003",
                    "coordinates": {"y": 0, "z": 4000}
                }
            ]
        }
    
    def check(self) -> int:
        """
        Perform comprehensive data integrity check.
        
        Returns:
            0 for success, 1 for errors
        """
        print("SPOTVISO Check - Cross-platform data integrity verification")
        print("=" * 60)
        
        try:
            # Check environment compatibility
            env_status = self.filters.check_environment_compatibility()
            print(f"Platform: {env_status['platform']}")
            print(f"Pathlib support: {'✓' if env_status['pathlib_support'] else '✗'}")
            print(f"File system access: {'✓' if env_status['file_system_access'] else '✗'}")
            print(f"Unicode support: {'✓' if env_status['unicode_support'] else '✗'}")
            print()
            
            # Check for data files
            excel_files = self.filters.find_excel_files("*Excel.txt")
            print(f"Found {len(excel_files)} Excel export files:")
            
            errors = 0
            warnings = 0
            
            for file_path in excel_files:
                print(f"  Checking: {file_path.name}")
                
                try:
                    data = self.filters.process_cross_section_data(file_path)
                    
                    if "error" in data:
                        print(f"    ✗ Error: {data['error']}")
                        errors += 1
                    else:
                        # Check for Windows-specific paths
                        has_windows_paths = self._check_windows_paths(data)
                        if has_windows_paths:
                            print(f"    ⚠ Warning: Contains Windows-specific paths")
                            warnings += 1
                        else:
                            print(f"    ✓ Cross-platform compatible")
                            
                except Exception as e:
                    print(f"    ✗ Processing error: {e}")
                    errors += 1
            
            print()
            print("Summary:")
            print(f"  Files processed: {len(excel_files)}")
            print(f"  Errors: {errors}")
            print(f"  Warnings: {warnings}")
            
            if errors == 0:
                print("✓ All checks passed - system is cross-platform compatible")
                return 0
            else:
                print("✗ Errors found - cross-platform compatibility issues detected")
                return 1
                
        except Exception as e:
            print(f"Check failed with error: {e}")
            return 1
    
    def _check_windows_paths(self, data) -> bool:
        """Check data for Windows-specific path patterns."""
        data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        
        # Look for Windows-specific patterns
        windows_patterns = [
            "C:\\",
            ".xlsb",
            "\\\\",  # UNC paths
            "SPOT_EXCEL_dla_krzysia_v2 (version 1).xlsb"
        ]
        
        for pattern in windows_patterns:
            if pattern in data_str:
                return True
        return False
    
    def viz(self, case: str = "demo") -> int:
        """
        Generate visualization for the specified case.
        
        Args:
            case: Case name to visualize (default: demo)
            
        Returns:
            0 for success, 1 for errors
        """
        print(f"SPOTVISO Visualization - Case: {case}")
        print("=" * 60)
        
        try:
            if case == "demo":
                # Use synthetic demo data
                data = self.demo_data
                print("Using synthetic demo data for visualization")
            else:
                # Try to load case from files
                case_files = self.filters.find_excel_files(f"*{case}*.txt")
                if not case_files:
                    print(f"No files found for case: {case}")
                    print("Available files:")
                    all_files = self.filters.find_excel_files()
                    for f in all_files:
                        print(f"  {f.name}")
                    return 1
                
                # Load first matching file
                data = self.filters.process_cross_section_data(case_files[0])
                if "error" in data:
                    print(f"Error loading case data: {data['error']}")
                    return 1
            
            # Generate visualization output
            self._generate_visualization_report(data, case)
            
            # Save visualization data using cross-platform paths
            output_path = self.filters.get_output_path(f"viz_{case}.json")
            
            try:
                with output_path.open('w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Visualization data saved to: {output_path}")
                
                # Create a simple text report
                report_path = self.filters.get_output_path(f"report_{case}.txt")
                with report_path.open('w', encoding='utf-8') as f:
                    f.write(f"SPOTVISO Visualization Report - Case: {case}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Generated on platform: {sys.platform}\n")
                    f.write(f"Data file: {output_path}\n")
                    f.write(f"Total data keys: {len(data) if isinstance(data, dict) else 'N/A'}\n")
                
                print(f"✓ Report saved to: {report_path}")
                
            except (OSError, PermissionError) as e:
                print(f"⚠ Warning: Could not save output files: {e}")
                # Continue without saving
            
            print("✓ Visualization completed successfully")
            return 0
            
        except Exception as e:
            print(f"Visualization failed: {e}")
            return 1
    
    def _generate_visualization_report(self, data: Dict, case: str):
        """Generate a simple text-based visualization report."""
        print("\nVisualization Report:")
        print("-" * 30)
        
        if isinstance(data, dict):
            if "cross_sections" in data:
                sections = data["cross_sections"]
                print(f"Cross Sections: {len(sections)}")
                for i, section in enumerate(sections[:3]):  # Show first 3
                    name = section.get("name", f"Section_{i+1}")
                    section_type = section.get("type", "Unknown")
                    print(f"  {name} ({section_type})")
            
            if "stations" in data:
                stations = data["stations"]
                print(f"Stations: {len(stations)}")
            
            if "bearings" in data:
                bearings = data["bearings"]
                print(f"Bearings: {len(bearings)}")
            
            # Show general data structure
            print(f"Data structure keys: {list(data.keys())[:5]}")  # First 5 keys
            
        else:
            print(f"Data type: {type(data)}")
            print("Raw data visualization not available")
        
        print(f"\n✓ Case '{case}' processed with cross-platform compatibility")


def main():
    """Main entry point for spotviso command."""
    parser = argparse.ArgumentParser(
        description="SPOTVISO - Cross-platform SPOT data visualization tool",
        epilog="Examples:\n  spotviso check\n  spotviso viz --case demo",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check data integrity and compatibility")
    
    # Visualization command
    viz_parser = subparsers.add_parser("viz", help="Generate visualization")
    viz_parser.add_argument("--case", default="demo", help="Case name to visualize (default: demo)")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    try:
        spotviso = SpotViso()
        
        if args.command == "check":
            exit_code = spotviso.check()
        elif args.command == "viz":
            exit_code = spotviso.viz(args.case)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            exit_code = 1
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()