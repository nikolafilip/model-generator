"""
Module for calculating grid layouts and divider positions.
"""
from typing import Dict, List, Optional, Tuple, Union

from src.config.constants import DEFAULT_COLS, DEFAULT_ROWS


class GridError(Exception):
    """Exception raised for errors in the grid configuration."""

    pass


class GridCell:
    """
    Class representing a cell in the grid.
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        length: float,
        height: float,
    ):
        """
        Initialize a grid cell.

        Args:
            x: X-coordinate of the cell (mm).
            y: Y-coordinate of the cell (mm).
            width: Width of the cell (mm).
            length: Length of the cell (mm).
            height: Height of the cell (mm).
        """
        self.x = x
        self.y = y
        self.width = width
        self.length = length
        self.height = height

    def to_dict(self) -> Dict[str, float]:
        """
        Convert the cell to a dictionary.

        Returns:
            Dictionary representation of the cell.
        """
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "length": self.length,
            "height": self.height,
        }


class GridEngine:
    """
    Class for calculating grid layouts and divider positions.
    """

    def __init__(self, width: float, height: float, length: float, 
                 wall_thickness: float, row_percentages: List[float], 
                 col_percentages: List[float], 
                 asymmetric_dividers: List[Dict] = None):
        """
        Initialize the GridEngine with dimensions and grid configuration.
        
        Args:
            width: Width of the drawer (left to right).
            height: Height of the drawer (bottom to top).
            length: Length of the drawer (front to back).
            wall_thickness: Thickness of the divider walls.
            row_percentages: List of row percentages (should sum to 100).
            col_percentages: List of column percentages (should sum to 100).
            asymmetric_dividers: Optional list of asymmetric dividers.
        """
        self.width = width
        self.height = height
        self.length = length
        self.wall_thickness = wall_thickness
        self.row_percentages = row_percentages
        self.col_percentages = col_percentages
        self.asymmetric_dividers = asymmetric_dividers
        
    def calculate_grid_positions(self) -> Tuple[List[float], List[float]]:
        """
        Calculate the actual positions of grid lines.
        
        Returns:
            Tuple containing two lists: row positions and column positions.
        """
        # Calculate row positions (width divisions)
        row_positions = [0]
        current_pos = 0
        for percentage in self.row_percentages:
            current_pos += percentage / 100.0 * self.width
            row_positions.append(current_pos)
            
        # Calculate column positions (length divisions)
        col_positions = [0]
        current_pos = 0
        for percentage in self.col_percentages:
            current_pos += percentage / 100.0 * self.length
            col_positions.append(current_pos)
            
        return row_positions, col_positions
    
    def calculate_divider_positions(self) -> Union[Dict[str, List[Dict[str, float]]], List[Dict[str, float]]]:
        """
        Calculate the positions of horizontal and vertical dividers.
        
        Returns:
            Either a dictionary with 'horizontal' and 'vertical' dividers,
            or a list of divider dictionaries for asymmetric grids.
            Each divider has its position and dimension information.
        """
        # If we have asymmetric dividers, return those directly
        if self.asymmetric_dividers is not None:
            return self.asymmetric_dividers
            
        # Otherwise calculate dividers for a regular grid
        row_positions, col_positions = self.calculate_grid_positions()
        
        # Calculate vertical dividers (along width)
        vertical_dividers = []
        for i in range(1, len(row_positions) - 1):
            vertical_dividers.append({
                'pos': row_positions[i],
                'start': 0,
                'end': self.length,
                'height': self.height
            })
            
        # Calculate horizontal dividers (along length)
        horizontal_dividers = []
        for i in range(1, len(col_positions) - 1):
            horizontal_dividers.append({
                'pos': col_positions[i],
                'start': 0,
                'end': self.width,
                'height': self.height
            })
            
        return {
            'vertical': vertical_dividers,
            'horizontal': horizontal_dividers
        }

    @staticmethod
    def create_regular_grid(
        width: float,
        length: float,
        height: float,
        rows: int = DEFAULT_ROWS,
        cols: int = DEFAULT_COLS,
        thickness: float = 2.0,
    ) -> Tuple[List[GridCell], List[Dict[str, float]]]:
        """
        Create a regular grid with equal-sized cells.

        Args:
            width: Width of the drawer (mm).
            length: Length of the drawer (mm).
            height: Height of the drawer (mm).
            rows: Number of rows in the grid.
            cols: Number of columns in the grid.
            thickness: Thickness of dividers (mm).

        Returns:
            Tuple containing a list of grid cells and a list of divider positions.

        Raises:
            GridError: If the grid configuration is invalid.
        """
        if rows < 1 or cols < 1:
            raise GridError("Number of rows and columns must be at least 1.")

        if rows == 1 and cols == 1:
            # No dividers needed
            cells = [GridCell(0, 0, width, length, height)]
            dividers = []
            return cells, dividers

        # Calculate cell dimensions
        cell_width = (width - (cols - 1) * thickness) / cols
        cell_length = (length - (rows - 1) * thickness) / rows

        if cell_width <= 0 or cell_length <= 0:
            raise GridError(
                "Grid configuration results in cells with non-positive dimensions. "
                "Try reducing the number of rows/columns or increasing the drawer size."
            )

        # Create cells
        cells = []
        for row in range(rows):
            for col in range(cols):
                x = col * (cell_width + thickness)
                y = row * (cell_length + thickness)
                cell = GridCell(x, y, cell_width, cell_length, height)
                cells.append(cell)

        # Calculate divider positions
        dividers = []

        # Vertical dividers (parallel to Y-axis)
        for col in range(1, cols):
            x_pos = col * (cell_width + thickness) - thickness / 2
            divider = {
                "type": "vertical",
                "x": x_pos,
                "y": 0,
                "width": thickness,
                "length": length,
                "height": height,
            }
            dividers.append(divider)

        # Horizontal dividers (parallel to X-axis)
        for row in range(1, rows):
            y_pos = row * (cell_length + thickness) - thickness / 2
            divider = {
                "type": "horizontal",
                "x": 0,
                "y": y_pos,
                "width": width,
                "length": thickness,
                "height": height,
            }
            dividers.append(divider)

        return cells, dividers

    @staticmethod
    def create_custom_grid(
        width: float,
        length: float,
        height: float,
        row_sizes: List[float],
        col_sizes: List[float],
        thickness: float = 2.0,
    ) -> Tuple[List[GridCell], List[Dict[str, float]]]:
        """
        Create a custom grid with cells of specified sizes.

        Args:
            width: Width of the drawer (mm).
            length: Length of the drawer (mm).
            height: Height of the drawer (mm).
            row_sizes: List of row sizes (percentages of total length).
            col_sizes: List of column sizes (percentages of total width).
            thickness: Thickness of dividers (mm).

        Returns:
            Tuple containing a list of grid cells and a list of divider positions.

        Raises:
            GridError: If the grid configuration is invalid.
        """
        # Validate percentages
        if abs(sum(row_sizes) - 100) > 0.01 or abs(sum(col_sizes) - 100) > 0.01:
            raise GridError("Row and column percentages must each sum to 100%.")

        # Convert percentages to actual dimensions
        row_lengths = [length * (r / 100) for r in row_sizes]
        col_widths = [width * (c / 100) for c in col_sizes]

        # Calculate divider positions (starting points for each cell)
        y_positions = [0]
        for row_length in row_lengths[:-1]:  # Exclude the last row
            y_positions.append(y_positions[-1] + row_length)

        x_positions = [0]
        for col_width in col_widths[:-1]:  # Exclude the last column
            x_positions.append(x_positions[-1] + col_width)

        # Create cells
        cells = []
        for row in range(len(row_sizes)):
            for col in range(len(col_sizes)):
                x = x_positions[col]
                y = y_positions[row]
                cell_width = col_widths[col]
                cell_length = row_lengths[row]
                cell = GridCell(x, y, cell_width, cell_length, height)
                cells.append(cell)

        # Calculate divider positions
        dividers = []

        # Vertical dividers (parallel to Y-axis)
        for i in range(1, len(col_sizes)):
            x_pos = x_positions[i]
            divider = {
                "type": "vertical",
                "x": x_pos - thickness / 2,
                "y": 0,
                "width": thickness,
                "length": length,
                "height": height,
            }
            dividers.append(divider)

        # Horizontal dividers (parallel to X-axis)
        for i in range(1, len(row_sizes)):
            y_pos = y_positions[i]
            divider = {
                "type": "horizontal",
                "x": 0,
                "y": y_pos - thickness / 2,
                "width": width,
                "length": thickness,
                "height": height,
            }
            dividers.append(divider)

        return cells, dividers

    @staticmethod
    def create_asymmetric_grid(
        width: float,
        length: float,
        height: float,
        rows_config: List[Dict],
        thickness: float = 2.0,
    ) -> Tuple[List[GridCell], List[Dict[str, float]]]:
        """
        Create an asymmetric grid where each row can have a different height
        and a different number of columns with variable widths.

        Args:
            width: Width of the drawer (mm).
            length: Length of the drawer (mm).
            height: Height of the drawer (mm).
            rows_config: List of row configurations, where each row has:
                - height_percent: The height as a percentage of the total height
                - columns: List of column configurations, where each column has:
                  - width_percent: The width as a percentage of the total width
            thickness: Thickness of dividers (mm).

        Returns:
            Tuple containing a list of grid cells and a list of divider positions.

        Raises:
            GridError: If the grid configuration is invalid.
        """
        from src.logic.asymmetric_grid import AsymmetricGrid
        
        # Create the asymmetric grid handler
        grid = AsymmetricGrid(
            width=width,
            length=length,
            height=height,
            wall_thickness=thickness,
            rows_config=rows_config
        )
        
        # Calculate cells
        cells = grid.calculate_cells()
        
        # Calculate dividers
        horizontal_dividers, vertical_dividers = grid.calculate_divider_positions()
        
        # Get all dividers as a flat list
        all_dividers = horizontal_dividers + vertical_dividers
        
        # Create a GridEngine with the asymmetric dividers
        grid_engine = GridEngine(
            width=width,
            height=height,
            length=length,
            wall_thickness=thickness,
            row_percentages=[100],  # dummy value, not used for asymmetric grids
            col_percentages=[100],  # dummy value, not used for asymmetric grids
            asymmetric_dividers=all_dividers  # pass the asymmetric dividers
        )
        
        # The ModelBuilder will use these dividers directly
        return cells, all_dividers
