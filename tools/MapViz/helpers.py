#!/usr/bin/python3
from PyQt5.QtGui import *
import numpy as np
import cv2 # use headless cv to avoid known bug when using PyQT5+CV
from collections import namedtuple


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


def rotateAndScale(img, degrees_ccw, scale_factor=1):
    old_y, old_x, _ = img.shape
    rotation_matrix = cv2.getRotationMatrix2D(center=(old_x/2, old_y/2), angle=degrees_ccw, scale=scale_factor)
    new_x, new_y = old_x*scale_factor, old_y*scale_factor
    r = np.deg2rad(degrees_ccw)
    new_x, new_y = (abs(np.sin(r)*new_y) + abs(np.cos(r)*new_x), abs(np.sin(r)*new_x) + abs(np.cos(r)*new_y))
    tx, ty = ((new_x-old_x)/2, (new_y-old_y)/2)
    rotation_matrix[0, 2] += tx
    rotation_matrix[1, 2] += ty
    return cv2.warpAffine(img, rotation_matrix, dsize=(int(new_x), int(new_y)))


def rotation(_pixmap, angle):
    img = _pixmap.toImage()
    channels_count = 4
    buffer_string = img.bits().asstring(img.width() * img.height() * channels_count)
    buffer_array = np.frombuffer(buffer_string, dtype=np.uint8).reshape((img.height(), img.width(), channels_count))
    rotated = rotateAndScale(buffer_array, angle)
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


def parse_map_yaml(path_to_yaml):
    import yaml  # pip pyaml
    import os.path
    """
    Opens YAML file via absolute or relative path. 
    CWD must be set to, where YAML file is located
    Makes sure, that all required fields are filled and within constraints
    specified in https://wiki.ros.org/map_server#YAML_format
    If no error:
        return parsed YAML dictionary
    else:
        list of error messages
    Should not throw.
    """

    error_messages = []
    try:
        with open(path_to_yaml, 'r') as stream:
            parsed_yaml = yaml.safe_load(stream)

        # * Required fields:
        if not os.path.isfile(parsed_yaml['image']):
            error_messages.append('No image found')

        # Resolution
        try:
            float(parsed_yaml['resolution'])
        except ValueError:
            error_messages.append('Faulty resolution type')

        # Origin
        yaml_origin = parsed_yaml['origin']
        if not (type(yaml_origin) is list):
            error_messages.append('Faulty origin type - not a list')
        if not (all(isinstance(n, (int, float)) for n in yaml_origin)):
            error_messages.append('Faulty element type in origin list')

        # Occupied threshold
        try:
            yaml_occupied_thresh = float(parsed_yaml['occupied_thresh'])
        except ValueError:
            error_messages.append('Faulty occupied threshold type')

        else:
            if not (0 <= yaml_occupied_thresh <= 1):
                error_messages.append('Faulty occupied threshold value')

        # Free threshold
        try:
            yaml_free_thresh = float(parsed_yaml['free_thresh'])
        except TypeError:
            error_messages.append('Faulty free threshold type')
        else:
            if not (0 <= yaml_free_thresh <= 1):
                error_messages.append('Faulty free threshold value')

        # Negate
        yaml_negate_thresh = parsed_yaml['negate']
        if not (yaml_negate_thresh == 0 or yaml_negate_thresh == 1):
            error_messages.append('Faulty negate value')

        # * Optional fields:

        # Mode
        try:
            yaml_mode = parsed_yaml['mode']
            if yaml_mode not in ('trinary', 'scale', 'raw'):
                error_messages.append('Faulty mode value')
        except KeyError:
            pass

    except yaml.YAMLError:
        error_messages.append('Corrupted YAML')
    except KeyError:
        error_messages.append('Required field missing')

    if not error_messages:
        return parsed_yaml
    else:
        return error_messages


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
