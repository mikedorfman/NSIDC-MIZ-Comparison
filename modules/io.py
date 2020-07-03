"""
A module to assist in the downloading of MIZ files and loading into memory (eg pandas df)
"""

import datetime
import os
from pathlib import Path
import urllib.request

from joblib import Parallel, delayed
import geopandas as gpd
import netCDF4 as nc
import numpy as np
import pandas as pd
import rasterio
import rasterio.features


def check_hemisphere(hemisphere):
    """
    Checks to make sure hemisphere is either 'north' or 'south'.
    :param hemisphere: string - 'south' or 'north' - hemisphere to convert
    :return:
    """
    assert hemisphere in ['north', 'south']


def cdr_to_np(start, end, cdr_input_folder, clobber=False, hemisphere='south', verbose=False):
    """
    Converts CDR netCDF input files to intermediate Numpy arrays saved to disk.  Uses joblib with a threading backend
    and runs concurrently based on the number of CPUs available.
    :param start: datetime - start date to convert netcdf to numpy array
    :param end: datetime - end date to convert netcdf to numpy array
    :param cdr_input_folder: string - input folder to pull CDR netcdfs from
    :param clobber: bool - overwrite the output if present
    :param hemisphere: string - 'south' or 'north' - hemisphere to convert
    :param verbose: bool - increase verbosity
    :return:
    """
    check_hemisphere(hemisphere)
    analyzed_dates = pd.date_range(start=start, end=end)
    Parallel(n_jobs=-1, backend='threading')(delayed(_cdr_to_np_grid)
                                             (dt, cdr_input_folder, hemisphere, clobber, verbose)
                                             for dt in analyzed_dates)


def datetime_to_cdr_fname(dt, hemisphere):
    """
    Generate a CDR FTP path given the datetime hemisphere
    :param dt: datetime - desired datetime for file
    :param hemisphere: string - 'south' or 'north' - hemisphere to generate the filename for
    :return:
    """
    check_hemisphere(hemisphere)
    # Before this date, files had a different naming convention and live in a different spot
    cutoff = datetime.datetime(2019, 1, 1)
    hemisphere_letter = hemisphere[0]  # "n" for north, "s" for south
    if dt < cutoff:
        ftp_dir = f"ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02202_V3/{hemisphere}/daily/{dt:%Y}/"
        ftp_file = f"seaice_conc_daily_{hemisphere_letter}h_f17_{dt:%Y%m%d}_v03r01.nc"
    else:
        ftp_dir = f"ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G10016/{hemisphere}/daily/{dt:%Y}/"
        ftp_file = f"seaice_conc_daily_icdr_{hemisphere_letter}h_f18_{dt:%Y%m%d}_v01r00.nc"
    return ftp_dir, ftp_file


def datetime_to_nic_fname(dt, hemisphere):
    """
    Generate an NIC FTP path given the datetime hemisphere
    :param dt: datetime - desired datetime for file
    :param hemisphere: string - 'south' or 'north' - hemisphere to generate the filename for
    :return:
    """
    check_hemisphere(hemisphere)
    hemisphere_letter = hemisphere[0]  # "n" for north, "s" for south
    ftp_dir = f"ftp://sidads.colorado.edu/DATASETS/NOAA/G10017/{hemisphere}/{dt:%Y}/"
    ftp_file = f"nic_miz{dt:%Y%j}{hemisphere_letter}c_pl_a.zip"
    return ftp_dir, ftp_file


def datetime_to_cdr_fname_grid(dt, hemisphere):
    """
    Generate a numpy grid filename given the datetime hemisphere.  This grid is used to speed up access to this data.
    :param dt: datetime - desired datetime for file
    :param hemisphere: string - 'south' or 'north' - hemisphere to generate the filename for
    :return:
    """
    check_hemisphere(hemisphere)
    return f'{dt:%Y%m%d}_{hemisphere}_cdr.npy'


def datetime_to_nic_fname_grid(dt, hemisphere):
    """
    Generate a numpy grid filename given the datetime hemisphere.  This grid is used to speed up access to this data.
    :param dt: datetime - desired datetime for file
    :param hemisphere: string - 'south' or 'north' - hemisphere to generate the filename for
    :return:
    """
    check_hemisphere(hemisphere)
    return f'{dt:%Y%m%d}_{hemisphere}_nic.npy'


