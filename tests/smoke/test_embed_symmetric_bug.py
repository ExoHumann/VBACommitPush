"""
Test to reproduce the broadcasting error in embed_section_points_world_symmetric.

This test creates a minimal axis + section that previously failed.
"""
import numpy as np
import pytest

from models.axis import Axis, embed_section_points_world_symmetric
from models.cross_section import CrossSection


@pytest.mark.smoke
def test_embed_symmetric_bug_minimal_case():
    """Test that reproduces the broadcasting error with minimal axis + section."""
    
    # Create minimal axis with basic height variable
    axis_variables = {
        'H': {
            'VarValue': [4000],  # Height in mm
            'VarUnit': ['[mm]']
        }
    }
    axis = Axis(name="AX", variables=axis_variables)
    
    # Create minimal section with just two points - this triggers the bug
    minimal_points = np.array([
        [0.0, 0.0],    # Point 1: Y=0, Z=0
        [1500.0, 0.0]  # Point 2: Y=1500mm, Z=0  
    ])
    
    # This should raise a broadcasting error due to the bug in the implementation
    with pytest.raises(RuntimeError, match="Broadcasting error"):
        world_points = embed_section_points_world_symmetric(
            axis=axis,
            section_points=minimal_points,
            station=0.0,
            target_units='[mm]'
        )


@pytest.mark.smoke
def test_embed_symmetric_fixed_behavior():
    """Test that shows the expected behavior after the bug is fixed."""
    
    # Create minimal axis with basic height variable
    axis_variables = {
        'H': {
            'VarValue': [4000],  # Height in mm
            'VarUnit': ['[mm]']
        }
    }
    axis = Axis(name="AX", variables=axis_variables)
    
    # Create minimal section with just two points
    minimal_points = np.array([
        [0.0, 0.0],    # Point 1: Y=0, Z=0
        [1500.0, 0.0]  # Point 2: Y=1500mm, Z=0  
    ])
    
    # This test will initially be skipped, then should pass after the fix
    pytest.skip("Will be enabled after broadcasting fix")
    
    # After fix, this should work:
    world_points = embed_section_points_world_symmetric(
        axis=axis,
        section_points=minimal_points,
        station=0.0,
        target_units='[mm]'
    )
    
    # Test that we get consistent output shape
    assert world_points.shape == minimal_points.shape, \
        f"Output shape {world_points.shape} != input shape {minimal_points.shape}"
    
    # Test that all values are finite
    assert np.all(np.isfinite(world_points)), \
        "World points contain non-finite values"
    
    # Test basic transformation - Z should be offset by H
    expected_z_offset = 4000.0  # H value in mm
    for i in range(len(minimal_points)):
        original_z = minimal_points[i, 1]
        transformed_z = world_points[i, 1]
        expected_z = original_z + expected_z_offset
        
        assert abs(transformed_z - expected_z) < 1e-6, \
            f"Point {i}: expected Z={expected_z}, got Z={transformed_z}"


@pytest.mark.smoke
def test_embed_symmetric_units_handling():
    """Test that units are handled explicitly (mm vs m)."""
    
    axis_variables = {
        'H': {
            'VarValue': [4.0],  # Height in m
            'VarUnit': ['[m]']
        }
    }
    axis = Axis(name="AX", variables=axis_variables)
    
    points_m = np.array([
        [0.0, 0.0],
        [1.5, 0.0]  # 1.5 meters
    ])
    
    # Test conversion to mm
    world_points = embed_section_points_world_symmetric(
        axis=axis,
        section_points=points_m,
        station=0.0,
        target_units='[mm]'
    )
    
    # Should handle units explicitly
    assert world_points.shape == points_m.shape
    assert np.all(np.isfinite(world_points))


@pytest.mark.smoke  
def test_cross_section_validation():
    """Test cross section validation for shapes and finite values."""
    
    # Test with minimal cross section
    section = CrossSection(name="Test", section_type="Minimal")
    
    points = section.get_section_points()
    
    # Validate shape
    is_valid, message = section.validate_shape()
    assert is_valid, f"Shape validation failed: {message}"
    
    # Validate finite values
    assert section.validate_finite_values(), "Section points contain non-finite values"
    
    # Validate expected shape properties
    assert points.ndim == 2, f"Points should be 2D, got {points.ndim}D"
    assert points.shape[1] == 2, f"Points should have 2 columns, got {points.shape[1]}"
    assert points.shape[0] >= 2, f"Should have at least 2 points, got {points.shape[0]}"