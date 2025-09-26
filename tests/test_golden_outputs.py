"""Golden output tests for regression safety."""
import json
import pytest
from pathlib import Path
from spot.data import GeometryProcessor


class TestGoldenOutputs:
    """Regression tests using golden outputs."""
    
    @pytest.fixture
    def golden_dir(self):
        """Get the golden outputs directory."""
        return Path(__file__).parent / "golden_outputs"
    
    def _save_golden_output(self, data, filename: str, golden_dir: Path):
        """Save data as golden output (helper for generating reference data)."""
        golden_dir.mkdir(exist_ok=True)
        output_file = golden_dir / filename
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)
    
    def _load_golden_output(self, filename: str, golden_dir: Path):
        """Load golden output data."""
        output_file = golden_dir / filename
        if not output_file.exists():
            pytest.skip(f"Golden output not found: {filename}. Run with --generate-golden to create.")
        
        with open(output_file, 'r') as f:
            return json.load(f)
    
    def test_axis_frames_golden(self, geometry_processor, golden_dir):
        """Test axis frames against golden output."""
        axis_frames = geometry_processor.get_axis_frames()
        
        # Sort for consistent comparison
        axis_frames_sorted = sorted(axis_frames, key=lambda x: x.get('name', ''))
        
        filename = "axis_frames.json"
        
        # Check if we should generate golden output
        if not (golden_dir / filename).exists():
            self._save_golden_output(axis_frames_sorted, filename, golden_dir)
            pytest.skip("Generated golden output for axis frames")
        
        expected = self._load_golden_output(filename, golden_dir)
        
        # Compare with golden output
        assert len(axis_frames_sorted) == len(expected), \
            f"Expected {len(expected)} axis frames, got {len(axis_frames_sorted)}"
        
        for actual, expected_frame in zip(axis_frames_sorted, expected):
            assert actual['name'] == expected_frame['name']
            assert actual['station'] == expected_frame['station']
            assert actual['axis'] == expected_frame['axis']
    
    def test_basic_embedding_golden(self, geometry_processor, golden_dir):
        """Test basic embedding against golden output."""
        section_name = "Pyl_CSB"
        result = geometry_processor.embed_section_points_basic(section_name)
        
        # Sort points for consistent comparison
        result_sorted = {
            **result,
            'points': sorted(result['points'], key=lambda x: str(x['point_name']))
        }
        
        filename = f"basic_embedding_{section_name}.json"
        
        # Check if we should generate golden output
        if not (golden_dir / filename).exists():
            self._save_golden_output(result_sorted, filename, golden_dir)
            pytest.skip(f"Generated golden output for basic embedding of {section_name}")
        
        expected = self._load_golden_output(filename, golden_dir)
        
        # Compare with golden output
        assert result_sorted['section_name'] == expected['section_name']
        assert result_sorted['point_count'] == expected['point_count']
        assert len(result_sorted['points']) == len(expected['points'])
        
        for actual_point, expected_point in zip(result_sorted['points'], expected['points']):
            assert actual_point['point_name'] == expected_point['point_name']
            assert abs(actual_point['coord_y'] - expected_point['coord_y']) < 1e-10
            assert abs(actual_point['coord_z'] - expected_point['coord_z']) < 1e-10
    
    def test_world_symmetric_embedding_golden(self, geometry_processor, golden_dir):
        """Test world symmetric embedding against golden output."""
        section_name = "Pyl_CSB"
        result = geometry_processor.embed_section_points_world_symmetric(section_name)
        
        # Sort points for consistent comparison
        result_sorted = {
            **result,
            'points': sorted(result['points'], key=lambda x: str(x['point_name']))
        }
        
        filename = f"world_symmetric_embedding_{section_name}.json"
        
        # Check if we should generate golden output
        if not (golden_dir / filename).exists():
            self._save_golden_output(result_sorted, filename, golden_dir)
            pytest.skip(f"Generated golden output for world symmetric embedding of {section_name}")
        
        expected = self._load_golden_output(filename, golden_dir)
        
        # Compare with golden output
        assert result_sorted['section_name'] == expected['section_name']
        assert result_sorted['point_count'] == expected['point_count']
        assert result_sorted['coordinate_system'] == expected['coordinate_system']
        assert len(result_sorted['points']) == len(expected['points'])
        
        for actual_point, expected_point in zip(result_sorted['points'], expected['points']):
            assert actual_point['point_name'] == expected_point['point_name']
            assert abs(actual_point['coord_y'] - expected_point['coord_y']) < 1e-10
            assert abs(actual_point['coord_z'] - expected_point['coord_z']) < 1e-10
    
    def test_coordinate_transformation_consistency_golden(self, geometry_processor, golden_dir):
        """Test that coordinate transformation is consistent."""
        section_name = "Pyl_CSB"
        
        local_result = geometry_processor.embed_section_points_basic(section_name)
        world_result = geometry_processor.embed_section_points_world_symmetric(section_name)
        
        # Create comparison data
        comparison_data = {
            'section_name': section_name,
            'local_point_count': local_result['point_count'],
            'world_point_count': world_result['point_count'],
            'coordinate_system_local': 'local',
            'coordinate_system_world': world_result['coordinate_system'],
            'transformation_differences': []
        }
        
        # Calculate transformation differences
        for local_pt, world_pt in zip(local_result['points'], world_result['points']):
            if local_pt['point_name'] == world_pt['point_name']:
                diff = {
                    'point_name': local_pt['point_name'],
                    'y_diff': world_pt['coord_y'] - local_pt['coord_y'],
                    'z_diff': world_pt['coord_z'] - local_pt['coord_z']
                }
                comparison_data['transformation_differences'].append(diff)
        
        # Sort for consistency
        comparison_data['transformation_differences'].sort(
            key=lambda x: str(x['point_name'])
        )
        
        filename = f"transformation_consistency_{section_name}.json"
        
        # Check if we should generate golden output
        if not (golden_dir / filename).exists():
            self._save_golden_output(comparison_data, filename, golden_dir)
            pytest.skip(f"Generated golden output for transformation consistency of {section_name}")
        
        expected = self._load_golden_output(filename, golden_dir)
        
        # Compare with golden output
        assert comparison_data['section_name'] == expected['section_name']
        assert comparison_data['local_point_count'] == expected['local_point_count']
        assert comparison_data['world_point_count'] == expected['world_point_count']
        assert comparison_data['coordinate_system_world'] == expected['coordinate_system_world']
        
        assert len(comparison_data['transformation_differences']) == len(expected['transformation_differences'])
        
        for actual_diff, expected_diff in zip(
            comparison_data['transformation_differences'], 
            expected['transformation_differences']
        ):
            assert actual_diff['point_name'] == expected_diff['point_name']
            assert abs(actual_diff['y_diff'] - expected_diff['y_diff']) < 1e-10
            assert abs(actual_diff['z_diff'] - expected_diff['z_diff']) < 1e-10