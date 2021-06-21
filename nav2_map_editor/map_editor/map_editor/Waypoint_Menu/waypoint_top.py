#!/usr/bin/python3

# PyQT
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QRadioButton, QGridLayout, QLabel, QSlider
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from map_editor.Waypoint_Menu.waypoint_class import Waypoint
from map_editor.Helpers.simple_focus_out_widgets import FocusOutLineEdit, FocusOutButton
from map_editor.Helpers.helpers import AddingPosition

# Constants
from map_editor.Helpers.magic_gui_numbers import wp_default_text_size, wp_text_size_divider
from map_editor.Helpers.magic_gui_numbers import success_background, error_background

logger = logging.getLogger("map_editor")


class WaypointChoices(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        logger.debug("Waypoint menu created")

        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()
        self.title = QLabel()
        self.title.setText("Waypoints:")
        self.title.setAlignment(Qt.AlignCenter)

        self.radio = QWidget()
        radio_layout = QGridLayout()
        self.radio1 = QRadioButton('Add to start')
        self.radio2 = QRadioButton('Add to end')
        self.radio3 = QRadioButton('Add after')
        self.radio3_line_edit = FocusOutLineEdit(canvas_instance)
        self.radio3_line_edit.setEnabled(False)
        self.radio2.setChecked(True)

        def line_edit_update_adding_position():
            if not self.radio3.isChecked():
                return
            line_edit = self.radio3_line_edit.text()
            if not line_edit:
                self.canvas_instance.waypoint_adding_position = 0
                Waypoint.waypoint_adding_position = 0
            else:
                try:
                    line_edit = float(line_edit)
                    self.radio3_line_edit.setStyleSheet(success_background)
                    self.button.setEnabled(True)
                except ValueError:
                    self.radio3_line_edit.setStyleSheet(error_background)
                    self.button.setEnabled(False)
                    self.canvas_instance.adding_waypoint = False
                Waypoint.waypoint_adding_position = line_edit
                self.canvas_instance.waypoint_adding_position = line_edit

        self.radio3_line_edit.textChanged.connect(line_edit_update_adding_position)

        def change_adding_type():
            self.button.setEnabled(True)
            if self.radio1.isChecked():
                position = AddingPosition.START.value
                self.radio3_line_edit.setEnabled(False)
            elif self.radio2.isChecked():
                position = AddingPosition.END.value
                self.radio3_line_edit.setEnabled(False)
            elif self.radio3.isChecked():
                self.button.setEnabled(True)
                self.radio3_line_edit.setEnabled(True)
                line_edit = self.radio3_line_edit.text()
                if not line_edit:
                    line_edit = 0
                    self.radio3_line_edit.setText("0")
                    position = AddingPosition.END.value
                else:
                    try:
                        line_edit = float(line_edit)
                        self.radio3_line_edit.setStyleSheet(success_background)
                        self.button.setEnabled(True)
                        position = line_edit
                    except ValueError:
                        self.radio3_line_edit.setStyleSheet(error_background)
                        self.button.setEnabled(False)
                        self.canvas_instance.adding_waypoint = False
                        position = AddingPosition.END.value


            Waypoint.waypoint_adding_position = position
            self.canvas_instance.waypoint_adding_position = position

        self.radio1.clicked.connect(change_adding_type)
        self.radio2.clicked.connect(change_adding_type)
        self.radio3.clicked.connect(change_adding_type)

        radio_layout.addWidget(self.radio1, 0, 0)
        radio_layout.addWidget(self.radio2, 1, 0)
        radio_layout.addWidget(self.radio3, 2, 0)
        radio_layout.addWidget(self.radio3_line_edit, 3, 0)
        radio_layout.setContentsMargins(0, 0, 0, 0)

        self.radio.setLayout(radio_layout)
        self.button = FocusOutButton(canvas_instance)
        self.button.setCheckable(True)
        self.button.setText("&Add waypoint")

        self.reindex_button = FocusOutButton(canvas_instance)
        self.reindex_button.setText("&Reindex")

        self.show_idx_button = FocusOutButton(canvas_instance)
        self.show_idx_button.setText("&Show indexes")
        self.show_idx_button.setCheckable(True)
        self.show_idx_button.setChecked(True)

        self.wp_size_slider = QSlider(Qt.Horizontal)
        self.wp_size_slider.setSingleStep(1)
        self.wp_size_slider.setRange(1, 12)
        self.wp_size_slider.setValue(wp_default_text_size)
        Waypoint.waypoint_text_size = wp_default_text_size/wp_text_size_divider

        def reindex():
            Waypoint.reindex_waypoint()
            if Waypoint.waypoint_container:
                self.radio3_line_edit.setText(str(Waypoint.waypoint_container[-1].id))
                self.canvas_instance.populate_waypoint_table()

        self.reindex_button.clicked.connect(reindex)

        def show_indexes():
            if self.show_idx_button.isChecked():
                Waypoint.show_indexes(True)
                Waypoint.waypoint_showing_text = True
                self.wp_size_slider.setEnabled(True)
            else:
                Waypoint.show_indexes(False)
                Waypoint.waypoint_showing_text = False
                self.wp_size_slider.setEnabled(False)

        self.show_idx_button.clicked.connect(show_indexes)

        def change_wp_size(size_value):
            Waypoint.change_waypoint_text_size(size_value/wp_text_size_divider)
            self.canvas_instance.setFocus(Qt.OtherFocusReason)

        self.wp_size_slider.valueChanged.connect(lambda: change_wp_size(self.wp_size_slider.value()))

        # self.grid.addWidget(self.title, 0, 0)
        self.grid.addWidget(self.radio, 1, 0)
        self.grid.addWidget(self.button, 2, 0)
        self.grid.addWidget(self.reindex_button, 3, 0)
        self.grid.addWidget(self.show_idx_button, 4, 0)
        self.grid.addWidget(self.wp_size_slider, 5, 0)
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

    def toggle_state(self):
        last_state = self.canvas_instance.adding_waypoint
        self.canvas_instance.adding_waypoint = not last_state
        logger.debug("Waypoint adding toggled to: " + str(last_state))
