# External lib
import numpy as np

# PyQT
from PyQt5.QtCore import Qt
from PyQt5.Qt import QColor

red_weight = 0.299
green_weight = 0.587
blue_weight = 0.114

colors = {
    'Nav2-blue': QColor(20, 88, 134, 255),
    'White': Qt.white,
    'Black': Qt.black,
    'Blue': Qt.blue,
    'Red': Qt.red,
    'Cyan': Qt.cyan,
    'Magenta': Qt.magenta,
    'Green': Qt.green,
    'Yellow': Qt.yellow
}


def rgb2gray(rgb):
    return np.round(np.dot(rgb[..., :3], [red_weight, green_weight, blue_weight]), 0)


def single_rgb2gray(rgb):
    if not isinstance(rgb, np.ndarray):
        rgb = np.array(rgb)
    return np.dot(rgb[..., :3], [red_weight, green_weight, blue_weight])


def calculate_lightness(rgb):
    if isinstance(rgb, QColor):
        rgb = rgb.getRgb()
    elif isinstance(rgb, type(Qt.white)):
        rgb = QColor(rgb).getRgb()
    rgb = rgb[0], rgb[1], rgb[2]
    return single_rgb2gray(rgb)


def change_lightness(rgb, lightness):
    tolerance = 0.1
    m = 0.1  # multiplier step
    target = lightness
    if isinstance(rgb, QColor):
        rgb = rgb.getRgb()
    elif isinstance(rgb, type(Qt.white)):
        rgb = QColor(rgb).getRgb()
    rgb = [rgb[0], rgb[1], rgb[2]]
    # mr = m * red_weight
    # mb = m * blue_weight
    # mg = m * green_weight
    mr = m
    mb = m
    mg = m
    if calculate_lightness(rgb) < target:
        while (target - tolerance) > calculate_lightness(rgb) < target:
            if rgb[0]+mr < 255:
                rgb[0] += mr
            if rgb[1]+mb < 255:
                rgb[1] += mb
            if rgb[2]+mg < 255:
                rgb[2] += mg
    elif calculate_lightness(rgb) > target:
        while (target + tolerance) < calculate_lightness(rgb) > target:
            if rgb[0]-mr > 0:
                rgb[0] -= mr
            if rgb[1]-mb > 0:
                rgb[1] -= mb
            if rgb[2]-mg > 0:
                rgb[2] -= mg
    rgb = round(rgb[0]), round(rgb[1]), round(rgb[2])
    return rgb

