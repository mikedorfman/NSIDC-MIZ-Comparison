'''
A module that contains functions to display MIZ data.
'''

import glob
import os
import pathlib

from matplotlib import colors
import matplotlib.image as mplimg
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.basemap import Basemap
import numpy as np

# These are shared across functions in this module and must remain the same
FIG_DPI = 300
NIC_COLOR = 'blue'
CDR_COLOR = 'red'
ALPHA = .5


def create_basemap_plot(title, lats, lons, meta, grids, save=None, show=True, legend=True):
    """
    Create a basemap plot of either the southern hemisphere or northern hemisphere with the provided grid(s) overlayed
    :param title: str - Title for the plot
    :param lats: np array - Latitude values associated with the data
    :param lons: np array - Longitude values associated with the data
    :param meta: Projection information from the CDR NetCDF
    :param grids: list of dictionaries - {
            'color' - the color of the plotted data.  If no color specified, then a plt.cm.Blues cmap applied.
            'grid' - the numpy array to plot.  Must match dimensions of lats/lons.
            'legend_label' - The label for the plot legend for this dataset.  Ignored if legend keyword is False.
        }
    :param save: str - Path to save plot as a png.  If None, don't save.
    :param show: bool - display the plot after creating it.
    :param legend: bool - Include a legend.  Legend information must also be in the grid dictionary.
    :return:
    """
    fig, axis = plt.subplots(dpi=300, figsize=(7, 7))

    height = meta.grid_boundary_top_projected_y - meta.grid_boundary_bottom_projected_y
    width = meta.grid_boundary_right_projected_x - meta.grid_boundary_left_projected_x

    # I don't understand why basemap isn't respecting the bounding lat.  Data is cut off in the
    # north if we don't adjust the standard parallel.
    standard_parallel = 20 if meta.standard_parallel == 70 else meta.standard_parallel

    bmap = Basemap(
        ax=axis,
        projection='stere',
        lat_0=meta.latitude_of_projection_origin,
        lat_ts=standard_parallel,
        lon_0=meta.longitude_of_projection_origin,
        resolution='i',
        round=True,
        height=height,
        width=width
    )

    bmap.drawcoastlines(linewidth=.25)
    bmap.drawmeridians(np.arange(0, 360, 30), linewidth=.1)
    bmap.drawparallels(np.arange(-90, 90, 10), linewidth=.1)
    x_coord, y_coord = bmap(lons, lats)
    for grid in grids:
        if 'color' in grid.keys():
            cmap = colors.ListedColormap(grid['color'])
            cmap.set_bad(alpha=0)
        else:
            # Choose a good cmap for ice
            cmap = plt.cm.Blues

        plt.imshow(np.ma.masked_where(grid['grid'] <= 0, grid['grid']),
                   cmap=cmap,
                   vmin=0,
                   vmax=1,
                   alpha=ALPHA,
                   extent=(x_coord.min(), x_coord.max(), y_coord.min(), y_coord.max()))
    if 'color' in grids[0].keys() and legend:
        plt.legend([plt.Rectangle((0, 0), 1, .1, fc=grid['color'], alpha=.5) for grid in grids],
                   [grid['legend_label'] for grid in grids], loc='lower left', ncol=2)
    else:
        cbar = plt.colorbar()
        cbar.set_label('Sea Ice Concentration')

    axis.set_title(title)

    if save is not None:
        os.makedirs(os.path.dirname(save), exist_ok=True)
        plt.savefig(save, dpi=500)

    if show:
        plt.show()

    plt.close(fig)


def images_to_animation(image_folder, save_path):
    '''
    Convert images to animation.  Animation will be created by globbing all .png files in folder
    :param folder: Folder to glob images from
    :return:
    '''

    files = glob.glob(os.path.join(image_folder, "*.png"))
    if not files:
        raise ValueError(f"Couldn't find any png files in {image_folder}")

    fig, _ = plt.subplots(dpi=FIG_DPI)
    plt.axis('off')

    img = mplimg.imread(files[0])
    imshow = plt.imshow(img, aspect='equal')

    def animate(i):
        img = mplimg.imread(files[i])
        imshow.set_data(img)

    ani = animation.FuncAnimation(fig, animate, len(files), interval=100)

    # Make sure our save path exists
    pathlib.Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
    ani.save(save_path)


def plot_hist(data):
    '''
    Plot a histogram of the provided data in bins of 1-100
    :param data: data to be plotted
    :return:
    '''
    # bins of .01-1.00 in increments of .01
    bins = [i/100 for i in range(1, 100, 1)]
    plt.hist(data, density=True, bins=bins)  # `density=False` would make counts
    plt.ylabel('Probability')
    plt.xlabel('Data')
    plt.show()
