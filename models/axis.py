"""Axis model with coordinate system and frame transformations."""

import numpy as np
from typing import List, Tuple, Optional


class Axis:
    """Bridge axis with coordinate transformations and frame transport."""
    
    def __init__(self, stations: np.ndarray, coordinates: np.ndarray):
        """Initialize axis with stations and their 3D coordinates.
        
        Args:
            stations: Station positions along axis (Nstations,)  
            coordinates: 3D coordinates at each station (Nstations, 3)
        """
        self.stations = np.array(stations)
        self.coordinates = np.array(coordinates)
        self._frames_cache = {}
    
    def embed_section_points_world(self, section_points: np.ndarray, 
                                 station_indices: np.ndarray) -> np.ndarray:
        """Embed cross-section points into world coordinate system.
        
        This function has loops over stations/points that can be vectorized.
        
        Args:
            section_points: Local section points (Npoints, 2) in Y-Z plane
            station_indices: Station indices where to embed points (Nstations,)
            
        Returns:
            World coordinates (Nstations, Npoints, 3)
        """
        n_stations = len(station_indices)
        n_points = len(section_points)
        
        # Current implementation uses Python loops - target for optimization
        world_points = np.zeros((n_stations, n_points, 3))
        
        for i, station_idx in enumerate(station_indices):
            # Get local coordinate frame at this station
            frame = self._get_local_frame(station_idx)
            station_coord = self.coordinates[station_idx]
            
            # Transform each section point to world coordinates
            for j, section_point in enumerate(section_points):
                # Local point in section plane (0, Y, Z)
                local_point = np.array([0.0, section_point[0], section_point[1]])
                
                # Transform to world coordinates using local frame
                world_point = station_coord + frame @ local_point
                world_points[i, j, :] = world_point
        
        return world_points
    
    def parallel_transport_frames(self, start_station: int, 
                                end_station: int) -> np.ndarray:
        """Compute parallel transport of coordinate frames along axis.
        
        This function has loops that can be vectorized.
        
        Args:
            start_station: Starting station index
            end_station: Ending station index
            
        Returns:
            Transported frames (Nstations, 3, 3)
        """
        station_range = range(start_station, end_station + 1)
        n_stations = len(station_range)
        
        # Current implementation uses Python loops - target for optimization  
        frames = np.zeros((n_stations, 3, 3))
        
        # Initial frame at start station
        frames[0] = self._get_local_frame(start_station)
        
        for i, station_idx in enumerate(station_range[1:], 1):
            prev_station = station_range[i-1]
            
            # Compute transport from previous station
            prev_frame = frames[i-1]
            
            # Get direction vector between stations
            direction = self._get_station_direction(prev_station, station_idx)
            
            # Apply parallel transport (simplified)
            transported_frame = self._transport_frame(prev_frame, direction)
            frames[i] = transported_frame
        
        return frames
    
    def _get_local_frame(self, station_idx: int) -> np.ndarray:
        """Get local coordinate frame at station (expensive computation)."""
        # Simulate expensive computation that benefits from caching
        if station_idx not in self._frames_cache:
            # Compute tangent, normal, and binormal vectors
            tangent = self._compute_tangent(station_idx)
            normal = self._compute_normal(station_idx)
            binormal = np.cross(tangent, normal)
            
            # Normalize vectors
            tangent = tangent / np.linalg.norm(tangent)
            normal = normal / np.linalg.norm(normal)  
            binormal = binormal / np.linalg.norm(binormal)
            
            frame = np.column_stack([tangent, normal, binormal])
            self._frames_cache[station_idx] = frame
        
        return self._frames_cache[station_idx]
    
    def _compute_tangent(self, station_idx: int) -> np.ndarray:
        """Compute tangent vector at station."""
        if station_idx == 0:
            return self.coordinates[1] - self.coordinates[0]
        elif station_idx == len(self.coordinates) - 1:
            return self.coordinates[-1] - self.coordinates[-2]
        else:
            return self.coordinates[station_idx + 1] - self.coordinates[station_idx - 1]
    
    def _compute_normal(self, station_idx: int) -> np.ndarray:
        """Compute normal vector at station."""
        tangent = self._compute_tangent(station_idx)
        
        # Choose up vector that's not parallel to tangent
        up = np.array([0.0, 0.0, 1.0])
        if abs(np.dot(tangent, up)) > 0.9:
            up = np.array([0.0, 1.0, 0.0])
        
        normal = np.cross(tangent, up)
        return normal
    
    def _get_station_direction(self, station1: int, station2: int) -> np.ndarray:
        """Get direction vector between two stations."""
        return self.coordinates[station2] - self.coordinates[station1]
    
    def _transport_frame(self, frame: np.ndarray, direction: np.ndarray) -> np.ndarray:
        """Transport coordinate frame along direction vector."""
        # Simplified parallel transport
        # In real implementation, this would use Rodrigues' rotation formula
        
        # Normalize direction
        direction = direction / np.linalg.norm(direction)
        
        # Apply small rotation based on direction change
        rotation_angle = np.linalg.norm(direction) * 0.01
        rotation_axis = np.cross(frame[:, 0], direction)
        
        if np.linalg.norm(rotation_axis) > 1e-10:
            rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
            
            # Create rotation matrix (simplified)
            cos_angle = np.cos(rotation_angle)
            sin_angle = np.sin(rotation_angle)
            
            # Rodrigues' formula components
            K = np.array([
                [0, -rotation_axis[2], rotation_axis[1]],
                [rotation_axis[2], 0, -rotation_axis[0]],
                [-rotation_axis[1], rotation_axis[0], 0]
            ])
            
            R = np.eye(3) + sin_angle * K + (1 - cos_angle) * np.dot(K, K)
            return R @ frame
        
        return frame


def create_test_axis(n_stations: int = 200) -> Axis:
    """Create a test axis for benchmarking.
    
    Args:
        n_stations: Number of stations along axis
        
    Returns:
        Test Axis instance
    """
    # Generate curved axis path
    stations = np.linspace(0, 1000, n_stations)  # 1000m long axis
    
    # Create curved path (spiral)
    t = stations / 1000.0  # Normalize to [0, 1]
    x = stations
    y = 50 * np.sin(2 * np.pi * t)  # Sinusoidal curve
    z = 10 * t * t  # Quadratic rise
    
    coordinates = np.column_stack([x, y, z])
    
    return Axis(stations, coordinates)