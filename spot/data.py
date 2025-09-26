"""Data loading and parsing utilities."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd


logger = logging.getLogger(__name__)


class DataLoader:
    """Loads and parses bridge geometry data from Excel JSON exports."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize data loader.
        
        Args:
            data_dir: Directory containing data files. Defaults to current directory.
        """
        self.data_dir = data_dir or Path.cwd()
        
    def load_cross_sections(self) -> List[Dict[str, Any]]:
        """Load cross-section data."""
        file_path = self.data_dir / "CrossSection_Excel.txt"
        return self._load_json_file(file_path)
    
    def load_cross_section_points(self) -> List[Dict[str, Any]]:
        """Load cross-section points data."""
        file_path = self.data_dir / "CrossSection_Points_Excel.txt"
        return self._load_json_file(file_path)
    
    def load_cross_section_variables(self) -> List[Dict[str, Any]]:
        """Load cross-section variables data."""
        file_path = self.data_dir / "CrossSection_Variables_Excel.txt"
        return self._load_json_file(file_path)
    
    def load_main_stations(self) -> List[Dict[str, Any]]:
        """Load main stations data."""
        file_path = self.data_dir / "MainStation_Excel.txt"
        return self._load_json_file(file_path)
    
    def load_deck_objects(self) -> List[Dict[str, Any]]:
        """Load deck objects data."""
        file_path = self.data_dir / "DeckObject_Excel.txt" 
        return self._load_json_file(file_path)
    
    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load and parse a JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} records from {file_path.name}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {file_path}: {e}")
            raise


class GeometryProcessor:
    """Processes bridge geometry data."""
    
    def __init__(self, data_loader: DataLoader):
        """Initialize geometry processor.
        
        Args:
            data_loader: Data loader instance
        """
        self.data_loader = data_loader
        
    def get_axis_frames(self) -> List[Dict[str, Any]]:
        """Get axis frame data - placeholder for actual implementation."""
        # This is a placeholder - actual implementation would process station data
        stations = self.data_loader.load_main_stations()
        
        # Filter for actual stations (not comments)
        axis_frames = []
        for station in stations:
            if (station.get('Class', [''])[0] == 'MainStation' and 
                station.get('InActive', [''])[0] != 'x'):
                axis_frames.append({
                    'name': station.get('Name', [''])[0],
                    'station': station.get('Station', [0])[0],
                    'axis': station.get('Axis', [''])[0]
                })
                
        return axis_frames
    
    def embed_section_points_basic(self, section_name: str) -> Dict[str, Any]:
        """Basic section point embedding - placeholder implementation."""
        points = self.data_loader.load_cross_section_points()
        variables = self.data_loader.load_cross_section_variables()
        
        # Find points for the given section
        section_points = []
        for point in points:
            if (point.get('Name', [''])[0] == section_name and 
                point.get('InActive', [''])[0] != 'x'):
                section_points.append({
                    'point_name': point.get('PointName', [''])[0],
                    'coord_y': point.get('CoorYVal', [0])[0],
                    'coord_z': point.get('CoorZVal', [0])[0]
                })
        
        return {
            'section_name': section_name,
            'points': section_points,
            'point_count': len(section_points)
        }
    
    def embed_section_points_world_symmetric(self, section_name: str) -> Dict[str, Any]:
        """World symmetric section point embedding - contains known bug for testing."""
        # This method intentionally contains a bug for testing purposes
        # The bug is that it doesn't handle coordinate transformation properly
        basic_embedding = self.embed_section_points_basic(section_name)
        
        # Bug: Missing proper coordinate transformation
        # Should transform local coordinates to world coordinates
        # But currently just returns local coordinates
        return {
            **basic_embedding,
            'coordinate_system': 'local',  # Should be 'world'
            'has_bug': True  # This will be used in tests
        }