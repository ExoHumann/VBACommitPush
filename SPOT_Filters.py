"""
SPOT Filters module for cross-platform path handling and Excel data processing.

This module replaces Windows-specific path operations with pathlib for 
cross-platform compatibility.
"""

from pathlib import Path
import json
import sys
import os
from typing import Dict, List, Union, Optional


class SPOTFilters:
    """Main class for handling SPOT filtering operations with cross-platform path support."""
    
    def __init__(self, base_path: Union[str, Path] = None):
        """Initialize with base path for data files."""
        if base_path is None:
            # Use current directory as default
            self.base_path = Path.cwd()
        else:
            self.base_path = Path(base_path)
        
        # Ensure base path exists
        try:
            self.base_path = self.base_path.resolve()
            if not self.base_path.exists():
                raise FileNotFoundError(f"Base path does not exist: {self.base_path}")
        except (OSError, RuntimeError) as e:
            # Handle environment-specific path resolution issues
            print(f"Warning: Path resolution issue: {e}")
            self.base_path = Path.cwd()
    
    def find_excel_files(self, pattern: str = "*.txt") -> List[Path]:
        """Find Excel export files with cross-platform path handling."""
        try:
            # Use pathlib's glob for cross-platform pattern matching
            files = list(self.base_path.glob(pattern))
            return sorted(files)  # Ensure consistent ordering across platforms
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not search for files: {e}")
            return []
    
    def normalize_file_reference(self, file_ref: str) -> str:
        """
        Normalize Excel file references to be cross-platform.
        
        Converts Windows-specific .xlsb references to generic format.
        """
        try:
            # Remove Windows-specific file extensions and normalize
            if file_ref.endswith('.xlsb'):
                # Extract base name without extension
                base_name = Path(file_ref).stem
                return f"{base_name}"
            return file_ref
        except Exception as e:
            print(f"Warning: Could not normalize file reference '{file_ref}': {e}")
            return file_ref
    
    def process_cross_section_data(self, file_path: Union[str, Path]) -> Dict:
        """Process cross-section data with cross-platform path handling."""
        file_path = Path(file_path)
        
        try:
            # Ensure file exists with cross-platform path
            if not file_path.exists():
                resolved_path = self.base_path / file_path.name
                if resolved_path.exists():
                    file_path = resolved_path
                else:
                    raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read and parse JSON data
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
                
            # Handle potential JSON parsing
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, treat as text data
                data = {"raw_content": content}
            
            # Normalize any Windows-specific file references in the data
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        self._normalize_dict_paths(item)
            elif isinstance(data, dict):
                self._normalize_dict_paths(data)
            
            return data
            
        except (OSError, PermissionError, UnicodeDecodeError) as e:
            # Handle environment-specific file access issues
            print(f"Error processing file {file_path}: {e}")
            return {"error": str(e), "file": str(file_path)}
    
    def _normalize_dict_paths(self, data: Dict):
        """Recursively normalize paths in dictionary data."""
        for key, value in data.items():
            if isinstance(value, str):
                # Look for Excel file references and normalize them
                if '.xlsb' in value:
                    data[key] = self.normalize_file_reference(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str) and '.xlsb' in item:
                        value[i] = self.normalize_file_reference(item)
                    elif isinstance(item, dict):
                        self._normalize_dict_paths(item)
            elif isinstance(value, dict):
                self._normalize_dict_paths(value)
    
    def get_output_path(self, filename: str, output_dir: Union[str, Path] = None) -> Path:
        """Get cross-platform output path."""
        if output_dir is None:
            output_dir = self.base_path / "output"
        else:
            output_dir = Path(output_dir)
        
        try:
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir / filename
        except (OSError, PermissionError) as e:
            # Fallback to current directory if can't create output dir
            print(f"Warning: Could not create output directory, using current dir: {e}")
            return Path(filename)
    
    def check_environment_compatibility(self) -> Dict[str, bool]:
        """Check platform compatibility and return status."""
        status = {
            "pathlib_support": True,
            "file_system_access": True,
            "unicode_support": True,
            "platform": sys.platform
        }
        
        try:
            # Test pathlib operations
            test_path = self.base_path / "test"
            test_path.resolve()
        except Exception:
            status["pathlib_support"] = False
        
        try:
            # Test file system access
            list(self.base_path.iterdir())
        except Exception:
            status["file_system_access"] = False
        
        try:
            # Test unicode handling
            "test_unicode_ÆØÅ".encode('utf-8')
        except Exception:
            status["unicode_support"] = False
        
        return status


def main():
    """Command line interface for SPOT_Filters."""
    if len(sys.argv) < 2:
        print("Usage: python SPOT_Filters.py <command> [args]")
        print("Commands:")
        print("  check - Check environment compatibility")
        print("  process <file> - Process a data file")
        print("  find - Find Excel export files")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        filters = SPOTFilters()
        
        if command == "check":
            status = filters.check_environment_compatibility()
            print(f"Platform: {status['platform']}")
            print(f"Pathlib support: {status['pathlib_support']}")
            print(f"File system access: {status['file_system_access']}")
            print(f"Unicode support: {status['unicode_support']}")
            
        elif command == "process" and len(sys.argv) > 2:
            file_path = sys.argv[2]
            data = filters.process_cross_section_data(file_path)
            print(f"Processed {file_path}")
            if "error" in data:
                print(f"Error: {data['error']}")
            else:
                print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'List data'}")
        
        elif command == "find":
            files = filters.find_excel_files()
            print(f"Found {len(files)} files:")
            for f in files:
                print(f"  {f}")
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()