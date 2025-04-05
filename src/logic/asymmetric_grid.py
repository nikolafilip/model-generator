"""
Module for handling asymmetric grid layouts where each row can have different heights
and a custom number of columns with variable widths.
"""
from typing import Dict, List, Tuple
from src.logic.grid_engine import GridCell, GridError


class AsymmetricGrid:
    """
    Class for handling asymmetric grid layouts where each row has a custom height
    and a custom set of column widths.
    """

    def __init__(
        self,
        width: float,
        length: float,
        height: float,
        wall_thickness: float,
        rows_config: List[Dict]
    ):
        """
        Initialize an asymmetric grid.

        Args:
            width: Width of the drawer (mm).
            length: Length of the drawer (mm).
            height: Height of the drawer (mm).
            wall_thickness: Thickness of divider walls (mm).
            rows_config: List of row configurations, where each row has:
                - height_percent: The height as a percentage of the total height
                - columns: List of column configurations, where each column has:
                  - width_percent: The width as a percentage of the total width
        
        Raises:
            GridError: If the grid configuration is invalid.
        """
        self.width = width
        self.length = length
        self.height = height
        self.wall_thickness = wall_thickness
        self.rows_config = rows_config
        
        # Validate the configuration
        self._validate_config()
        
    def _validate_config(self):
        """
        Validate the asymmetric grid configuration.
        
        Raises:
            GridError: If the configuration is invalid.
        """
        # Check if we have any rows
        if not self.rows_config:
            raise GridError("Asymmetric grid must have at least one row.")
        
        # Check if row height percentages sum to 100%
        row_heights_sum = sum(row.get('height_percent', 0) for row in self.rows_config)
        if abs(row_heights_sum - 100) > 0.001:  # Allow for small floating-point errors
            raise GridError(f"Row height percentages must sum to 100, got {row_heights_sum}")
        
        # Check each row's columns
        for i, row in enumerate(self.rows_config):
            if 'columns' not in row or not row['columns']:
                raise GridError(f"Row {i+1} must have at least one column.")
            
            # Check if column width percentages sum to 100%
            col_widths_sum = sum(col.get('width_percent', 0) for col in row['columns'])
            if abs(col_widths_sum - 100) > 0.001:  # Allow for small floating-point errors
                raise GridError(f"Column width percentages in row {i+1} must sum to 100, got {col_widths_sum}")
    
    def calculate_row_positions(self) -> List[float]:
        """
        Calculate the positions for each row.
        
        Returns:
            List of y-positions for each row divider.
        """
        positions = [0]  # Start at the front of the drawer
        current_pos = 0
        
        for row in self.rows_config:
            row_height = (row['height_percent'] / 100) * self.length
            current_pos += row_height
            positions.append(current_pos)
            
        return positions
    
    def calculate_column_positions_for_row(self, row_index: int) -> List[float]:
        """
        Calculate the column positions for a specific row.
        
        Args:
            row_index: Index of the row in the rows_config list.
            
        Returns:
            List of x-positions for each column divider in this row.
        """
        if row_index < 0 or row_index >= len(self.rows_config):
            raise GridError(f"Invalid row index: {row_index}")
            
        row_config = self.rows_config[row_index]
        positions = [0]  # Start at the left side of the drawer
        current_pos = 0
        
        for column in row_config['columns']:
            column_width = (column['width_percent'] / 100) * self.width
            current_pos += column_width
            positions.append(current_pos)
            
        return positions
    
    def calculate_cells(self) -> List[GridCell]:
        """
        Calculate all cells in the asymmetric grid.
        
        Returns:
            List of GridCell objects representing each cell in the grid.
        """
        cells = []
        row_positions = self.calculate_row_positions()
        
        for row_idx, row_config in enumerate(self.rows_config):
            row_start = row_positions[row_idx]
            row_end = row_positions[row_idx + 1]
            row_height = row_end - row_start
            
            column_positions = self.calculate_column_positions_for_row(row_idx)
            
            for col_idx in range(len(row_config['columns'])):
                col_start = column_positions[col_idx]
                col_end = column_positions[col_idx + 1]
                col_width = col_end - col_start
                
                cell = GridCell(
                    x=col_start,
                    y=row_start,
                    width=col_width,
                    length=row_height,
                    height=self.height
                )
                cells.append(cell)
                
        return cells
    
    def calculate_divider_positions(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Calculate the positions of all dividers in the asymmetric grid.
        
        Returns:
            Tuple containing:
            - List of horizontal divider positions (as dictionaries)
            - List of vertical divider positions (as dictionaries)
        """
        horizontal_dividers = []
        vertical_dividers = []
        
        # Calculate row (horizontal) dividers
        row_positions = self.calculate_row_positions()
        for i in range(1, len(row_positions) - 1):  # Skip first and last positions (drawer edges)
            divider = {
                "type": "horizontal",
                "x": 0,
                "y": row_positions[i] - self.wall_thickness / 2,
                "width": self.width,
                "length": self.wall_thickness,
                "height": self.height
            }
            horizontal_dividers.append(divider)
        
        # Calculate column (vertical) dividers for each row
        for row_idx, row_config in enumerate(self.rows_config):
            row_start = row_positions[row_idx]
            row_end = row_positions[row_idx + 1]
            
            column_positions = self.calculate_column_positions_for_row(row_idx)
            
            for i in range(1, len(column_positions) - 1):  # Skip first and last positions (drawer edges)
                divider = {
                    "type": "vertical",
                    "x": column_positions[i] - self.wall_thickness / 2,
                    "y": row_start,
                    "width": self.wall_thickness,
                    "length": row_end - row_start, # This is correct - divider only goes from row_start to row_end
                    "height": self.height
                }
                vertical_dividers.append(divider)
        
        return horizontal_dividers, vertical_dividers
    
    def get_all_dividers(self) -> List[Dict]:
        """
        Get a combined list of all dividers.
        
        Returns:
            List of all divider positions (as dictionaries).
        """
        horizontal, vertical = self.calculate_divider_positions()
        return horizontal + vertical 