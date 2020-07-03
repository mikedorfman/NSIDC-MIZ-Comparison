import argparse
import datetime
import os

import numpy as np
import pandas as pd

from . import compare
from . import display
from . import io

INPUT_FOLDER_FMT = os.path.join("data", "{hemisphere}", "inputs", "{product}")

OUTPUT_ANIM_FOLDER_FMT = os.path.join("data", "{hemisphere}", "outputs", "cli", "{product}", "png")
OUTPUT_PNG_FOLDER_FMT = os.path.join("data", "{hemisphere}", "outputs", "cli", "{product}", "anim")
OUTPUT_CSV_FOLDER_FMT = os.path.join("data", "{hemisphere}", "outputs", "cli", "{product}", "csv")

def main():
    datetime_format = "%Y%m%d"
    parser = argparse.ArgumentParser(description='This is the CLI for the NIC/CDR comparison.  To run a specific '
                                                 'analysis, pass at least the start and end time and the analysis you '
                                                 'would like to run.  You may specify multiple analyses.  If the '
                                                 'products are images or animations, they will be saved to disk in a '
                                                 'directory structure outlined by README.  If the specified products '
                                                 'are statistics, they are printed to stdout.  See README for more '
                                                 'information.')
    parser.add_argument('start',
                        help=f'Start datetime to analyze.  Must be in format {datetime_format}. Interval includes '
                             f'start.',
                        type=lambda s: datetime.datetime.strptime(s, datetime_format))
    parser.add_argument('end',
                        help=f'End datetime to analyze.  Must be in format {datetime_format}. Interval includes '
                             f'end.',
                        type=lambda s: datetime.datetime.strptime(s, datetime_format))
    parser.add_argument('--animation',
                        help=f'Generate an animation of the files in the provided directory.  Order determined by glob'
                             f'order.',
                        action='store_true')

    parser.add_argument('--daily-plots',
                        help=f'Generate plots for individual days - products plotted separately.', action='store_true')
    parser.add_argument('--plot-cdr',
                        help=f'Specific to the daily-plots action, only create CDR plots.', action='store_true')
    parser.add_argument('--plot-nic',
                        help=f'Specific to the daily-plots action, only create NIC plots.', action='store_true')

    parser.add_argument('--daily-plots-combined',
                        help=f'Generate plots for individual days - products plotted together.', action='store_true')
    parser.add_argument('--median-plot',
                        help=f'Generate a plot of the median ice edge at.', action='store_true')
    parser.add_argument('--cdr-plotting-thresh',
                        default=0.8, help=f'The CDR sea ice concentration threshold for plotting.')
    parser.add_argument('--nic-plotting-thresh',
                        default=0.8, help=f'The NIC sea ice concentration threshold for plotting.')

    parser.add_argument('--stats',
                        help=f'Calculate total area of sea ice concentration within different contour lines for each '
                             f'product.', action='store_true')
    parser.add_argument('--thresh-lower',
                        default=0.1, help=f'The lower sea ice concentration to use when calculating statistics.')
    parser.add_argument('--thresh-upper',
                        default=1.0, help=f'The upper sea ice concentration to use when calculating statistics.')
    parser.add_argument('--thresh-interval',
                        default=0.05, help=f'The sea ice concentration interval to use when calculating statistics.')

    parser.add_argument('--hemisphere',
                        choices=['arctic', 'antarctic'], default='antarctic', help=f'The hemisphere to analyze.')
    parser.add_argument('--verbose', action='store_true', help=f'Increase verbosity.')
    args = parser.parse_args()

    if args.start >= args.end:
        raise argparse.ArgumentTypeError(f"Start {args.start} is greater than or equal to end {args.end}!")

    if not any(args.animation,
               args.daily_plots,
               args.daily_plots_combined,
               args.median_plot,
               args.stats):
        raise argparse.ArgumentTypeError(f"Must specify what type of output you would like to generate.")

    days = pd.date_range(start=args.start, end=args.end)

    # First, make sure everything is downloaded and download files if necessary
    cdr_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='cdr')
    nic_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='nic')

    io.download_cdr_miz_range(args.start, args.end, cdr_input_folder, hemisphere=args.hemisphere, verbose=args.verbose)
    io.download_nic_miz_range(args.start, args.end, nic_input_folder, hemisphere=args.hemisphere, verbose=args.verbose)

    # Optimize the data - save cdr data to numpy array on disk for quick access and rasterize the NIC shapefile
    # If these files are already present, don't do anything
    io.cdr_to_np(args.start, args.end, cdr_input_folder, hemisphere=args.hemisphere, verbose=args.verbose)
    _, file_name = io.datetime_to_cdr_fname(args.start, args.hemisphere)
    args.lats, args.lons, args.meta = io.get_cdr_metadata(os.path.join(cdr_input_folder, file_name))

    print("Rasterizing numpy array data range - this may take a while if this hasn't already been done...")
    io.nic_to_np(args.start,
                 args.end,
                 nic_input_folder,
                 args.meta,
                 args.lats.shape,
                 hemisphere=args.hemisphere,
                 verbose=args.verbose)

    if args.daily_plots:
        if not (args.plot_cdr or args.plot_nic):
            raise argparse.ArgumentTypeError(
                f"Must specify either plot_nic or plot_cdr if plotting daily, single-product plots.")
        create_daily_plots(days, args)
    if args.daily_plots_combined:
        create_daily_plots_combined(days, args)
    if args.median_plot:
        create_median_plot(days, args)
    if args.animation:
        create_animation(args)
    if args.stats:
        create_stats(days, args)


