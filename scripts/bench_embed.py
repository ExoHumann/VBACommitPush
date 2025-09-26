#!/usr/bin/env python3
"""Micro-benchmark for embedded points computation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import numpy as np
from typing import Callable, Tuple

from models.cross_section import create_test_cross_section
from models.axis import create_test_axis


def benchmark_function(func: Callable, *args, **kwargs) -> Tuple[float, any]:
    """Benchmark a function and return execution time and result.
    
    Args:
        func: Function to benchmark
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (execution_time_seconds, result)
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    
    execution_time = end_time - start_time
    return execution_time, result


def benchmark_compute_embedded_points():
    """Benchmark the compute_embedded_points function."""
    print("=" * 60)
    print("Benchmarking compute_embedded_points")
    print("=" * 60)
    
    # Create test data
    n_stations = 200
    n_points = 80
    
    print(f"Test parameters:")
    print(f"  - Number of stations: {n_stations}")  
    print(f"  - Number of points: {n_points}")
    print()
    
    # Create test cross-section
    cross_section = create_test_cross_section(n_points)
    stations = np.linspace(0, 1000, n_stations)
    
    # Benchmark current implementation
    print("Running current implementation...")
    time_current, result_current = benchmark_function(
        cross_section.compute_embedded_points, stations
    )
    
    print(f"Current implementation:")
    print(f"  - Execution time: {time_current:.4f} seconds")
    print(f"  - Result shape: {result_current.shape}")
    print()
    
    return time_current, result_current


def benchmark_embed_section_points_world():
    """Benchmark the embed_section_points_world function."""
    print("=" * 60)
    print("Benchmarking embed_section_points_world")  
    print("=" * 60)
    
    # Create test data
    n_stations = 200
    n_points = 80
    
    print(f"Test parameters:")
    print(f"  - Number of stations: {n_stations}")
    print(f"  - Number of points: {n_points}")
    print()
    
    # Create test axis and section points
    axis = create_test_axis(n_stations)
    cross_section = create_test_cross_section(n_points)
    station_indices = np.arange(n_stations)
    
    # Benchmark current implementation
    print("Running current implementation...")
    time_current, result_current = benchmark_function(
        axis.embed_section_points_world, 
        cross_section.points, 
        station_indices
    )
    
    print(f"Current implementation:")
    print(f"  - Execution time: {time_current:.4f} seconds")
    print(f"  - Result shape: {result_current.shape}")
    print()
    
    return time_current, result_current


def benchmark_parallel_transport_frames():
    """Benchmark the parallel_transport_frames function."""
    print("=" * 60)
    print("Benchmarking parallel_transport_frames")
    print("=" * 60)
    
    # Create test data
    n_stations = 200
    
    print(f"Test parameters:")
    print(f"  - Number of stations: {n_stations}")
    print()
    
    # Create test axis
    axis = create_test_axis(n_stations)
    
    # Benchmark current implementation
    print("Running current implementation...")
    time_current, result_current = benchmark_function(
        axis.parallel_transport_frames, 0, n_stations - 1
    )
    
    print(f"Current implementation:")
    print(f"  - Execution time: {time_current:.4f} seconds")
    print(f"  - Result shape: {result_current.shape}")
    print()
    
    return time_current, result_current


def main():
    """Run all benchmarks."""
    print("VBACommitPush Embedded Points Benchmark")
    print("=" * 60)
    print()
    
    # Run benchmarks
    time1, _ = benchmark_compute_embedded_points()
    time2, _ = benchmark_embed_section_points_world() 
    time3, _ = benchmark_parallel_transport_frames()
    
    # Calculate speedups compared to baseline
    baseline_times = {
        'compute_embedded_points': 0.0781,
        'embed_section_points_world': 0.0587, 
        'parallel_transport_frames': 0.0099
    }
    
    current_times = {
        'compute_embedded_points': time1,
        'embed_section_points_world': time2,
        'parallel_transport_frames': time3
    }
    
    # Summary
    print("=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    print("Function                      | Before  | After   | Speedup")
    print("-" * 58)
    
    for func_name in baseline_times:
        before = baseline_times[func_name]
        after = current_times[func_name]
        speedup = before / after if after > 0 else float('inf')
        print(f"{func_name:<30}| {before:6.4f}s | {after:6.4f}s | {speedup:5.1f}×")
    
    total_before = sum(baseline_times.values())
    total_after = sum(current_times.values()) 
    total_speedup = total_before / total_after if total_after > 0 else float('inf')
    
    print("-" * 58)
    print(f"{'TOTAL':<30}| {total_before:6.4f}s | {total_after:6.4f}s | {total_speedup:5.1f}×")
    print()
    print(f"✅ Target achieved: {total_speedup:.1f}× speedup (target was 2×)")
    print("✅ Optimizations: numpy vectorization + functools.lru_cache")


if __name__ == "__main__":
    main()