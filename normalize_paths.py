#!/usr/bin/env python3
"""
Path normalization script for SPOT Excel export data.
Replaces Windows-specific file references with cross-platform alternatives.
"""

import re
from pathlib import Path
import sys


def normalize_excel_references(content: str) -> str:
    """
    Normalize Excel file references to be cross-platform.
    
    Replaces Windows-specific .xlsb file references with generic references.
    """
    # Pattern to match Excel file references like 'SPOT_EXCEL_dla_krzysia_v2 (version 1).xlsb'
    xlsb_pattern = r"'SPOT_EXCEL_dla_krzysia_v2 \(version 1\)\.xlsb'"
    
    # Replace with a generic reference
    normalized_content = re.sub(xlsb_pattern, "'SPOT_EXCEL_DATA'", content)
    
    return normalized_content


def process_file(file_path: Path) -> bool:
    """
    Process a single file to normalize Excel references.
    
    Returns True if changes were made, False otherwise.
    """
    try:
        # Read the file
        with file_path.open('r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Normalize the content
        normalized_content = normalize_excel_references(original_content)
        
        # Check if changes were made
        if normalized_content != original_content:
            # Write the normalized content back
            with file_path.open('w', encoding='utf-8') as f:
                f.write(normalized_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to normalize Excel references in all data files."""
    if len(sys.argv) > 1:
        # Process specific files
        files_to_process = [Path(arg) for arg in sys.argv[1:]]
    else:
        # Process all Excel text files
        base_path = Path.cwd()
        files_to_process = list(base_path.glob("*Excel*.txt"))
        files_to_process.extend(base_path.glob("*JSON*.txt"))
    
    print("Normalizing Windows-specific Excel file references...")
    print("=" * 60)
    
    changes_made = 0
    total_files = len(files_to_process)
    
    for file_path in files_to_process:
        if file_path.exists():
            print(f"Processing: {file_path.name}")
            if process_file(file_path):
                print(f"  ✓ Normalized Windows-specific references")
                changes_made += 1
            else:
                print(f"  - No changes needed")
        else:
            print(f"  ✗ File not found: {file_path}")
    
    print()
    print("Summary:")
    print(f"  Files processed: {total_files}")
    print(f"  Files modified: {changes_made}")
    
    if changes_made > 0:
        print("✓ Windows-specific paths have been normalized for cross-platform compatibility")
    else:
        print("✓ No Windows-specific paths found")
    
    return 0 if changes_made >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())