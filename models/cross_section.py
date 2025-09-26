"""Cross-section model with embedded points computation."""

import numpy as np
from functools import lru_cache
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
        
        Optimized version using numpy vectorization and caching.
        
        Args:
            stations: Array of station positions along axis (Nstations,)
            
        Returns:
            Array of 3D points (Nstations, Npoints, 3) in world coordinates
        """
        n_stations = len(stations)
        n_points = len(self.points)
        
        # Vectorized implementation - process all stations and points at once
        
        # Get all variable values for all stations (with caching)
        scale_factors = np.array([self._get_variable_at_station_cached("scale", station) 
                                 for station in stations])
        offset_y_values = np.array([self._get_variable_at_station_cached("offset_y", station)
                                   for station in stations])  
        offset_z_values = np.array([self._get_variable_at_station_cached("offset_z", station)
                                   for station in stations])
        
        # Broadcast operations for all points and stations
        # Shape manipulations for broadcasting:
        # stations: (n_stations,) -> (n_stations, 1, 1)
        # points: (n_points, 2) -> (1, n_points, 2)
        # scale_factors: (n_stations,) -> (n_stations, 1)
        
        # Prepare broadcasting dimensions
        stations_bc = stations[:, np.newaxis, np.newaxis]  # (n_stations, 1, 1)
        points_bc = self.points[np.newaxis, :, :]           # (1, n_points, 2)
        scale_factors_bc = scale_factors[:, np.newaxis]     # (n_stations, 1)
        offset_y_bc = offset_y_values[:, np.newaxis]        # (n_stations, 1)
        offset_z_bc = offset_z_values[:, np.newaxis]        # (n_stations, 1)
        
        # Extract Y and Z coordinates
        y_local = points_bc[:, :, 0]  # (1, n_points) -> broadcast to (n_stations, n_points)
        z_local = points_bc[:, :, 1]  # (1, n_points) -> broadcast to (n_stations, n_points)
        
        # Vectorized transformations
        x_world = np.broadcast_to(stations_bc[:, :, 0], (n_stations, n_points))
        y_world = (y_local * scale_factors_bc) + offset_y_bc
        z_world = (z_local * scale_factors_bc) + offset_z_bc
        
        # Stack into final result
        embedded_points = np.stack([x_world, y_world, z_world], axis=-1)
        
        return embedded_points
    
    @lru_cache(maxsize=1000)
    def _get_variable_at_station_cached(self, var_name: str, station: float) -> float:
        """Cached version of variable lookup for performance."""
        return self._get_variable_at_station(var_name, station)
    
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