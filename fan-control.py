# Fan controller for odroid xu4
# Luke Seale 12/16/19

class FanController:

    def __init__(self):
        self.trip_temps = [0, 60000, 70000, 80000]
        self.trip_speeds = [0, 120, 180, 240]
        self.hysteresis = 2000
        self.fan_on = False
        self.current_fan_level = 0

    def set_speed(self, current_temp):

        fan_on = (self.current_fan_level > 0)
        current_trip_temp = self.trip_temps(self.current_fan_level)
        new_fan_level = -1
        loop_max = len(self.trip_temps)-1
        
        # If the temperature has increased, check if we need to spin the fan faster
        if(current_temp > current_trip_temp):
            for i in range(loop_max):
                if(i <= self.current_fan_level): continue # Don't look at temp ranges at or below the current one
                if((current_temp >= self.trip_temps[i] and current_temp < self.trip_temps[i+1]) or
                   (i == (loop_max-1) and current_temp >= self.trip_temps[i+1]):
                    new_fan_level = i
                    break
                   
        # If the temperature has decreased, check if we should spin the fan slower
        else if(current temp < current_trip_temp):
            for i in range(loop_max):
                if(i >= self.current_fan_level): continue # Don't look at temp ranges at or above the current one
                if(current_temp >= self.trip_temps[i] and current_temp < (self.trip_temps[i+1] - self.hysteresis)):
                    new_fan_level = i
                    break
        
        if(new_fan_level != -1):
            self.current_fan_level = new_fan_level
            return self.trip_speeds[new_fan_level]
        else:
            return self.trip_speeds[self.current_fan_level]
