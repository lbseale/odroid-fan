
===========================
 Odroid XU4 Fan Controller
===========================

A hysteresis fan controller for the Odroid XU4.

The fan will come on at a set trip-point, but will only turn off after it has cooled down to its 'hysteresis' temperature.

For example, say the trip point is 60C, and the hysteresis is 8C. The fan will turn on when the temperature reaches 60C, but will not turn off until the temperature reaches (60-8) = 52C.

For more information about this type of controller, see this `Wikipedia article <https://en.wikipedia.org/wiki/Bang%E2%80%93bang_control>`_.


Installation
============

To install using the debian package, use::

  sudo apt install xu4fan-XXX.deb

To uninstall, use::

  sudo dpkg --remove xu4fan

Systemd Service
===============

The fan controller is run by a systemd service. Which is started automatically when it is installed.

To stop it use::

  sudo systemctl stop xu4fan.service

To restart use::

  sudo systemctl restart xu4fan.service

To disable it, and not allow it to start automatically, use::

  sudo systemctl disable xu4fan.service

To enable, use::

  sudo systemctl enable xu4fan.service
  
Configuration
=============

The configuration file for the fan controller is located in::

  /etc/xu4fan.cfg

You can use this file to change the settings for the fan contoller, such as trip points and hysteresis.

You must restart the fan controller after changing the configuration file. To do this use::

  sudo systemctl restart xu4fan.service

Sample Files
============

A sample configuration file, and systemd .service file are located in::

  /usr/share/xu4fan/
