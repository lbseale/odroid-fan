#!/usr/bin/python3

# Fan controller for odroid xu4
# Luke Seale 12/16/19

from time import sleep
import atexit
import signal
import configparser
import json
import logging
import logging.handlers

class FanController:

    def __init__(self, config):

        trip_temp_str = config.get('FanController', 'trip_temps', fallback='[60000, 70000, 80000]')
        trip_temp_list = json.loads(trip_temp_str)
        trip_temp_list.insert(0,0)
        self.trip_temps = trip_temp_list

        trip_speed_str = config.get('FanController', 'trip_speeds', fallback='[120, 180, 240]')
        trip_speed_list = json.loads(trip_speed_str)
        trip_speed_list.insert(0, 0)
        self.trip_speeds = trip_speed_list

        self.hysteresis = config.getint('FanController', 'hysteresis', fallback=8000)
        self.poll_interval = config.getfloat('FanController', 'poll_interval', fallback=0.25)

        self.fan_on = False
        self.current_fan_level = 0

        # Define hysteresis trip points as the ordinary trip points minus the hysteresis
        hyst_trip_temps = []
        for temp in self.trip_temps:
            if(temp == 0):
                hyst_trip_temps.append(0)
            else:
                hyst_trip_temps.append(temp - self.hysteresis)
        self.hyst_trip_temps = hyst_trip_temps

    def get_pwm(self, current_temp):

        current_trip_temp = self.trip_temps[self.current_fan_level]

        # Look up the current temp in the trip_temp list
        # Use the ordinary list if the level might increase
        # Use the hysteresis list if the level mimght decrease
        if(current_temp >= current_trip_temp):
            new_fan_level = self._lookup(self.trip_temps, current_temp)
        elif(current_temp < current_trip_temp):
            new_fan_level = self._lookup(self.hyst_trip_temps, current_temp)

        self.current_fan_level = new_fan_level
        return self.trip_speeds[new_fan_level]

    # Look up a temperature in the temp_list, being smart about greater than/less than
    def _lookup(self, temp_list, temp):
        list_end = len(temp_list)-1
        found_index = -1
        for i in range(len(temp_list)):
            if(i == 0 and temp < temp_list[i]):
                found_index = i
            elif(i == list_end and temp >= temp_list[i]):
                found_index = i
            elif(i < list_end and temp >= temp_list[i] and temp < temp_list[i+1]):
                found_index = i
        return found_index

    def wait(self):
        sleep(self.poll_interval)
    
class Thermometer:
    
    def __init__(self, config):
        prefix = config.get('Thermometer','file_prefix', fallback='/sys/devices/virtual/thermal/thermal_zone')
        suffix = config.get('Thermometer', 'file_suffix', fallback='/temp')
        
        zone_list_str = config.get('Thermometer', 'zones', fallback='[0,1,2,3]')
        zones = json.loads(zone_list_str)
        
        self.read_files = [prefix + str(z) + suffix for z in zones]
        self.read_temps = []
    
    def read_temp(self):
        self.read_temps = []
        for filename in self.read_files:
            file = open(filename, 'r')
            self.read_temps.append(int(file.read()))
            file.close()
            
        return max(self.read_temps)

class Fan:
    
    def __init__(self, config):
        self.fan_mode_file = config.get('Fan', 'fan_mode_file', fallback='/sys/devices/platform/pwm-fan/hwmon/hwmon0/automatic')
        self.fan_speed_file = config.get('Fan', 'fan_speed_file', fallback='/sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1')
    
    def set_pwm(self, pwm_value):
        file = open(self.fan_speed_file, 'w')
        file.write(str(pwm_value))
        file.close()
    
    def take_control(self):
        self._write_to_fan_mode('0')
        
    def release_control(self):
        self._write_to_fan_mode('1')
        
    def _write_to_fan_mode(self, value_to_write):
        file = open(self.fan_mode_file, 'w')
        file.write(value_to_write)
        file.close()

class SignalHandler:
    exit_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.time_to_exit)
        signal.signal(signal.SIGTERM, self.time_to_exit)

    def time_to_exit(self, signum, frame):
        self.exit_now = True
        

def load_config(config_path):
    
    config = configparser.ConfigParser()
    config_found = config.read(config_path)
    if not config_found:
        print('[odroid-fan] - Config file ' + config_path + ' not found, using defaults')

    return config

# Set up the logger
def setup_logger():
    logger = logging.getLogger('odroid-fan')
    logger.setLevel(logging.INFO)
    
    #add handler to the logger
    handler = logging.handlers.SysLogHandler('/dev/log')
    
    #add formatter to the handler
    #formatter = logging.Formatter('Python: { "loggerName":"%(name)s", "timestamp":"%(asctime)s", "pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}')
    #formatter = logging.Formatter(fmt="[%(name)s] [%(levelname)-8s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    format = "fan-control[%(process)d]: [%(levelname)-8s] %(message)s"
    formatter = logging.Formatter(fmt=format)
    
    handler.formatter = formatter
    logger.addHandler(handler)
    return logger
    

# Function to release control of the fan, to be registered to run before exit
def safety_release(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    fan = Fan(config)
    fan.release_control()

# Main Loop
# Read the temperature, use the fan controller to get the proper PWM for the fan, then write it to the fan
# Wait the given interval
# Runs forever until interrupted
def main():
    
    config_path = '/home/luke/odroid-fan/config.ini'
    #print_prefix = '[odroid-fan] - '
    old_pwm = -1

    config = load_config(config_path)
    verbose = config.getboolean('FanController', 'verbose', fallback=False)
    # Always release control of the fan before exiting
    atexit.register(safety_release, config_path=config_path)
    signal_handler = SignalHandler()

    logger = setup_logger()
    fan = Fan(config)
    thermo = Thermometer(config)
    fan_controller = FanController(config)

    logger.info('Taking control of fan')
    fan.take_control()
    
    while (signal_handler.exit_now == False):
        current_temp = thermo.read_temp()
        new_pwm = fan_controller.get_pwm(current_temp)

        if (verbose and (new_pwm != old_pwm)): 
            #print(timestamp() + 'Temp: ' + str(current_temp) + ' setting pwm: ' + str(new_pwm))
            logger.info('Temp: ' + str(current_temp) + ' setting pwm: ' + str(new_pwm))

        fan.set_pwm(new_pwm)
        old_pwm = new_pwm
        fan_controller.wait()

    safety_release(config_path)
    logger.info('Received signal to terminate')

if __name__ == '__main__':
    main()
