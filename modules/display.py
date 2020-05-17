'''
A module that contains functions to display MIZ data.
'''

import matplotlib.pyplot as plt
from matplotlib import colors

def plot_grid(grid, save=None):
    # Simulating the colors on the NIC website
    cmap = colors.ListedColormap(['yellow', 'red'])
    bounds = [0, .19, .81]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots()
    im = ax.imshow(grid, cmap=cmap, vmax=1, vmin=0, norm=norm)

    if save is not None:
        raise NotImplementedError("Can't save grid yet...")

    plt.show()

# TODO - Set up an animation plot
# eg;
# ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)