def create_stats(days, args):
    """
    For each day provided, add a row to a pandas dataframe representing total sea ice area within a specified sea ice
    concentration value.  Save the pandas dataframe out to a csv.
    :param days: A pandas datetime series for the days to analyze
    :param args: argparse args (see help)
    :return:
    """
    nic_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='nic')
    cdr_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='cdr')

    csv_out_path = OUTPUT_CSV_FOLDER_FMT.format(hemisphere=args.hemisphere, product='combined')
    threshold_range = np.arange(args.thresh_lower, args.thresh_upper, args.interval)

    # 1 since we're calculating the difference between this threshold and 100% SIC
    upper_threshold = 1.0

    df = pd.DataFrame()
    df.set_index(pd.DatetimeIndex([]))

    for day_analyzed in days:
        try:
            cdr_grid = io.get_cdr(day_analyzed, cdr_input_folder, args.hemisphere)
            nic_grid = io.get_nic(day_analyzed, nic_input_folder, args.hemisphere)

            for thresh in threshold_range:
                cdr_area, nic_area = compare.calculate_ice_area(cdr_grid,
                                                                nic_grid,
                                                                thresh,
                                                                upper_threshold,
                                                                thresh,
                                                                upper_threshold,
                                                                verbose=args.verbose)
                df.at[day_analyzed, f'NIC sea ice area within {thresh:.2f}'] = nic_area
                df.at[day_analyzed, f'CDR sea ice area within {thresh:.2f}'] = cdr_area

        except Exception as e:
            if args.verbose:
                print(f"Could not run {day_analyzed}; {e}")

    if args.verbose:
        print(df)

    df.to_csv(csv_out_path)


def create_animation(args):
    """
    Wraps images_to_animation, create an animation from the provided input folder
    :param args: argparse args (see help)
    :return:
    """
    display.images_to_animation(args.animation_directory)


def create_daily_plots_combined(days, args):
    """
    Create daily plots of the marginal ice zone with both products displayed on the same plot
    :param days: The days to create daily plots for (pandas datetime series)
    :param args: argparse args (see help)
    :return:
    """
    for day in days:
        nic_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='nic')
        cdr_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='cdr')

        output_folder = OUTPUT_PNG_FOLDER_FMT.format(hemisphere=args.hemisphere, product='combined')

        cdr_grid = io.get_cdr(day, cdr_input_folder, args.hemisphere)
        nic_grid = io.get_cdr(day, nic_input_folder, args.hemisphere)

        cdr_mask = np.where(cdr_grid >= args.plotting_cdr_thresh, True, False)
        nic_mask = np.where(nic_grid >= args.plotting_nic_thresh, True, False)

        display.create_basemap_plot(f"US NIC and NSIDC Marginal Ice Zone\n{day:%Y-%m-%d}",
                                    args.lats,
                                    args.lons,
                                    args.meta,
                                    [{'grid': cdr_mask, 'color': 'cyan', 'legend_label': 'CDR Extent'},
                                     {'grid': nic_mask, 'color': 'magenta', 'legend_label': 'NIC Extent'}],
                                    show=False,
                                    save=output_folder)


