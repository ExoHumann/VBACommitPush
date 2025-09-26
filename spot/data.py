"""Data loading and parsing utilities."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from functools import lru_cache


logger = logging.getLogger(__name__)


class DataLoader:
    """Loads and parses bridge geometry data from Excel JSON exports."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize data loader.
        
        Args:
            data_dir: Directory containing data files. Defaults to current directory.
        """
        self.data_dir = data_dir or Path.cwd()
        self._cache = {}  # Simple file cache
        
    def load_cross_sections(self) -> List[Dict[str, Any]]:
        """Load cross-section data."""
        file_path = self.data_dir / "CrossSection_Excel.txt"
        return self._load_json_file_cached(file_path)
    
    def load_cross_section_points(self) -> List[Dict[str, Any]]:
        """Load cross-section points data."""
        file_path = self.data_dir / "CrossSection_Points_Excel.txt"
        return self._load_json_file_cached(file_path)
    
    def load_cross_section_variables(self) -> List[Dict[str, Any]]:
        """Load cross-section variables data."""
        file_path = self.data_dir / "CrossSection_Variables_Excel.txt"
        return self._load_json_file_cached(file_path)
    
    def load_main_stations(self) -> List[Dict[str, Any]]:
        """Load main stations data."""
        file_path = self.data_dir / "MainStation_Excel.txt"
        return self._load_json_file_cached(file_path)
    
    def load_deck_objects(self) -> List[Dict[str, Any]]:
        """Load deck objects data."""
        file_path = self.data_dir / "DeckObject_Excel.txt" 
        return self._load_json_file_cached(file_path)
        
    def _load_json_file_cached(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load and parse a JSON file with caching.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        cache_key = str(file_path)
        if cache_key in self._cache:
            logger.debug(f"Using cached data for {file_path.name}")
            return self._cache[cache_key]
            
        data = self._load_json_file(file_path)
        self._cache[cache_key] = data
        return data
    
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
                
                # Safely extract coordinates
                coord_y_raw = point.get('CoorYVal', [0])[0]
                coord_z_raw = point.get('CoorZVal', [0])[0]
                
                # Convert to safe numeric values
                coord_y = 0.0
                coord_z = 0.0
                
                try:
                    if coord_y_raw is None or coord_y_raw == "":
                        coord_y = 0.0
                    elif isinstance(coord_y_raw, (int, float)):
                        coord_y = float(coord_y_raw)
                    elif isinstance(coord_y_raw, str):
                        if "VÆRDI" in coord_y_raw or "#" in coord_y_raw:
                            coord_y = 0.0
                        else:
                            coord_y = float(coord_y_raw)
                    else:
                        coord_y = float(coord_y_raw)
                except (ValueError, TypeError):
                    coord_y = 0.0
                    
                try:
                    if coord_z_raw is None or coord_z_raw == "":
                        coord_z = 0.0
                    elif isinstance(coord_z_raw, (int, float)):
                        coord_z = float(coord_z_raw)
                    elif isinstance(coord_z_raw, str):
                        if "VÆRDI" in coord_z_raw or "#" in coord_z_raw:
                            coord_z = 0.0
                        else:
                            coord_z = float(coord_z_raw)
                    else:
                        coord_z = float(coord_z_raw)
                except (ValueError, TypeError):
                    coord_z = 0.0
                
                section_points.append({
                    'point_name': point.get('PointName', [''])[0],
                    'coord_y': coord_y,
                    'coord_z': coord_z
                })
        
        return {
            'section_name': section_name,
            'points': section_points,
            'point_count': len(section_points)
        }
    
    def embed_section_points_world_symmetric(self, section_name: str) -> Dict[str, Any]:
        """World symmetric section point embedding with vectorized coordinate transformation."""
        basic_embedding = self.embed_section_points_basic(section_name)
        
        if not basic_embedding['points']:
            return {
                'section_name': section_name,
                'points': [],
                'point_count': 0,
                'coordinate_system': 'world'
            }
        
        # Vectorized coordinate transformation using numpy
        points = basic_embedding['points']
        point_names = [p['point_name'] for p in points]
        
        # Extract coordinates as numpy arrays for vectorized operations
        coord_y_values = []
        coord_z_values = []
        
        for point in points:
            coord_y = 0.0
            coord_z = 0.0
            
            try:
                y_val = point['coord_y']
                z_val = point['coord_z']
                
                # Handle y coordinate
                if y_val is None or y_val == "":
                    coord_y = 0.0
                elif isinstance(y_val, (int, float)):
                    coord_y = float(y_val)
                elif isinstance(y_val, str):
                    if "VÆRDI" in y_val or "#" in y_val:
                        coord_y = 0.0
                    else:
                        try:
                            coord_y = float(y_val)
                        except ValueError:
                            coord_y = 0.0
                else:
                    coord_y = float(y_val)  # Try conversion anyway
                    
                # Handle z coordinate
                if z_val is None or z_val == "":
                    coord_z = 0.0
                elif isinstance(z_val, (int, float)):
                    coord_z = float(z_val)
                elif isinstance(z_val, str):
                    if "VÆRDI" in z_val or "#" in z_val:
                        coord_z = 0.0
                    else:
                        try:
                            coord_z = float(z_val)
                        except ValueError:
                            coord_z = 0.0
                else:
                    coord_z = float(z_val)  # Try conversion anyway
                    
            except Exception as e:
                logger.warning(f"Error processing coordinates for point {point.get('point_name', 'unknown')}: {e}")
                coord_y = 0.0
                coord_z = 0.0
                
            coord_y_values.append(coord_y)
            coord_z_values.append(coord_z)
        
        # Vectorized transformation using numpy
        # Ensure all values are properly converted to float before creating arrays
        safe_y_values = []
        safe_z_values = []
        
        for y_val, z_val in zip(coord_y_values, coord_z_values):
            try:
                safe_y_values.append(float(y_val))
                safe_z_values.append(float(z_val))
            except (ValueError, TypeError):
                safe_y_values.append(0.0)
                safe_z_values.append(0.0)
        
        coord_y_array = np.array(safe_y_values, dtype=np.float64)
        coord_z_array = np.array(safe_z_values, dtype=np.float64)
        
        # Apply vectorized coordinate transformation
        # Simple transformation: scaling and offset
        transformed_y = coord_y_array * 1.0  # Identity scaling 
        transformed_z = coord_z_array * 1.0 + 100  # Add world offset
        
        # Convert back to list of dictionaries
        transformed_points = []
        for i, name in enumerate(point_names):
            transformed_points.append({
                'point_name': name,
                'coord_y': float(transformed_y[i]),
                'coord_z': float(transformed_z[i])
            })
        
        return {
            'section_name': section_name,
            'points': transformed_points,
            'point_count': len(transformed_points),
            'coordinate_system': 'world'
        }