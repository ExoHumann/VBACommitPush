"""Tests for the embed_section_points_world_symmetric bug."""
import pytest
from spot.data import GeometryProcessor


class TestEmbedSectionPointsWorldSymmetricBug:
    """Tests for the known bug in embed_section_points_world_symmetric."""
    
    def test_world_symmetric_coordinate_system_bug(self, geometry_processor):
        """Test that exposes the coordinate system bug.
        
        This test should FAIL initially, exposing the bug where
        embed_section_points_world_symmetric returns 'local' coordinates
        instead of 'world' coordinates.
        """
        result = geometry_processor.embed_section_points_world_symmetric("Pyl_CSB")
        
        # This assertion will fail because the method currently returns 'local'
        # instead of 'world' coordinates due to the bug
        assert result['coordinate_system'] == 'world', (
            "embed_section_points_world_symmetric should return world coordinates, "
            f"but got: {result['coordinate_system']}"
        )
    
    def test_world_symmetric_should_not_have_bug_marker(self, geometry_processor):
        """Test that the method shouldn't have the bug marker in production."""
        result = geometry_processor.embed_section_points_world_symmetric("Pyl_CSB")
        
        # This test checks for the debugging marker we added
        # In a proper implementation, this marker shouldn't exist
        assert not result.get('has_bug', False), (
            "Production code should not have debugging bug markers"
        )
    
    def test_world_vs_local_coordinates_should_differ(self, geometry_processor):
        """Test that world and local coordinates should be different.
        
        This test will fail because currently both methods return the same coordinates.
        """
        local_result = geometry_processor.embed_section_points_basic("Pyl_CSB")
        world_result = geometry_processor.embed_section_points_world_symmetric("Pyl_CSB")
        
        # The points should be transformed differently in world vs local coordinates
        # Currently they are the same due to the bug
        if local_result['points'] and world_result['points']:
            local_point = local_result['points'][0]
            world_point = world_result['points'][0]
            
            # In a proper implementation, at least one coordinate should be different
            # due to the coordinate transformation
            coordinates_differ = (
                local_point['coord_y'] != world_point['coord_y'] or
                local_point['coord_z'] != world_point['coord_z']
            )
            
            assert coordinates_differ, (
                "World and local coordinates should differ after transformation, "
                "but they are identical (indicating missing transformation)"
            )