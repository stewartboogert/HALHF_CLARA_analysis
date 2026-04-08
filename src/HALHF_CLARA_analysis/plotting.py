from typing import List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.colors import Normalize
from matplotlib.figure import Figure

def plot_grouped_waterfall(
    traces,
    group_values: Optional[List[float]] = None,
    group_label: Optional[str] = None,
    group_units: Optional[str] = None,
    coord_name = 'x',
    figsize: Tuple[int, int] = (24, 8),
    xtick_rotation: int = 90,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    cmap='magma',
    ax: Optional[Axes] = None,
    add_colorbar: bool = True,
    cbar_ax=None,
    linestyle: str = '-',
    linealpha: float = 1,
    linecolor: str = 'k',
    linewidth: float = 1,
    norm: Optional[Normalize] = None,
    rasterize: bool = False,
) -> Tuple[Figure, Axes]:
    """
    Plots a grouped waterfall plot.

    Parameters:
    - traces (List[xr.DataArray]): The trace data to plot.
    - group_values (Optional[List[float]], optional): Values to group the traces by.
    - group_label (Optional[str], optional): Label for the group axis.
    - group_units (Optional[str], optional): Units for the group axis.
    - figsize (Tuple[int, int], optional): Figure size, default is (24, 8).
    - xtick_rotation (int, optional): Rotation of x-tick labels, default is 90.
    - vmin (float, optional): Minimum value for the colormap.
    - vmax (Optional[float], optional): Maximum value for the colormap.
    - cmap (Union[str, plt.cm.Colormap], optional): Colormap to use for the plot.
    - ax (Optional[Axes], optional): Axis to plot on. Creates new if None.
    - add_colorbar (bool, optional): Whether to add a colorbar.
    - linestyle (str, optional): Style of the line separating groups.
    - linealpha (float, optional): Alpha transparency of the line.
    - linecolor (str, optional): Color of the line.
    - linewidth (float, optional): Width of the line.
    - norm (Optional[Normalize], optional): Normalization for the colormap.
    - rasterize (bool, optional): Whether to rasterize the plot (useful for large data).

    Returns:
    - Tuple[Figure, Axes]: The figure and axis objects.
    """

    # Prepare the DataFrame from traces and group values
    traces = [xr.DataArray(trace , coords = {coord_name : np.arange(0 , len(trace))}) for trace in traces]
    df = pd.DataFrame({'traces': traces, 'group_values': group_values})

    # Create plot and axis if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = plt.gcf()

    wf_parts: List[xr.DataArray] = []
    xticks: List[float] = []
    xtick_labels: List[str] = []
    group_start = 0

    # Iterate over grouped traces and prepare for concatenation
    for val, group_shots in df.groupby('group_values'):
        group_end = group_start + len(group_shots)

        wf_parts += list(group_shots['traces'])
        xticks.append(group_start + len(group_shots) / 2)
        xtick_labels.append(f'{val:.2f}')

        ax.axvline(
            group_end - 0.5,
            color=linecolor,
            linewidth=linewidth,
            alpha=linealpha,
            linestyle=linestyle,
        )

        group_start = group_end

    # Concatenate the grouped traces and transpose for plotting
    wf = xr.concat(wf_parts, dim='shots').transpose()

    # Plot the waterfall image
    wf_im = wf.plot(
        ax=ax,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        add_colorbar=add_colorbar,
        cbar_ax=cbar_ax,
        norm=norm,
    )

    # Rasterize the plot if specified
    if rasterize:
        wf_im.set_rasterized(True)

    # Set x-ticks and labels
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, rotation=xtick_rotation)

    # Set x-axis label with optional units
    group_units_str = f' [{group_units}]' if group_units else ''
    ax.set_xlabel(f'{group_label}{group_units_str}')

    # Adjust layout
    fig.subplots_adjust(bottom=0.2)

    return fig, ax