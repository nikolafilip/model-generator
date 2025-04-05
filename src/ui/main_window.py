"""
Main window UI for the 3D Divider Generator application.
"""
import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict, List, Optional, Tuple, Union

from src.config.constants import (
    DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_WALL_THICKNESS,
    DEFAULT_WIDTH, DEFAULT_LENGTH, DEFAULT_HEIGHT, DEFAULT_DIVIDER_THICKNESS,
    DEFAULT_ASYMMETRIC_ROWS, DEFAULT_ASYMMETRIC_COL_WIDTH, DEFAULT_ASYMMETRIC_ROW_HEIGHT,
    PRESET_GRIDS, PADDING, ENTRY_WIDTH, GRID_TYPES
)
from src.logic.grid_engine import GridEngine
from src.logic.model_builder import ModelBuilder
from src.logic.file_exporter import FileExporter, ExportError
from src.ui.asymmetric_grid_window import AsymmetricGridWindow


class DimensionFrame(ttk.LabelFrame):
    """
    Frame for entering drawer dimensions.
    """

    def __init__(self, parent):
        """
        Initialize the dimensions frame.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent, text="Drawer Dimensions")
        self.parent = parent
        self._create_widgets()

    def _create_widgets(self):
        """Create the dimension input widgets."""
        # Width input
        ttk.Label(self, text="Width (mm):").grid(
            row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.width_var = tk.StringVar(value=str(DEFAULT_WIDTH))
        ttk.Entry(self, textvariable=self.width_var, width=ENTRY_WIDTH).grid(
            row=0, column=1, padx=PADDING, pady=PADDING
        )

        # Length input
        ttk.Label(self, text="Length (mm):").grid(
            row=1, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.length_var = tk.StringVar(value=str(DEFAULT_LENGTH))
        ttk.Entry(self, textvariable=self.length_var, width=ENTRY_WIDTH).grid(
            row=1, column=1, padx=PADDING, pady=PADDING
        )

        # Height input
        ttk.Label(self, text="Height (mm):").grid(
            row=2, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.height_var = tk.StringVar(value=str(DEFAULT_HEIGHT))
        ttk.Entry(self, textvariable=self.height_var, width=ENTRY_WIDTH).grid(
            row=2, column=1, padx=PADDING, pady=PADDING
        )

        # Divider thickness input
        ttk.Label(self, text="Divider Thickness (mm):").grid(
            row=3, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.thickness_var = tk.StringVar(value=str(DEFAULT_DIVIDER_THICKNESS))
        ttk.Entry(self, textvariable=self.thickness_var, width=ENTRY_WIDTH).grid(
            row=3, column=1, padx=PADDING, pady=PADDING
        )

    def get_dimensions(self) -> Dict[str, str]:
        """
        Get the entered dimensions as strings.

        Returns:
            Dictionary containing the dimension values.
        """
        return {
            "width": self.width_var.get(),
            "length": self.length_var.get(),
            "height": self.height_var.get(),
            "thickness": self.thickness_var.get(),
        }


class GridFrame(ttk.LabelFrame):
    """
    Frame for configuring the grid layout.
    """

    def __init__(self, parent):
        """
        Initialize the grid frame.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent, text="Grid Configuration")
        self.parent = parent
        self.custom_grid_window = None
        self.asymmetric_grid_window = None
        self.custom_rows = []
        self.custom_cols = []
        self.asymmetric_grid_config = []
        self._create_widgets()

    def _create_widgets(self):
        """Create the grid configuration widgets."""
        # Grid type selection
        ttk.Label(self, text="Grid Type:").grid(
            row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        
        self.grid_type_var = tk.StringVar(value="preset")
        
        ttk.Radiobutton(
            self, text="No Dividers", variable=self.grid_type_var, value="none",
            command=self._update_grid_options
        ).grid(row=0, column=1, padx=PADDING, pady=PADDING)
        
        ttk.Radiobutton(
            self, text="Equal Divisions", variable=self.grid_type_var, value="preset",
            command=self._update_grid_options
        ).grid(row=0, column=2, padx=PADDING, pady=PADDING)
        
        ttk.Radiobutton(
            self, text="Custom Grid", variable=self.grid_type_var, value="custom",
            command=self._update_grid_options
        ).grid(row=1, column=1, padx=PADDING, pady=PADDING)
        
        ttk.Radiobutton(
            self, text="Asymmetric Grid", variable=self.grid_type_var, value="asymmetric",
            command=self._update_grid_options
        ).grid(row=1, column=2, padx=PADDING, pady=PADDING)

        # Create a frame for preset grid controls
        self.preset_frame = ttk.Frame(self)
        self.preset_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=PADDING, pady=PADDING)
        
        # Preset grid selection
        ttk.Label(self.preset_frame, text="Preset Grid:").grid(
            row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.preset_var = tk.StringVar(value="2×2")
        preset_dropdown = ttk.Combobox(
            self.preset_frame, textvariable=self.preset_var, values=list(PRESET_GRIDS.keys()),
            width=ENTRY_WIDTH
        )
        preset_dropdown.grid(row=0, column=1, padx=PADDING, pady=PADDING)
        preset_dropdown.current(0)
        preset_dropdown.bind("<<ComboboxSelected>>", self._update_rows_cols_from_preset)
        
        # Add manual controls for rows and columns
        ttk.Label(self.preset_frame, text="Rows:").grid(
            row=1, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.num_rows_var = tk.IntVar(value=DEFAULT_ROWS)
        rows_spinbox = ttk.Spinbox(
            self.preset_frame, from_=1, to=50, width=ENTRY_WIDTH,
            textvariable=self.num_rows_var, command=self._update_preset_from_rows_cols
        )
        rows_spinbox.grid(row=1, column=1, padx=PADDING, pady=PADDING)
        # Make sure the spinbox updates when user types a value and presses Enter
        rows_spinbox.bind('<Return>', self._update_preset_from_rows_cols)
        # Also update when focus leaves the spinbox
        rows_spinbox.bind('<FocusOut>', self._update_preset_from_rows_cols)
        
        ttk.Label(self.preset_frame, text="Columns:").grid(
            row=2, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.num_cols_var = tk.IntVar(value=DEFAULT_COLS)
        cols_spinbox = ttk.Spinbox(
            self.preset_frame, from_=1, to=50, width=ENTRY_WIDTH,
            textvariable=self.num_cols_var, command=self._update_preset_from_rows_cols
        )
        cols_spinbox.grid(row=2, column=1, padx=PADDING, pady=PADDING)
        # Make sure the spinbox updates when user types a value and presses Enter
        cols_spinbox.bind('<Return>', self._update_preset_from_rows_cols)
        # Also update when focus leaves the spinbox
        cols_spinbox.bind('<FocusOut>', self._update_preset_from_rows_cols)

        # Custom grid button
        self.custom_button = ttk.Button(
            self, text="Configure Custom Grid", command=self._open_custom_grid
        )
        self.custom_button.grid(
            row=3, column=0, columnspan=3, padx=PADDING, pady=PADDING, sticky=tk.W+tk.E
        )
        
        # Asymmetric grid button
        self.asymmetric_button = ttk.Button(
            self, text="Configure Asymmetric Grid", command=self._open_asymmetric_grid
        )
        self.asymmetric_button.grid(
            row=4, column=0, columnspan=3, padx=PADDING, pady=PADDING, sticky=tk.W+tk.E
        )

        # Model options
        ttk.Label(self, text="Model Options:").grid(
            row=5, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.model_type_var = tk.StringVar(value="dividers_only")
        ttk.Radiobutton(
            self, text="Dividers Only", variable=self.model_type_var, value="dividers_only"
        ).grid(row=5, column=1, padx=PADDING, pady=PADDING)
        ttk.Radiobutton(
            self, text="Complete Drawer", variable=self.model_type_var, value="complete_drawer"
        ).grid(row=5, column=2, padx=PADDING, pady=PADDING)

        # Frame option
        self.with_frame_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self, text="Include Frame", variable=self.with_frame_var
        ).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=PADDING, pady=PADDING)

        # Floor option
        self.with_floor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self, text="Include Floor", variable=self.with_floor_var
        ).grid(row=7, column=0, columnspan=3, sticky=tk.W, padx=PADDING, pady=PADDING)
        
        # Initialize grid options
        self._update_grid_options()
    
    def _update_grid_options(self):
        """Update the grid options based on the selected grid type."""
        grid_type = self.grid_type_var.get()
        
        # Disable all configuration buttons initially
        self.custom_button.config(state=tk.DISABLED)
        self.asymmetric_button.config(state=tk.DISABLED)
        self.preset_frame.grid_remove()
        
        # Enable appropriate controls based on grid type
        if grid_type == "preset":
            self.preset_frame.grid()
            # Initialize rows/cols from preset
            self._update_rows_cols_from_preset()
        elif grid_type == "custom":
            self.custom_button.config(state=tk.NORMAL)
        elif grid_type == "asymmetric":
            self.asymmetric_button.config(state=tk.NORMAL)
    
    def _update_rows_cols_from_preset(self, *args):
        """Update the rows and columns based on the selected preset."""
        preset = self.preset_var.get()
        
        # Check if this is a custom preset (it will have "(custom)" in the name)
        if "(custom)" in preset:
            # Extract rows and columns from the preset text
            # Format is like "4×2 (custom)"
            grid_spec = preset.split(" ")[0]  # Get "4×2" part
            rows_cols = grid_spec.split("×")  # Split into ["4", "2"]
            if len(rows_cols) == 2:
                num_rows = int(rows_cols[0])
                num_cols = int(rows_cols[1])
            else:
                # Fallback to default if format is unexpected
                num_rows, num_cols = DEFAULT_ROWS, DEFAULT_COLS
        else:
            # Use the preset grid configuration
            num_rows, num_cols = PRESET_GRIDS[preset]
        
        self.num_rows_var.set(num_rows)
        self.num_cols_var.set(num_cols)
    
    def _update_preset_from_rows_cols(self, *args):
        """Update the preset based on the rows and columns."""
        rows = self.num_rows_var.get()
        cols = self.num_cols_var.get()
        
        # Find a matching preset or set to custom
        preset_key = f"{rows}×{cols}"
        if preset_key in PRESET_GRIDS:
            self.preset_var.set(preset_key)
        else:
            # If no matching preset found, create a custom format string
            self.preset_var.set(f"{rows}×{cols} (custom)")
        
    def _open_asymmetric_grid(self):
        """Open the asymmetric grid configuration window."""
        if self.asymmetric_grid_window is not None:
            self.asymmetric_grid_window.window.destroy()
            self.asymmetric_grid_window = None
            
        # Create the asymmetric grid configuration window
        self.asymmetric_grid_window = AsymmetricGridWindow(
            self.parent,
            on_apply=self._on_asymmetric_grid_configure
        )
        
        # If we already have a configuration, pre-populate it
        if self.asymmetric_grid_config:
            self.asymmetric_grid_window.row_configs = self.asymmetric_grid_config
            self.asymmetric_grid_window.num_rows_var.set(len(self.asymmetric_grid_config))
            self.asymmetric_grid_window._update_rows()
    
    def _on_asymmetric_grid_configure(self, rows_config: List[Dict]):
        """
        Callback for when the asymmetric grid is configured.
        
        Args:
            rows_config: The configuration for the asymmetric grid.
        """
        self.asymmetric_grid_config = rows_config
        self.grid_type_var.set("asymmetric")
        
        # Construct a summary string for the status
        num_rows = len(rows_config)
        total_cells = sum(len(row["columns"]) for row in rows_config)
        messagebox.showinfo(
            "Asymmetric Grid Configured",
            f"Successfully configured asymmetric grid with {num_rows} rows and {total_cells} total cells."
        )

    def _open_custom_grid(self):
        """Open the custom grid configuration window."""
        if self.custom_grid_window is not None:
            self.custom_grid_window.destroy()

        self.custom_grid_window = tk.Toplevel(self)
        self.custom_grid_window.title("Custom Grid Configuration")
        self.custom_grid_window.geometry("600x500")  # Increased size
        self.custom_grid_window.resizable(True, True)  # Allow resizing

        # Create a frame for the configuration
        config_frame = ttk.Frame(self.custom_grid_window)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

        # Rows and columns entry
        ttk.Label(config_frame, text="Number of Rows:").grid(
            row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        rows_var = tk.IntVar(value=DEFAULT_ROWS)
        rows_spinbox = ttk.Spinbox(config_frame, from_=1, to=50, textvariable=rows_var, width=ENTRY_WIDTH)
        rows_spinbox.grid(
            row=0, column=1, padx=PADDING, pady=PADDING
        )

        ttk.Label(config_frame, text="Number of Columns:").grid(
            row=1, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        cols_var = tk.IntVar(value=DEFAULT_COLS)
        cols_spinbox = ttk.Spinbox(config_frame, from_=1, to=50, textvariable=cols_var, width=ENTRY_WIDTH)
        cols_spinbox.grid(
            row=1, column=1, padx=PADDING, pady=PADDING
        )

        # Create a container for the size fields with scrollbars
        scroll_container = ttk.Frame(config_frame)
        scroll_container.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=PADDING, pady=PADDING)
        
        # Configure grid weights for proper expansion
        config_frame.rowconfigure(3, weight=1)
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)
        
        scroll_container.rowconfigure(0, weight=1)
        scroll_container.columnconfigure(0, weight=1)
        
        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(scroll_container, orient="vertical")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        h_scrollbar = ttk.Scrollbar(scroll_container, orient="horizontal")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Create a canvas for scrolling
        canvas = tk.Canvas(scroll_container)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Configure scrollbars
        v_scrollbar.config(command=canvas.yview)
        h_scrollbar.config(command=canvas.xview)
        canvas.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Create a frame inside the canvas for the content
        content_frame = ttk.Frame(canvas)
        
        # Add the content frame to the canvas
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Update the scrollregion when the content frame changes size
        def update_scroll_region(event):
            canvas.config(scrollregion=canvas.bbox("all"))
            
        content_frame.bind("<Configure>", update_scroll_region)

        # Generate fields button
        def generate_fields():
            # Clear any existing fields
            for widget in content_frame.winfo_children():
                widget.destroy()

            rows = max(1, min(50, rows_var.get()))  # Increased max rows to 50
            cols = max(1, min(50, cols_var.get()))  # Increased max columns to 50

            # Create row and column containers
            row_container = ttk.LabelFrame(content_frame, text="Row Sizes (%)")
            row_container.grid(row=0, column=0, sticky="nsew", padx=PADDING, pady=PADDING)
            
            col_container = ttk.LabelFrame(content_frame, text="Column Sizes (%)")
            col_container.grid(row=0, column=1, sticky="nsew", padx=PADDING, pady=PADDING)
            
            # Create row size fields
            self.custom_rows = []
            for i in range(rows):
                var = tk.DoubleVar(value=100.0 / rows)
                ttk.Label(row_container, text=f"Row {i+1}:").grid(
                    row=i, column=0, sticky=tk.W, padx=PADDING, pady=2
                )
                ttk.Entry(row_container, textvariable=var, width=ENTRY_WIDTH).grid(
                    row=i, column=1, padx=PADDING, pady=2
                )
                self.custom_rows.append(var)
            
            # Create column size fields
            self.custom_cols = []
            for i in range(cols):
                var = tk.DoubleVar(value=100.0 / cols)
                ttk.Label(col_container, text=f"Column {i+1}:").grid(
                    row=i, column=0, sticky=tk.W, padx=PADDING, pady=2
                )
                ttk.Entry(col_container, textvariable=var, width=ENTRY_WIDTH).grid(
                    row=i, column=1, padx=PADDING, pady=2
                )
                self.custom_cols.append(var)
            
            # Update the scroll region
            canvas.config(scrollregion=canvas.bbox("all"))

        ttk.Button(config_frame, text="Generate Fields", command=generate_fields).grid(
            row=2, column=0, columnspan=2, padx=PADDING, pady=PADDING
        )

        # Function to handle cleanup when window is closed
        def on_closing():
            self.custom_grid_window.destroy()
            self.custom_grid_window = None
            # Switch grid type to custom
            self.grid_type_var.set("custom")
            self._update_grid_options()
            
        # Set the close protocol
        self.custom_grid_window.protocol("WM_DELETE_WINDOW", on_closing)

        # Save button
        ttk.Button(
            config_frame, text="Save Configuration", command=on_closing
        ).grid(row=4, column=0, columnspan=2, padx=PADDING, pady=PADDING)

        # Generate initial fields
        generate_fields()

    def get_grid_config(self) -> Dict:
        """
        Get the grid configuration.

        Returns:
            Dictionary containing the grid configuration.
        """
        grid_type = self.grid_type_var.get()
        config = {
            "type": grid_type,
            "with_frame": self.with_frame_var.get(),
            "with_floor": self.with_floor_var.get(),
            "model_type": self.model_type_var.get(),
        }

        if grid_type == "preset":
            config["preset"] = self.preset_var.get()
            config["rows"] = self.num_rows_var.get()
            config["cols"] = self.num_cols_var.get()
        elif grid_type == "custom":
            if self.custom_rows and self.custom_cols:
                config["row_sizes"] = [var.get() for var in self.custom_rows]
                config["col_sizes"] = [var.get() for var in self.custom_cols]
        elif grid_type == "asymmetric":
            config["rows_config"] = self.asymmetric_grid_config
        
        return config


class ExportFrame(ttk.LabelFrame):
    """
    Frame for export settings and controls.
    """

    def __init__(self, parent):
        """
        Initialize the export frame.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent, text="Export Settings")
        self.parent = parent
        self._create_widgets()

    def _create_widgets(self):
        """Create the export settings widgets."""
        # Filename input
        ttk.Label(self, text="Filename:").grid(
            row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.filename_var = tk.StringVar(value=DEFAULT_FILENAME)
        ttk.Entry(self, textvariable=self.filename_var, width=ENTRY_WIDTH * 2).grid(
            row=0, column=1, padx=PADDING, pady=PADDING
        )

        # Export directory
        ttk.Label(self, text="Export Directory:").grid(
            row=1, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.directory_var = tk.StringVar(value="")
        ttk.Entry(self, textvariable=self.directory_var, width=ENTRY_WIDTH * 2).grid(
            row=1, column=1, padx=PADDING, pady=PADDING
        )
        ttk.Button(self, text="Browse...", command=self._browse_directory).grid(
            row=1, column=2, padx=PADDING, pady=PADDING
        )

        # Resolution selection
        ttk.Label(self, text="Resolution:").grid(
            row=2, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.resolution_var = tk.StringVar(value=DEFAULT_STL_RESOLUTION)
        resolution_dropdown = ttk.Combobox(
            self, textvariable=self.resolution_var, values=["low", "normal", "high"]
        )
        resolution_dropdown.grid(row=2, column=1, padx=PADDING, pady=PADDING)
        resolution_dropdown.current(1)  # "normal" is default

    def _browse_directory(self):
        """Open a directory selection dialog."""
        directory = filedialog.askdirectory()
        if directory:
            self.directory_var.set(directory)

    def get_export_settings(self) -> Dict[str, str]:
        """
        Get the export settings.

        Returns:
            Dictionary containing the export settings.
        """
        return {
            "filename": self.filename_var.get(),
            "directory": self.directory_var.get(),
            "resolution": self.resolution_var.get(),
        }


class MainWindow(ttk.Frame):
    """
    Main application window with UI elements for the 3D Divider Generator.
    """

    def __init__(self, master, project_root: str):
        """Initialize the main window."""
        super().__init__(master)
        self.master = master
        self.project_root = project_root
        
        # Set window properties
        self.master.title("3D Divider Generator")
        self.master.geometry("800x600")
        
        # Unit selection
        self.unit_selection = tk.StringVar(value="mm")  # Default to millimeters
        
        # Initialize dimensions variables
        self.width_var = tk.DoubleVar(value=DEFAULT_WIDTH)
        self.height_var = tk.DoubleVar(value=DEFAULT_HEIGHT)
        self.length_var = tk.DoubleVar(value=DEFAULT_LENGTH)
        self.wall_thickness_var = tk.DoubleVar(value=DEFAULT_WALL_THICKNESS)
        
        # Export variables
        self.export_path_var = tk.StringVar(value=os.path.join(project_root, "exports"))
        self.filename_var = tk.StringVar(value="drawer_divider")
        
        # Create the main container
        main_container = ttk.Frame(self.master)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for inputs
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create the main frame for inputs
        self.main_frame = ttk.Frame(left_panel)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create right panel for preview
        preview_frame = ttk.LabelFrame(main_container, text="Preview")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Canvas for drawing the preview
        self.preview_canvas = tk.Canvas(preview_frame, bg="white")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Preview refresh button
        ttk.Button(
            preview_frame, text="Refresh Preview", command=self._update_preview
        ).pack(pady=PADDING)
        
        # Create the UI components
        self.create_dimensions_frame()
        self.grid_frame = self.create_layout_frame()
        self.create_export_frame()
        
        # Create generate button
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=PADDING)
        
        ttk.Button(
            button_frame, text="Generate 3D Model", command=self._generate_model
        ).pack(side=tk.RIGHT, padx=PADDING)

    def create_dimensions_frame(self):
        """Create the dimensions input frame."""
        # Frame for drawer dimensions
        dimensions_frame = ttk.LabelFrame(self.main_frame, text="Drawer Dimensions")
        dimensions_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Unit selection
        unit_frame = ttk.Frame(dimensions_frame)
        unit_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=PADDING, pady=PADDING)
        
        ttk.Label(unit_frame, text="Units:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(unit_frame, text="mm", variable=self.unit_selection, value="mm").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(unit_frame, text="inches", variable=self.unit_selection, value="inches").pack(side=tk.LEFT, padx=5)
        
        # Width
        ttk.Label(dimensions_frame, text="Width:").grid(
            row=1, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        width_entry = ttk.Entry(dimensions_frame, textvariable=self.width_var, width=ENTRY_WIDTH)
        width_entry.grid(row=1, column=1, padx=PADDING, pady=PADDING)
        ttk.Label(dimensions_frame, text="(left to right)").grid(
            row=1, column=2, sticky=tk.W, padx=0, pady=PADDING
        )
        
        # Length
        ttk.Label(dimensions_frame, text="Length:").grid(
            row=2, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        length_entry = ttk.Entry(dimensions_frame, textvariable=self.length_var, width=ENTRY_WIDTH)
        length_entry.grid(row=2, column=1, padx=PADDING, pady=PADDING)
        ttk.Label(dimensions_frame, text="(front to back)").grid(
            row=2, column=2, sticky=tk.W, padx=0, pady=PADDING
        )
        
        # Height
        ttk.Label(dimensions_frame, text="Height:").grid(
            row=3, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        height_entry = ttk.Entry(dimensions_frame, textvariable=self.height_var, width=ENTRY_WIDTH)
        height_entry.grid(row=3, column=1, padx=PADDING, pady=PADDING)
        ttk.Label(dimensions_frame, text="(bottom to top)").grid(
            row=3, column=2, sticky=tk.W, padx=0, pady=PADDING
        )
        
        # Wall thickness
        ttk.Label(dimensions_frame, text="Wall Thickness:").grid(
            row=4, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        wall_thickness_entry = ttk.Entry(
            dimensions_frame, textvariable=self.wall_thickness_var, width=ENTRY_WIDTH
        )
        wall_thickness_entry.grid(row=4, column=1, padx=PADDING, pady=PADDING)
        
        # Return the frame
        return dimensions_frame

    def create_layout_frame(self):
        """Create the grid layout configuration frame."""
        layout_frame = GridFrame(self.main_frame)
        layout_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        return layout_frame

    def create_export_frame(self):
        """Create the export settings frame."""
        # Frame for export settings
        export_frame = ttk.LabelFrame(self.main_frame, text="Export Settings")
        export_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Filename
        ttk.Label(export_frame, text="Filename:").grid(
            row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        filename_entry = ttk.Entry(export_frame, textvariable=self.filename_var, width=ENTRY_WIDTH * 2)
        filename_entry.grid(row=0, column=1, columnspan=2, padx=PADDING, pady=PADDING, sticky=tk.W+tk.E)
        
        # Export path
        ttk.Label(export_frame, text="Export Path:").grid(
            row=1, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        path_entry = ttk.Entry(export_frame, textvariable=self.export_path_var, width=ENTRY_WIDTH * 2)
        path_entry.grid(row=1, column=1, padx=PADDING, pady=PADDING, sticky=tk.W+tk.E)
        
        ttk.Button(
            export_frame, text="Browse...", command=self._browse_export_path
        ).grid(row=1, column=2, padx=PADDING, pady=PADDING)
        
        # Return frame
        return export_frame

    def _update_preview(self):
        """Update the preview with the current settings."""
        try:
            # Clear the canvas
            self.preview_canvas.delete("all")
            
            # Get dimensions
            width = self.width_var.get()
            height = self.height_var.get()
            length = self.length_var.get()
            wall_thickness = self.wall_thickness_var.get()
            
            # Convert to mm if inches are selected
            if self.unit_selection.get() == "inches":
                # 1 inch = 25.4 mm
                width *= 25.4
                height *= 25.4
                length *= 25.4
                wall_thickness *= 25.4
            
            # Validate dimensions
            if width <= 0 or height <= 0 or length <= 0 or wall_thickness <= 0:
                raise ValueError("All dimensions must be positive numbers")
            
            # Get grid configuration
            rows = []
            cols = []
            
            # Access grid type through the grid_frame
            grid_type = self.grid_frame.grid_type_var.get()
            
            if grid_type == "none":
                # No dividers
                rows = [100]
                cols = [100]
            elif grid_type == "preset":
                # Get preset grid
                preset = self.grid_frame.preset_var.get()
                
                # Check if this is a custom preset (it will have "(custom)" in the name)
                if "(custom)" in preset:
                    # Extract rows and columns from the preset text
                    # Format is like "4×2 (custom)"
                    grid_spec = preset.split(" ")[0]  # Get "4×2" part
                    rows_cols = grid_spec.split("×")  # Split into ["4", "2"]
                    if len(rows_cols) == 2:
                        num_rows = int(rows_cols[0])
                        num_cols = int(rows_cols[1])
                    else:
                        # Fallback to default if format is unexpected
                        num_rows, num_cols = DEFAULT_ROWS, DEFAULT_COLS
                else:
                    # Use the preset grid configuration
                    num_rows, num_cols = PRESET_GRIDS[preset]
                
                # Equal divisions
                rows = [100.0 / num_rows] * num_rows
                cols = [100.0 / num_cols] * num_cols
            elif grid_type == "custom":
                # Custom grid from user input
                if not self.grid_frame.custom_rows or not self.grid_frame.custom_cols:
                    raise ValueError("No custom grid configuration has been defined")
                
                rows = [var.get() for var in self.grid_frame.custom_rows]
                cols = [var.get() for var in self.grid_frame.custom_cols]
            elif grid_type == "asymmetric":
                # Asymmetric grid
                if not self.grid_frame.asymmetric_grid_config:
                    raise ValueError("No asymmetric grid configuration has been defined")
                
                # For preview purposes, use the row heights
                rows = [row["height_percent"] for row in self.grid_frame.asymmetric_grid_config]
            
            # Calculate the canvas size
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Determine the scaling factor to fit the preview in the canvas
            # Use top view (width x length)
            max_dim = max(width, length)
            padding = 20  # Padding from the canvas edges
            scale = min((canvas_width - 2 * padding) / width, (canvas_height - 2 * padding) / length)
            
            # Calculate the size of the drawer in the preview
            preview_width = width * scale
            preview_length = length * scale
            
            # Calculate the starting position to center the drawer
            start_x = (canvas_width - preview_width) / 2
            start_y = (canvas_height - preview_length) / 2
            
            # Draw the drawer outline
            self.preview_canvas.create_rectangle(
                start_x, start_y, 
                start_x + preview_width, start_y + preview_length, 
                outline="black", width=2
            )
            
            # Draw the grid dividers
            if grid_type != "none":
                # Calculate row positions
                row_positions = []
                current_pos = 0
                for row_percent in rows:
                    row_positions.append(current_pos)
                    current_pos += row_percent / 100.0 * preview_length
                
                # Draw the horizontal dividers (rows)
                for i in range(1, len(row_positions)):
                    y_pos = start_y + row_positions[i]
                    self.preview_canvas.create_line(
                        start_x, y_pos, 
                        start_x + preview_width, y_pos, 
                        fill="blue", width=max(1, int(wall_thickness * scale / 2))
                    )
                
                # Special handling for asymmetric grid's columns
                if grid_type == "asymmetric":
                    # Draw each row's columns separately
                    for row_idx, row_config in enumerate(self.grid_frame.asymmetric_grid_config):
                        # Calculate row boundaries
                        row_start = row_positions[row_idx]
                        row_end = row_positions[row_idx + 1] if row_idx + 1 < len(row_positions) else preview_length
                        
                        # Get column configuration for this row
                        columns = row_config.get("columns", [])
                        if not columns:
                            continue
                            
                        # Calculate column positions for this row
                        col_positions = []
                        current_pos = 0
                        for col in columns:
                            col_positions.append(current_pos)
                            current_pos += col["width_percent"] / 100.0 * preview_width
                        
                        # Draw vertical dividers for this row's columns
                        for i in range(1, len(col_positions)):
                            x_pos = start_x + col_positions[i]
                            # Only draw the divider within this row's bounds
                            self.preview_canvas.create_line(
                                x_pos, start_y + row_start, 
                                x_pos, start_y + row_end, 
                                fill="blue", width=max(1, int(wall_thickness * scale / 2))
                            )
                else:
                    # For standard grids (preset, custom), draw vertical dividers that span all rows
                    # Calculate column positions
                    col_positions = []
                    current_pos = 0
                    for col_percent in cols:
                        col_positions.append(current_pos)
                        current_pos += col_percent / 100.0 * preview_width
                    
                    # Draw the vertical dividers (columns)
                    for i in range(1, len(col_positions)):
                        x_pos = start_x + col_positions[i]
                        self.preview_canvas.create_line(
                            x_pos, start_y, 
                            x_pos, start_y + preview_length, 
                            fill="blue", width=max(1, int(wall_thickness * scale / 2))
                        )
            
            # Add a label for the top view
            self.preview_canvas.create_text(
                canvas_width / 2, start_y - 10, 
                text="Top View (Width × Length)", 
                fill="black", font=("Arial", 10, "bold")
            )
            
            # Add dimension labels
            self.preview_canvas.create_text(
                start_x + preview_width / 2, start_y + preview_length + 15,
                text=f"Width: {width:.1f} {'mm' if self.unit_selection.get() == 'mm' else 'inches'}", 
                fill="black"
            )
            
            self.preview_canvas.create_text(
                start_x - 15, start_y + preview_length / 2,
                text=f"Length: {length:.1f} {'mm' if self.unit_selection.get() == 'mm' else 'inches'}", 
                fill="black", angle=90
            )
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to generate preview: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def _generate_model(self):
        """Generate the 3D model based on the current configuration."""
        try:
            # Get dimensions
            width = self.width_var.get()
            height = self.height_var.get()
            length = self.length_var.get()
            wall_thickness = self.wall_thickness_var.get()
            
            # Convert to mm if inches are selected
            if self.unit_selection.get() == "inches":
                # 1 inch = 25.4 mm
                width *= 25.4
                height *= 25.4
                length *= 25.4
                wall_thickness *= 25.4
            
            # Validate dimensions
            if width <= 0 or height <= 0 or length <= 0 or wall_thickness <= 0:
                raise ValueError("All dimensions must be positive numbers")
            
            if wall_thickness >= min(width, height, length) / 3:
                raise ValueError("Wall thickness is too large for the given dimensions")
            
            # Get grid configuration from the grid frame
            grid_config = self.grid_frame.get_grid_config()
            grid_type = grid_config["type"]
            
            # Handle different grid types
            cells = []
            dividers = []
            grid_engine = None
            
            if grid_type == "none":
                # No dividers, just create a single cell
                cells, dividers = GridEngine.create_regular_grid(
                    width, length, height, rows=1, cols=1, thickness=wall_thickness
                )
                
                # Create the grid engine for model builder (standard grid)
                grid_engine = GridEngine(
                    width=width,
                    height=height,
                    length=length,
                    wall_thickness=wall_thickness,
                    row_percentages=[100],
                    col_percentages=[100]
                )
                
            elif grid_type == "preset":
                # Get rows and columns from the configuration
                rows = grid_config["rows"]
                cols = grid_config["cols"]
                
                cells, dividers = GridEngine.create_regular_grid(
                    width, length, height, rows=rows, cols=cols, thickness=wall_thickness
                )
                
                # Create row and column percentages (equal divisions)
                row_percentages = [100.0 / rows] * rows
                col_percentages = [100.0 / cols] * cols
                
                # Create the grid engine for model builder
                grid_engine = GridEngine(
                    width=width,
                    height=height,
                    length=length,
                    wall_thickness=wall_thickness,
                    row_percentages=row_percentages,
                    col_percentages=col_percentages
                )
                
            elif grid_type == "custom":
                # Use custom grid
                row_sizes = grid_config.get("row_sizes", [])
                col_sizes = grid_config.get("col_sizes", [])
                
                if not row_sizes or not col_sizes:
                    messagebox.showerror(
                        "Invalid Grid Configuration",
                        "Please configure the custom grid first."
                    )
                    return
                    
                cells, dividers = GridEngine.create_custom_grid(
                    width, length, height, row_sizes, col_sizes, thickness=wall_thickness
                )
                
                # Create the grid engine for model builder
                grid_engine = GridEngine(
                    width=width,
                    height=height,
                    length=length,
                    wall_thickness=wall_thickness,
                    row_percentages=row_sizes,
                    col_percentages=col_sizes
                )
                
            elif grid_type == "asymmetric":
                # Use asymmetric grid
                rows_config = grid_config.get("rows_config", [])
                
                if not rows_config:
                    messagebox.showerror(
                        "Invalid Grid Configuration",
                        "Please configure the asymmetric grid first."
                    )
                    return
                    
                # Generate cells and dividers
                cells, dividers = GridEngine.create_asymmetric_grid(
                    width, length, height, rows_config, thickness=wall_thickness
                )
                
                # Create the grid engine for model builder with asymmetric dividers
                grid_engine = GridEngine(
                    width=width,
                    height=height,
                    length=length,
                    wall_thickness=wall_thickness,
                    row_percentages=[100],  # Not used for asymmetric grid
                    col_percentages=[100],  # Not used for asymmetric grid
                    asymmetric_dividers=dividers  # Pass the asymmetric dividers directly
                )
            
            # Get model options
            model_type = grid_config["model_type"]
            with_frame = grid_config["with_frame"]
            with_floor = grid_config["with_floor"]
            
            # Get export path and filename
            export_path = self.export_path_var.get() or os.path.join(self.project_root, "exports")
            filename = self.filename_var.get() or "drawer_divider"
            
            # Ensure the export directory exists
            os.makedirs(export_path, exist_ok=True)
            
            # Create the model builder with our configured grid engine
            model_builder = ModelBuilder(grid_engine)
            
            # Generate the appropriate model based on user selection
            if model_type == "complete_drawer":
                model = model_builder.create_complete_drawer_model(with_frame=with_frame, with_floor=with_floor)
            else:
                model = model_builder.create_divider_only_model(with_frame=with_frame, with_floor=with_floor)
            
            # Export the model
            exporter = FileExporter(os.path.join(export_path, filename))
            scad_path = exporter.generate_model(model)
            
            # Try to export to STL
            try:
                stl_path = exporter.export_model(scad_path)
                messagebox.showinfo(
                    "Success",
                    f"Model generated and exported successfully to {stl_path}"
                )
            except ExportError as e:
                # If automatic export fails, try to open with OpenSCAD
                try:
                    exporter.open_scad_file(scad_path)
                    messagebox.showinfo(
                        "Model Generated",
                        f"Model generated successfully as SCAD file at {scad_path}.\n\n"
                        f"Please manually export as STL using OpenSCAD."
                    )
                except Exception as open_error:
                    messagebox.showerror(
                        "Export Error",
                        f"Failed to export model automatically: {str(e)}\n\n"
                        f"Also failed to open with OpenSCAD: {str(open_error)}\n\n"
                        f"You can find the SCAD file at: {scad_path}"
                    )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate model: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def _browse_export_path(self):
        """Open a directory dialog to select the export path."""
        directory = filedialog.askdirectory(
            initialdir=self.export_path_var.get() or os.path.join(self.project_root, "exports")
        )
        if directory:  # User didn't cancel
            self.export_path_var.set(directory)
