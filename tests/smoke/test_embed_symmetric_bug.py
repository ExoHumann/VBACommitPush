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
    """Test that the broadcasting error is now fixed with minimal axis + section."""
    
    # Create minimal axis with basic height variable
    axis_variables = {
        'H': {
            'VarValue': [4000],  # Height in mm
            'VarUnit': ['[mm]']
        }
    }
    axis = Axis(name="AX", variables=axis_variables)
    
    # Create minimal section with just two points - this previously triggered the bug
    minimal_points = np.array([
        [0.0, 0.0],    # Point 1: Y=0, Z=0
        [1500.0, 0.0]  # Point 2: Y=1500mm, Z=0  
    ])
    
    # This should now work correctly without raising an exception
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
    
    # This should now work correctly
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
    
    # Test with height in meters
    axis_variables_m = {
        'H': {
            'VarValue': [4.0],  # Height in m
            'VarUnit': ['[m]']
        }
    }
    axis_m = Axis(name="AX", variables=axis_variables_m)
    
    points_m = np.array([
        [0.0, 0.0],
        [1.5, 0.0]  # 1.5 meters
    ])
    
    # Test with m input, expect proper transformation
    world_points_m = embed_section_points_world_symmetric(
        axis=axis_m,
        section_points=points_m,
        station=0.0,
        target_units='[m]'
    )
    
    # Should handle units properly
    assert world_points_m.shape == points_m.shape, \
        f"Shape mismatch: {world_points_m.shape} != {points_m.shape}"
    assert np.all(np.isfinite(world_points_m)), "Non-finite values in output"
    
    # Check Z transformation - should add 4.0m to Z coordinates
    expected_z_values = np.array([4.0, 4.0])  # H=4.0m added to original Z=0.0
    actual_z_values = world_points_m[:, 1]
    np.testing.assert_allclose(actual_z_values, expected_z_values, rtol=1e-6)
    
    # Test with height in millimeters
    axis_variables_mm = {
        'H': {
            'VarValue': [4000.0],  # Height in mm
            'VarUnit': ['[mm]']
        }
    }
    axis_mm = Axis(name="AX", variables=axis_variables_mm)
    
    points_mm = np.array([
        [0.0, 0.0],
        [1500.0, 0.0]  # 1500 millimeters
    ])
    
    world_points_mm = embed_section_points_world_symmetric(
        axis=axis_mm,
        section_points=points_mm,
        station=0.0,
        target_units='[mm]'
    )
    
    # Check Z transformation - should add 4000.0mm to Z coordinates  
    expected_z_values_mm = np.array([4000.0, 4000.0])  # H=4000.0mm added to original Z=0.0
    actual_z_values_mm = world_points_mm[:, 1]
    np.testing.assert_allclose(actual_z_values_mm, expected_z_values_mm, rtol=1e-6)


@pytest.mark.smoke
def test_embed_symmetric_shape_validation():
    """Test comprehensive shape and value validation."""
    
    axis_variables = {
        'H': {
            'VarValue': [1000.0],  # Height in mm
            'VarUnit': ['[mm]']
        }
    }
    axis = Axis(name="AX", variables=axis_variables)
    
    # Test various point configurations
    test_cases = [
        # Single point
        np.array([[0.0, 0.0]]),
        # Two points
        np.array([[0.0, 0.0], [100.0, 200.0]]),
        # Multiple points
        np.array([[0.0, 0.0], [100.0, 200.0], [200.0, 300.0], [300.0, 400.0]]),
        # Negative coordinates
        np.array([[-100.0, -50.0], [100.0, 50.0]]),
    ]
    
    for i, points in enumerate(test_cases):
        world_points = embed_section_points_world_symmetric(
            axis=axis,
            section_points=points,
            station=0.0,
            target_units='[mm]'
        )
        
        # Shape validation
        assert world_points.shape == points.shape, \
            f"Case {i}: Shape mismatch {world_points.shape} != {points.shape}"
        
        # Finite values validation
        assert np.all(np.isfinite(world_points)), \
            f"Case {i}: Non-finite values in output"
        
        # Y coordinates should be preserved (no offset)
        np.testing.assert_allclose(world_points[:, 0], points[:, 0], rtol=1e-6,
                                 err_msg=f"Case {i}: Y coordinates not preserved")
        
        # Z coordinates should be offset by H
        expected_z = points[:, 1] + 1000.0
        np.testing.assert_allclose(world_points[:, 1], expected_z, rtol=1e-6,
                                 err_msg=f"Case {i}: Z coordinates not properly offset")


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