"""
Module for parsing and validating drawer dimensions.
"""
from typing import Dict, Optional, Tuple, Union

from src.config.constants import (
    DEFAULT_HEIGHT,
    DEFAULT_LENGTH,
    DEFAULT_WIDTH,
    MM_PER_INCH,
    MAX_HEIGHT,
    MAX_LENGTH,
    MAX_WIDTH,
    MIN_HEIGHT,
    MIN_LENGTH,
    MIN_WIDTH,
    DEFAULT_DIVIDER_THICKNESS,
    MIN_DIVIDER_THICKNESS,
    MAX_DIVIDER_THICKNESS,
)


class DimensionError(Exception):
    """Exception raised for errors in the input dimensions."""

    pass


class DimensionParser:
    """
    Class for parsing and validating drawer dimensions.
    """

    @staticmethod
    def parse_dimension(
        value: str, default: float, min_value: float, max_value: float, unit: str = "mm"
    ) -> float:
        """
        Parse a dimension value from a string input.

        Args:
            value: The input string to parse.
            default: Default value to use if input is empty.
            min_value: Minimum allowed value.
            max_value: Maximum allowed value.
            unit: Unit of measurement ('mm' or 'in').

        Returns:
            The parsed dimension in millimeters.

        Raises:
            DimensionError: If the input is invalid or out of range.
        """
        # If input is empty, use default
        if not value.strip():
            return default

        try:
            # Remove any non-numeric characters except decimal point and minus sign
            # This allows for inputs like "100mm" or "10.5 in"
            numeric_part = ""
            for char in value:
                if char.isdigit() or char == "." or char == "-":
                    numeric_part += char

            # Convert to float
            dimension = float(numeric_part)

            # Convert to mm if in inches
            if "in" in value.lower():
                dimension *= MM_PER_INCH

            # Validate range
            if dimension < min_value:
                raise DimensionError(
                    f"Dimension {dimension:.2f}mm is too small. "
                    f"Minimum value is {min_value:.2f}mm."
                )
            if dimension > max_value:
                raise DimensionError(
                    f"Dimension {dimension:.2f}mm is too large. "
                    f"Maximum value is {max_value:.2f}mm."
                )

            return dimension

        except ValueError:
            raise DimensionError(f"Invalid dimension format: {value}")

    @staticmethod
    def parse_dimensions(
        width: str, height: str, length: str, thickness: str
    ) -> Dict[str, float]:
        """
        Parse and validate all drawer dimensions.

        Args:
            width: Width of the drawer (string input).
            height: Height of the drawer (string input).
            length: Length of the drawer (string input).
            thickness: Thickness of dividers (string input).

        Returns:
            Dictionary containing the parsed dimensions in millimeters.

        Raises:
            DimensionError: If any dimension is invalid or out of range.
        """
        try:
            parsed_width = DimensionParser.parse_dimension(
                width, DEFAULT_WIDTH, MIN_WIDTH, MAX_WIDTH
            )
            parsed_height = DimensionParser.parse_dimension(
                height, DEFAULT_HEIGHT, MIN_HEIGHT, MAX_HEIGHT
            )
            parsed_length = DimensionParser.parse_dimension(
                length, DEFAULT_LENGTH, MIN_LENGTH, MAX_LENGTH
            )
            parsed_thickness = DimensionParser.parse_dimension(
                thickness,
                DEFAULT_DIVIDER_THICKNESS,
                MIN_DIVIDER_THICKNESS,
                MAX_DIVIDER_THICKNESS,
            )

            return {
                "width": parsed_width,
                "height": parsed_height,
                "length": parsed_length,
                "thickness": parsed_thickness,
            }

        except DimensionError as e:
            raise e
        except Exception as e:
            raise DimensionError(f"Error parsing dimensions: {str(e)}")
