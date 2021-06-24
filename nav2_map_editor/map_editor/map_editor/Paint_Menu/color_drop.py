#!/usr/bin/python3

# External lib
import qimage2ndarray
import numpy as np

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.Qt import Qt, QColor

# Python
import logging

# Source files
from map_editor.Helpers.colors_helpers import colors

# Constants
from map_editor.Helpers.magic_gui_numbers import color_icon_width, color_icon_height

logger = logging.getLogger("map_editor")


class ChangeColor(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignTop)

        self.label_color = QLabel()
        self.label_color.setText('Color')

        def create_color_icon(_color, _width=color_icon_width, _height=color_icon_height) -> QIcon:
            '''Used to create rectangle icons of each color, used for drop down menu'''
            _r, _g, _b, _ = QColor(_color).getRgb()
            return QIcon(QPixmap.fromImage(qimage2ndarray.array2qimage(
                (_r, _g, _b) * np.ones((_height, _width, 3), np.ubyte))))

        self.combo = QComboBox(self)
        for color_name, qt_color in colors.items():
            icon = create_color_icon(qt_color)
            self.combo.addItem(icon, color_name)

        def update_color() -> None:
            current_color = list(colors.values())[self.combo.currentIndex()]
            self.canvas_instance.paintColor = current_color
            self.canvas_instance.const_paintColor = current_color
            self.canvas_instance.update_light()
            logger.debug("Color changed to: " + str(current_color))

        self.combo.activated.connect(update_color)
        self.combo.activated.connect(lambda: self.canvas_instance.setFocus(Qt.OtherFocusReason))

        # self.grid.addWidget(self.label_color, 0, 0)
        self.grid.addWidget(self.combo, 0, 1)

        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
