'''
A module that contains functions to help compare MIZ products.
'''

import numpy as np
import pandas as pd

import download as dwn

# Each grid cell is 25 km2
GRID_CELL_AREA = 25*25


def median_cdr(thresh, start, end, folder, hemisphere):
    """
    Return the median CDR grid values between the provided dates and at the specified threshold
    :param thresh: Threshold for median sea ice
    :param start: Start date
    :param end: End date
    :param folder: Folder to look for data
    :param hemisphere: Hemisphere
    :return:
    """
    return _median_grid(dwn.get_cdr, thresh, start, end, folder, hemisphere)


def median_nic(thresh, start, end, folder, hemisphere):
    """
    Return the median NIC grid values between the provided dates and at the specified threshold
    :param thresh: Threshold for median sea ice
    :param start: Start date
    :param end: End date
    :param folder: Folder to look for data
    :param hemisphere: Hemisphere
    :return:
    """
    return _median_grid(dwn.get_nic, thresh, start, end, folder, hemisphere)


def _median_grid(retrieval_func, thresh, start, end, folder, hemisphere):
    """
    Return the median grid values between the provided dates and at the specified threshold
    :param retrieval_func: Function that is called with date, folder and hemisphere to retrieve grid
    :param thresh: Threshold for median sea ice
    :param start: Start date
    :param end: End date
    :param folder: Folder to look for data
    :param hemisphere: Hemisphere
    :return:
    """
    sum_grid = None
    counter = 0

    # should always be 0.5 - we're looking for qualifying ice concentrations 50% of the time or greater.
    median_percentage = 0.5

    # This one loops on a daily frequency
    for date in pd.date_range(start=start, end=end):
        try:
            grid = retrieval_func(date, folder, hemisphere)
            mask = np.where(grid >= thresh, True, False)

            # Either add onto the sum grid or make the sum grid the mask, updated as int type (instead of bool)
            sum_grid = sum_grid + mask if sum_grid is not None else 1*mask
            counter += 1
        except Exception as exc:
            print(f"Could not run {date} because {exc}; continuing")

    percent_hit_grid = sum_grid / counter

    return np.where(percent_hit_grid >= median_percentage, True, False)


def calculate_ice_area(cdr_grid, nic_grid, min_sic_nic, max_sic_nic, min_sic_cdr, max_sic_cdr, verbose=False):
    """
    Calculate the total ice area between two thresholds
    :param cdr_grid: np array - cdr data array
    :param nic_grid: np array - nic data array - same shape as cdr_grid
    :param min_sic_nic: float - 0 to 1 - fractional percentage SIC lower threshold for nic data
    :param max_sic_nic: float - 0 to 1 - fractional percentage SIC upper threshold for nic data
    :param min_sic_cdr: float - 0 to 1 - fractional percentage SIC lower threshold for cdr data
    :param max_sic_cdr: float - 0 to 1 - fractional percentage SIC upper threshold for cdr data
    :param verbose: bool - Add additional output
    :return:
    """

    # We need a lower threshold that is less than an upper threshold
    assert min_sic_nic <= max_sic_nic
    assert min_sic_cdr <= max_sic_cdr

    cdr_cell_count = np.where((cdr_grid >= min_sic_cdr) &
                              (cdr_grid <= max_sic_cdr) &
                              (cdr_grid >= 0), True, False).sum()
    nic_cell_count = np.where((nic_grid >= min_sic_nic) &
                              (nic_grid <= max_sic_nic) &
                              (cdr_grid >= 0), True, False).sum()

    if verbose:
        cdr_initial_count = np.where((cdr_grid > 0), True, False).sum()
        nic_initial_count = np.where((nic_grid > 0), True, False).sum()

        print(f"CDR went from {cdr_initial_count} unfiltered to {cdr_cell_count}")
        print(f"NIC went from {nic_initial_count} unfiltered to {nic_cell_count}")

    cdr_area = cdr_cell_count * GRID_CELL_AREA
    nic_area = nic_cell_count * GRID_CELL_AREA

    return cdr_area, nic_area


def calculate_ice_footprint_diff(nic_grid, min_nic, max_nic, cdr_grid, min_cdr, max_cdr):
    """
    First, calculate a boolean array between the min and max thresholds for both nic grids and cdr grids.  Then
    create an array that represents the following -
        - value "1" - nic and cdr both True
        - value "2" - nic and cdr both False
        - value "3" - nic True and cdr False
        - value "4" - cdr True and nic False

    :param nic_grid: numpy arr - nic data
    :param min_nic: float - min nic threshold
    :param max_nic: float - max nic threshold
    :param cdr_grid: numpy arr - cdr data
    :param min_cdr: float - min cdr threshold
    :param max_cdr: float - max cdr threshold
    :return: numpy array as described above
    """

    overlap_grid = np.zeros_like(cdr_grid)

    # Threshold the grids
    cdr_grid = np.where((cdr_grid >= min_cdr) & (cdr_grid <= max_cdr), True, False)
    nic_grid = np.where((nic_grid >= min_nic) & (nic_grid <= max_nic), True, False)

    # Create a new grid and populate
    overlap_grid[(nic_grid & cdr_grid)] = 1
    overlap_grid[(nic_grid & ~cdr_grid)] = 2
    overlap_grid[(~nic_grid & cdr_grid)] = 3
    overlap_grid[(~nic_grid & ~cdr_grid)] = 4
    return overlap_grid
