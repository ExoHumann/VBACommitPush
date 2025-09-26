"""Cross-section model with embedded points computation."""

import numpy as np
from typing import List, Tuple, Optional


class CrossSection:
    """Cross-section model for bridge structures."""
    
    def __init__(self, points: np.ndarray, variables: dict):
        """Initialize cross-section with points and variables.
        
        Args:
            points: Array of cross-section points (N, 2) with Y, Z coordinates
            variables: Dictionary of section variables (dimensions, etc.)
        """
        self.points = np.array(points)
        self.variables = variables
    
    def compute_embedded_points(self, stations: np.ndarray) -> np.ndarray:
        """Compute embedded 3D points for cross-section at multiple stations.
        
        This function has loops over stations that can be vectorized.
        
        Args:
            stations: Array of station positions along axis (Nstations,)
            
        Returns:
            Array of 3D points (Nstations, Npoints, 3) in world coordinates
        """
        n_stations = len(stations)
        n_points = len(self.points)
        
        # Current implementation uses Python loops - target for optimization
        embedded_points = np.zeros((n_stations, n_points, 3))
        
        for i, station in enumerate(stations):
            # Transform each point from local to world coordinates
            for j, point in enumerate(self.points):
                # Apply station-specific transformations
                y_local = point[0]
                z_local = point[1]
                
                # Apply variable scaling based on station
                scale_factor = self._get_variable_at_station("scale", station)
                offset_y = self._get_variable_at_station("offset_y", station)
                offset_z = self._get_variable_at_station("offset_z", station)
                
                # Transform to world coordinates (X=station, Y, Z)
                x_world = station
                y_world = (y_local * scale_factor) + offset_y
                z_world = (z_local * scale_factor) + offset_z
                
                embedded_points[i, j, :] = [x_world, y_world, z_world]
        
        return embedded_points
    
    def _get_variable_at_station(self, var_name: str, station: float) -> float:
        """Get variable value at specific station with interpolation."""
        # Simulate expensive computation that would benefit from caching
        base_value = self.variables.get(var_name, 1.0)
        
        # Complex computation that varies with station
        variation = np.sin(station * 0.01) * 0.1
        return base_value + variation


def create_test_cross_section(n_points: int = 80) -> CrossSection:
    """Create a test cross-section for benchmarking.
    
    Args:
        n_points: Number of points in cross-section
        
    Returns:
        Test CrossSection instance
    """
    # Generate representative cross-section points (Y, Z coordinates)
    angles = np.linspace(0, 2*np.pi, n_points)
    radius = 2.0
    points = np.column_stack([
        radius * np.cos(angles),  # Y coordinates
        radius * np.sin(angles)   # Z coordinates
    ])
    
    variables = {
        "scale": 1.0,
        "offset_y": 0.0,
        "offset_z": 0.0,
        "width": 4.0,
        "height": 3.0
    }
    
    return CrossSection(points, variables)