def download_range(sftp_formatter, start, end, local_dir, hemisphere='south', no_clobber=True, verbose=False):
    """
    Download a temporal range of data for a MIZ product
    :param sftp_formatter: Formatter function that returns the sftp directory and file names as tuples when provided a
     date and hemisphere
    :param start: datetime - start time for period downloaded
    :param end: datetime - end time for period downloaded
    :param local_dir: str - Local directory to save files
    :param hemisphere: str - hemisphere - either north for the arctic or south for antarctica
    :param no_clobber: bool - Don't clobber files that already exist (existence based on matching filename)
    :param verbose: bool - Add additional output
    :return:
    """
    check_hemisphere(hemisphere)

    # Make directory if it doesn't exist
    Path(local_dir).mkdir(parents=True, exist_ok=True)

    for download_date in pd.date_range(start=start, end=end):
        ftp_dir, ftp_file = sftp_formatter(download_date, hemisphere)
        ftp_full = ftp_dir + ftp_file
        file_full = os.path.join(local_dir, ftp_file)

        try:
            if no_clobber and os.path.exists(file_full):
                # No clobber is specified and we already have a file
                if verbose:
                    print("Skipping %s - already exists" % ftp_full)
                continue

            if verbose:
                print("Downloading %s" % ftp_full)
            urllib.request.urlretrieve(ftp_full, file_full)
        except Exception as e:
            if verbose:
                print(f"Could not download {ftp_full} to {file_full} for some reason; {e}")


def download_cdr_miz_range(*args, **kwargs):
    """
    Downloads a temporal range of CDR data.  See datetime_to_cdr_fname for args and kwargs.
    :param args: Shares with datetime_to_cdr_fname
    :param kwargs: Shares with datetime_to_cdr_fname
    :return:
    """
    download_range(datetime_to_cdr_fname, *args, **kwargs)


def download_nic_miz_range(*args, **kwargs):
    """
    Downloads a temporal range of NIC data.  See datetime_to_nic_fname for args and kwargs.
    :param args: Shares with datetime_to_nic_fname
    :param kwargs: Shares with datetime_to_nic_fname
    :return:
    """
    download_range(datetime_to_nic_fname, *args, **kwargs)


def get_nic(dt, dirname, hemisphere):
    """
    Loads an NIC array stored on disk to a numpy array in memory.
    :param dt: datetime - datetime to load
    :param dirname: string - Directory to search for files
    :param hemisphere: str - hemisphere - either north for the arctic or south for antarctica
    :return:
    """
    check_hemisphere(hemisphere)
    fname = datetime_to_nic_fname_grid(dt, hemisphere)
    full_fname = os.path.join(dirname, fname)
    return np.load(full_fname)


def get_cdr(dt, dirname, hemisphere):
    """
    Loads a CDR numpy array stored on disk to a numpy array in memory.
    :param dt: datetime - datetime to load
    :param dirname: string - Directory to search for files
    :param hemisphere: str - hemisphere - either north for the arctic or south for antarctica
    :return:
    """
    check_hemisphere(hemisphere)
    fname = datetime_to_cdr_fname_grid(dt, hemisphere)
    full_fname = os.path.join(dirname, fname)
    return np.load(full_fname)


def get_cdr_metadata(cdr_file_path):
    """
    From a CDR netcdf, extract the array shape, proj4 text and extent.
    :param cdr_file_path: string - path to the CDR file
    :return: (
        lats,
        lons,
        projection variable data
    )
    """
    cdr_file = nc.Dataset(cdr_file_path)

    lats_squeezed = np.squeeze(cdr_file.variables['latitude'][:])
    lons_squeezed = np.squeeze(cdr_file.variables['longitude'][:])
    nc_proj_data = cdr_file.variables['projection']

    return lats_squeezed, lons_squeezed, nc_proj_data


