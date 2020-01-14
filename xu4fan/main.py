"""
Main loop for the Odroid XU4 fan controller
Reads the CPU thermometer, gives the output to the Fan Controller, and sets the Fan speed
Also handles the configuration file, logging and releasing control of the fan
"""

import atexit
import configparser
import logging
import logging.handlers
from xu4fan.hardware import FanController, Thermometer, Fan, SignalHandler

def load_config(config_path, logger):
    """
    Load the configuration file and return a ConfigParser object
    """
    config = configparser.ConfigParser()
    config_found = config.read(config_path)
    if not config_found:
        logger.warning('Config file ' + config_path + ' not found, using defaults')

    return config

def setup_logger():
    """
    Initialize the logging object to write to syslog
    """
    # Initialize the logger object
    logger = logging.getLogger('xu4fan')
    logger.setLevel(logging.INFO)
    
    # Add handler to the logger
    handler = logging.handlers.SysLogHandler('/dev/log')
    
    # Add formatter to the handler
    format = "xu4fan[%(process)d]: [%(levelname)-8s] %(message)s"
    formatter = logging.Formatter(fmt=format)
    
    handler.formatter = formatter
    logger.addHandler(handler)
    return logger
    

# Function to release control of the fan, to be registered to run before exit
def safety_release(config_path):
    """
    Release control of the fan. To be called by upon exit or reciept of a signal
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    fan = Fan(config)
    fan.release_control()

def control_fan():
    """
    Main loop to control the fan

    Sets up the controller by reading configuration file, initializing the logger, and registering the safety release
    Initializes all of the hardware objects and loops forever, reading temperature and setting the fan PWM
    Stops if SIGINT or SIGTERM are received, and releases control of the fan
    """

    # Config is hardcoded to this path, could add an option to set a config file in the future ...
    config_path = '/etc/xu4fan/xu4fan.conf'
    old_pwm = -1

    # Initialize the config and logger
    logger = setup_logger()
    config = load_config(config_path, logger)
    verbose = config.getboolean('FanController', 'verbose', fallback=False)

    # Register to run the safety release when the program exits
    atexit.register(safety_release, config_path=config_path)
    signal_handler = SignalHandler()

    # Initialize hardware objects
    fan = Fan(config)
    thermo = Thermometer(config)
    fan_controller = FanController(config)

    logger.info('Taking control of fan')
    fan.take_control()

    # Main loop, run until the signal handler receives SIGTERM or SIGINT
    while (signal_handler.exit_now == False):
        current_temp = thermo.read_temp()
        new_pwm = fan_controller.get_pwm(current_temp)

        # Only print a message if the fan's setting has changed
        if (verbose and (new_pwm != old_pwm)): 
            logger.info('Temp: ' + str(current_temp) + ' setting pwm: ' + str(new_pwm))

        fan.set_pwm(new_pwm)
        old_pwm = new_pwm
        fan_controller.wait()

    safety_release(config_path)
    logger.info('Received signal to terminate')

# Can be run standalone as well
if __name__ == '__main__':
    control_fan()
