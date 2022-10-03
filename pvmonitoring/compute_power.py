"""
Computes power by:
    - Step 1: Preprocess data to fix the outliers and then smooth data by using the moving average
    - Step 2: Compute power by using the pvwatts model implemented by pvlib:
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.pvwatts_dc.html
        - Irridance fed to pvwatts model is adjusted for reflection loss by using IAM (Incident Angle Modifier)
            implemented by pvlib: https://pvlib-python.readthedocs.io/en/stable/_modules/pvlib/iam.html
    - Step 3: Adjust the pvwatts power from Step 2 with coefficient to account for system inefficiencies
        like mppt tracking, wire loss, etc.
        - The coefficient is obtained by linear regression on calibration data.
        
Example usage: 'python compute_power.py -f 2022-09-14.csv' or 'python compute_power.py -d 2022-09-14'
    This would output 2022-09-14_processed.csv which copies the columns of 2022-09-14.csv and add new columns for
    the computed results, e.g., pvwatts power, iam, and most importantly, computed power.
"""

import argparse
import pvlib
import pandas as pd
from constants import *
from preprocess_data import *
import json

class Config:
    def __init__(self):
        with open(CONFIG_FILE, 'r') as file:
            dict = json.load(file)
            self.pvsystem = dict['pvsystem']
            self.location = dict['location']

# Returns IAM: Incidence Angle modifier.
# Details: https://pvpmc.sandia.gov/modeling-steps/1-weather-design-inputs/shading-soiling-and-reflection-losses/incident-angle-reflection-losses/
# pvlib implements multiple IAM models: https://pvlib-python.readthedocs.io/en/stable/_modules/pvlib/iam.html. 
# This function uses pvlib physical IAM model and its default params.
def get_iam(time, config):
    pvsystem = config.pvsystem
    location = config.location
    # Get sun position for the given time
    dti = pd.DatetimeIndex(pd.to_datetime(time, format=TIME_FORMAT), tz='US/Pacific')
    solpos = pvlib.solarposition.get_solarposition(
        time=dti,
        latitude=location['latitude'],
        longitude=location['longitude'],
        altitude=location['altitude']
    )
 
    # Get AOI(angle of incident) for the current sun postion
    aoi = pvlib.irradiance.aoi(
        pvsystem['surface_tilt'],
        pvsystem['surface_azimuth'],
        solpos["apparent_zenith"],
        solpos["azimuth"],
    )
    
    # Get IAM
    # Ashrae IAM model： https://pvpmc.sandia.gov/modeling-steps/1-weather-design-inputs/shading-soiling-and-reflection-losses/incident-angle-reflection-losses/ashre-model/
    #iam = pvlib.iam.ashrae(aoi)
    # Martin and Ruiz model： https://pvpmc.sandia.gov/modeling-steps/1-weather-design-inputs/shading-soiling-and-reflection-losses/incident-angle-reflection-losses/martin-and-ruiz-model/
    #iam = pvlib.iam.martin_ruiz(aoi)

    # Physical IAM model: https://pvpmc.sandia.gov/modeling-steps/1-weather-design-inputs/shading-soiling-and-reflection-losses/incident-angle-reflection-losses/physical-model-of-iam/
    iam = pvlib.iam.physical(aoi)
    iam.reset_index(drop=True, inplace=True)
    return iam

def compute_power(irradiance, temp_cell, time, power_coefficient, config):
    # Adjust irradiance to account for reflection losses
    # See https://pvpmc.sandia.gov/modeling-steps/1-weather-design-inputs/shading-soiling-and-reflection-losses/.
    iam = get_iam(time, config)
    effective_irradiance = iam * irradiance
    gamma_pdc = config.pvsystem['gamma_pdc']
    pdc0 = config.pvsystem['pdc0']
    pvwatts_dc = pvlib.pvsystem.pvwatts_dc(effective_irradiance,
                               temp_cell,
                               pdc0, #pdc0 (numeric) – Power of the modules at 1000 W/m^2 and cell reference temperature. [W]
                               gamma_pdc=gamma_pdc)
    return iam, round(pvwatts_dc, 2), round(pvwatts_dc * power_coefficient, 2)

def process(filename, power_coefficient):
    fname = DATA_FILE_RELATIVE_DIR + filename
    df = pd.read_csv(fname)
    df = preprocess_data(df)
    config = Config()

    df[IAM_FACTOR], df[PVWATTS_POWER], df[COMPUTED_POWER] = compute_power(df[IRRADIANCE_SMOOTHED], df[TEMPERATURE_SMOOTHED], df[TIME], power_coefficient, config)
    processed_filename = fname[:-4] + "_processed.csv"
    df.to_csv(processed_filename, index=False)

def main():
    parser = argparse.ArgumentParser()
    # Either'-f' and '-d' must be specified, but not both.
    parser.add_argument("-f", "--filename", help="Filename of the data file, e.g. 2022-09-14.csv")
    parser.add_argument("-d", "--date", help="The date part of the data file, e.g. 2022-09-14.")
    parser.add_argument("-c", "--power_coef", type=float, default=0.9, help="power coefficient to adjust pvwatts power, defaluts to 0.88")
    args = parser.parse_args()

    filenames = ''
    if args.filename:
        filename = args.filename
    elif args.date:
        filename = args.date + '.csv'
    else:
         raise Exception("Option -f or -d must be specified")

    # Power efficiency coefficient. It relfects power loss due to MPPT tracking and
    # pyranometer calibration. 1.0 represents no power loss, and 0.9 represents 10%
    # power loss.
    #
    # This coefficient should be obtained from calibration. In calibration stage, collect sensor
    # data when the system is operating at optimalenvironmental situation, e.g., no soiling.
    # Then linear regression is done on the data to optimalily match pvwatts power to the measured
    # power. After calibration, the computed power is the pvwatts power adjusted by this coefficient.
    # The computed power is used as the reference baseline for detecting anomolies.
    
    #TODO: remove this. Instead, read calibrated coef from file outputted by calibriate.py
    power_coefficient = args.power_coef

    process(filename, power_coefficient)

if __name__ == "__main__":
    main()