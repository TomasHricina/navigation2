#!/usr/bin/python3

# PyQT
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QGridLayout, QLabel, QTableWidget
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from mapViz.Waypoint_Menu.waypoint_class import Waypoint
from mapViz.Waypoint_Menu.waypoint_top import WaypointChoices

# Constants
from mapViz.Helpers.magic_gui_numbers import waypoint_menu_width, waypoint_column_width

logger = logging.getLogger("MapViz")


class WaypointMenu(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        logger.debug("Waypoint menu created")

        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()

        self.choices = WaypointChoices(canvas_instance)

        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.horizontalHeader().setVisible(False)

        self.table.setMinimumWidth(waypoint_menu_width)
        self.table.setMaximumWidth(waypoint_menu_width)
        self.table.setColumnWidth(0, waypoint_column_width)

        self.grid.addWidget(self.choices, 0, 0)
        self.grid.addWidget(self.table, 1, 0)

        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

    def populate(self):
        wpc = Waypoint.waypoint_container
        self.table.setRowCount(len(wpc))

        for wp_idx, wp_value in enumerate(wpc):
            cell_text = str(wp_value.x) + ' ' + str(wp_value.y)
            cell_widget = QLabel()
            cell_widget.setText(cell_text)
            self.table.setCellWidget(wp_idx, 0, cell_widget)

    def refresh_specific_waypoint(self, wp_idx):
        wp = Waypoint.waypoint_container[wp_idx]
        cell_text = str(wp.x) + ' ' + str(wp.y)
        cell_widget = QLabel()
        cell_widget.setText(cell_text)
        self.table.setCellWidget(wp_idx, 0, cell_widget)
