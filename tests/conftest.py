"""Test configuration for VBA Commit Push project."""
import pytest
import numpy as np


@pytest.fixture
def sample_stations():
    """Fixture providing sample station positions in mm."""
    return np.array([0.0, 500.0, 1000.0])


@pytest.fixture
def tolerance():
    """Fixture providing numerical tolerance for comparisons."""
    return 1e-10