'''
A module to assist in the downloading of MIZ files and loading into memory (eg pandas df)
'''

import datetime
import os
import urllib.request


def download_cdr_miz_range(start, end, hemi='south', local_dir=os.path.join("data", "inputs", "cdr"), no_clobber=True,
                           verbose=False):
    '''
    Downloads a time range of MIZ ftp files.  Inclusive of start and end times.
    :param start: datetime - start time for period downloaded
    :param end: datetime - end time for period downloaded
    :param hemi: string - 'north' or 'south' defining which hemisphere to download
    :return:
    '''
    assert hemi in ['north', 'south']
    files = []

    download_date = start

    while download_date <= end:
        ftp_dir = f"ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G10016/{hemi}/daily/{download_date:%Y}/"
        ftp_file = f"seaice_conc_daily_icdr_sh_f18_{download_date:%Y%m%d}_v01r00.nc"
        ftp_full = ftp_dir + ftp_file
        file_full = os.path.join(local_dir, ftp_file)

        files.append(file_full)
        if no_clobber and os.path.exists(file_full):
            # No clobber is specified and we already have a file
            if verbose:
                print("Skipping %s - already exists" % ftp_full)
            download_date += datetime.timedelta(days=1)
            continue
        print("Downloading %s" % ftp_full)
        urllib.request.urlretrieve(ftp_full, file_full)
        download_date += datetime.timedelta(days=1)
    return files


def download_nic_miz_range(start, end, hemi='south', local_dir=os.path.join("data", "inputs", "nic"), no_clobber=True,
                           verbose=False):
    '''
    Downloads a time range of MIZ ftp files.  Inclusive of start and end times.
    :param start: datetime - start time for period downloaded
    :param end: datetime - end time for period downloaded
    :param hemi: string - 'north' or 'south' defining which hemisphere to download
    :return:
    '''
    assert hemi in ['north', 'south']
    ftp_dir_fmt = "ftp://sidads.colorado.edu/DATASETS/NOAA/G10017/{hemi}/%Y/".format(hemi=hemi)
    ftp_shp_fmt = "nic_miz%Y%jsc_pl_a.zip"
    ftp_fmt = ftp_dir_fmt + ftp_shp_fmt
    files = []

    download_date = start
    while download_date <= end:
        ftp_shp_name = download_date.strftime(ftp_shp_fmt)
        ftp_name = download_date.strftime(ftp_fmt)
        file_name = os.path.join(local_dir, ftp_shp_name)
        files.append(file_name)
        if no_clobber and os.path.exists(file_name):
            # No clobber is specified and we already have a file
            if verbose:
                print("Skipping %s - already exists" % ftp_name)
            download_date += datetime.timedelta(days=1)
            continue
        print("Downloading %s" % ftp_name)
        # TODO - check retrieve_status
        retrieve_status = urllib.request.urlretrieve(ftp_name, file_name)
        download_date += datetime.timedelta(days=1)
    return files