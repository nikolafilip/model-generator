"""Constants and configuration parameters for the 3D Divider Generator."""
from typing import Dict, List, Tuple, Union

# Unit conversion constants
MM_PER_INCH = 25.4

# Default dimensions in mm
DEFAULT_WIDTH = 300.0  # mm
DEFAULT_HEIGHT = 100.0  # mm
DEFAULT_LENGTH = 400.0  # mm

# Minimum dimensions in mm
MIN_WIDTH = 50.0  # mm
MIN_HEIGHT = 20.0  # mm
MIN_LENGTH = 50.0  # mm

# Maximum dimensions in mm
MAX_WIDTH = 1000.0  # mm
MAX_HEIGHT = 500.0  # mm
MAX_LENGTH = 1000.0  # mm

# Divider thickness
DEFAULT_DIVIDER_THICKNESS = 2.0  # mm
DEFAULT_WALL_THICKNESS = 2.0  # mm (alias for DEFAULT_DIVIDER_THICKNESS)
MIN_DIVIDER_THICKNESS = 1.0  # mm
MAX_DIVIDER_THICKNESS = 5.0  # mm

# Default grid layout
DEFAULT_ROWS = 2
DEFAULT_COLS = 2

# Asymmetric grid defaults
DEFAULT_ASYMMETRIC_ROWS = 2
DEFAULT_ASYMMETRIC_ROW_HEIGHT = 50.0  # Percentage (%)
DEFAULT_ASYMMETRIC_COLS = 1
DEFAULT_ASYMMETRIC_COL_WIDTH = 100.0  # Percentage (%)

# Preset grid layouts
PRESET_GRIDS: Dict[str, Tuple[int, int]] = {
    "2×2": (2, 2),
    "2×3": (2, 3),
    "3×2": (3, 2),
    "3×3": (3, 3),
    "3×4": (3, 4),
    "4×3": (4, 3),
    "4×4": (4, 4),
}

# Grid types
GRID_TYPES = [
    "none",         # No dividers
    "preset",       # Equal divisions with presets
    "custom",       # Custom grid with percentage-based sizing
    "asymmetric"    # Asymmetric grid with variable rows and columns
]

# File export settings
DEFAULT_STL_RESOLUTION = "normal"  # Options: "low", "normal", "high"
STL_RESOLUTION_VALUES: Dict[str, float] = {
    "low": 10.0,     # Lower is less detailed but faster to generate and slice
    "normal": 5.0,   # Good balance of detail and file size
    "high": 2.0,     # More detailed but larger files and slower to generate
}

# UI settings
PADDING = 10  # Padding for UI elements
ENTRY_WIDTH = 10  # Width of entry fields
BUTTON_WIDTH = 15  # Width of buttons

# Preview settings
PREVIEW_SIZE = (400, 400)  # Size of preview canvas (width, height)
PREVIEW_BG_COLOR = "#f0f0f0"  # Background color for preview

# File paths
DEFAULT_EXPORT_DIRECTORY = "exports"
DEFAULT_FILENAME = "drawer_divider"
