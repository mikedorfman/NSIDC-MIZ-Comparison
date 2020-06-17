'''
A module that contains functions to display MIZ data.
'''

import glob
import os

import matplotlib.image as mplimg
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import animation
import pathlib

# These are shared across functions in this module and must remain the same
FIG_DPI = 300
NIC_COLOR = 'blue'
CDR_COLOR = 'red'
ALPHA = .2

def create_basemap_plot(lats, lons, cdr, nic, save=None, show=True):
    '''
    Create a basemap plot of the cdr and nic data with spstere projection.

    TODO; make this function more generalized
    :param lats: Numpy array of lats (matches other array dimensions)
    :param lons: Numpy array of lons (matches other array dimensions)
    :param cdr: CDR array (matches other array dimensions)
    :param nic: NIC array (matches other array dimensions)
    :param save: Location to save png, bypassing save if None
    :param show: Display the plot
    :return:
    '''
    bounding_lat = -41.5
    # We only want the boolean "True" values contoured...this is the only way I could figure how to do that
    levels = [0.5, 1.5]

    fig, ax = plt.subplots(dpi=FIG_DPI)

    m = Basemap(
        ax=ax,
        projection='spstere', boundinglat=bounding_lat, lon_0=180,
        resolution='i', round=True
    )

    x, y = m(lons, lats)

    m.drawcoastlines(linewidth=.25)

    m.contourf(x, y, cdr, levels, colors=CDR_COLOR, alpha=ALPHA)
    m.contourf(x, y, nic, levels, colors=NIC_COLOR, alpha=ALPHA)

    if save is not None:
        os.makedirs(os.path.dirname(save), exist_ok=True)
        plt.savefig(save, dpi=FIG_DPI)

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

    fig, ax = plt.subplots(dpi=FIG_DPI)
    plt.axis('off')

    plt.legend([plt.Rectangle((0, 0), 1, 1, fc=CDR_COLOR, alpha=ALPHA),
                plt.Rectangle((0, 0), 1, 1, fc=NIC_COLOR, alpha=ALPHA),
                plt.Rectangle((0, 0), 1, 1, fc='purple', alpha=ALPHA)],
               ['CDR', 'NIC', 'Overlap'], loc='lower left')

    img = mplimg.imread(files[0])
    imshow = plt.imshow(img, aspect='equal')

    def animate(i):
        img = mplimg.imread(files[i])
        imshow.set_data(img)
        ax.set_title(f"Sea Ice Concentration from 20%-100%\n {os.path.basename(files[i])[:8]}")

    ani = animation.FuncAnimation(fig, animate, len(files), interval=100)

    # Make sure our save path exists
    pathlib.Path(os.path.basename(save_path)).mkdir(parents=True, exist_ok=True)
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

