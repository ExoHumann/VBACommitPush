"""Axis and frame computation module."""
import numpy as np
from typing import Tuple, Optional


def create_straight_axis(start: float, end: float, num_points: int = 100) -> np.ndarray:
    """Create a straight synthetic axis in mm.
    
    Args:
        start: Start position in mm
        end: End position in mm  
        num_points: Number of points along the axis
        
    Returns:
        Array of shape (num_points, 3) representing axis points [x, y, z]
    """
    x = np.linspace(start, end, num_points)
    y = np.zeros(num_points)
    z = np.zeros(num_points)
    return np.column_stack([x, y, z])


def compute_frames_at_stations(axis: np.ndarray, stations: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute frames (local coordinate systems) at specified stations.
    
    Args:
        axis: Array of shape (N, 3) representing axis points
        stations: Array of station positions in mm
        
    Returns:
        Tuple of (positions, tangents) where:
        - positions: Array of shape (len(stations), 3) for frame origins
        - tangents: Array of shape (len(stations), 3) for frame tangent vectors
    """
    positions = []
    tangents = []
    
    for station in stations:
        # Find closest point on axis to the station
        axis_x = axis[:, 0]
        idx = np.argmin(np.abs(axis_x - station))
        
        # Get position at this station
        pos = axis[idx]
        positions.append(pos)
        
        # Compute tangent vector
        if idx == 0:
            # Forward difference at start
            tangent = axis[idx + 1] - axis[idx]
        elif idx == len(axis) - 1:
            # Backward difference at end
            tangent = axis[idx] - axis[idx - 1]
        else:
            # Central difference
            tangent = (axis[idx + 1] - axis[idx - 1]) / 2
            
        # Normalize tangent
        norm = np.linalg.norm(tangent)
        if norm > 0:
            tangent = tangent / norm
        tangents.append(tangent)
    
    return np.array(positions), np.array(tangents)


def validate_tangents(tangents: np.ndarray, tolerance: float = 1e-10) -> Tuple[bool, bool]:
    """Validate that tangent vectors have unit norm and no NaNs.
    
    Args:
        tangents: Array of tangent vectors
        tolerance: Tolerance for unit norm check
        
    Returns:
        Tuple of (unit_norm_ok, no_nans_ok)
    """
    # Check for NaNs
    no_nans = not np.any(np.isnan(tangents))
    
    # Check unit norm
    norms = np.linalg.norm(tangents, axis=1)
    unit_norm = np.all(np.abs(norms - 1.0) < tolerance)
    
    return unit_norm, no_nans