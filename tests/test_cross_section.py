"""Smoke tests for cross-section model."""

import pytest
import numpy as np

from models.cross_section import CrossSection, create_test_cross_section


@pytest.mark.smoke
def test_cross_section_creation():
    """Test basic cross-section creation."""
    points = np.array([[0.0, 1.0], [1.0, 0.0], [0.0, -1.0], [-1.0, 0.0]])
    variables = {"scale": 1.0}
    
    section = CrossSection(points, variables)
    
    assert section.points.shape == (4, 2)
    assert section.variables["scale"] == 1.0


@pytest.mark.smoke 
def test_compute_embedded_points_shape():
    """Test that compute_embedded_points returns correct shape."""
    section = create_test_cross_section(n_points=10)
    stations = np.array([0.0, 100.0, 200.0])
    
    result = section.compute_embedded_points(stations)
    
    assert result.shape == (3, 10, 3)  # (n_stations, n_points, 3D)


@pytest.mark.smoke
def test_compute_embedded_points_values():
    """Test that compute_embedded_points produces reasonable values."""
    section = create_test_cross_section(n_points=4)
    stations = np.array([100.0])
    
    result = section.compute_embedded_points(stations)
    
    # Check that X coordinates match station
    assert np.allclose(result[0, :, 0], 100.0)
    
    # Check that result contains finite values
    assert np.all(np.isfinite(result))


@pytest.mark.smoke
def test_variable_interpolation():
    """Test that variable interpolation works."""
    points = np.array([[1.0, 0.0]])
    variables = {"scale": 2.0, "offset_y": 5.0, "offset_z": 10.0}
    
    section = CrossSection(points, variables)
    stations = np.array([0.0])
    
    result = section.compute_embedded_points(stations)
    
    # Y should be scaled and offset
    expected_y = 1.0 * 2.0 + 5.0  # point_y * scale + offset_y + variation
    assert abs(result[0, 0, 1] - expected_y) < 1.0  # Allow for variation