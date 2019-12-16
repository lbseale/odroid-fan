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
        new_fan_level = -1

        # If the fan is on, check if current_temp is below hysteresis of current level (or one below), and we need to slow down
        if fan_on:
            for i in range(1, (self.current_fan_level + 1)):
                off_temp = (self.trip_temps[i] - self.hysteresis)
                if(current_temp < off_temp):
                    new_fan_level = (i - 1)
                    break

        # Look to see if current_temp is above any trip point above the current level, and we need to speed up
        # Loop backwards through trip_temps, up to the current one
        if(new_fan_level != -1):
            for i in range((len(self.trip_temps) - 1), (self.current_fan_level - 1), -1):
                if(current_temp > self.trip_temps[i]):
                    new_fan_level = i
                    break

        if(new_fan_level != -1):
            self.current_fan_level = new_fan_level
            return self.trip_speeds[new_fan_level]
        else:
            return self.trip_speeds[self.current_fan_level]
