"""
Utility to plot for a list of data files or a list of dates. It plots in 2 modes:
    - full mode: for each data file or date, plots a figure containing all plots, 
        including irradiance, temperature, voltage, current, power, etc. The plots
        usually use time as the x-axis.
    - simple mode: plots one figure for all data files or dates. Only power is plotted.
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import ceil, floor
from matplotlib.dates import DateFormatter, AutoDateLocator
from constants import *
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Format time to display as x-axis 
def format_time_xaxis(ax):
    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax.set_xlabel("Time of day")

def plot_irradiance(ax, plot_raw_data, df):
    format_time_xaxis(ax)
    ax.set_title("Irradiance vs. Time")
    ax.set_ylabel("Irradiance (W/m^2)")
    if plot_raw_data:
        ax.plot(df.index, df.loc[:,IRRADIANCE], label='irradiance raw')
    if IRRADIANCE_SMOOTHED in df.columns:
        ax.plot(df.index, df.loc[:,IRRADIANCE_SMOOTHED], label='irradiance')
    ax.legend()
    ax.grid(True)

def plot_temperature(ax, plot_raw_data, df):
    format_time_xaxis(ax)
    if plot_raw_data:
        ax.plot(df.index, df.loc[:,TEMPERATURE], label='temperature raw')
        ax.legend()
    if TEMPERATURE_SMOOTHED in df.columns:
        ax.plot(df.index, df.loc[:,TEMPERATURE_SMOOTHED], label='temperature')
    ax.set_title("Temperature vs. Time")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(True)
    
def plot_voltage(ax, plot_raw_data, df):
    format_time_xaxis(ax)
    ax.set_title("Voltage vs. Time")
    ax.set_ylabel("Voltage (V)")
    if plot_raw_data:
        ax.plot(df.index, df.loc[:,VOLTAGE], label='voltage raw')
        ax.legend()
    if VOLTAGE_SMOOTHED in df.columns:
        ax.plot(df.index, df.loc[:,VOLTAGE_SMOOTHED], label='voltage')
    ax.grid(True)
    
def plot_current(ax, plot_raw_data, df):
    format_time_xaxis(ax)
    ax.set_title("Current vs. Time")
    ax.set_ylabel("Current (A)")
    if plot_raw_data:
        ax.plot(df.index, df.loc[:,CURRENT], label = 'current raw')
        ax.legend()
    if CURRENT_SMOOTHED in df.columns:
        ax.plot(df.index, df.loc[:,CURRENT_SMOOTHED], label='current')
    ax.legend()
    ax.grid(True)
    
def plot_iam(ax, plot_raw_data, df):
    format_time_xaxis(ax)
    ax.set_title("IAM: Incident Angle Modifier")
    ax.set_ylabel("IAM: Incident Angle Modifier")
    ax.plot(df.index, df.loc[:,IAM_FACTOR])
    ax.grid(True)
    
def plot_power(ax, plot_raw_data, df):
    dt = df.index
    format_time_xaxis(ax)
    if plot_raw_data:
        ax.plot(dt, df.loc[:,POWER], label='measured power raw')
    ax.plot(dt, df.loc[:,POWER_SMOOTHED], label='measured power')
    ax.set_title("Power vs. Time")
    ax.set_ylabel("Power (W)")
    if COMPUTED_POWER in df.columns:
        ax.plot(dt, df.loc[:,COMPUTED_POWER], label='computed power')
#    if PVWATTS_POWER in df.columns:
#        ax.plot(dt, df.loc[:,PVWATTS_POWER], label='pvwatts power')

    ax.legend()
    ax.grid(True)

#TODO: 
def plot_metrics(ax, df):
    print('plot metrics')
    # df has 3 colums: 'date', 'mae', 'power mean'.
    # for each row, draw 2 bars: 'mae' and 'power mean'. Add legend for the 2 bars
    # xticks is date, yticks
    # xlabel is 'date', ylabel is 'Power (w)'
    # Hint: Use the same way as Example 3 in https://www.geeksforgeeks.org/create-a-grouped-bar-plot-in-matplotlib/ 
    
def get_df_for_time_range(df, start_time, end_time):
    date_str = df.index[0].strftime("%Y-%m-%d ");    
    start = date_str + start_time
    end = date_str + end_time
    return df[start:end]

def get_metrics_dict(df):
    print('return a dict containing metrics related data for the given df')
    # TODO: return a dict like this: {'date': '2022-09-24', 'mae': 0.3, 'power mean': 20}


def plot_full_for_file(filename, plot_raw_data):
    fname = DATA_FILE_RELATIVE_DIR + filename
    df = pd.read_csv(fname, index_col=TIME, parse_dates=True)
    # only use data between start and end time
        
    df = get_df_for_time_range(df, DAY_START_TIME, DAY_END_TIME)
    
    # create a figure which contains 2x3 plots
    fig, ax = plt.subplots(2, 3, figsize=(20, 15))
    date_str = df.index[0].strftime("%Y-%m-%d");
    fig.suptitle(date_str, fontsize = 30)
    plot_irradiance(ax[0,0], plot_raw_data, df)
    plot_temperature(ax[0,1], plot_raw_data, df)
    plot_voltage(ax[0,2], plot_raw_data, df)
    plot_current(ax[1,0], plot_raw_data, df)
    plot_iam(ax[1,1], plot_raw_data, df)
    plot_power(ax[1,2], plot_raw_data, df)

# Plot figures for filenames, one figure per filename. Each figure contains all plots.
def plot_full_mode(filenames, plot_raw_data):
    for fname in filenames:
        plot_full_for_file(fname, plot_raw_data)
    plt.show()

# One fig for all days in filenames.
def plot_simple_mode(filenames, plot_raw_data):
    nplots = len(filenames)
    ncols = 3
    nrows = ceil(nplots / ncols)
    fig = plt.figure(1, figsize=(18,10))
    metrics_df = pd.DataFrame(columns=['date', 'mae', 'power mean'])
    for i in range(len(filenames)):
        fname = DATA_FILE_RELATIVE_DIR + filenames[i]
        df = pd.read_csv(fname, index_col=TIME, parse_dates=True)
        df = get_df_for_time_range(df, DAY_START_TIME, DAY_END_TIME)
        # call get
        subplot_pos = i+1 # subplot position starts at 1
        ax = fig.add_subplot(nrows, ncols, subplot_pos)
        plot_power(ax, plot_raw_data, df)
        date_str = df.index[0].strftime("%Y-%m-%d"); 
        ax.set_title(date_str)

    plt.show()

def main():
    parser = argparse.ArgumentParser()
    # Either'-f' and '-d' must be specified, but not both.
    parser.add_argument("-f", "--filenames", default='', help="Comma separated data filenames. E.g. 2022-09-01_processed.csv,2022-09-02_processed.csv")
    parser.add_argument("-d", "--dates", default='',
                        help="The dates to plot, specified as comma separated list of date strings. E.g. 2022-09-01,2022-09-02")    
    parser.add_argument("-r", "--plot_raw", action='store_true', help="If present, plot for raw (i.e., not smoothed) data")
    parser.add_argument("-s", "--simple", action='store_true', help="If present, plot in simple mode, one fig for all days; otherwise, one fig each day with all plots for that day.")
    args = parser.parse_args()

    filenames = ''
    if args.filenames:
        filenames = args.filenames.split(',')
    elif args.dates:
        dates = args.dates.split(',')
        suffix = '_processed.csv'
        filenames = [date + suffix for date in dates]
    else:
         raise Exception("Option -f or -d must be specified")

    plot_raw_data = args.plot_raw
    simple_mode = args.simple

    #get_mppt_fixed_points(filename)
    if simple_mode:
        plot_simple_mode(filenames, plot_raw_data)
    else:
        plot_full_mode(filenames, plot_raw_data)

if __name__ == "__main__":
    main()