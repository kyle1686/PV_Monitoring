TIMESTAMP = "timestamp"
TIME = "time"
TEMPERATURE = "temperature"
IRRADIANCE = "irradiance"
VOLTAGE = "voltage"
CURRENT = "current"
POWER = "power"
TEMPERATURE_SMOOTHED = "temperature smoothed"
IRRADIANCE_SMOOTHED = "irradiance smoothed"
VOLTAGE_SMOOTHED = "voltage smoothed"
CURRENT_SMOOTHED = "current smoothed"
POWER_SMOOTHED = "power smoothed"
IAM_FACTOR = "IAM factor"
PVWATTS_POWER = "pvwatts power"
COMPUTED_POWER = "computed power"
SIM_POWER = "sim_power" #TODO: remove this after simulate_power.py is decommisioned
RAW_DATA_COLUMN_NAMES = [TIMESTAMP, TIME, TEMPERATURE,IRRADIANCE, VOLTAGE, CURRENT, POWER]

SMOOTH_DATA_WINDOW_SIZE = 5
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATA_FILE_RELATIVE_DIR = './data/'
CONFIG_FILE = './config/config.json'

DEFAULT_POWER_COEF = 0.88

DAY_START_TIME = '08:30:00'
DAY_END_TIME = '18:30:00'