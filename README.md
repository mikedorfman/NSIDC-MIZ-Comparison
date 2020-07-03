# National Snow and Ice Data Center Marginal Ice Zone Comparison

## Project Overview
The ice surrounding Antarctica is critical to understand for several reasons; it teams with sea life sheltering in the broken ice, it drives distinct weather patterns, and it impacts crucial trade routes for ships.  It’s also essential to study the changing state and annual cycles of sea ice as ice caps shrink in a warming climate.  For these reasons, among others, it's important we fully realize the extent of this floating ice.

How do we define the extent of this floating ice?  Scientists use a term called Sea Ice Concentration, which is a proportion of sea ice to water surface.  The area between 80% sea ice to 10-20% sea ice is categorized as the Marginal Ice Zone, and that is where we’ll focus our attention in the comparison below. 

There are two products which offer varying views of this ice; one is a 30-year Climate Data Record from the National Snow and Ice Data Center (referred to below as the "CDR" product) and one is a 10-year operational product from the US National Ice Center (referred to below as the "NIC" product).  They paint very different pictures of the state of the ice. The NIC product is drawn by specialists using a variety of sources to identify two categories – Sea Ice Concentration values between 10% to 80%, and Sea Ice Concentration values 80% and greater.  The lower concentration represents the outer boundary of the Marginal Ice Zone and the higher concentration represents the inner boundary. The CDR product offers a more continuous view because it measures Sea Ice Concentration from 15% to 100% continuously instead of the two categories that the NIC data offers. It’s important to note that the outer perimeter is defined as 10% Sea Ice Concentration in the CDR as opposed to 15% in the NIC – given this difference, we expect the NIC outer perimeter to extend further north. Below are two visualizations of the products on the same day - note the two discrete values in the NIC data and the continuous values in the CDR data.

This repository provides a method of reproducing the output from this comparison as well as providing an easy way to run this comparison for specified days.  

## U.S. NIC Operational MIZ Product
The U.S. NIC Operation MIZ product classifies sea ice into two categories; between 10% and 80% sea ice concentration greater than 80% sea ice concentration.  This data is initially saved in shapefile format, then converted to ASCII, KMZ and png formats.  The U.S. NIC [daily graphics page](https://www.natice.noaa.gov/daily_graphics.htm) generally describes the process used to generate this product;

> The daily ice edge is analyzed by sea ice experts using multiple sources of near real time satellite data, derived satellite products, buoy data, weather, and analyst interpretation of current sea ice conditions.

Historical png images can be found [here](https://www.natice.noaa.gov/products/miz.html) and all other data types can be found [here](ftp://sidads.colorado.edu/DATASETS/NOAA/G10017/).  Data from this product spans from 2010-current.
[![US NIC MIZ Producct](https://www.natice.noaa.gov/images/polar_miz.png)](https://www.natice.noaa.gov/Main_Products.htm)

## NSIDC Passive-Microwave CDR MIZ Product
The NSIDC offers a climate data record of sea ice concentration derived from passive microwave data.  This dataset is generated from two commonly-used passive microwave algorithms then merged together based on the algorithm with the higher value. This data set spans 1987-current, however only the 2010-current data that overlaps with the NIC product was used in this comparison.  The CDR archive can be found [here](ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02202_V3) and additional information on this product can be found with the user guide [here](https://nsidc.org/data/g02202).  
[![US NIC MIZ Producct](https://ndownloader.figshare.com/files/23482928/preview/23482928/preview.jpg?private_link=4264c259caccf8e06253)](https://figshare.com/s/4264c259caccf8e06253)


## Important Differences Between Products
The NIC product user guide draft makes an important note that differentiates this product from the NSIDC dataset;

  >Mariners would not expect to encounter sea ice in significant concentrations when sailing outside of the line. Therefore, while it can be thought of as a 10% contour, on a practical level it functions as a contour between open ocean and ice at any concentration.

Therefore, the outer edge of the MIZ as shown by the US NIC product will likely be farther out to sea than the NSIDC product, since the lowest sea ice concentration measured by the latter is 15%.

Per the NSIDC user guide on the CDR product;

>...the concentration value given by the NASA Team algorithm and that given by the Bootstrap algorithm are compared; whichever value is greater is selected as the CDR value. This is done because both algorithms tend to underestimate ice concentration, however the source of this bias differs between algorithms (Meier et al. 2014).

If the passive microwave algorithms do typically underestimate the sea ice concentration values, then the same sea ice concentration thresholds for the inner and outer boundary of the MIZ would result in an MIZ that is further inland when compared to the NIC product.

## Running the Comparison

### Prerequisites
You must have git and Anaconda/Miniconda installed as well as sufficient storage to store inputs and outputs.  You'll need sufficient disk space to store all input files from the two sources.  These storage requirements may change depending on the date range you would like to download.  The USNIC CDR will require 2.3 mb per day downloaded and the NIC MIZ product will require roughly 1-2 mb per day downloaded.  This data will be downloaded to a "data" directory within this directory.

### Setup
1) Clone this repository.
2) Run `conda env create -f environment.yaml`.

### Running
1) There are two methods of running this comparison.  It can be run in one of two ways;  

    a) Run interactively with miz_comparison.ipynb through Jupyter Notebooks.  This is set up to run cells in sequential order and has thorough documentation cells.  
       
    b) Run through the compare_products.py script (**Note - script still under construction**).  This script will store outputs on disk or, if specified, in stdout.  For more information on how to use compare_products.py, run this script with the `--help` flag. All outputs, by default, will be stored in outputs/data within this directory.

**TODO; update this with any workflow changes**

## Example Usage

**Example usage to be built out further once comparison script is assembled**
To compare products between 20200101 and 20200102, generating all output;  
`python compare_products.py 20200101 20200102`  
To compare products between 20200101 and 20200102, generating csv only;  
`python compare_products.py 20200101 20200102 --output csv`  

Note - this comparison is designed to be run with the above-described datasets only - additional modifications will be necessary outside of comparing these two inputs (zipped shapefiles for USNIC MIZ product and netcdf files for NSIDC product).

## Directory Structure

* modules/ `Modules to assist in the comparison, display and download of files`
    * compare.py
    * display.py
    * io.py
* environment.yml `The environment definition for running the comparison`
* LICENSE `License file`
* miz_comparison.ipynb `Notebook that walks through the comparison process`
* README.md `This document`

**Note - the below data directory will be automatically generated by the scripts in this repository and is not stored in version control**
* data/  
    * antarctic|arctic
        * inputs/
            * cdr/ `Contains all NSIDC CDR MIZ products`
                * seaice_conc_daily_icdr_sh_f18_%Y%m%d_v01r00.nc
            * nic/ `Contains all USNIC MIZ products`
                * nic_miz%Y%jsc_pl_a.zip
        * outputs/ `Optional output files`
            * csv/
            * png/
            * gif/

## Resources
User Guide Draft - U.S. National Ice Center Daily Marginal Ice Zone Products, Version 1. 

User Guide Draft - National Snow and Ice Data Center Climate Data Record of Passive Microwave Sea Ice Concentration, Version 3.  Retrieved from https://nsidc.org/data/g02202

Meier, W. N., G. Peng, D. J. Scott, and M. H. Savoie. 2014. Verification of a new NOAA/NSIDC passive microwave sea-ice concentration climate record. Polar Research 33. doi:10.3402/polar.v33.21004.

