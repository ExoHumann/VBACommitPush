"""Smoke tests for axis frame functionality."""
import pytest
import numpy as np
import sys
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from vbacommitpush.axis_frame import (
    create_straight_axis,
    compute_frames_at_stations,
    validate_tangents
)


@pytest.mark.smoke
def test_straight_synthetic_axis(sample_stations, tolerance):
    """Test building a straight synthetic axis and computing frames at 3 stations."""
    # Create a straight axis from 0 to 1000 mm
    axis = create_straight_axis(0.0, 1000.0, num_points=1000)
    
    # Verify axis is created correctly
    assert axis.shape[0] == 1000
    assert axis.shape[1] == 3
    
    # Check that it's straight (y and z should be zero)
    assert np.allclose(axis[:, 1], 0.0, atol=tolerance)
    assert np.allclose(axis[:, 2], 0.0, atol=tolerance)
    
    # Check that x values are linearly spaced
    expected_x = np.linspace(0.0, 1000.0, 1000)
    assert np.allclose(axis[:, 0], expected_x, atol=tolerance)


@pytest.mark.smoke
def test_compute_frames_at_stations(sample_stations, tolerance):
    """Test computing frames at 3 stations along a straight axis."""
    # Create a straight axis
    axis = create_straight_axis(0.0, 1000.0, num_points=1000)
    
    # Compute frames at the sample stations
    positions, tangents = compute_frames_at_stations(axis, sample_stations)
    
    # Verify we get the correct number of frames
    assert len(positions) == len(sample_stations)
    assert len(tangents) == len(sample_stations)
    assert positions.shape == (3, 3)  # 3 stations, 3D positions
    assert tangents.shape == (3, 3)   # 3 stations, 3D tangents


@pytest.mark.smoke
def test_tangent_validation(sample_stations, tolerance):
    """Test that tangent vectors have unit norm and no NaNs."""
    # Create a straight axis
    axis = create_straight_axis(0.0, 1000.0, num_points=1000)
    
    # Compute frames at stations
    positions, tangents = compute_frames_at_stations(axis, sample_stations)
    
    # Validate tangents
    unit_norm_ok, no_nans_ok = validate_tangents(tangents, tolerance)
    
    # Assert tangents have unit norm
    assert unit_norm_ok, "Tangent vectors should have unit norm"
    
    # Assert no NaNs in tangents
    assert no_nans_ok, "Tangent vectors should not contain NaN values"
    
    # Additional direct checks
    norms = np.linalg.norm(tangents, axis=1)
    assert np.all(np.abs(norms - 1.0) < tolerance), f"Norms: {norms}"
    assert not np.any(np.isnan(tangents)), "Found NaN values in tangents"