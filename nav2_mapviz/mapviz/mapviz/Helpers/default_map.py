#!/usr/bin/python3

# External lib
import yaml  # pip pyaml

# PyQT
from PyQt5.QtGui import QImage

# Source files
from mapviz.Helpers.magic_gui_numbers import default_image_name
from mapviz.Helpers.helpers import correct_image_path

def yaml_and_image():
    try:
        with open(correct_image_path('default_yaml.yaml'), 'r') as file:
            _default_yaml = yaml.safe_load(file)
        _default_image = QImage()
        _default_image.load(correct_image_path(default_image_name))
        return _default_yaml, _default_image
    except FileNotFoundError:
        pass

default_yaml, default_image = yaml_and_image()
