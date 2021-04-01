#!/usr/bin/python3
from PyQt5.QtGui import *
import numpy as np
import cv2
from collections import namedtuple
from enum import Enum, auto, unique


@unique
class Routine(Enum):
    LOAD = auto()
    CROP = auto()
    ANGLE = auto()


def dict2str(dictionary) -> str:
    result_string = ''
    for key, value in dictionary.items():
        result_string += (key + ': ' + str(value) + '\n')
    return result_string


def calc_angle(x, y):
    from math import atan2, degrees
    res = round(degrees(atan2(x, y)))
    if res < 0:
        return res + 360
    return res


def clamp(a, _min, _max):
    return max(min(a, _max), _min)


def numpyQImage(image):
    q_image = QImage()
    if image.dtype == np.uint8:
        if len(image.shape) == 2:
            channels = 1
            height, width = image.shape
            bytes_per_line = channels * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Indexed8)
            q_image.setColorTable([qRgb(i, i, i) for i in range(256)])
        elif len(image.shape) == 3:
            if image.shape[2] == 3:
                height, width, channels = image.shape
                bytes_per_line = channels * width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            elif image.shape[2] == 4:
                height, width, channels = image.shape
                bytes_per_line = channels * width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_ARGB32)
    return q_image


def rotateAndScale(img, degrees_clockwise, scale_factor=1):
    old_y, old_x, _ = img.shape
    rotation_matrix = cv2.getRotationMatrix2D(center=(old_x/2, old_y/2), angle=degrees_clockwise, scale=scale_factor)
    new_x, new_y = old_x*scale_factor, old_y*scale_factor
    r = np.deg2rad(degrees_clockwise)
    new_x, new_y = abs(np.sin(r)*new_y) + abs(np.cos(r)*new_x), abs(np.sin(r)*new_x) + abs(np.cos(r)*new_y)
    tx, ty = (new_x-old_x)/2, (new_y-old_y)/2
    rotation_matrix[0, 2] += tx
    rotation_matrix[1, 2] += ty
    return cv2.warpAffine(img, rotation_matrix, dsize=(int(new_x), int(new_y)))


def rotation(_pixmap, degrees_clockwise):
    img = _pixmap.toImage()
    channels_count = 4  # TODO: dont hardcode this stuff
    buffer_string = img.bits().asstring(img.width() * img.height() * channels_count)
    buffer_array = np.frombuffer(buffer_string, dtype=np.uint8).reshape((img.height(), img.width(), channels_count))
    rotated = rotateAndScale(buffer_array, -degrees_clockwise)
    rotated_q_image = numpyQImage(rotated)
    rotated_pixmap = QPixmap.fromImage(rotated_q_image)
    return rotated_pixmap


def scaleToFit(canvas_w, canvas_h, image_w, image_h):
    dimensions = namedtuple('dimensions', 'width height')
    image_width_height_ratio = image_w / image_h
    image_w = canvas_w
    image_h = image_w / image_width_height_ratio
    if image_h > canvas_h:
        image_h = canvas_h
        image_w = image_h * image_width_height_ratio
    return dimensions(int(image_w), int(image_h))


def dirr(dirable):
    """
    Function for developing
    """
    print('--------DIRRRR----------')
    try:
        print('print: ', dirable)
        print('type: ', type(dirable))
        print('--------DIR----------')
        print(*dir(dirable), sep='\n')
        print('--------/DIR----------')
    except:
        pass
    try:
        print('LEN: ', len(dirable))
    except:
        pass
    try:
        print('--------STR----------')
        print(dirable.__str__)
        print('--------/STR----------')
    except:
        pass
    try:
        print('--------REPR----------')
        print(dirable.__repr__)
        print('--------/REPR----------')
    except:
        pass
    print('--------/DIRRRR----------')
