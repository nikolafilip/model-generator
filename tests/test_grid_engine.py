"""
Tests for the grid engine module.
"""
import pytest

from src.logic.grid_engine import GridCell, GridEngine, GridError


class TestGridEngine:
    """
    Tests for the GridEngine class.
    """

    def test_create_regular_grid_valid(self):
        """Test creating a valid regular grid."""
        # Test with 2x2 grid
        cells, dividers = GridEngine.create_regular_grid(
            width=300.0, length=400.0, height=100.0, rows=2, cols=2, thickness=2.0
        )

        # Check cells
        assert len(cells) == 4  # 2x2 = 4 cells
        
        # Check cell dimensions
        # Each cell should be (300 - 2) / 2 = 149 wide and (400 - 2) / 2 = 199 long
        assert cells[0].width == pytest.approx(149.0)
        assert cells[0].length == pytest.approx(199.0)
        assert cells[0].height == 100.0
        
        # Check dividers
        assert len(dividers) == 2  # 1 vertical + 1 horizontal = 2 dividers
        
        # Check if there's a vertical divider
        assert any(d["type"] == "vertical" for d in dividers)
        # Check if there's a horizontal divider
        assert any(d["type"] == "horizontal" for d in dividers)

    def test_create_regular_grid_invalid(self):
        """Test creating an invalid regular grid."""
        # Test with invalid row count
        with pytest.raises(GridError):
            GridEngine.create_regular_grid(
                width=300.0, length=400.0, height=100.0, rows=0, cols=2, thickness=2.0
            )

        # Test with invalid column count
        with pytest.raises(GridError):
            GridEngine.create_regular_grid(
                width=300.0, length=400.0, height=100.0, rows=2, cols=0, thickness=2.0
            )

        # Test with too many rows/columns for the given space
        with pytest.raises(GridError):
            GridEngine.create_regular_grid(
                width=10.0, length=10.0, height=100.0, rows=100, cols=100, thickness=2.0
            )

    def test_create_custom_grid_valid(self):
        """Test creating a valid custom grid."""
        row_sizes = [30.0, 70.0]  # 30% and 70% of length
        col_sizes = [40.0, 60.0]  # 40% and 60% of width
        
        cells, dividers = GridEngine.create_custom_grid(
            width=300.0,
            length=400.0,
            height=100.0,
            row_sizes=row_sizes,
            col_sizes=col_sizes,
            thickness=2.0,
        )
        
        # Check cells
        assert len(cells) == 4  # 2x2 = 4 cells
        
        # Check dividers
        assert len(dividers) == 2  # 1 vertical + 1 horizontal = 2 dividers
        
        # Get the first row cells
        first_row_cells = [cells[0], cells[1]]
        
        # Get the first column cells
        first_col_cells = [cells[0], cells[2]]
        
        # Check that the first row cells have the same length but different widths
        assert first_row_cells[0].length == first_row_cells[1].length
        assert first_row_cells[0].width != first_row_cells[1].width
        
        # Check that the first column cells have the same width but different lengths
        assert first_col_cells[0].width == first_col_cells[1].width
        assert first_col_cells[0].length != first_col_cells[1].length

    def test_create_custom_grid_invalid(self):
        """Test creating an invalid custom grid."""
        # Test with empty row sizes
        with pytest.raises(GridError):
            GridEngine.create_custom_grid(
                width=300.0,
                length=400.0,
                height=100.0,
                row_sizes=[],
                col_sizes=[50.0, 50.0],
                thickness=2.0,
            )

        # Test with empty column sizes
        with pytest.raises(GridError):
            GridEngine.create_custom_grid(
                width=300.0,
                length=400.0,
                height=100.0,
                row_sizes=[50.0, 50.0],
                col_sizes=[],
                thickness=2.0,
            )

        # Test with row percentages that don't sum to 100
        with pytest.raises(GridError):
            GridEngine.create_custom_grid(
                width=300.0,
                length=400.0,
                height=100.0,
                row_sizes=[20.0, 30.0],  # 50% total
                col_sizes=[50.0, 50.0],
                thickness=2.0,
            )

        # Test with column percentages that don't sum to 100
        with pytest.raises(GridError):
            GridEngine.create_custom_grid(
                width=300.0,
                length=400.0,
                height=100.0,
                row_sizes=[50.0, 50.0],
                col_sizes=[60.0, 60.0],  # 120% total
                thickness=2.0,
            )
