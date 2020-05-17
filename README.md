# National Snow and Ice Data Center Marginal Ice Zone Comparison

## Background
The Marginal Ice Zone is defined as the area in the Arctic and the Antarctic where sea ice concentration is between 0% (open water) and 80%.  Knowing the extent of the MIZ is of particular importance for several reasons including biological research, atmospheric processes and maritime navigation.   

## Project Description

There are several products that describe the extent of the MIZ; this project will focus on comparing the National Snow and Ice Data Center's passive-microwave MIZ CDR to the US National Ice Center's operational MIZ product.  The primary goal of this comparison is to quantify how these two products differ in both a time-static comparison of the two products in recent months as well as a time-series comparison of their differences.  While data is available for both the northern and southern hemisphere, this project will focus on comparing southern hemisphere data.  This repository provides a method of reproducing the output from this comparison as well as providing an easy way to run this comparison for specified days.  

## U.S. NIC Operational MIZ Product
*Description to be added*

## NSIDC Passive-Microwave CDR MIZ Product
*Description to be added*

## Running the Comparison

### Prerequisites
You must have git and Anaconda/Miniconda installed as well as sufficient storage to store inputs and outputs.  You'll need sufficient disk space to store all input files from the two sources.  These storage requirements may change depending on the date range you would like to download.  The USNIC CDR will require 2.3 mb per day downloaded and the NIC MIZ product will require roughly 1-2 mb per day downloaded.  This data will be downloaded to a "data" directory within this directory.

### Setup
1) Clone this repository.
2) **Note - environment.yml still under construction.  This step won't work until that's complete.**  Run `conda env create -f environment.yml`.

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
    * inputs/
        * cdr/ `Contains all NSIDC CDR MIZ products`
            * seaice_conc_daily_icdr_sh_f18_%Y%m%d_v01r00.nc
        * nic/ `Contains all USNIC MIZ products`
            * nic_miz%Y%jsc_pl_a.zip
    * outputs/ `Optional output files`
        * csv/
        * png/
        * gif/