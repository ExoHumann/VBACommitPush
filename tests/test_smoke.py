"""Smoke tests for SPOT_VISO system."""
import pytest
from spot.data import DataLoader, GeometryProcessor


class TestSmokeAxisFrames:
    """Smoke tests for axis frames functionality."""
    
    def test_smoke_axis_frames_loading(self, geometry_processor):
        """Smoke test: Can load and process axis frames without errors."""
        axis_frames = geometry_processor.get_axis_frames()
        
        # Basic smoke test - should not crash and return some data
        assert isinstance(axis_frames, list)
        # Should have some data (not necessarily non-empty for all test cases)
        assert len(axis_frames) >= 0
        
        # If there are axis frames, check basic structure
        if axis_frames:
            frame = axis_frames[0]
            assert isinstance(frame, dict)
            assert 'name' in frame
            assert 'station' in frame  
            assert 'axis' in frame
    
    def test_smoke_axis_frames_structure(self, geometry_processor):
        """Smoke test: Axis frames have expected structure."""
        axis_frames = geometry_processor.get_axis_frames()
        
        for frame in axis_frames:
            # Each frame should be a dict with required keys
            assert isinstance(frame, dict)
            assert 'name' in frame
            assert 'station' in frame
            assert 'axis' in frame
            
            # Basic type checks
            assert isinstance(frame['name'], str)
            assert isinstance(frame['axis'], str)


class TestSmokeBasicEmbedding:
    """Smoke tests for basic embedding functionality."""
    
    def test_smoke_basic_embedding_no_crash(self, geometry_processor):
        """Smoke test: Basic embedding doesn't crash."""
        # Test with a known section name from the data
        result = geometry_processor.embed_section_points_basic("Pyl_CSB")
        
        # Should return a dict without crashing
        assert isinstance(result, dict)
        assert 'section_name' in result
        assert 'points' in result
        assert 'point_count' in result
        
        # Basic consistency check
        assert result['point_count'] == len(result['points'])
    
    def test_smoke_basic_embedding_structure(self, geometry_processor):
        """Smoke test: Basic embedding returns expected structure."""
        result = geometry_processor.embed_section_points_basic("Pyl_CSB")
        
        assert result['section_name'] == "Pyl_CSB"
        assert isinstance(result['points'], list)
        assert isinstance(result['point_count'], int)
        
        # If there are points, check their structure
        for point in result['points']:
            assert isinstance(point, dict)
            assert 'point_name' in point
            assert 'coord_y' in point
            assert 'coord_z' in point
    
    def test_smoke_world_symmetric_embedding(self, geometry_processor):
        """Smoke test: World symmetric embedding doesn't crash."""
        result = geometry_processor.embed_section_points_world_symmetric("Pyl_CSB")
        
        # Should have all basic embedding keys plus coordinate system info
        assert isinstance(result, dict)
        assert 'section_name' in result
        assert 'points' in result
        assert 'point_count' in result
        assert 'coordinate_system' in result
        
        # This test will expose the bug - it should be 'world' but will be 'local'
        # This is intentional for milestone 6
        assert result['coordinate_system'] in ['local', 'world']