def create_daily_plots(days, args):
    """
    Create daily plots of the marginal ice zone of individual products
    :param days: The days to create daily plots for (pandas datetime series)
    :param args: argparse args (see help)
    :return:
    """
    for day in days:
        if args.plot_cdr:
            cdr_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='cdr')
            output_folder = OUTPUT_PNG_FOLDER_FMT.format(hemisphere=args.hemisphere, product='cdr')

            cdr_grid = io.get_cdr(day, cdr_input_folder, args.hemisphere)

            cdr_mask = np.where(cdr_grid >= args.plotting_cdr_thresh, True, False)

            display.create_basemap_plot(f"Sea Ice Concentration Climate Data Record (CDR)\n{day:%Y-%m-%d}",
                                        args.lats,
                                        args.lons,
                                        args.meta,
                                        [{'grid': cdr_mask, 'color': 'cyan', 'legend_label': 'CDR Extent'}],
                                        show=False,
                                        save=output_folder)

        if args.plot_nic:
            nic_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='nic')

            output_folder = OUTPUT_PNG_FOLDER_FMT.format(hemisphere=args.hemisphere, product='nic')

            nic_grid = io.get_cdr(day, nic_input_folder, args.hemisphere)

            nic_mask = np.where(nic_grid >= args.nic_thresh, True, False)

            display.create_basemap_plot(f"US National Ice Center Marginal Ice Zone\n{day:%Y-%m-%d}",
                                        args.lats,
                                        args.lons,
                                        args.meta,
                                        [{'grid': nic_mask, 'color': 'magenta', 'legend_label': 'NIC Extent'}],
                                        show=False,
                                        save=output_folder)


def create_median_plot(args):
    """
    Create plots that represent the median sea ice extent for the provided threshold in each month in the specified
    time period.
    :param args:  argparse args (see help)
    :return:
    """
    nic_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='nic')
    cdr_input_folder = INPUT_FOLDER_FMT.format(hemisphere=args.hemisphere, product='cdr')
    output_folder = OUTPUT_PNG_FOLDER_FMT.format(hemisphere=args.hemisphere, product='combined')

    freq = 'MS'
    last_day_of_month_offset = pd.offsets.MonthEnd(1)

    start_rounded_up = args.start + last_day_of_month_offset
    end_rounded_down = args.end.replace(day=1)

    for median_start_date in pd.date_range(start=start_rounded_up, end=end_rounded_down, freq=freq):
        median_end_date = median_start_date + last_day_of_month_offset

        cdr_median_threshold_grid = compare.median_cdr(args.plotting_cdr_thresh, median_start_date, median_end_date,
                                                       cdr_input_folder, args.hemisphere)
        nic_median_threshold_grid = compare.median_nic(args.plotting_nic_thresh, median_start_date, median_end_date,
                                                       nic_input_folder, args.hemisphere)

        # Let's only set the pixels on the boundary to True
        cdr_diff_arr = np.diff(cdr_median_threshold_grid, axis=0, prepend=False) | np.diff(
            cdr_median_threshold_grid, axis=1, prepend=False)
        nic_diff_arr = np.diff(nic_median_threshold_grid, axis=0, prepend=False) | np.diff(
            nic_median_threshold_grid, axis=1, prepend=False)

        output_name = os.path.join(output_folder,
                                   f"{args.plotting_cdr_thresh}_{args.plotting_nic_thresh}_"
                                   f"for_{median_start_date:%Y%m%d}_to_{median_end_date:%Y%m%d}.png")

        display.create_basemap_plot(f'Monthly Median Sea Ice Extent - {median_start_date:%b, %Y}\n'
                                    f'Thresholds; NIC={int(100 * args.nic_threshold)}%, '
                                    f'CDR={int(100 * args.plotting_cdr_threshold)}%',
                                    args.lats,
                                    args.lons,
                                    args.meta,
                                    [{'grid': cdr_diff_arr, 'color': 'cyan', 'legend_label': 'CDR Extent'},
                                     {'grid': nic_diff_arr, 'color': 'magenta', 'legend_label': 'NIC Extent'}],
                                    show=True,
                                    legend=True,
                                    save=output_name)


if __name__ == '__main__':
    main()
