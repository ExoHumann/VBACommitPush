"""Smoke tests for axis model."""

import pytest
import numpy as np

from models.axis import Axis, create_test_axis


@pytest.mark.smoke
def test_axis_creation():
    """Test basic axis creation."""
    stations = np.array([0.0, 100.0, 200.0])
    coordinates = np.array([[0.0, 0.0, 0.0], [100.0, 0.0, 0.0], [200.0, 0.0, 0.0]])
    
    axis = Axis(stations, coordinates)
    
    assert axis.stations.shape == (3,)
    assert axis.coordinates.shape == (3, 3)


@pytest.mark.smoke
def test_embed_section_points_world_shape():
    """Test that embed_section_points_world returns correct shape."""
    axis = create_test_axis(n_stations=5)
    section_points = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]])
    station_indices = np.array([0, 2, 4])
    
    result = axis.embed_section_points_world(section_points, station_indices)
    
    assert result.shape == (3, 4, 3)  # (n_stations, n_points, 3D)


@pytest.mark.smoke
def test_embed_section_points_world_values():
    """Test that embed_section_points_world produces reasonable values."""
    axis = create_test_axis(n_stations=3)
    section_points = np.array([[0.0, 0.0]])  # Single point at origin
    station_indices = np.array([1])
    
    result = axis.embed_section_points_world(section_points, station_indices)
    
    # Result should be finite
    assert np.all(np.isfinite(result))
    
    # Should have correct shape
    assert result.shape == (1, 1, 3)


@pytest.mark.smoke  
def test_parallel_transport_frames_shape():
    """Test that parallel_transport_frames returns correct shape."""
    axis = create_test_axis(n_stations=10)
    
    result = axis.parallel_transport_frames(0, 5)
    
    assert result.shape == (6, 3, 3)  # (n_stations, 3x3 frame)


@pytest.mark.smoke
def test_parallel_transport_frames_values():
    """Test that parallel_transport_frames produces valid rotation matrices."""
    axis = create_test_axis(n_stations=5)
    
    result = axis.parallel_transport_frames(0, 2)
    
    # Each frame should be a valid rotation matrix (orthogonal)
    for i in range(result.shape[0]):
        frame = result[i]
        # Check that columns are orthonormal (approximately)
        for j in range(3):
            col_norm = np.linalg.norm(frame[:, j])
            assert abs(col_norm - 1.0) < 0.1, f"Column {j} norm: {col_norm}"
        
        # Check that it's approximately orthogonal
        should_be_identity = frame.T @ frame
        identity_error = np.linalg.norm(should_be_identity - np.eye(3))
        assert identity_error < 1.0, f"Orthogonality error: {identity_error}"


@pytest.mark.smoke
def test_frame_caching():
    """Test that local frame caching works."""
    axis = create_test_axis(n_stations=3)
    
    # Get frame twice - second call should use cache
    frame1 = axis._get_local_frame(1)
    frame2 = axis._get_local_frame(1)
    
    assert np.allclose(frame1, frame2)
    assert 1 in axis._frames_cache