#!/usr/bin/python3

# External lib
import yaml  # pip pyaml

# PyQT
from PyQt5.QtGui import QImage

# Source files
from mapViz.Helpers.magic_gui_numbers import default_image_name


def yaml_and_image():
    try:
        with open('Images/default_yaml.yaml', 'r') as file:
            _default_yaml = yaml.safe_load(file)
        _default_image = QImage()
        _default_image.load('Images/'+default_image_name)
        return _default_yaml, _default_image
    except FileNotFoundError:
        pass

default_yaml, default_image = yaml_and_image()
