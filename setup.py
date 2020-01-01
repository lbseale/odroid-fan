#!/usr/bin/env python
# Used this as a template: https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages

#here = path.abspath(path.dirname(__file__))
## Get the long description from the README file
#with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()

setup(
    name = 'odroid-fan',
    version = '0.1',
    description = 'A hysteresis fan controller for odroid xu4',
    #long_description = long_description,
    url = 'https://github.com/lbseale/odroid-fan',
    author = 'Luke Seale',
    author_email = '19484084+lbseale@users.noreply.github.com',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop'
        'Topic :: System :: Hardware',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
    keywords = 'odroid fan hardware driver',
    pacakge_dir = {'': 'odroid-fan'},
    python_requires = '>=3.6',
    install_requires = ['atexit', 'signal', 'configparser', 'json', 'logging'],
    entry_points = {
        'console_scripts': [
            'odroid-fan = odroid-fan.main:main',
        ],
    },
)
