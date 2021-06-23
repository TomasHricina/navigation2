#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton
from PyQt5.QtGui import QFont

# Python
import logging

# Source files
from map_editor.Helpers.helpers import correct_image_path
from map_editor.Helpers.simple_focus_out_widgets import FocusOutLineEdit

# Constants
from map_editor.Helpers.magic_gui_numbers import left_menu_width

logger = logging.getLogger("map_editor")


class PathBox(QWidget):
    def __init__(self, left_menu):
        super().__init__()
        logger.debug("PathBox created")

        self.left_menu = left_menu
        self.title = QLabel()
        self.title.setText('______Yaml and Image Path:_____')
        self.parent_vbox = QVBoxLayout()
        self.parent_vbox.addWidget(self.title)

        self.yaml_widget = QWidget()
        self.yaml_hbox = QHBoxLayout()

        self.yaml_entry = FocusOutLineEdit(left_menu.canvas_instance)
        self.yaml_entry.setReadOnly(True)

        self.yaml_entry.setText(correct_image_path('default_map.yaml'))
        self.yaml_hbox.addWidget(self.yaml_entry)
        self.yaml_hbox.setContentsMargins(0, 0, 0, 0)
        self.yaml_widget.setLayout(self.yaml_hbox)

        self.img_widget = QWidget()
        self.img_hbox = QHBoxLayout()

        self.img_entry = FocusOutLineEdit(left_menu.canvas_instance)
        self.img_entry.setReadOnly(True)
        self.img_entry.setText(correct_image_path('default_map.pgm'))
        self.img_hbox.addWidget(self.img_entry)
        self.img_hbox.setContentsMargins(0, 0, 0, 0)
        self.img_widget.setLayout(self.img_hbox)

        self.save_as_widget = QWidget()
        self.save_as_hbox = QHBoxLayout()

        self.save_as_title = QLabel()
        self.save_as_title.setFont(QFont('Arial', 8))
        self.save_as_title.setText('Save path as:  ')
        self.save_as_hbox.addWidget(self.save_as_title)

        self.save_as_relative_radio = QRadioButton()
        self.save_as_relative_radio.setChecked(True)
        self.save_as_relative_radio.setFont(QFont('Arial', 10))
        self.save_as_relative_radio.setText('Relative')
        self.save_as_hbox.addWidget(self.save_as_relative_radio)

        self.save_as_absolute_radio = QRadioButton()
        self.save_as_absolute_radio.setFont(QFont('Arial', 10))
        self.save_as_absolute_radio.setText('Absolute')
        self.save_as_hbox.addWidget(self.save_as_absolute_radio)

        self.save_as_hbox.setContentsMargins(0, 0, 0, 0)
        self.save_as_widget.setLayout(self.save_as_hbox)

        self.parent_vbox.addWidget(self.yaml_widget)
        self.parent_vbox.addWidget(self.img_widget)
        self.parent_vbox.addWidget(self.save_as_widget)
        self.setFixedWidth(left_menu_width)
        self.parent_vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.parent_vbox)


