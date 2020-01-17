===========================
 Odroid XU4 Fan Controller
===========================

Hysteresis fan controller for the Odroid XU4.

**This controller only works with Ubuntu on the Odroid XU4, it is not designed for any other computer or operating system**

When the fan comes on, it stays on for a while. It cools down the CPU enough that it stays off for a while too. As the CPU gets hotter, the fan spins harder.

For example, say the trip point is 60C, and the hysteresis is 8C. The fan will turn on when the temperature reaches 60C, but will not turn off until the temperature reaches (60-8) = 52C.

For more information about this type of controller, see this `Wikipedia article <https://en.wikipedia.org/wiki/Bang%E2%80%93bang_control>`_.

Installation
============

`Download <https://github.com/lbseale/odroid-fan/raw/master/xu4fan-installer.deb>`_ the installer from GitHub

To install using the GUI installer, double-click on ``xu4fan-installer.deb`` file. Then click the ``Install Package`` button in the top-right of the window.

To install using the command line, use::

  sudo apt install xu4fan-installer.deb

To uninstall, use::

  sudo apt remove xu4fan
  
The fan controller will start automatically after it is installed. 
  
Configuration
=============

The configuration file for the fan controller is located in::

  /etc/xu4fan/xu4fan.conf

You can use this file to change the settings for the fan contoller, such as trip points and hysteresis.

You must restart the fan controller after changing the configuration file. To do this use::

  sudo systemctl restart xu4fan.service

Configuration Options
---------------------

:trip_temps: List of temperatures corresponding to PWM values.
   When the temperature is increasing, and one of these temperatures is reached,
   the corresponding PWM value will be set.
   Units are Degrees C * 1000. 
   **Example:** ``[60000, 70000, 80000]``
:trip_speeds: List of PWM values corresponding to temperatures.
   Units are PWM values in the range (0-255). A value of 120 is (120 / 255) = 47% of the fan's maximum power. 
   As the CPU gets hotter, the fan spins harder. Note that values below 120 are not powerful enough to spin the stock fan.
   **Example:** ``[120, 200, 240]``
:hysteresis: Number of degrees past the trip point the temperature must reach
   to drop to the preceeding trip point. If the trip point is 60C, and the hysteresis
   is 8C, then the temperature must fall below (60 - 8) = 52C for the fan to turn off.
   Units are Degrees C * 1000. 
   **Example:** ``8000``
:poll_interval: Number of seconds for the fan controller to wait between temperature checks
   **Example:** ``0.25``
:verbose: If True, print a message to syslog every time the fan changes speed

The options for the ``[Thermometer]`` and ``[Fan]`` sections should not need to change. 
These are specific to the Odroid XU4

Systemd Service
===============

The fan controller is run by a systemd service. Which is started automatically when it is installed. It will also start automatically when your Odroid XU4 starts.

To see its status, use::

  sudo systemctl status xu4fan.service

To stop it use::

  sudo systemctl stop xu4fan.service

To disable it, and not allow it to start automatically, use::

  sudo systemctl disable xu4fan.service

To enable, use::

  sudo systemctl enable xu4fan.service

Sample Files
============

A sample configuration file, and systemd .service file are located in::

  /usr/share/xu4fan/
