"""
UI component for configuring asymmetric grids.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Optional, Tuple

# UI Constants
PADDING = 10
ENTRY_WIDTH = 10
DEFAULT_ROWS = 2


class AsymmetricGridWindow:
    """
    Window for configuring an asymmetric grid.
    """

    def __init__(self, parent, on_apply: Callable[[List[Dict]], None]):
        """
        Initialize the asymmetric grid configuration window.

        Args:
            parent: Parent widget.
            on_apply: Callback function to call when the grid is configured.
                      Takes a list of row configurations as an argument.
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Asymmetric Grid Configuration")
        self.window.geometry("700x600")  # Larger window for complex grids
        self.window.resizable(True, True)
        
        self.on_apply = on_apply
        self.row_configs = []  # Will hold the row configurations
        
        self._create_widgets()
        self._initialize_rows()
        
        # Set up window close handler
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Center the window on the parent
        self.window.transient(parent)
        self.window.update_idletasks()
        self.window.wait_visibility()
        self.window.grab_set()
        
    def _create_widgets(self):
        """Create and arrange window widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding=PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instruction label
        instructions = (
            "Configure an asymmetric grid where each row has its own height\n"
            "and custom number of columns with variable widths.\n"
            "Each row's height percentage and each column's width percentage\n"
            "must add up to 100%."
        )
        ttk.Label(main_frame, text=instructions, justify=tk.LEFT, wraplength=600).pack(
            fill=tk.X, pady=(0, PADDING)
        )
        
        # Row controls frame
        row_controls_frame = ttk.Frame(main_frame)
        row_controls_frame.pack(fill=tk.X, pady=PADDING)
        
        ttk.Label(row_controls_frame, text="Number of Rows:").pack(side=tk.LEFT, padx=PADDING)
        
        self.num_rows_var = tk.IntVar(value=DEFAULT_ROWS)
        ttk.Spinbox(
            row_controls_frame, 
            from_=1, 
            to=10, 
            width=ENTRY_WIDTH,
            textvariable=self.num_rows_var, 
            command=self._update_rows
        ).pack(side=tk.LEFT, padx=PADDING)
        
        ttk.Button(
            row_controls_frame, 
            text="Update Rows", 
            command=self._update_rows
        ).pack(side=tk.LEFT, padx=PADDING)
        
        # Create scrollable content area
        self.canvas_frame = ttk.Frame(main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=PADDING)
        
        # Configure grid weights for proper expansion
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbars
        self.canvas = tk.Canvas(self.canvas_frame, borderwidth=0, highlightthickness=0)
        vscrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        hscrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        vscrollbar.grid(row=0, column=1, sticky="ns")
        hscrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.canvas.configure(
            yscrollcommand=vscrollbar.set,
            xscrollcommand=hscrollbar.set
        )
        
        # Create a frame inside the canvas which will contain row configurations
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.content_frame, anchor="nw"
        )
        
        # Update the scroll region when the content frame changes size
        self.content_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=PADDING)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self._on_cancel
        ).pack(side=tk.RIGHT, padx=PADDING)
        
        ttk.Button(
            button_frame, 
            text="Apply", 
            command=self._on_apply
        ).pack(side=tk.RIGHT, padx=PADDING)
    
    def _update_scroll_region(self, event):
        """Update the canvas scroll region when the content size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_resize(self, event):
        """Adjust the inner frame's width when the canvas is resized."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _initialize_rows(self):
        """Initialize the row configurations."""
        self._update_rows()
    
    def _update_rows(self, *args):
        """Update the row configuration widgets based on the number of rows."""
        num_rows = max(1, min(10, self.num_rows_var.get()))
        
        # Clear existing rows
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Initialize row configs if needed
        if not self.row_configs or len(self.row_configs) != num_rows:
            # Create default row configs
            self.row_configs = []
            default_height = 100.0 / num_rows
            
            for i in range(num_rows):
                row_config = {
                    "height_percent": default_height,
                    "columns": [
                        {"width_percent": 100.0}  # One column taking 100% by default
                    ]
                }
                self.row_configs.append(row_config)
        
        # Create row configuration widgets
        self._create_row_widgets()
        
        # Update the scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _create_row_widgets(self):
        """Create widgets for configuring each row."""
        # Header
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        ttk.Label(header_frame, text="Row", width=6).pack(side=tk.LEFT, padx=PADDING)
        ttk.Label(header_frame, text="Height %", width=10).pack(side=tk.LEFT, padx=PADDING)
        ttk.Label(header_frame, text="Columns", width=10).pack(side=tk.LEFT, padx=PADDING)
        ttk.Label(header_frame, text="Configuration", width=20).pack(side=tk.LEFT, padx=PADDING)
        
        # Create widgets for each row
        for i, row_config in enumerate(self.row_configs):
            row_frame = ttk.Frame(self.content_frame)
            row_frame.pack(fill=tk.X, padx=PADDING, pady=(0, PADDING))
            
            # Row number
            ttk.Label(row_frame, text=f"Row {i+1}", width=6).pack(side=tk.LEFT, padx=PADDING)
            
            # Height percentage
            height_var = tk.DoubleVar(value=row_config["height_percent"])
            height_entry = ttk.Entry(row_frame, textvariable=height_var, width=10)
            height_entry.pack(side=tk.LEFT, padx=PADDING)
            
            # Store the variable for later access
            row_config["height_var"] = height_var
            
            # Number of columns
            ttk.Label(row_frame, text="Columns:").pack(side=tk.LEFT, padx=PADDING)
            
            num_cols_var = tk.IntVar(value=len(row_config["columns"]))
            cols_spinbox = ttk.Spinbox(
                row_frame, 
                from_=1, 
                to=10, 
                width=5,
                textvariable=num_cols_var
            )
            cols_spinbox.pack(side=tk.LEFT, padx=PADDING)
            
            # Configure columns button
            ttk.Button(
                row_frame, 
                text="Configure Columns", 
                command=lambda row_idx=i: self._configure_columns(row_idx)
            ).pack(side=tk.LEFT, padx=PADDING)
            
            # Store the variables
            row_config["num_cols_var"] = num_cols_var
        
        # Add button to validate heights
        ttk.Button(
            self.content_frame, 
            text="Validate Heights", 
            command=self._validate_heights
        ).pack(pady=PADDING)
    
    def _validate_heights(self):
        """Validate that the row heights sum to 100%."""
        total = sum(row_config["height_var"].get() for row_config in self.row_configs)
        
        if abs(total - 100.0) > 0.01:
            messagebox.showerror(
                "Invalid Heights",
                f"Row heights must sum to 100%. Current sum: {total:.2f}%."
            )
        else:
            messagebox.showinfo(
                "Valid Heights",
                "Row heights sum to 100%. Configuration is valid."
            )
    
    def _configure_columns(self, row_idx):
        """Open a dialog to configure columns for a specific row."""
        row_config = self.row_configs[row_idx]
        num_cols = row_config["num_cols_var"].get()
        
        # Create a new window for column configuration
        col_window = tk.Toplevel(self.window)
        col_window.title(f"Configure Columns for Row {row_idx + 1}")
        col_window.geometry("500x400")
        col_window.resizable(True, True)
        col_window.transient(self.window)
        
        # Main frame
        main_frame = ttk.Frame(col_window, padding=PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(
            main_frame, 
            text=f"Configure the {num_cols} columns for Row {row_idx + 1}.\nColumn widths must sum to 100%.",
            justify=tk.LEFT
        ).pack(fill=tk.X, pady=(0, PADDING))
        
        # Initialize columns if needed
        if len(row_config["columns"]) != num_cols:
            # Create default even widths
            default_width = 100.0 / num_cols
            row_config["columns"] = [
                {"width_percent": default_width} for _ in range(num_cols)
            ]
        
        # Create a frame for the columns
        cols_frame = ttk.Frame(main_frame)
        cols_frame.pack(fill=tk.BOTH, expand=True, pady=PADDING)
        
        # Headers
        ttk.Label(cols_frame, text="Column", width=10).grid(row=0, column=0, padx=PADDING, pady=PADDING)
        ttk.Label(cols_frame, text="Width %", width=10).grid(row=0, column=1, padx=PADDING, pady=PADDING)
        
        # Create entries for each column
        width_vars = []
        for i, col in enumerate(row_config["columns"]):
            ttk.Label(cols_frame, text=f"Column {i+1}", width=10).grid(
                row=i+1, column=0, padx=PADDING, pady=PADDING
            )
            
            width_var = tk.DoubleVar(value=col["width_percent"])
            ttk.Entry(cols_frame, textvariable=width_var, width=10).grid(
                row=i+1, column=1, padx=PADDING, pady=PADDING
            )
            
            width_vars.append(width_var)
        
        # Add a validate button
        def validate_and_save():
            # Validate that widths sum to 100%
            total = sum(var.get() for var in width_vars)
            
            if abs(total - 100.0) > 0.01:
                messagebox.showerror(
                    "Invalid Widths",
                    f"Column widths must sum to 100%. Current sum: {total:.2f}%."
                )
                return
            
            # Save the values
            for i, var in enumerate(width_vars):
                row_config["columns"][i]["width_percent"] = var.get()
            
            messagebox.showinfo(
                "Columns Configured",
                "Column widths have been saved."
            )
            col_window.destroy()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=PADDING)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=col_window.destroy
        ).pack(side=tk.RIGHT, padx=PADDING)
        
        ttk.Button(
            button_frame, 
            text="Validate & Save", 
            command=validate_and_save
        ).pack(side=tk.RIGHT, padx=PADDING)
        
        # Make this window modal
        col_window.grab_set()
        col_window.wait_window()
    
    def _on_apply(self):
        """Apply the grid configuration."""
        # Update row configurations from the UI inputs
        for row_config in self.row_configs:
            row_config["height_percent"] = row_config["height_var"].get()
        
        # Validate row heights
        total_height = sum(row["height_percent"] for row in self.row_configs)
        if abs(total_height - 100.0) > 0.01:
            messagebox.showerror(
                "Invalid Configuration",
                f"Row heights must sum to 100%. Current sum: {total_height:.2f}%."
            )
            return
        
        # Check that all column widths for each row sum to 100%
        for i, row_config in enumerate(self.row_configs):
            total_width = sum(col["width_percent"] for col in row_config["columns"])
            if abs(total_width - 100.0) > 0.01:
                messagebox.showerror(
                    "Invalid Configuration",
                    f"Column widths in row {i+1} must sum to 100%. Current sum: {total_width:.2f}%."
                )
                return
        
        # Convert to format expected by the grid engine
        result = []
        for row in self.row_configs:
            row_data = {
                "height_percent": row["height_percent"],
                "columns": row["columns"]
            }
            result.append(row_data)
        
        # Call the callback with the configured grid
        self.on_apply(result)
        self.window.destroy()
    
    def _on_cancel(self):
        """Cancel the grid configuration."""
        self.window.destroy() 