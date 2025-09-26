"""Smoke tests for cross-section embedding functionality."""
import pytest
import numpy as np
import sys
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from vbacommitpush.cross_section import (
    create_rectangular_cross_section,
    embed_cross_section_at_stations,
    validate_embedding_shape,
    validate_stations_monotonic
)
from vbacommitpush.axis_frame import (
    create_straight_axis,
    compute_frames_at_stations
)


@pytest.mark.smoke
def test_tiny_rectangular_cross_section():
    """Test defining a tiny rectangular cross-section with point IDs."""
    # Create a small rectangular cross-section (10mm x 8mm)
    width, height = 10.0, 8.0
    cs = create_rectangular_cross_section(width, height, name="tiny_rect")
    
    # Verify cross-section properties
    assert cs.name == "tiny_rect"
    assert len(cs.points) == 4  # Rectangle has 4 corner points
    
    # Check point IDs exist
    expected_ids = {"P1", "P2", "P3", "P4"}
    assert set(cs.points.keys()) == expected_ids
    
    # Verify point coordinates
    points_array, point_ids = cs.get_points_array()
    assert points_array.shape == (4, 2)  # 4 points, 2D coordinates
    assert len(point_ids) == 4


@pytest.mark.smoke
def test_embed_at_three_stations_default_mode(sample_stations, tolerance):
    """Test embedding cross-section at 3 stations with default frame mode."""
    # Create a tiny rectangular cross-section
    cs = create_rectangular_cross_section(10.0, 8.0, name="test_rect")
    
    # Create axis and compute frames
    axis = create_straight_axis(0.0, 1000.0, num_points=1000)
    positions, tangents = compute_frames_at_stations(axis, sample_stations)
    
    # Embed cross-section at stations with default frame mode
    embedded = embed_cross_section_at_stations(
        cs, sample_stations, positions, tangents, frame_mode="default"
    )
    
    # Verify embedding shape
    n_stations = len(sample_stations)
    n_points = len(cs.points)
    assert validate_embedding_shape(embedded, n_stations, n_points)
    assert embedded.shape == (3, 4, 3)  # 3 stations, 4 points, 3D coordinates


@pytest.mark.smoke 
def test_embed_at_three_stations_symmetric_mode(sample_stations, tolerance):
    """Test embedding cross-section at 3 stations with symmetric frame mode."""
    # Create a tiny rectangular cross-section
    cs = create_rectangular_cross_section(10.0, 8.0, name="test_rect")
    
    # Create axis and compute frames  
    axis = create_straight_axis(0.0, 1000.0, num_points=1000)
    positions, tangents = compute_frames_at_stations(axis, sample_stations)
    
    # Embed cross-section at stations with symmetric frame mode
    embedded = embed_cross_section_at_stations(
        cs, sample_stations, positions, tangents, frame_mode="symmetric"
    )
    
    # Verify embedding shape
    n_stations = len(sample_stations)
    n_points = len(cs.points)
    assert validate_embedding_shape(embedded, n_stations, n_points)
    assert embedded.shape == (3, 4, 3)  # 3 stations, 4 points, 3D coordinates


@pytest.mark.smoke
def test_stations_monotonic(sample_stations):
    """Test that stations are monotonic."""
    # Test with the sample stations (should be monotonic)
    assert validate_stations_monotonic(sample_stations)
    
    # Test with explicitly monotonic array
    monotonic_stations = np.array([0.0, 100.0, 200.0, 500.0])
    assert validate_stations_monotonic(monotonic_stations)
    
    # Test with non-monotonic array
    non_monotonic_stations = np.array([0.0, 500.0, 200.0])
    assert not validate_stations_monotonic(non_monotonic_stations)


@pytest.mark.smoke
def test_embedding_shapes_match_expectations(sample_stations):
    """Test that embedding shapes match expected dimensions."""
    # Create cross-section
    cs = create_rectangular_cross_section(5.0, 4.0)
    
    # Create axis and frames
    axis = create_straight_axis(0.0, 1000.0)
    positions, tangents = compute_frames_at_stations(axis, sample_stations)
    
    # Embed with both modes
    for frame_mode in ["default", "symmetric"]:
        embedded = embed_cross_section_at_stations(
            cs, sample_stations, positions, tangents, frame_mode=frame_mode
        )
        
        # Verify shapes match expectations
        n_stations = len(sample_stations)  # 3
        n_points = len(cs.points)          # 4
        
        assert embedded.shape[0] == n_stations, f"Expected {n_stations} stations, got {embedded.shape[0]}"
        assert embedded.shape[1] == n_points, f"Expected {n_points} points, got {embedded.shape[1]}" 
        assert embedded.shape[2] == 3, f"Expected 3D coordinates, got {embedded.shape[2]}D"
        
        # Verify using the validation function
        assert validate_embedding_shape(embedded, n_stations, n_points)