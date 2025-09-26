"""Visualization and plotting utilities."""
import logging
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


logger = logging.getLogger(__name__)


class BridgePlotter:
    """Handles plotting and visualization of bridge geometry."""
    
    def __init__(self, figsize: Tuple[float, float] = (12, 8), dpi: int = 100):
        """Initialize plotter with configuration.
        
        Args:
            figsize: Figure size (width, height) in inches
            dpi: Dots per inch for figure resolution
        """
        self.figsize = figsize
        self.dpi = dpi
        self.current_fig = None
        self.current_ax = None
    
    def plot_cross_section_points(self, points_data: Dict[str, Any], 
                                 title: Optional[str] = None,
                                 show_labels: bool = True) -> None:
        """Plot cross-section points.
        
        Args:
            points_data: Dictionary containing points data from GeometryProcessor
            title: Optional title for the plot
            show_labels: Whether to show point name labels
        """
        self._setup_figure(title or f"Cross Section: {points_data.get('section_name', 'Unknown')}")
        
        points = points_data.get('points', [])
        if not points:
            logger.warning("No points to plot")
            self.current_ax.text(0.5, 0.5, 'No points to display', 
                               horizontalalignment='center', transform=self.current_ax.transAxes)
            return
        
        # Extract coordinates
        y_coords = [p['coord_y'] for p in points]
        z_coords = [p['coord_z'] for p in points]
        point_names = [str(p['point_name']) for p in points]
        
        # Plot points
        scatter = self.current_ax.scatter(y_coords, z_coords, c='blue', s=50, alpha=0.7)
        
        # Add labels if requested
        if show_labels:
            for i, name in enumerate(point_names):
                self.current_ax.annotate(name, (y_coords[i], z_coords[i]), 
                                       xytext=(5, 5), textcoords='offset points',
                                       fontsize=8, alpha=0.8)
        
        # Set labels and grid
        self.current_ax.set_xlabel('Y Coordinate (mm)')
        self.current_ax.set_ylabel('Z Coordinate (mm)')
        self.current_ax.grid(True, alpha=0.3)
        self.current_ax.set_aspect('equal', adjustable='box')
        
        logger.info(f"Plotted {len(points)} points for section {points_data.get('section_name')}")
    
    def plot_axis_frames(self, axis_frames: List[Dict[str, Any]], 
                        title: Optional[str] = None) -> None:
        """Plot axis frames along the bridge.
        
        Args:
            axis_frames: List of axis frame data
            title: Optional title for the plot
        """
        self._setup_figure(title or "Axis Frames")
        
        if not axis_frames:
            logger.warning("No axis frames to plot")
            self.current_ax.text(0.5, 0.5, 'No axis frames to display', 
                               horizontalalignment='center', transform=self.current_ax.transAxes)
            return
        
        # Extract data
        stations = [frame.get('station', 0) for frame in axis_frames]
        names = [frame.get('name', '') for frame in axis_frames]
        axes = [frame.get('axis', '') for frame in axis_frames]
        
        # Create bar plot
        y_pos = np.arange(len(names))
        bars = self.current_ax.barh(y_pos, stations, alpha=0.7)
        
        # Customize plot
        self.current_ax.set_yticks(y_pos)
        self.current_ax.set_yticklabels(names, fontsize=8)
        self.current_ax.set_xlabel('Station')
        self.current_ax.set_ylabel('Frame Name')
        
        # Add value labels on bars
        for i, (bar, station) in enumerate(zip(bars, stations)):
            self.current_ax.text(bar.get_width() + max(stations) * 0.01, 
                               bar.get_y() + bar.get_height()/2,
                               f'{station:.1f}', 
                               va='center', fontsize=8, alpha=0.8)
        
        self.current_ax.grid(True, alpha=0.3, axis='x')
        
        logger.info(f"Plotted {len(axis_frames)} axis frames")
    
    def compare_coordinate_systems(self, local_data: Dict[str, Any], 
                                 world_data: Dict[str, Any],
                                 title: Optional[str] = None) -> None:
        """Compare local vs world coordinate systems.
        
        Args:
            local_data: Local coordinate system points
            world_data: World coordinate system points  
            title: Optional title for the plot
        """
        section_name = local_data.get('section_name', 'Unknown')
        self._setup_figure(title or f"Coordinate Systems Comparison: {section_name}")
        
        local_points = local_data.get('points', [])
        world_points = world_data.get('points', [])
        
        if not local_points or not world_points:
            logger.warning("Missing coordinate data for comparison")
            return
        
        # Extract coordinates
        local_y = [p['coord_y'] for p in local_points]
        local_z = [p['coord_z'] for p in local_points]
        world_y = [p['coord_y'] for p in world_points]
        world_z = [p['coord_z'] for p in world_points]
        
        # Plot both coordinate systems
        self.current_ax.scatter(local_y, local_z, c='blue', s=50, alpha=0.7, 
                              label='Local Coordinates')
        self.current_ax.scatter(world_y, world_z, c='red', s=50, alpha=0.7, 
                              label='World Coordinates')
        
        # Add connecting lines to show transformation
        for i in range(min(len(local_points), len(world_points))):
            self.current_ax.plot([local_y[i], world_y[i]], [local_z[i], world_z[i]], 
                               'gray', alpha=0.3, linewidth=1)
        
        # Customize plot
        self.current_ax.set_xlabel('Y Coordinate (mm)')
        self.current_ax.set_ylabel('Z Coordinate (mm)')
        self.current_ax.legend()
        self.current_ax.grid(True, alpha=0.3)
        self.current_ax.set_aspect('equal', adjustable='box')
        
        logger.info(f"Compared coordinate systems for {len(local_points)} points")
    
    def save_plot(self, filename: str, output_dir: Optional[Path] = None) -> Path:
        """Save the current plot to file.
        
        Args:
            filename: Name of the output file (with or without extension)
            output_dir: Directory to save to. Defaults to current directory.
            
        Returns:
            Path to saved file
        """
        if self.current_fig is None:
            raise ValueError("No active plot to save")
        
        output_dir = output_dir or Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure .png extension
        if not filename.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf')):
            filename += '.png'
        
        output_path = output_dir / filename
        self.current_fig.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        
        logger.info(f"Plot saved to: {output_path}")
        return output_path
    
    def show_plot(self) -> None:
        """Display the current plot."""
        if self.current_fig is not None:
            plt.show()
        else:
            logger.warning("No active plot to display")
    
    def close_plot(self) -> None:
        """Close the current plot and clean up."""
        if self.current_fig is not None:
            plt.close(self.current_fig)
            self.current_fig = None
            self.current_ax = None
    
    def _setup_figure(self, title: str) -> None:
        """Setup a new figure for plotting.
        
        Args:
            title: Title for the plot
        """
        if self.current_fig is not None:
            self.close_plot()
        
        self.current_fig, self.current_ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set style
        plt.style.use('default')
        
        logger.debug(f"Created new figure: {title}")