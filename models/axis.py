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
    
    Fixed version that handles broadcasting correctly.
    
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
        H = axis.get_variable_value('H', station)  # Height - always a scalar
        
        # Extract coordinates properly
        y_coords = section_points[:, 0]  # Shape: (N,)
        z_coords = section_points[:, 1]  # Shape: (N,)
        
        # Get additional axis parameters, ensuring they are scalars
        try:
            offset_y = axis.get_variable_value('offset_y', station)
            offset_z = axis.get_variable_value('offset_z', station)
        except KeyError:
            # FIX: Use scalar defaults instead of arrays to prevent broadcasting issues
            offset_y = 0.0  # Scalar, not array
            offset_z = 0.0  # Scalar, not array
        
        # FIX: All operations now work with proper broadcasting
        # y_coords (N,) + offset_y (scalar) = (N,)
        # z_coords (N,) + offset_z (scalar) + H (scalar) = (N,)
        world_y = y_coords + offset_y  # Proper broadcasting: (N,) + scalar = (N,)
        world_z = z_coords + offset_z + H  # Proper broadcasting: (N,) + scalar + scalar = (N,)
        
        # FIX: column_stack with two (N,) arrays produces (N, 2) as expected
        world_points = np.column_stack([world_y, world_z])  # (N,) + (N,) -> (N, 2)
        
        # Validate output shape
        assert world_points.shape == section_points.shape, \
            f"Output shape mismatch: {world_points.shape} != {section_points.shape}"
        
        # Validate finite values
        if not np.all(np.isfinite(world_points)):
            raise ValueError("Transformation resulted in non-finite values")
            
    except KeyError as ke:
        raise RuntimeError(f"Broadcasting error in embed_section_points_world_symmetric: Missing axis variable: {ke}")
    except Exception as e:
        raise RuntimeError(f"Broadcasting error in embed_section_points_world_symmetric: {e}")
    
    return world_points