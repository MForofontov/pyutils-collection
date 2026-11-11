# Data Visualization Functions

A comprehensive collection of data visualization utilities for creating, configuring, and exporting high-quality plots and charts using matplotlib.

## Module Organization

This module contains 28 functions organized into 5 categories:

### 1. Plot Generation Helpers (4 functions)
Matplotlib wrapper functions for common plot types with enhanced features:

- **`create_line_plot`** - Multi-series line plots with comprehensive customization
- **`create_scatter_plot`** - Scatter plots with flexible styling options
- **`create_bar_plot`** - Grouped and stacked bar charts (horizontal/vertical)
- **`create_histogram`** - Histograms with multiple distributions support

### 2. Chart Configuration Utilities (6 functions)
Theme management and plot customization:

- **`ChartTheme`** - Dataclass for theme configuration (colors, fonts, sizes)
- **`get_preset_theme`** - Get 6 preset themes (default, dark, minimal, colorful, presentation, publication)
- **`apply_theme`** - Apply ChartTheme to matplotlib globally
- **`reset_theme`** - Reset matplotlib to default settings
- **`configure_axes_style`** - Fine-grained axes customization (grid, spines, labels)
- **`set_figure_size`** - Set default figure dimensions and DPI

### 3. Color Palette Generators (7 functions)
Color manipulation and palette creation:

- **`generate_color_palette`** - Generate palettes (sequential, diverging, qualitative, rainbow)
- **`create_gradient`** - Create smooth color gradients between two colors
- **`get_colorblind_safe_palette`** - Paul Tol's colorblind-safe 12-color palette
- **`hex_to_rgb`** - Convert hex color codes to RGB tuples
- **`rgb_to_hex`** - Convert RGB tuples to hex color codes
- **`adjust_brightness`** - Adjust color brightness (lighter/darker)
- **`generate_categorical_colors`** - Generate visually distinct categorical colors

### 4. Data-to-Visualization Transformers (6 functions)
Data preparation and transformation for visualization:

- **`normalize_data`** - Normalize data (minmax, zscore, robust methods)
- **`bin_data`** - Bin continuous data into discrete intervals
- **`aggregate_by_group`** - Aggregate data by group with various statistics
- **`pivot_for_heatmap`** - Pivot data into matrix format for heatmaps
- **`smooth_timeseries`** - Smooth timeseries (moving average, exponential, Savitzky-Golay)
- **`calculate_moving_statistics`** - Calculate moving statistics (mean, std, min, max, median)

### 5. Export Utilities (5 functions)
Figure export and management:

- **`save_figure`** - Save matplotlib figure to file (PNG, PDF, SVG, etc.)
- **`save_multiple_formats`** - Save figure in multiple formats simultaneously
- **`export_current_figure`** - Export current matplotlib figure
- **`create_figure_grid`** - Create grid of subplots
- **`configure_export_defaults`** - Set default export settings (DPI, format, transparency)

## Installation

Required dependencies:
```bash
pip install matplotlib numpy
```

Optional dependencies:
```bash
pip install scipy  # For Savitzky-Golay smoothing
```

## Quick Start Examples

### Creating Basic Plots

```python
from data_visualization_functions import create_line_plot, create_scatter_plot

# Line plot with multiple series
fig, ax = create_line_plot(
    x=[1, 2, 3, 4],
    y=[[1, 4, 9, 16], [1, 2, 3, 4]],
    labels=["Squared", "Linear"],
    title="Growth Comparison",
    xlabel="Time",
    ylabel="Value",
)

# Scatter plot
fig, ax = create_scatter_plot(
    x=[1, 2, 3, 4, 5],
    y=[2, 4, 5, 7, 8],
    colors="blue",
    sizes=100,
    alpha=0.7,
    title="Data Points",
)
```

### Applying Themes

```python
from data_visualization_functions import get_preset_theme, apply_theme

# Apply a professional theme
theme = get_preset_theme("publication")
apply_theme(theme)

# All subsequent plots will use this theme
```

### Working with Color Palettes

```python
from data_visualization_functions import (
    generate_color_palette,
    get_colorblind_safe_palette,
    adjust_brightness,
)

# Generate sequential palette
colors = generate_color_palette(5, palette_type="sequential")

# Get colorblind-safe colors
safe_colors = get_colorblind_safe_palette(8)

# Adjust color brightness
darker = adjust_brightness("red", 0.5)  # Darker
lighter = adjust_brightness("#FF0000", 1.5)  # Lighter
```

### Data Transformation for Visualization

```python
from data_visualization_functions import (
    normalize_data,
    pivot_for_heatmap,
    smooth_timeseries,
)

# Normalize data for better visualization
data = [1, 5, 10, 15, 20]
normalized = normalize_data(data, method="minmax")

# Prepare heatmap data
matrix, row_labels, col_labels = pivot_for_heatmap(
    data=[10, 20, 30, 40],
    row_labels=["A", "A", "B", "B"],
    col_labels=["X", "Y", "X", "Y"],
)

# Smooth noisy timeseries
noisy_data = [1, 5, 2, 8, 3, 9, 4, 7]
smoothed = smooth_timeseries(noisy_data, method="moving_average", window_size=3)
```

### Exporting Figures

