"""Test configuration and fixtures."""
import pytest
from pathlib import Path
from spot.data import DataLoader, GeometryProcessor


@pytest.fixture
def data_dir():
    """Get the data directory containing test data files."""
    return Path.cwd()


@pytest.fixture  
def data_loader(data_dir):
    """Create a DataLoader instance."""
    return DataLoader(data_dir)


@pytest.fixture
def geometry_processor(data_loader):
    """Create a GeometryProcessor instance."""
    return GeometryProcessor(data_loader)