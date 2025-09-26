"""
Axis model for handling axis variables and coordinates.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Union


class Axis:
    """Represents a structural axis with variables and coordinates."""
    
    def __init__(self, name: str, variables: Optional[Dict[str, Dict]] = None):
        self.name = name
        self.variables = variables or {}
        
    def get_variable_value(self, var_name: str, station: float = 0.0) -> float:
        """Get variable value at a specific station."""
        if var_name not in self.variables:
            raise KeyError(f"Variable {var_name} not found in axis {self.name}")
            
        var_data = self.variables[var_name]
        # For now, return the first value if it's a list, or the value directly
        if isinstance(var_data.get('VarValue'), list):
            return float(var_data['VarValue'][0])
        else:
            return float(var_data['VarValue'])
    
    def convert_units(self, value: Union[float, np.ndarray], from_unit: str, to_unit: str) -> Union[float, np.ndarray]:
        """Convert between units (mm and m)."""
        if from_unit == to_unit:
            return value
            
        # Convert from mm to m
        if from_unit == '[mm]' and to_unit == '[m]':
            return value / 1000.0
        # Convert from m to mm  
        elif from_unit == '[m]' and to_unit == '[mm]':
            return value * 1000.0
        else:
            raise ValueError(f"Unsupported unit conversion from {from_unit} to {to_unit}")


def embed_section_points_world_symmetric(
    axis: Axis,
    section_points: np.ndarray,
    station: float = 0.0,
    target_units: str = '[m]'
) -> np.ndarray:
    """
    Embed section points into world coordinates using symmetric transformation.
    
    This function has a known broadcasting error when handling minimal axis + section
    combinations that needs to be fixed.
    
    Args:
        axis: Axis object with variables
        section_points: Array of section points (N, 2) with Y, Z coordinates
        station: Station position along the axis
        target_units: Target units for output ('[m]' or '[mm]')
    
    Returns:
        Array of world coordinates (N, 2)
    """
    if section_points.ndim != 2 or section_points.shape[1] != 2:
        raise ValueError("section_points must be (N, 2) array")
        
    # Get axis variables for transformation
    try:
        # This is where the bug occurs - broadcasting issue with minimal data
        H = axis.get_variable_value('H', station)  # Height
        
        # BUG: Attempt to use vectorized operations but with incorrect broadcasting
        # This creates shape mismatch errors with certain axis + section combinations
        y_coords = section_points[:, 0]  # Shape: (N,)
        z_coords = section_points[:, 1]  # Shape: (N,)
        
        # Try to get additional axis parameters that may not exist
        try:
            # These may return scalars or arrays, causing broadcasting issues
            offset_y = axis.get_variable_value('offset_y', station)  # May not exist
            offset_z = axis.get_variable_value('offset_z', station)  # May not exist
        except KeyError:
            # Set defaults, but with wrong shapes that cause broadcasting errors
            offset_y = np.array([[0.0]])  # Shape: (1,1) - WRONG! Causes broadcasting issue
            offset_z = np.array([[0.0]])  # Shape: (1,1) - WRONG! Causes broadcasting issue
        
        # BROADCASTING BUG: These operations fail when shapes don't match
        # y_coords is (N,), offset_y is (1,) - this works
        # but when we try to assign back to world_points, shapes mismatch
        world_y = y_coords + offset_y  # May work or fail depending on offset_y shape
        world_z = z_coords + offset_z + H  # Broadcasting error here!
        
        # BUG: Try to stack with potentially mismatched shapes
        # This line causes the actual broadcasting error
        try:
            world_points = np.column_stack([world_y, world_z])  # FAILS HERE when shapes don't match
        except ValueError as ve:
            # Convert numpy ValueError to RuntimeError to indicate broadcasting issue
            raise RuntimeError(f"Broadcasting error in embed_section_points_world_symmetric: {ve}")
            
    except KeyError as ke:
        raise RuntimeError(f"Broadcasting error in embed_section_points_world_symmetric: Missing axis variable: {ke}")
    except Exception as e:
        # This catches other broadcasting errors
        raise RuntimeError(f"Broadcasting error in embed_section_points_world_symmetric: {e}")
    
    return world_points