'''
A module that contains functions to display MIZ data.
'''

import glob
import os
import pathlib

from matplotlib import colors
import matplotlib.image as mplimg
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import animation
import numpy as np

# These are shared across functions in this module and must remain the same
FIG_DPI = 300
NIC_COLOR = 'blue'
CDR_COLOR = 'red'
ALPHA = .2


def create_basemap_plot(title, lats, lons, meta, grid, save=None, show=True, legend=True):
    fig, ax = plt.subplots(dpi=300)

    height = meta.grid_boundary_top_projected_y - meta.grid_boundary_bottom_projected_y
    width = meta.grid_boundary_right_projected_x - meta.grid_boundary_left_projected_x

    # I don't understand why basemap isn't respecting the bounding lat.  Data is cut off in the
    # north if we don't adjust the standard parallel.
    standard_parallel = 20 if meta.standard_parallel == 70 else meta.standard_parallel

    m = Basemap(
        ax=ax,
        projection='stere',
        lat_0=meta.latitude_of_projection_origin,
        lat_ts=standard_parallel,
        lon_0=meta.longitude_of_projection_origin,
        boundinglat=0,
        resolution='i',
        round=True,
        height=height,
        width=width
    )

    m.drawcoastlines(linewidth=.25)
    m.drawmeridians(np.arange(0, 360, 30), linewidth=.1)
    m.drawparallels(np.arange(-90, 90, 10), linewidth=.1)
    x, y = m(lons, lats)
    for gr in grid:
        if 'color' in gr.keys():
            cmap = colors.ListedColormap(gr['color'])
            cmap.set_bad(alpha=0)
        else:
            # Choose a good cmap for ice
            cmap = plt.cm.Blues

        plt.imshow(np.ma.masked_where(gr['grid'] <= 0, gr['grid']),
                   cmap=cmap,
                   vmin=0,
                   vmax=1,
                   extent=(x.min(), x.max(), y.min(), y.max()))
    if 'color' in grid[0].keys() and legend:
        plt.legend([plt.Rectangle((0, 0), 1, .1, fc=gr['color'], alpha=.5) for gr in grid],
                   [gr['legend_label'] for gr in grid], loc='lower left', ncol=2)
    else:
        cbar = plt.colorbar()
        cbar.set_label('Sea Ice Concentration')

    ax.set_title(title)

    if save is not None:
        os.makedirs(os.path.dirname(save), exist_ok=True)
        plt.savefig(save, dpi=FIG_DPI)

    if show:
        plt.show()


def images_to_animation(image_folder, save_path):
    '''
    Convert images to animation.  Animation will be created by globbing all .png files in folder
    :param folder: Folder to glob images from
    :return:
    '''

    files = glob.glob(os.path.join(image_folder, "*.png"))
    fig, ax = plt.subplots(dpi=FIG_DPI)
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