```python
from data_visualization_functions import (
    save_figure,
    save_multiple_formats,
    configure_export_defaults,
)

# Save single figure
save_figure(fig, "output/plot.png", dpi=300)

# Save in multiple formats
paths = save_multiple_formats(
    fig, "output/plot", formats=["png", "pdf", "svg"], dpi=600
)

# Configure defaults for all exports
configure_export_defaults(dpi=300, format="pdf", transparent=True)
```

## Advanced Examples

### Complete Workflow with Theme and Export

```python
from data_visualization_functions import (
    get_preset_theme,
    apply_theme,
    create_line_plot,
    save_multiple_formats,
)

# 1. Apply professional theme
theme = get_preset_theme("publication")
apply_theme(theme)

# 2. Create plot
fig, ax = create_line_plot(
    x=[1, 2, 3, 4, 5],
    y=[[1, 4, 9, 16, 25], [1, 2, 3, 4, 5]],
    labels=["Squared", "Linear"],
    title="Mathematical Functions",
    xlabel="Input (x)",
    ylabel="Output f(x)",
    grid=True,
    markers=["o", "s"],
)

# 3. Export in multiple formats
save_multiple_formats(
    fig, "publication_plot", formats=["png", "pdf", "svg"], dpi=600, transparent=False
)
```

### Custom Bar Chart with Grouping

```python
from data_visualization_functions import create_bar_plot, generate_categorical_colors

# Generate distinct colors for categories
colors = generate_categorical_colors(3)

# Create grouped bar chart
fig, ax = create_bar_plot(
    categories=["Q1", "Q2", "Q3", "Q4"],
    values=[[10, 15, 12, 18], [8, 12, 14, 16], [12, 10, 15, 14]],
    labels=["Product A", "Product B", "Product C"],
    title="Quarterly Sales by Product",
    xlabel="Quarter",
    ylabel="Sales (millions)",
    stacked=False,
    colors=colors,
)
```

### Heatmap with Data Aggregation

```python
import matplotlib.pyplot as plt
from data_visualization_functions import (
    pivot_for_heatmap,
    get_preset_theme,
    apply_theme,
)

# Apply dark theme
apply_theme(get_preset_theme("dark"))

# Prepare heatmap data
data = [10, 20, 30, 15, 25, 35, 12, 22, 32]
rows = ["A", "A", "A", "B", "B", "B", "C", "C", "C"]
cols = ["X", "Y", "Z", "X", "Y", "Z", "X", "Y", "Z"]

matrix, row_labels, col_labels = pivot_for_heatmap(data, rows, cols, agg_func="mean")

# Create heatmap
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(matrix, cmap="viridis")
ax.set_xticks(range(len(col_labels)))
ax.set_yticks(range(len(row_labels)))
ax.set_xticklabels(col_labels)
ax.set_yticklabels(row_labels)
plt.colorbar(im, ax=ax)
plt.title("Heatmap Visualization")
```

### Timeseries Smoothing and Analysis

```python
import numpy as np
from data_visualization_functions import (
    smooth_timeseries,
    calculate_moving_statistics,
    create_line_plot,
)

# Generate noisy timeseries
t = np.linspace(0, 10, 100)
signal = np.sin(t)
noise = np.random.normal(0, 0.2, 100)
noisy_data = signal + noise

# Apply different smoothing methods
ma_smoothed = smooth_timeseries(noisy_data, method="moving_average", window_size=5)
exp_smoothed = smooth_timeseries(noisy_data, method="exponential", window_size=5)

# Calculate moving statistics
stats = calculate_moving_statistics(
    noisy_data, window_size=10, statistics=["mean", "std", "min", "max"]
)

# Visualize
fig, ax = create_line_plot(
    x=t,
    y=[noisy_data, ma_smoothed, exp_smoothed, signal],
    labels=["Noisy", "Moving Avg", "Exponential", "True Signal"],
    title="Timeseries Smoothing Comparison",
    xlabel="Time",
    ylabel="Value",
    alpha=[0.3, 1.0, 1.0, 1.0],
)
```

## Design Principles

All functions in this module follow these principles:

1. **Type Safety**: Complete type hints for all parameters and returns
2. **Validation**: Comprehensive input validation with descriptive error messages
3. **Documentation**: NumPy-style docstrings with examples and complexity notes
4. **Consistency**: Uniform API design across all functions
5. **Flexibility**: Sensible defaults with extensive customization options

## Function Signatures

For detailed parameter descriptions, see individual function docstrings. All functions include:
- Complete type hints
- Input validation
- Error handling with descriptive messages
- Usage examples
- Time/space complexity notes

## Testing

Each function has comprehensive unit tests covering:
- Normal operation with typical inputs
- Edge cases (empty data, boundary values)
- Error cases (invalid types, invalid values)

Run tests with:
```bash
pytest pytest/unit/data_visualization_functions/
```

## Contributing

When adding new functions to this module:

1. Follow the one-function-per-file structure
2. Use NumPy-style docstrings
3. Include comprehensive type hints
4. Add input validation with descriptive errors
5. Create minimum 6 test cases per function
6. Update this README with new function descriptions
7. Update `__init__.py` and `__all__` exports

## Dependencies

- **Required**: matplotlib, numpy
- **Optional**: scipy (for Savitzky-Golay filter)

## License

This module is part of the Python Utilities Library.
