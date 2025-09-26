"""Cross-section and embedding module."""
import numpy as np
from typing import List, Tuple, Optional


class CrossSection:
    """A cross-section with named points."""
    
    def __init__(self, name: str):
        self.name = name
        self.points = {}  # point_id -> (y, z) coordinates in mm
        
    def add_point(self, point_id: str, y: float, z: float):
        """Add a point to the cross-section.
        
        Args:
            point_id: Unique identifier for the point
            y: Y coordinate in mm
            z: Z coordinate in mm
        """
        self.points[point_id] = (y, z)
        
    def get_points_array(self) -> Tuple[np.ndarray, List[str]]:
        """Get points as numpy array.
        
        Returns:
            Tuple of (points_array, point_ids) where points_array has shape (N, 2)
        """
        if not self.points:
            return np.empty((0, 2)), []
            
        point_ids = list(self.points.keys())
        points = np.array([self.points[pid] for pid in point_ids])
        return points, point_ids


def create_rectangular_cross_section(width: float, height: float, name: str = "rect") -> CrossSection:
    """Create a simple rectangular cross-section with corner points.
    
    Args:
        width: Width in mm
        height: Height in mm
        name: Name for the cross-section
        
    Returns:
        CrossSection with 4 corner points
    """
    cs = CrossSection(name)
    
    # Add corner points (y, z coordinates)
    cs.add_point("P1", -width/2, -height/2)  # Bottom left
    cs.add_point("P2", width/2, -height/2)   # Bottom right  
    cs.add_point("P3", width/2, height/2)    # Top right
    cs.add_point("P4", -width/2, height/2)   # Top left
    
    return cs


def embed_cross_section_at_stations(
    cross_section: CrossSection, 
    stations: np.ndarray,
    positions: np.ndarray,
    tangents: np.ndarray,
    frame_mode: str = "default"
) -> np.ndarray:
    """Embed cross-section at multiple stations along an axis.
    
    Args:
        cross_section: CrossSection to embed
        stations: Station positions in mm
        positions: Frame positions at stations, shape (N, 3)
        tangents: Frame tangent vectors at stations, shape (N, 3)
        frame_mode: Frame mode ("default" or "symmetric")
        
    Returns:
        Array of shape (N_stations, N_points, 3) with embedded 3D coordinates
    """
    points_2d, point_ids = cross_section.get_points_array()
    
    if len(points_2d) == 0:
        return np.empty((len(stations), 0, 3))
    
    n_stations = len(stations)
    n_points = len(points_2d)
    embedded_points = np.zeros((n_stations, n_points, 3))
    
    for i, (station, position, tangent) in enumerate(zip(stations, positions, tangents)):
        # Create local frame at this station
        x_axis = tangent  # Tangent direction
        
        # Create perpendicular axes (simplified approach)
        if np.abs(x_axis[2]) < 0.9:
            y_axis = np.cross(x_axis, [0, 0, 1])
        else:
            y_axis = np.cross(x_axis, [0, 1, 0])
        y_axis = y_axis / np.linalg.norm(y_axis)
        
        z_axis = np.cross(x_axis, y_axis)
        z_axis = z_axis / np.linalg.norm(z_axis)
        
        # Apply frame mode modifications
        if frame_mode == "symmetric":
            # For symmetric mode, flip z-axis for odd stations
            if i % 2 == 1:
                z_axis = -z_axis
        
        # Transform 2D cross-section points to 3D
        for j, (y_local, z_local) in enumerate(points_2d):
            # Convert local coordinates to global 3D coordinates
            point_3d = position + y_local * y_axis + z_local * z_axis
            embedded_points[i, j] = point_3d
            
    return embedded_points


def validate_embedding_shape(embedded_points: np.ndarray, n_stations: int, n_points: int) -> bool:
    """Validate that embedded points have the correct shape.
    
    Args:
        embedded_points: Array of embedded 3D points
        n_stations: Expected number of stations
        n_points: Expected number of points per station
        
    Returns:
        True if shape matches expectations
    """
    expected_shape = (n_stations, n_points, 3)
    return embedded_points.shape == expected_shape


def validate_stations_monotonic(stations: np.ndarray, tolerance: float = 1e-10) -> bool:
    """Validate that stations are monotonically increasing.
    
    Args:
        stations: Array of station positions
        tolerance: Tolerance for comparison
        
    Returns:
        True if stations are monotonically increasing
    """
    if len(stations) <= 1:
        return True
    
    diffs = np.diff(stations)
    return np.all(diffs >= -tolerance)