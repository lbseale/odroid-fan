# Fan controller for odroid xu4
# Luke Seale 12/16/19

class FanController:

    def __init__(self):
        self.trip_temps = [0, 60000, 70000, 80000]
        self.trip_speeds = [0, 120, 180, 240]
        self.hysteresis = 2000
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

    def set_speed(self, current_temp):

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

class Thermometer:
    
    def __init__(self):
        prefix = '/sys/devices/virtual/thermal/thermal_zone'
        suffix = '/temp'
        zones = [0, 1, 2, 3]
        
        self.read_files = [prefix + str(z) + suffix for z in zones]
        self.read_temps = []
    
    def read_temp(self):
        self.read_temps = []
        for filename in self.read_files:
            file = open(filename, 'r')
            self.read_temps.append(str(file.read()))
            file.close()
            
        return max(self.read_temps)

class Fan:
    
    def __init__(self):
        self.fan_mode_file = '/sys/devices/platform/pwm-fan/hwmon/hwmon0/automatic'
        self.fan_speed_file = '/sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1'
    
    def set_pwm(self, pwm_value):
        self.take_control()
        file = open(self.fan_speed_file, 'w')
        file.write(pwm_value)
        file.close()
    
    def take_control(self):
        self._write_to_fan_mode('0')
        
    def release_control(self):
        self._write_to_fan_mode('1')
        
    def _write_to_fan_mode(self, value_to_write):
        file = open(self.fan_mode_file, 'w')
        file.write(value_to_write)
        file.close()
    
def debug1():
    fc = FanController()
    test_temps = [45000, 55000, 61000, 60000, 59000, 58000, 57000, 72000, 75000, 80000, 79000, 77000, 59000, 57000]

    for tt in test_temps:
        print('test temp: ' + str(tt) + ' set speed: ' + str(fc.set_speed(tt)))

debug1()
