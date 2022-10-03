import pandas as pd
from constants import *
import argparse
import sys, getopt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score,  mean_absolute_error
import json

def linear_regression(df):
    #TODO: limit the df's time to DAY_START_TIME to DAY_END_TIME
    regr = linear_model.LinearRegression(fit_intercept=False)
    regr.fit(df[[PVWATTS_POWER]], df[POWER_SMOOTHED])
    coef = regr.coef_[0]
    return coef

def main():
    filename = ''
    argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="Filename of the data file, e.g. 2022-09-14.csv")
    args = parser.parse_args()
    if args.filename:
        filename = args.filename
    fname = DATA_FILE_RELATIVE_DIR + filename
    df = pd.read_csv(fname)
    
    dict = {"coefficient": linear_regression(df)}
    with open("./config/calibration.json", "w+") as e:
        json.dump(dict, e)
        
    
if __name__ == "__main__":
    main()