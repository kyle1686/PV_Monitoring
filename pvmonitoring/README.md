**NOTE: All python scripts must be run in the directory where the scripts are.
    Data files must locate in subdirectory ./data/ relative to the scripts.**

This project is composed the following parts:

Part 1. Sensor Data collection: 
Collect sensor data of a day and writes it into file named as yyyy-mm-dd.csv. Data sampling
frequency is once every minute. This can be done by configuring crontab to invoke collect_data.py
at every minute.

    This step generates yyyy-mm-dd.csv

Part 2. Process data to compute expected power, using hybrid modeling, physical model and
    machine learning model. This step generates yyyy-mm-dd_processed.csv 
    
    Example: ```python compute_power.py -d 2022-08-27```
    
Part 3. WIP: Calibration: use machine learning linear regression to get a model to adjust
    the power value computed by applying physical model.

Part 4. Plot results: plot feature vs time plots for one or more dates. 
    Example 1: ```python plot.py -d 2022-08-27```
    Example 2: ```python plot.py -d 2022-08-27,2022-08-28,2022-08-29,2022-08-30```

Part 5. TODO: Machine learning model to detect anomalies like soiling, shading, etc.

Part 6. TODO: Detect anomalies 
