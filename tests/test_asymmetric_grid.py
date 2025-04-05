"""
Test module for asymmetric grid functionality.
"""
import unittest
from src.logic.asymmetric_grid import AsymmetricGrid
from src.logic.grid_engine import GridError


class TestAsymmetricGrid(unittest.TestCase):
    """Test cases for the AsymmetricGrid class."""

    def test_valid_config(self):
        """Test that a valid configuration is accepted."""
        # Valid configuration with 2 rows and variable columns
        config = [
            {
                "height_percent": 60.0,
                "columns": [
                    {"width_percent": 30.0},
                    {"width_percent": 70.0}
                ]
            },
            {
                "height_percent": 40.0,
                "columns": [
                    {"width_percent": 50.0},
                    {"width_percent": 30.0},
                    {"width_percent": 20.0}
                ]
            }
        ]
        
        grid = AsymmetricGrid(
            width=200.0,
            length=300.0,
            height=100.0,
            wall_thickness=2.0,
            rows_config=config
        )
        
        # Check that initialization completes without errors
        self.assertIsNotNone(grid)
        
        # Check the row positions calculation
        row_positions = grid.calculate_row_positions()
        self.assertEqual(len(row_positions), 3)  # Start, middle, end
        self.assertEqual(row_positions[0], 0)
        self.assertAlmostEqual(row_positions[1], 180.0)  # 60% of 300
        self.assertEqual(row_positions[2], 300.0)
        
        # Check column positions for row 0
        col_positions_row0 = grid.calculate_column_positions_for_row(0)
        self.assertEqual(len(col_positions_row0), 3)  # Start, middle, end
        self.assertEqual(col_positions_row0[0], 0)
        self.assertAlmostEqual(col_positions_row0[1], 60.0)  # 30% of 200
        self.assertEqual(col_positions_row0[2], 200.0)
        
        # Check column positions for row 1
        col_positions_row1 = grid.calculate_column_positions_for_row(1)
        self.assertEqual(len(col_positions_row1), 4)  # Start, 3 dividers, end
        self.assertEqual(col_positions_row1[0], 0)
        self.assertAlmostEqual(col_positions_row1[1], 100.0)  # 50% of 200
        self.assertAlmostEqual(col_positions_row1[2], 160.0)  # +30% of 200
        self.assertEqual(col_positions_row1[3], 200.0)
    
    def test_invalid_height_percentage(self):
        """Test that row heights not summing to 100% raises an error."""
        # Invalid configuration with row heights summing to more than 100%
        config = [
            {
                "height_percent": 60.0,
                "columns": [{"width_percent": 100.0}]
            },
            {
                "height_percent": 50.0,  # Sum is 110%
                "columns": [{"width_percent": 100.0}]
            }
        ]
        
        with self.assertRaises(GridError):
            AsymmetricGrid(
                width=200.0,
                length=300.0,
                height=100.0,
                wall_thickness=2.0,
                rows_config=config
            )
    
    def test_invalid_width_percentage(self):
        """Test that column widths not summing to 100% raises an error."""
        # Invalid configuration with column widths summing to less than 100%
        config = [
            {
                "height_percent": 100.0,
                "columns": [
                    {"width_percent": 50.0},
                    {"width_percent": 40.0}  # Sum is 90%
                ]
            }
        ]
        
        with self.assertRaises(GridError):
            AsymmetricGrid(
                width=200.0,
                length=300.0,
                height=100.0,
                wall_thickness=2.0,
                rows_config=config
            )
    
    def test_empty_rows(self):
        """Test that empty rows_config raises an error."""
        with self.assertRaises(GridError):
            AsymmetricGrid(
                width=200.0,
                length=300.0,
                height=100.0,
                wall_thickness=2.0,
                rows_config=[]
            )
    
    def test_invalid_row_index(self):
        """Test that requesting column positions for an invalid row index raises an error."""
        config = [
            {
                "height_percent": 100.0,
                "columns": [{"width_percent": 100.0}]
            }
        ]
        
        grid = AsymmetricGrid(
            width=200.0,
            length=300.0,
            height=100.0,
            wall_thickness=2.0,
            rows_config=config
        )
        
        with self.assertRaises(GridError):
            grid.calculate_column_positions_for_row(1)  # Only row 0 exists
    
    def test_cells_calculation(self):
        """Test calculating cells for an asymmetric grid."""
        config = [
            {
                "height_percent": 50.0,
                "columns": [
                    {"width_percent": 50.0},
                    {"width_percent": 50.0}
                ]
            },
            {
                "height_percent": 50.0,
                "columns": [
                    {"width_percent": 100.0}
                ]
            }
        ]
        
        grid = AsymmetricGrid(
            width=200.0,
            length=300.0,
            height=100.0,
            wall_thickness=2.0,
            rows_config=config
        )
        
        cells = grid.calculate_cells()
        self.assertEqual(len(cells), 3)  # 2 cells in row 1, 1 cell in row 2
        
        # Check cell dimensions and positions
        # First row, first cell
        self.assertEqual(cells[0].x, 0)
        self.assertEqual(cells[0].y, 0)
        self.assertEqual(cells[0].width, 100.0)
        self.assertEqual(cells[0].length, 150.0)
        
        # First row, second cell
        self.assertEqual(cells[1].x, 100.0)
        self.assertEqual(cells[1].y, 0)
        self.assertEqual(cells[1].width, 100.0)
        self.assertEqual(cells[1].length, 150.0)
        
        # Second row, single cell
        self.assertEqual(cells[2].x, 0)
        self.assertEqual(cells[2].y, 150.0)
        self.assertEqual(cells[2].width, 200.0)
        self.assertEqual(cells[2].length, 150.0)
    
    def test_divider_positions(self):
        """Test calculating divider positions for an asymmetric grid."""
        config = [
            {
                "height_percent": 50.0,
                "columns": [
                    {"width_percent": 50.0},
                    {"width_percent": 50.0}
                ]
            },
            {
                "height_percent": 50.0,
                "columns": [
                    {"width_percent": 100.0}
                ]
            }
        ]
        
        grid = AsymmetricGrid(
            width=200.0,
            length=300.0,
            height=100.0,
            wall_thickness=2.0,
            rows_config=config
        )
        
        horizontal, vertical = grid.calculate_divider_positions()
        
        # Should have 1 horizontal divider (between rows)
        self.assertEqual(len(horizontal), 1)
        self.assertEqual(horizontal[0]["type"], "horizontal")
        self.assertAlmostEqual(horizontal[0]["y"], 150.0 - 1.0)  # y - thickness/2
        
        # Should have 1 vertical divider (in the first row only)
        self.assertEqual(len(vertical), 1)
        self.assertEqual(vertical[0]["type"], "vertical")
        self.assertAlmostEqual(vertical[0]["x"], 100.0 - 1.0)  # x - thickness/2
        self.assertEqual(vertical[0]["y"], 0)
        self.assertEqual(vertical[0]["length"], 150.0)  # height of first row
        
        # Check combined list
        all_dividers = grid.get_all_dividers()
        self.assertEqual(len(all_dividers), 2)  # 1 horizontal + 1 vertical
        
        
if __name__ == "__main__":
    unittest.main() 