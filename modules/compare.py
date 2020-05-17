'''
A module that contains functions to help compare MIZ products.
'''

import geopandas as gpd
import netCDF4 as nc
import numpy as np
import rasterio
import rasterio.features

import os

def nic_file_to_grid(nic_file):
    # basic check to make sure we're dealing with a zipfile
    assert os.path.splitext(nic_file)[1] == ".zip"

    icecode_mapping = {
        "CT18": .18,
        "CT81": .8
    }

    gdf = gpd.read_file("zip://" + nic_file)

    # From the cdr netcdf
    # TODO - pass this into the function based on the netcdf vals
    southern_view_crs = "+proj=stere +lat_0=-90 +lat_ts=-70 +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=6378273 +b=6356889.449 +units=m +no_defs"
    gdf = gdf.to_crs(southern_view_crs)
    shapes = ((geom, icecode_mapping[value]) for geom, value in zip(gdf.geometry, gdf.ICECODE))

    # From the cdr netcdf
    # TODO - pass this into the function based on the netcdf vals
    geo_transform = rasterio.transform.from_origin(-3950000.0, 4350000.0, 25000.0, 25000.0)
    return rasterio.features.rasterize(shapes=shapes,
                                       transform=geo_transform,
                                       # From the cdr netcdf
                                       # TODO - pass this into the function based on the netcdf vals
                                       out_shape=(332, 316))

def cdr_file_to_grid(cdr_file_path):
    cdr_file = nc.Dataset(cdr_file_path)
    ds_squeezed = np.squeeze(cdr_file.variables['seaice_conc_cdr'][:])
    return ds_squeezed