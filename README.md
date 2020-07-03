#Edge of Antarctica; Looking Into Where Ice and Water Mix

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
You must have git and Anaconda/Miniconda installed as well as sufficient storage to store inputs and outputs.  You'll need sufficient disk space to store all input files from the two sources.  These storage requirements may change depending on the date range you would like to download.  The USNIC CDR will require 2.3 mb per day downloaded and the NIC MIZ product will require roughly 1-2 mb per day downloaded.  This data will be downloaded to a "data" directory within this directory.  Additionally, there will be a ~1 mb file generated for each daily file.  Finally, you will have to confirm you have sufficient space to store all desired output (several mb per day at the most).

### Setup
1) Clone this repository.
2) Run `conda env create -f environment.yaml`.

### Running
1) There are two methods of running this comparison.  It can be run in one of two ways;

    a) Run interactively with miz_comparison.ipynb through Jupyter Notebooks.  This is set up to run cells in sequential order and has thorough documentation cells.  Open open `Edge of Antarctica; Looking into where ice and water mix.ipynb` to get started.  You may also view the HTML slides - a static snapshot of this Jupyter Notebook including ithe pre-generated images.

    b) Run through the main.py script.  All outputs, by default, will be stored in outputs/data within this directory.  Some examples with running this script;
      -  `python modules/main.py 20200130 20200220 --daily-plots-combined --cdr-plotting-thresh 0.8 --nic-plotting-thresh 0.8 --hemisphere south` - generates daily plots of the southern hemisphere showing the extent of the sea ice at the 80% sea ice concentration threshold.
      -  `python modules/main.py 20200130 20200220 --daily-plots --plot-cdr --plot-nic --hemisphere north` - creates individual plots (two plots per day) for the northern hemisphere - each plot showing the extent of either the CDR ice or NIC ice at the default 80% sea ice concentration.
      -  `python modules/main.py 20200130 20200220 --median-plot` - Creates the monthly median sea ice extent plots for the provided dates for the default southern hemisphere and 80% sea ice concentration.
      -  `python modules/main.py 20200130 20200220 --stats` - Calculates the area of sea ice measured by each product above a certain threshold at specified intervals.  If the defaults are used, then this will calculate both NIC and CDR sea ice areas within 5% SIC, 10% SIC, 15% SIC...and 95% SIC.
      -  `python modules/main.py 20200130 20200220 --animate data/sout/outputs/combined/png` - Creates an mp4 animation of the files in the provided directory and saves the mp4 alongside those files.  Files are added to the animation in the default order which they appear in the filesystem.  Start time and end time are ignored since this is just grabbing the files in the provided folder.
    run `python modules/main.py --help` for more information.  You may also pass more than one flag at a time to generate multiple products.

## Workflow
The Jupyter Notebook follows the following workflow;
 - For each day in the analysis:
     - Download USNIC shapefile data from NSIDC FTP, skipping files that already exist.
     - Download NetCDF CDR Data from NSIDC FTP, skipping files that already exist.
     - Load CDR NetCDFs, extract the `seaice_conc_cdr` variable into a numpy array and save to disk as a .npy file.
     - Load NIC data, rasterize to the same grid as the NIC data and save to disk as a .npy file.
 
 - Generate daily view plots;
     - For each day analyzed;
         - Load the .npy file for NIC
         - Load the .npy file for CDR
         - Threshold based on desired sea ice concentration threshold
         - Create basemap plot
 
 - Calculate total-area-within-threshold data
     - For each day analyzed;
         - Load the .npy file for NIC
         - Load the .npy file for CDR
         - For each sea ice concentration threshold investigated
             - Select the data that falls within this sea ice concentration threshold
             - Calculate the total area this data represents
             - Write to a pandas dataframe
     - Save pandas dataframe to csv
     - Plot subsets of that data
     
 - Calculate monthly median ice edge
     - For each month to calculate
         - Create a numpy array to hold the sea ice concentration sum information
         - For each day within this month
             - Create a boolean array representing data that is greater than this threshold as "True" and data that is less than this threshold as "False".
             - Add the integer representation of this boolean array to the sum array.
             - Iterate a counter
         - Divide the sum array by the counter - this represents the percent time in this month this pixel was greater than the specified value.
         - Create a boolean array where this sum/counter array is greater than 0.5.
         - Run a numpy diff calculation on this boolean array to find the edge of this median.
         - Plot the result. 
 - Generate animations of the time series plots.
## Directory Structure

* modules/ `Modules to assist in the comparison, display and download of files`
    * compare.py
    * display.py
    * download.py
    * main.py
* environment.yml `The environment definition for running the comparison`
* LICENSE `License file`
* miz_comparison.ipynb `Notebook that walks through the comparison process`
* README.md `This document`
* Edge of Antarctica; Looking into where ice and water mix.ipynb `Main Jupyter Notebook Workflow`
* Edge of Antarctica; Looking into where ice and water mix.html `HTML snapshot of the Jupyter Notebook`

**Note - the below data directory will be automatically generated by the scripts in this repository and is not stored in version control**
* data/
    * antarctic|arctic
        * inputs/
            * cdr/ `Contains all NSIDC CDR MIZ products`
                * `seaice_conc_daily_icdr_sh_f18_%Y%m%d_v01r00.nc`
                * `%Y%m%d_[south|north]_cdr.npy`
            * nic/ `Contains all USNIC MIZ products`
                * `nic_miz%Y%jsc_pl_a.zip`
                * `%Y%m%d_[south|north]_nic.npy`
        * outputs/ `Optional output files`
            * cdr
                * png/
                    * `daily_extent_%Y%m%d_[threshold]_percent_thresh.png` - plots showing the sea ice extent at the given threshold
            * nic
                * png/
                    * `daily_extent_%Y%m%d_[threshold]_percent_thresh.png` - plots showing the sea ice extent at the given threshold
            * combined
                * png/
                    * `daily_extent_[nic threshold]_[cdr threshold]_for_%Y%m%d.png` - plots showing the sea ice extent at the given threshold for both products overlayed
                    * `monthly_median_[nic threshold]_[cdr threshold]_for_%Y%m%d_to_%Y%m%d.png` - plots showing monthly median sea ice extent for the provided concentrations for both products.
                * csv/
                    * `stats_[low threshold]_to_[high threshold].csv` - A CSV that holds total sea ice within specified threshold intervals for both products.

## Resources
User Guide Draft - U.S. National Ice Center Daily Marginal Ice Zone Products, Version 1.

User Guide Draft - National Snow and Ice Data Center Climate Data Record of Passive Microwave Sea Ice Concentration, Version 3.  Retrieved from https://nsidc.org/data/g02202

Meier, W. N., G. Peng, D. J. Scott, and M. H. Savoie. 2014. Verification of a new NOAA/NSIDC passive microwave sea-ice concentration climate record. Polar Research 33. doi:10.3402/polar.v33.21004.

