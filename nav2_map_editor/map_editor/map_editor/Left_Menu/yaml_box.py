#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt

# Python
import os
from re import match
import logging

# Source files
from map_editor.Helpers.simple_focus_out_widgets import FocusOutLineEdit
from map_editor.Helpers.default_map import default_yaml
from map_editor.Helpers.helpers import correct_image_path

# Constants
from map_editor.Helpers.magic_gui_numbers import left_menu_width
from map_editor.Helpers.magic_gui_numbers import warning_background, success_background, error_background
from map_editor.Helpers.magic_gui_numbers import valid_filename_regex, list_sanitizer_regex


logger = logging.getLogger("map_editor")


class YamlSingleRow(QWidget):
    def __init__(self, label, left_menu):
        super().__init__()

        self.hbox = QHBoxLayout()
        self.label = QLabel()
        self.label.setText(label)
        self.entry = FocusOutLineEdit(left_menu.canvas_instance)

        self.button = QPushButton()
        self.button.setIcon(QIcon(correct_image_path('default_button.png')))
        self.label_image = QLabel()

        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.entry)
        self.hbox.addWidget(self.button)
        self.setFixedWidth(left_menu_width)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.hbox)


class YamlBox(QWidget):
    def __init__(self, left_menu):
        super().__init__()
        logger.debug("YamlBox created")

        self.vbox = QVBoxLayout()
        self.title = QLabel()
        self.left_menu = left_menu
        self.latest_yaml_name = 'default_map.yaml'
        self.latest_yaml = default_yaml
        self.flags = {  # used for disabling Save, when input is invalid, call self.update_flags()
            'yaml': True,
            'image': True,
            'resolution': True,
            'origin': True,
            'occupied_thresh': True,
            'free_thresh': True,
            'negate': True,
            'mode': True}

        self.title.setText('________Edit Yaml file:________')
        self.entry_yaml = YamlSingleRow('yaml', left_menu)
        self.entry_image = YamlSingleRow('image', left_menu)
        self.entry_resolution = YamlSingleRow('resolution', left_menu)
        self.entry_origin = YamlSingleRow('origin', left_menu)
        self.entry_occupied_thresh = YamlSingleRow('occupied_thresh', left_menu)
        self.entry_free_thresh = YamlSingleRow('free_thresh', left_menu)
        self.entry_negate = YamlSingleRow('negate', left_menu)
        self.entry_mode = YamlSingleRow('mode', left_menu)

        # below functions are used to verify correct user input and notify user, by changing background
        def yaml_entry_func() -> None:
            yaml_value = self.entry_yaml.entry.text()
            valid_filename = match(valid_filename_regex, yaml_value)

            if valid_filename:
                self.entry_yaml.entry.setStyleSheet(success_background)
                self.flags['yaml'] = True
            else:
                self.entry_yaml.entry.setStyleSheet(error_background)
                self.flags['yaml'] = False

        def image_entry_func() -> None:
            image_value = self.entry_image.entry.text()
            valid_filename = match(valid_filename_regex, image_value)

            if valid_filename:
                self.entry_image.entry.setStyleSheet(success_background)
                self.flags['image'] = True
            else:
                self.entry_image.entry.setStyleSheet(error_background)
                self.flags['image'] = False

        def resolution_entry_func() -> None:
            resolution_value = self.entry_resolution.entry.text()
            try:
                resolution_value = float(resolution_value)
                0 / resolution_value  # cant be zero
                self.entry_resolution.entry.setStyleSheet(success_background)
                self.flags['resolution'] = True
            except (KeyError, ValueError, ZeroDivisionError):
                self.entry_resolution.entry.setStyleSheet(error_background)
                self.flags['resolution'] = False

        def origin_entry_func() -> None:
            origin_value = self.entry_origin.entry.text()
            sanitized = match(list_sanitizer_regex, origin_value)
            if not sanitized:
                self.entry_origin.entry.setStyleSheet(error_background)
                self.flags['origin'] = False
            else:
                try:
                    origin_value = eval(origin_value)
                    if all(isinstance(n, (int, float)) for n in origin_value) and len(origin_value) == 3:
                        self.entry_origin.entry.setStyleSheet(success_background)
                        self.flags['origin'] = True
                    else:
                        self.entry_origin.entry.setStyleSheet(error_background)
                        self.flags['origin'] = False
                except (NameError, SyntaxError, TypeError):
                    self.entry_origin.entry.setStyleSheet(error_background)
                    self.flags['origin'] = False

        def occupied_thresh_entry_func() -> None:
            try:
                occupied_thresh_value = float(self.entry_occupied_thresh.entry.text())
            except ValueError:
                self.entry_occupied_thresh.entry.setStyleSheet(error_background)
                self.flags['occupied_thresh'] = False
            else:
                if 0 <= occupied_thresh_value <= 1:
                    self.entry_occupied_thresh.entry.setStyleSheet(success_background)
                    self.flags['occupied_thresh'] = True
                else:
                    self.entry_occupied_thresh.entry.setStyleSheet(error_background)
                    self.flags['occupied_thresh'] = False

        def free_thresh_entry_func() -> None:
            try:
                free_thresh_value = float(self.entry_free_thresh.entry.text())
            except ValueError:
                self.entry_free_thresh.entry.setStyleSheet(error_background)
                self.flags['free_thresh'] = False
            else:
                if 0 <= free_thresh_value <= 1:
                    self.entry_free_thresh.entry.setStyleSheet(success_background)
                    self.flags['free_thresh'] = True
                else:
                    self.entry_free_thresh.entry.setStyleSheet(error_background)
                    self.flags['free_thresh'] = False

        def negate_entry_func() -> None:
            negate_value = self.entry_negate.entry.text()
            if negate_value == '0' or negate_value == '1':
                self.entry_negate.entry.setStyleSheet(success_background)
                self.flags['negate'] = True
            else:
                self.entry_negate.entry.setStyleSheet(error_background)
                self.flags['negate'] = False

        def mode_entry_func() -> None:
            mode_value = self.entry_mode.entry.text()
            if mode_value in ('', 'trinary', 'scale', 'raw'):
                self.entry_mode.entry.setStyleSheet(success_background)
                self.flags['mode'] = True
            else:
                self.entry_mode.entry.setStyleSheet(error_background)
                self.flags['mode'] = False

        self.entry_yaml.entry.textChanged.connect(yaml_entry_func)
        self.entry_image.entry.textChanged.connect(image_entry_func)
        self.entry_resolution.entry.textChanged.connect(resolution_entry_func)
        self.entry_origin.entry.textChanged.connect(origin_entry_func)
        self.entry_occupied_thresh.entry.textChanged.connect(occupied_thresh_entry_func)
        self.entry_free_thresh.entry.textChanged.connect(free_thresh_entry_func)
        self.entry_negate.entry.textChanged.connect(negate_entry_func)
        self.entry_mode.entry.textChanged.connect(mode_entry_func)

        def yaml_default_button_func() -> None:
            self.entry_yaml.entry.setText(self.latest_yaml_name)
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def image_default_button_func() -> None:
            self.entry_image.entry.setText(str(self.latest_yaml['image']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def resolution_default_button_func() -> None:
            self.entry_resolution.entry.setText(str(self.latest_yaml['resolution']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def origin_default_button_func() -> None:
            self.entry_origin.entry.setText(str(self.latest_yaml['origin']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def occupied_thresh_default_button_func() -> None:
            self.entry_occupied_thresh.entry.setText(str(self.latest_yaml['occupied_thresh']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def free_thresh_default_button_func() -> None:
            self.entry_free_thresh.entry.setText(str(self.latest_yaml['free_thresh']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def negate_default_button_func() -> None:
            self.entry_negate.entry.setText(str(self.latest_yaml['negate']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def mode_default_button_func() -> None:
            try:
                # optional
                self.entry_mode.entry.setText(str(self.latest_yaml['mode']))
            except KeyError:
                self.entry_mode.entry.setText('')
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        self.entry_yaml.button.clicked.connect(yaml_default_button_func)
        self.entry_image.button.clicked.connect(image_default_button_func)
        self.entry_resolution.button.clicked.connect(resolution_default_button_func)
        self.entry_origin.button.clicked.connect(origin_default_button_func)
        self.entry_occupied_thresh.button.clicked.connect(occupied_thresh_default_button_func)
        self.entry_free_thresh.button.clicked.connect(free_thresh_default_button_func)
        self.entry_negate.button.clicked.connect(negate_default_button_func)
        self.entry_mode.button.clicked.connect(mode_default_button_func)

        self.vbox.addWidget(self.title)
        self.vbox.addWidget(self.entry_yaml)
        self.vbox.addWidget(self.entry_image)
        self.vbox.addWidget(self.entry_resolution)
        self.vbox.addWidget(self.entry_origin)
        self.vbox.addWidget(self.entry_occupied_thresh)
        self.vbox.addWidget(self.entry_free_thresh)
        self.vbox.addWidget(self.entry_negate)
        self.vbox.addWidget(self.entry_mode)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

    # after yaml is read (default or loaded), its shown to the user via entries
    def insert_yaml_into_entries(self) -> None:
        logger.debug("Yaml inserted into entries")
        self.entry_yaml.entry.setText(self.latest_yaml_name)
        self.entry_image.entry.setText(str(self.latest_yaml['image']))
        self.entry_resolution.entry.setText(str(self.latest_yaml['resolution']))
        self.entry_origin.entry.setText(str(self.latest_yaml['origin']))
        self.entry_occupied_thresh.entry.setText(str(self.latest_yaml['occupied_thresh']))
        self.entry_free_thresh.entry.setText(str(self.latest_yaml['free_thresh']))
        self.entry_negate.entry.setText(str(self.latest_yaml['negate']))
        try:
            # optional
            self.entry_mode.entry.setText(str(self.latest_yaml['mode']))
        except KeyError:
            self.entry_mode.entry.setText('')

    # reads user input from entries and puts them in dict
    def harvest_entry_into_latest_yaml(self) -> None:
        logger.debug("Entry harvested into yaml")
        self.latest_yaml['image'] = self.entry_image.entry.text()
        self.latest_yaml['resolution'] = self.entry_resolution.entry.text()
        self.latest_yaml['origin'] = self.entry_origin.entry.text()
        self.latest_yaml['occupied_thresh'] = self.entry_occupied_thresh.entry.text()
        self.latest_yaml['free_thresh'] = self.entry_free_thresh.entry.text()
        self.latest_yaml['negate'] = self.entry_negate.entry.text()

        mode_value = self.entry_mode.entry.text()
        if mode_value == '':
            self.latest_yaml.pop('mode', None)
        else:
            self.latest_yaml['mode'] = mode_value

    def update_flags(self) -> None:
        self.left_menu.yaml_box.flags = self.flags
