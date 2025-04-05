"""
Tests for the dimension parser module.
"""
import pytest

from src.logic.dimension_parser import DimensionError, DimensionParser


class TestDimensionParser:
    """
    Tests for the DimensionParser class.
    """

    def test_parse_dimension_valid(self):
        """Test parsing a valid dimension."""
        # Test with valid numeric input
        result = DimensionParser.parse_dimension("100", 200.0, 10.0, 1000.0)
        assert result == 100.0

        # Test with valid numeric input and mm unit
        result = DimensionParser.parse_dimension("100mm", 200.0, 10.0, 1000.0)
        assert result == 100.0

        # Test with valid numeric input and inch unit
        result = DimensionParser.parse_dimension("10in", 200.0, 10.0, 1000.0)
        assert result == 254.0  # 10 inches = 254 mm

        # Test with empty input (should use default)
        result = DimensionParser.parse_dimension("", 200.0, 10.0, 1000.0)
        assert result == 200.0

    def test_parse_dimension_invalid(self):
        """Test parsing an invalid dimension."""
        # Test with non-numeric input
        with pytest.raises(DimensionError):
            DimensionParser.parse_dimension("abc", 200.0, 10.0, 1000.0)

        # Test with value below minimum
        with pytest.raises(DimensionError):
            DimensionParser.parse_dimension("5", 200.0, 10.0, 1000.0)

        # Test with value above maximum
        with pytest.raises(DimensionError):
            DimensionParser.parse_dimension("1500", 200.0, 10.0, 1000.0)

    def test_parse_dimensions_valid(self):
        """Test parsing valid dimensions."""
        dimensions = DimensionParser.parse_dimensions("300", "100", "400", "2")
        assert dimensions["width"] == 300.0
        assert dimensions["height"] == 100.0
        assert dimensions["length"] == 400.0
        assert dimensions["thickness"] == 2.0

    def test_parse_dimensions_invalid(self):
        """Test parsing invalid dimensions."""
        # Test with invalid width
        with pytest.raises(DimensionError):
            DimensionParser.parse_dimensions("abc", "100", "400", "2")

        # Test with invalid height
        with pytest.raises(DimensionError):
            DimensionParser.parse_dimensions("300", "abc", "400", "2")

        # Test with invalid length
        with pytest.raises(DimensionError):
            DimensionParser.parse_dimensions("300", "100", "abc", "2")

        # Test with invalid thickness
        with pytest.raises(DimensionError):
            DimensionParser.parse_dimensions("300", "100", "400", "abc")
