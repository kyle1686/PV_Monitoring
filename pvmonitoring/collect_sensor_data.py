"""
Sample usage: python collect_sensor_data.py -w

Gets irradiance, temperature, voltage/current/power from corresponding
sensors and writes the sensor data as a row to a csv file if -w option
is specified.

The ouput csv file is named by the date, e.g. 2022-09-15.csv
"""

from datetime import datetime, date
import sys, getopt
import time
import os
import board
import adafruit_ads1x15
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
from w1thermsensor import W1ThermSensor, Unit
import csv
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from constants import *

i2c_bus = board.I2C()
ina1 = INA219(i2c_bus,addr=0x40)

ina1.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.bus_voltage_range = BusVoltageRange.RANGE_32V

def get_vip():
    load_voltage = round(ina1.bus_voltage, 2) # volts
    current = round(ina1.current / 1000, 2) # amps
    power = round(ina1.power, 2) # watts
    return [load_voltage, current, power]

def get_temp():
    sensor = W1ThermSensor() 
    temp = sensor.get_temperature()
    return round(temp, 2)

def get_irradiance():
    ads = ADS.ADS1115(i2c_bus)
    ads.range = 16
    chan = AnalogIn(ads, ADS.P3)
    if chan.voltage < 0:
        return 0.0
    # Apogee SP-110-SS calibration factor is 5w/m^2 per mV
    return round(chan.voltage * 1000 * 5, 2)
    # return 300

def get_sensor_data():
    temp = get_temp()
    volt, current, power = get_vip()
    irradiance = get_irradiance()
    
    now = datetime.now()
    timestamp = round(now.timestamp())
    time = now.strftime(TIME_FORMAT)
    dict = {TIMESTAMP : timestamp, TIME: time, TEMPERATURE: temp, IRRADIANCE : irradiance, VOLTAGE : volt, CURRENT : current, POWER : power}

    return dict

# format of the filename is yyyy-mm-dd, e.g., 2022-08-01.csv
def gen_data_filename_for_date(day):
    return DATA_FILE_RELATIVE_DIR + day.strftime("%Y-%m-%d.csv")

def write_row_to_file(dict):
    dt = datetime.strptime(dict[TIME], TIME_FORMAT)
    filename = gen_data_filename_for_date(dt.today())
    write_column_names = not(os.path.exists(filename))
    with open(filename, 'a+', newline = '', encoding='utf-8') as file:
        writer = csv.DictWriter(file, RAW_DATA_COLUMN_NAMES)
        if write_column_names:
            writer.writeheader()
        writer.writerow(dict)
        file.close()

def main():
    write_file = False
    
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "w", ["write_file"])
    except:
        print("Wrong arg")
  
    for opt, arg in opts:
        if opt in ['-w', '--write_file']:
            write_file = True

    dict = get_sensor_data()
    print(dict)
    if write_file:
        write_row_to_file(dict)

if __name__ == "__main__":
    main()