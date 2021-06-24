#!/usr/bin/python3

# PyQT
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtWidgets import QGridLayout, QLabel, QTableWidget
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from map_editor.Waypoint_Menu.waypoint_class import Waypoint
from map_editor.Waypoint_Menu.waypoint_top import WaypointChoices
from map_editor.Waypoint_Menu.waypoint_table import WaypointTable

# Constants
from map_editor.Helpers.magic_gui_numbers import waypoint_menu_width, waypoint_column_width

logger = logging.getLogger("map_editor")


class WaypointMenu(QWidget):
    '''
    Whole Waypoint column
    '''
    def __init__(self, canvas_instance):
        super().__init__()
        logger.debug("Waypoint menu created")

        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()

        self.choices = WaypointChoices(canvas_instance)

        self.waypoint_table = WaypointTable(canvas_instance)

        self.grid.addWidget(self.choices, 0, 0)
        self.grid.addWidget(self.waypoint_table, 1, 0)

        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)