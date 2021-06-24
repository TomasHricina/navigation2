#!/usr/bin/python3

# External lib
import numpy as np
import cv2
import qimage2ndarray


# PyQT
from PyQt5.QtGui import *
from PyQt5.QtCore import QRect, QPoint

# Python
from collections import namedtuple
from enum import Enum, auto, unique


def correct_image_path(image_name):
    import os
    _ = os.path.split(__file__)[0]
    _ = os.path.split(_)[0]
    return os.path.join(_, 'Images', image_name)


@unique
class Routine(Enum):
    '''Each routine represents action by user'''
    LOAD = auto()
    CROP = auto()
    ANGLE = auto()
    PAINT_BRUSH = auto()
    PAINT_LINE = auto()
    PAINT_RECT = auto()
    GRAY = auto()


@unique
class AddingPosition(Enum):
    '''Informs the Waypoint class, where user wants to put waypoint,
     if it is number, it is after that number'''
    END = 'e'
    START = 's'


def create_logger(app_name):
    import logging
    import os
    """Create a logging interface"""
    logging_level = os.getenv('logging', logging.INFO)
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(app_name)
    return logger


unit_vectors = {'up': QPoint(0, 1),
                'down': QPoint(0, -1),
                'left': QPoint(1, 0),
                'right': QPoint(-1, 0),
                'upleft': QPoint(1, 1),
                'upright': QPoint(-1, 1),
                'downleft': QPoint(1, -1),
                'downright': QPoint(-1, -1)
                }


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
    channels_count = 4
    buffer_string = img.bits().asstring(img.width() * img.height() * channels_count)
    buffer_array = np.frombuffer(buffer_string, dtype=np.uint8).reshape((img.height(), img.width(), channels_count))
    rotated = rotateAndScale(buffer_array, -degrees_clockwise)
    rotated_q_image = numpyQImage(rotated)
    rotated_pixmap = QPixmap.fromImage(rotated_q_image)
    return rotated_pixmap


def remove_rotation_artifacts(_pixmap, _width, _height):
    delta_w = (_pixmap.width() - _width) // 2
    delta_h = (_pixmap.height() - _height) // 2
    crop_rect = QRect(delta_w, delta_h, _width, _height)
    return _pixmap.copy(crop_rect)


def scaleToFit(canvas_w, canvas_h, image_w, image_h):
    dimensions = namedtuple('dimensions', 'width height')
    image_width_height_ratio = image_w / image_h
    image_w = canvas_w
    image_h = image_w / image_width_height_ratio
    if image_h > canvas_h:
        image_h = canvas_h
        image_w = image_h * image_width_height_ratio
    return dimensions(int(image_w), int(image_h))

def qimage2array(_qimage):
    return qimage2ndarray.rgb_view(_qimage)


def qimage2raw_array(_qimage):
    return qimage2ndarray.raw_view(_qimage)


def single_rgb2gray(rgb):
    return round(np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])[0][0])


def show_images(*_images, gray=False):
    """
    Function for developing
    """
    import matplotlib.pyplot as plt

    ax = []
    # fig = plt.figure(figsize=(9, 13))
    fig = plt.figure()
    columns = len(_images)
    rows = 1

    def show(_img):
        if gray:
            plt.imshow(_img, cmap='gray')
        else:
            plt.imshow(_img)

    for i, _image in enumerate(_images):
        print()
        print('Image type:')
        ax.append(fig.add_subplot(rows, columns, i + 1))
        if isinstance(_image, QImage):
            print('Qimage')
            show(qimage2array(_image))
        elif isinstance(_image, QPixmap):
            print('Qpixmap')
            show(qimage2array(_image.toImage()))
        elif isinstance(_image, np.ndarray):
            print('Ndarray')
            show(_image)
        else:
            print('show_image: unsupported image type')
            return
        print()
    plt.show()


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