
"""
Main functions for the odroid fan controller

Set up logging and the config file
"""

import atexit
import configparser
import logging
import logging.handlers
from xu4fan.hardware import FanController, Thermometer, Fan, SignalHandler

def load_config(config_path, logger):
    
    config = configparser.ConfigParser()
    config_found = config.read(config_path)
    if not config_found:
        logger.warning('Config file ' + config_path + ' not found, using defaults')

    return config

# Set up the logger
def setup_logger():
    logger = logging.getLogger('xu4fan')
    logger.setLevel(logging.INFO)
    
    #add handler to the logger
    handler = logging.handlers.SysLogHandler('/dev/log')
    
    #add formatter to the handler
    #formatter = logging.Formatter('Python: { "loggerName":"%(name)s", "timestamp":"%(asctime)s", "pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}')
    #formatter = logging.Formatter(fmt="[%(name)s] [%(levelname)-8s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    format = "xu4fan[%(process)d]: [%(levelname)-8s] %(message)s"
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
def control_fan():
    
    config_path = '/etc/xu4fan/xu4fan.conf'
    #print_prefix = '[odroid-fan] - '
    old_pwm = -1

    logger = setup_logger()
    config = load_config(config_path, logger)
    verbose = config.getboolean('FanController', 'verbose', fallback=False)
    # Always release control of the fan before exiting
    atexit.register(safety_release, config_path=config_path)
    signal_handler = SignalHandler()

    fan = Fan(config)
    thermo = Thermometer(config)
    fan_controller = FanController(config)

    logger.info('Taking control of fan')
    fan.take_control()
    
    while (signal_handler.exit_now == False):
        current_temp = thermo.read_temp()
        new_pwm = fan_controller.get_pwm(current_temp)

        if (verbose and (new_pwm != old_pwm)): 
            logger.info('Temp: ' + str(current_temp) + ' setting pwm: ' + str(new_pwm))

        fan.set_pwm(new_pwm)
        old_pwm = new_pwm
        fan_controller.wait()

    safety_release(config_path)
    logger.info('Received signal to terminate')

if __name__ == '__main__':
    control_fan()
