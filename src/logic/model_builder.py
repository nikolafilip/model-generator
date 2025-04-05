"""
Module for building 3D models of drawer dividers using SolidPython/OpenSCAD.
"""
import os
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from solid import scad_render_to_file
from solid.objects import cube, translate, union, difference

from src.config.constants import DEFAULT_STL_RESOLUTION, STL_RESOLUTION_VALUES
from src.logic.grid_engine import GridEngine


class ModelError(Exception):
    """Exception raised for errors in the model building process."""

    pass


class ModelBuilder:
    """
    Class for building 3D models of drawer dividers.
    """

    def __init__(self, grid_engine: GridEngine):
        """
        Initialize the ModelBuilder with a GridEngine.
        
        Args:
            grid_engine: GridEngine with grid layout configuration.
        """
        self.grid_engine = grid_engine

    @staticmethod
    def _create_box(width: float, length: float, height: float) -> object:
        """
        Create a 3D box using SolidPython.

        Args:
            width: Width of the box (mm).
            length: Length of the box (mm).
            height: Height of the box (mm).

        Returns:
            SolidPython object representing the box.
        """
        return cube([width, length, height])

    @staticmethod
    def _create_divider(
        x: float, y: float, width: float, length: float, height: float
    ) -> object:
        """
        Create a divider using SolidPython.

        Args:
            x: X-coordinate of the divider (mm).
            y: Y-coordinate of the divider (mm).
            width: Width of the divider (mm).
            length: Length of the divider (mm).
            height: Height of the divider (mm).

        Returns:
            SolidPython object representing the divider.
        """
        return translate([x, y, 0])(cube([width, length, height]))

    @staticmethod
    def create_drawer_with_dividers(
        width: float,
        length: float,
        height: float,
        dividers: List[Dict[str, float]],
        wall_thickness: float = 2.0,
        bottom_thickness: float = 2.0,
        with_floor: bool = True,
    ) -> object:
        """
        Create a drawer with dividers using SolidPython.

        Args:
            width: Width of the drawer (mm).
            length: Length of the drawer (mm).
            height: Height of the drawer (mm).
            dividers: List of divider positions and dimensions.
            wall_thickness: Thickness of drawer walls (mm).
            bottom_thickness: Thickness of drawer bottom (mm).
            with_floor: Whether to include a floor in the model.

        Returns:
            SolidPython object representing the drawer with dividers.
        """
        # Create the outer walls
        left_wall = translate([0, 0, 0])(
            cube([wall_thickness, length, height])
        )
        right_wall = translate([width - wall_thickness, 0, 0])(
            cube([wall_thickness, length, height])
        )
        front_wall = translate([0, 0, 0])(
            cube([width, wall_thickness, height])
        )
        back_wall = translate([0, length - wall_thickness, 0])(
            cube([width, wall_thickness, height])
        )

        # Create the floor if requested
        floor = None
        if with_floor:
            floor = translate([0, 0, 0])(
                cube([width, length, bottom_thickness])
            )

        # Build the basic structure
        model_parts = [left_wall, right_wall, front_wall, back_wall]
        if floor:
            model_parts.append(floor)

        # Add the dividers
        for div in dividers:
            divider = ModelBuilder._create_divider(
                div["x"],
                div["y"],
                div["width"],
                div["length"],
                div["height"],
            )
            model_parts.append(divider)

        # Combine all parts
        return union()(*model_parts)

    def create_divider_only_model(self, with_frame: bool = True, with_floor: bool = True, floor_thickness: float = 2.0):
        """
        Create a 3D model for just the dividers.
        
        Args:
            with_frame: Whether to include a frame around the dividers.
            with_floor: Whether to include a floor for the dividers.
            floor_thickness: Thickness of the floor (if included).
            
        Returns:
            A solid-python model object.
        """
        try:
            # Try to get dividers using the standard method (dictionary with 'vertical' and 'horizontal' keys)
            dividers = self.grid_engine.calculate_divider_positions()
            
            width = self.grid_engine.width
            length = self.grid_engine.length
            height = self.grid_engine.height
            wall_thickness = self.grid_engine.wall_thickness
            
            # Parts to be combined
            parts = []
            
            # Process dividers based on format (handle both standard and asymmetric grids)
            if isinstance(dividers, dict) and 'vertical' in dividers and 'horizontal' in dividers:
                # Standard grid format
                # Add vertical dividers
                for divider in dividers['vertical']:
                    pos = divider['pos']
                    start = divider['start']
                    end = divider['end']
                    div_height = divider['height']
                    
                    # Create the vertical divider
                    divider_obj = cube([wall_thickness, end - start, div_height])
                    divider_obj = translate([pos - wall_thickness / 2, start, 0])(divider_obj)
                    parts.append(divider_obj)
                    
                # Add horizontal dividers
                for divider in dividers['horizontal']:
                    pos = divider['pos']
                    start = divider['start']
                    end = divider['end']
                    div_height = divider['height']
                    
                    # Create the horizontal divider
                    divider_obj = cube([end - start, wall_thickness, div_height])
                    divider_obj = translate([start, pos - wall_thickness / 2, 0])(divider_obj)
                    parts.append(divider_obj)
            else:
                # This must be a list of dividers (e.g., from asymmetric grid)
                # Process all dividers based on their type
                for divider in dividers:
                    if divider['type'] == 'vertical':
                        # Vertical divider
                        divider_obj = cube([divider['width'], divider['length'], divider['height']])
                        divider_obj = translate([divider['x'], divider['y'], 0])(divider_obj)
                        parts.append(divider_obj)
                    elif divider['type'] == 'horizontal':
                        # Horizontal divider
                        divider_obj = cube([divider['width'], divider['length'], divider['height']])
                        divider_obj = translate([divider['x'], divider['y'], 0])(divider_obj)
                        parts.append(divider_obj)
            
            # Add frame if requested
            if with_frame:
                # Front edge
                front = cube([width, wall_thickness, height])
                front = translate([0, 0, 0])(front)
                parts.append(front)
                
                # Back edge
                back = cube([width, wall_thickness, height])
                back = translate([0, length - wall_thickness, 0])(back)
                parts.append(back)
                
                # Left edge
                left = cube([wall_thickness, length, height])
                left = translate([0, 0, 0])(left)
                parts.append(left)
                
                # Right edge
                right = cube([wall_thickness, length, height])
                right = translate([width - wall_thickness, 0, 0])(right)
                parts.append(right)
                
            # Add floor if requested
            if with_floor:
                floor = cube([width, length, floor_thickness])
                floor = translate([0, 0, 0])(floor)
                parts.append(floor)
                
            # Combine all parts
            return union()(*parts)
        except Exception as e:
            import traceback
            print(f"Error creating divider model: {str(e)}")
            traceback.print_exc()
            raise
        
    def create_complete_drawer_model(self, with_frame: bool = True, with_floor: bool = True):
        """
        Create a 3D model for a complete drawer with dividers.
        
        Args:
            with_frame: Whether to include a frame around the dividers.
            with_floor: Whether to include a floor for the drawer.
            
        Returns:
            A solid-python model object.
        """
        # Get the divider model
        divider_model = self.create_divider_only_model(with_frame=with_frame, with_floor=with_floor)
        
        # Create the outer shell
        width = self.grid_engine.width
        length = self.grid_engine.length
        height = self.grid_engine.height
        wall_thickness = self.grid_engine.wall_thickness
        
        # Outer shell dimensions (including walls)
        outer_width = width + 2 * wall_thickness
        outer_length = length + 2 * wall_thickness
        outer_height = height + (wall_thickness if with_floor else 0)
        
        # Create the outer shell
        outer_shell = cube([outer_width, outer_length, outer_height])
        
        # Create the inner cavity
        inner_shell = cube([width, length, height])
        inner_shell = translate([wall_thickness, wall_thickness, with_floor and wall_thickness])(inner_shell)
        
        # Subtract inner from outer to create the shell
        drawer_shell = difference()(outer_shell, inner_shell)
        
        # Position the dividers inside the drawer
        positioned_dividers = translate([wall_thickness, wall_thickness, with_floor and wall_thickness])(divider_model)
        
        # Combine the shell and dividers
        return union()(drawer_shell, positioned_dividers)

    @staticmethod
    def render_to_file(
        model: object,
        filepath: str,
        resolution: str = DEFAULT_STL_RESOLUTION,
    ) -> str:
        """
        Render the model to an OpenSCAD file.

        Args:
            model: SolidPython object to render.
            filepath: Path to save the rendered file.
            resolution: Resolution of the STL file ('low', 'normal', 'high').

        Returns:
            Path to the rendered OpenSCAD file.

        Raises:
            ModelError: If the file cannot be written.
        """
        try:
            # Get the resolution value
            if resolution not in STL_RESOLUTION_VALUES:
                resolution = DEFAULT_STL_RESOLUTION
            fs_value = STL_RESOLUTION_VALUES[resolution]

            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            # Add a $fs parameter for controlling the resolution
            scad_header = f"$fs = {fs_value};\n"

            # Render the model to a file
            scad_render_to_file(
                model, filepath, file_header=scad_header, include_orig_code=False
            )

            return filepath
        except Exception as e:
            raise ModelError(f"Error rendering model to file: {str(e)}")

    @staticmethod
    def generate_model(
        dimensions: Dict[str, float],
        dividers: List[Dict[str, float]],
        model_type: str = "dividers_only",
        with_frame: bool = True,
        with_floor: bool = True,
    ) -> object:
        """
        Generate a 3D model based on the provided dimensions and dividers.

        Args:
            dimensions: Dictionary containing drawer dimensions (width, length, height, thickness).
            dividers: List of divider positions and dimensions.
            model_type: Type of model to generate ('complete_drawer' or 'dividers_only').
            with_frame: Whether to include a frame around the dividers (for 'dividers_only').
            with_floor: Whether to include a floor (defaults to True for both model types).

        Returns:
            SolidPython object representing the generated model.

        Raises:
            ModelError: If the model type is invalid.
        """
        width = dimensions["width"]
        length = dimensions["length"]
        height = dimensions["height"]
        thickness = dimensions["thickness"]

        if model_type == "complete_drawer":
            return ModelBuilder.create_drawer_with_dividers(
                width,
                length,
                height,
                dividers,
                wall_thickness=thickness,
                bottom_thickness=thickness,
                with_floor=with_floor,
            )
        elif model_type == "dividers_only":
            return ModelBuilder.create_divider_only_model(
                width,
                length,
                height,
                dividers,
                with_frame=with_frame,
                wall_thickness=thickness,
                with_floor=with_floor,
                floor_thickness=thickness,
            )
        else:
            raise ModelError(f"Invalid model type: {model_type}")