def nic_to_np(start, end, nic_input_folder, cdr_meta, shape, clobber=False, hemisphere='south', verbose=False):
    """
    Runs _nic_to_np grid on all dates from start to end.
    :param start: datetime - start time for period downloaded
    :param end: datetime - end time for period downloaded
    :param nic_input_folder: string - input folder to look for zipped shapefiles
    :param cdr_meta: CDR projection information
    :param shape: tuple of ints - shape of the data array
    :param clobber: bool - overwrite output if it exists
    :param hemisphere: string - 'south' or 'north' - hemisphere to process
    :param verbose: bool - increase verbosity
    :return:
    """
    check_hemisphere(hemisphere)
    analyzed_dates = pd.date_range(start=start, end=end)
    Parallel(n_jobs=-1, backend='threading')(delayed(_nic_to_np_grid)
                                             (dt, nic_input_folder, hemisphere, clobber, cdr_meta, shape, verbose)
                                             for dt in analyzed_dates)


def _cdr_to_np_grid(dt, input_folder, hemisphere, clobber, verbose):
    """
    Loads the CDR netcdf data into memory then saves to disk as a numpy array for easy access.
    :param dt: datetime - Date to process
    :param input_folder: string - Input folder that holds CDR netcdf files and numpy files
    :param hemisphere: string - 'south' or 'north' - hemisphere to process
    :param clobber: bool - overwrite output
    :param verbose: bool - increase verbosity
    :return:
    """
    check_hemisphere(hemisphere)
    if verbose:
        print(f"Running {dt} for cdr")
    try:
        grid_fname = os.path.join(input_folder, datetime_to_cdr_fname_grid(dt, hemisphere))
        if clobber or not os.path.exists(grid_fname):
            _, cdr_fname = datetime_to_cdr_fname(dt, hemisphere)
            cdr_file = nc.Dataset(os.path.join(input_folder, cdr_fname), 'r')
            grid = np.squeeze(cdr_file.variables['seaice_conc_cdr'][:])

            # This is a masked array - replace all masked values and all <0 values (flags) with 0
            grid = grid.filled(0)
            grid[grid < 0] = 0

            np.save(grid_fname, grid)
    except Exception as e:
        if verbose:
            print(f"COULDN'T RUN {dt} BECAUSE {e}")


def _nic_to_np_grid(dt, input_folder, hemisphere, clobber, cdr_meta, shape, verbose):
    """
    Rasterizes an NIC shapefile input and saves to disk as a numpy array.
    :param dt: datetime - Date to process
    :param input_folder: string - Input folder to find NIC zipped shapefiles
    :param hemisphere: string - 'south' or 'north' - hemisphere to process
    :param clobber: bool - overwrite output
    :param cdr_meta: cdr projection information
    :param verbose: bool - increase verbosity
    :return:
    """
    check_hemisphere(hemisphere)
    if verbose:
        print(f"Running {dt} for nic")

    try:
        grid_fname = os.path.join(input_folder, datetime_to_nic_fname_grid(dt, hemisphere))
        if clobber or not os.path.exists(grid_fname):
            _, nic_fname = datetime_to_nic_fname(dt, hemisphere)
            nic_full_fname = os.path.join(input_folder, nic_fname)

            # basic check to make sure we're dealing with a zipfile
            assert os.path.splitext(nic_full_fname)[1] == ".zip"
            icecode_mapping = {
                "CT18": .18,
                "CT81": .8
            }

            gdf = gpd.read_file("zip://" + nic_full_fname)
            gdf = gdf.to_crs(cdr_meta.proj4text)

            shapes = ((geom, icecode_mapping[value]) for geom, value in zip(gdf.geometry, gdf.ICECODE))
            extent = cdr_meta.GeoTransform.split(" ")

            # The "extent" has the top y, left x values in it...but accessing them from gir grid_boundary_[left|top]
            # _projected_[y|x] is more clear.  Unfortunately, the order of GeoTransform and what from_origin is
            # looking for don't line up.

            top_y = cdr_meta.grid_boundary_top_projected_y
            left_x = cdr_meta.grid_boundary_left_projected_x
            pixel_y = float(extent[5])
            pixel_x = float(extent[1])

            geo_transform = rasterio.transform.from_origin(left_x,
                                                           top_y,
                                                           pixel_x,
                                                           pixel_y)

            grid = rasterio.features.rasterize(shapes=shapes,
                                               transform=geo_transform,
                                               fill=-1,
                                               out_shape=shape)

            np.save(grid_fname, grid)
    except Exception as e:
        if verbose:
            print(f"COULDN'T RUN {dt} BECAUSE {e}")
