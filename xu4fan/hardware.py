"""
Hardware classes for the Odroid XU4

These enable interaction with the Fan Controller, CPU thermometer, Fan PWM input, and Signal handler
"""

from time import sleep
import signal
import json

class FanController:
    """
    Fan Controller class

    Computes PWM values given temperatures
    """

    def __init__(self, config):
        """
        Contstructor for the FanController

        Expects a ConfigParser object, with a category 'FanController'
        See the sample config file for the names and values expected by this class
        """
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
        """
        Compute a PWM value for the fan, given the current temperature

        If the temperature increased, looks it up in the ordinary trip_temp list
        If it decreased, looks the temperature up in the hysteresis list, which is the trip_temp list minus the hysteresis
        """
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

    def _lookup(self, temp_list, temp):
        """
        Look up a temperature in a trip_temp list, return the found index

        Handles the possibility that the temperature is less than the first value, or greater than the last value
        Assumes that the trip_temps are in ascending order
        """
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
        """Just sleep for the number of seconds set in the config file"""
        sleep(self.poll_interval)
    
class Thermometer:
    """
    Thermometer class, which is used to read the CPU temperature of the Odroid XU4
    """

    def __init__(self, config):
        """
        Constructor for the Thermometer class

        Expects a ConfigParser object, with a category 'Thermometer'
        See the sample config file for the names and values expected by this class
        """
        prefix = config.get('Thermometer','file_prefix', fallback='/sys/devices/virtual/thermal/thermal_zone')
        suffix = config.get('Thermometer', 'file_suffix', fallback='/temp')
        
        zone_list_str = config.get('Thermometer', 'zones', fallback='[0,1,2,3]')
        zones = json.loads(zone_list_str)
        
        self.read_files = [prefix + str(z) + suffix for z in zones]
        self.read_temps = []
    
    def read_temp(self):
        """
        Read the temperature of the CPU

        Actually reads 4 temperatures, and returns the highest one
        """
        self.read_temps = []
        for filename in self.read_files:
            file = open(filename, 'r')
            self.read_temps.append(int(file.read()))
            file.close()
            
        return max(self.read_temps)

class Fan:
    """
    Fan class, used to set the fan PWM value
    """
    
    def __init__(self, config):
        """
        Constructor for the Fan class

        Expects a ConfigParser object, with a category 'Fan'
        See the sample config file for the names and values expected by this class
        """
        self.fan_mode_file = config.get('Fan', 'fan_mode_file', fallback='/sys/devices/platform/pwm-fan/hwmon/hwmon0/automatic')
        self.fan_speed_file = config.get('Fan', 'fan_speed_file', fallback='/sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1')
    
    def set_pwm(self, pwm_value):
        """
        Set the PWM value of the fan, it we must have control of it for this to work
        """
        file = open(self.fan_speed_file, 'w')
        file.write(str(pwm_value))
        file.close()
    
    def take_control(self):
        """ Take control of the fan from the Odroid """
        self._write_to_fan_mode('0')
        
    def release_control(self):
        """ Release control of the fan back to the Odroid """
        self._write_to_fan_mode('1')
        
    def _write_to_fan_mode(self, value_to_write):
        """
        Write to the special file which sets the fan in manual or automatic mode
        """
        file = open(self.fan_mode_file, 'w')
        file.write(value_to_write)
        file.close()

class SignalHandler:
    """
    SignalHandler class, to catch signals sent to the main loop

    This is needed to make sure control of the fan is released before the controller exits
    The exit_now attribute can be read to know if a signal has been received
    """
    exit_now = False

    def __init__(self):
        """
        Set up listeners for SIGINT and SIGTERM
        """
        signal.signal(signal.SIGINT, self.time_to_exit)
        signal.signal(signal.SIGTERM, self.time_to_exit)

    def time_to_exit(self, signum, frame):
        """
        Called if SIGINT or SIGTERM are received, set the exit_now attribute to True
        """
        self.exit_now = True
