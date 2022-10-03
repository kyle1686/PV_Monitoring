"""
 Preprocess data to:
     - fix power dips caused by MPPT charge controller sweeping
     - smooth sensor data by using the moving average of a window. Window size is 5 minutes by default.
"""
import pandas as pd
from constants import *
import sys, getopt

# The Victron MPPT charge controller sweeps every 10 minutes to find the maximum power point lasts about 33 seconds.
# During sweeping the power drops significantly.
# See https://community.victronenergy.com/questions/10361/change-mppt-tracking-refresh-interval.htm
# This function finds the data sampled during sweeping and fixes the data. For POWER, VOLTAGE and CURRENT columns,
# the data sampled during sweeping is replaced with the mean of the two values sampled at 1 minute before sweeping
# and 1 minute after sweeping.
def fix_mppt_dips(df):
    df_copy = df.copy()
    for i in range(1, len(df)-1):
        voltage_mean = (df.at[i-1,VOLTAGE] + df.at[i+1,VOLTAGE]) / 2
        current_mean = (df.at[i-1,CURRENT] + df.at[i+1,CURRENT]) / 2
        power_mean = (df.at[i-1,POWER] + df.at[i+1,POWER]) / 2
        irradiance_mean = (df.at[i-1,IRRADIANCE] + df.at[i+1,IRRADIANCE]) / 2

        if irradiance_mean != 0 and power_mean != 0:
            irradiance_ratio = df.at[i,IRRADIANCE] / irradiance_mean
            power_ratio = df.at[i,POWER] / power_mean     
            if irradiance_ratio > 0.9 and power_ratio < 0.85:
                df_copy.at[i,POWER] = power_mean
                df_copy.at[i,VOLTAGE] = voltage_mean
                df_copy.at[i,CURRENT] = current_mean

    return df_copy

# Smooth TEMPERATURE, IRRADIANCE, VOLTAGE, CURRENT and POWER data by the using moving average of
# a window size of SMOOTH_DATA_WINDOW_SIZE. The data after smoothing are added as new columns.
#  Original df columns are unchanged.
def add_smoothed_data(df):
    window = SMOOTH_DATA_WINDOW_SIZE
    df[TEMPERATURE_SMOOTHED] = df[TEMPERATURE].rolling(window, min_periods=1, center=True).mean().round(2)
    df[IRRADIANCE_SMOOTHED] = df[IRRADIANCE].rolling(window, min_periods=1, center=True).mean().round(2)
    df[VOLTAGE_SMOOTHED] = df[VOLTAGE].rolling(window, min_periods=1, center=True).mean().round(2)
    df[CURRENT_SMOOTHED] = df[CURRENT].rolling(window, min_periods=1, center=True).mean().round(2)
    df[POWER_SMOOTHED] = df[POWER].rolling(window, min_periods=1, center=True).mean().round(2)

def preprocess_data(df):
    df = fix_mppt_dips(df)
    add_smoothed_data(df)
    return df
