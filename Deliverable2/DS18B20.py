import os
import glob
import time

# Setup for DS18B20
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]  # DS18B20 device id
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    """Read raw temperature data"""
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    """Convert raw data to temperature in Celsius"""
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_str = lines[1][equals_pos + 2:]
        temp_c = float(temp_str) / 1000.0
        return temp_c

# Print temperature every 2 seconds
while True:
    temp = read_temp()
    print(f"Current temperature: {temp} °C")
    time.sleep(2)
