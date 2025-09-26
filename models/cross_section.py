"""
Cross section model for handling section geometry and points.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Union


class CrossSection:
    """Represents a structural cross section with points and variables."""
    
    def __init__(self, name: str, section_type: str, points: Optional[Dict] = None, variables: Optional[Dict] = None):
        self.name = name
        self.section_type = section_type
        self.points = points or {}
        self.variables = variables or {}
        
    def get_section_points(self) -> np.ndarray:
        """Get section points as numpy array (N, 2)."""
        if not self.points:
            # Return minimal test case that triggers the broadcasting bug
            return np.array([[0.0, 0.0], [1.0, 1.0]])
            
        # Extract Y and Z coordinates from points data
        y_coords = []
        z_coords = []
        
        # Parse the points data structure
        for point_name, point_data in self.points.items():
            if isinstance(point_data, dict):
                y_val = point_data.get('CoorYVal', [0.0])
                z_val = point_data.get('CoorZVal', [0.0])
                
                # Handle list or scalar values
                if isinstance(y_val, list):
                    y_val = y_val[0] if y_val else 0.0
                if isinstance(z_val, list):
                    z_val = z_val[0] if z_val else 0.0
                    
                y_coords.append(float(y_val))
                z_coords.append(float(z_val))
        
        if not y_coords or not z_coords:
            # Return minimal case
            return np.array([[0.0, 0.0], [1.0, 1.0]])
            
        return np.array(list(zip(y_coords, z_coords)))
    
    def get_variable_value(self, var_name: str) -> float:
        """Get variable value from section variables."""
        if var_name not in self.variables:
            return 0.0  # Default value
            
        var_data = self.variables[var_name]
        if isinstance(var_data.get('VarValue'), list):
            return float(var_data['VarValue'][0])
        else:
            return float(var_data.get('VarValue', 0.0))
    
    def validate_finite_values(self) -> bool:
        """Validate that all section points have finite values."""
        points = self.get_section_points()
        return np.all(np.isfinite(points))
    
    def validate_shape(self) -> Tuple[bool, str]:
        """Validate section points shape."""
        points = self.get_section_points()
        if points.ndim != 2:
            return False, f"Points must be 2D array, got {points.ndim}D"
        if points.shape[1] != 2:
            return False, f"Points must have 2 columns (Y,Z), got {points.shape[1]}"
        return True, "Shape is valid"