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

    # def populate(self):
    #     wpc = Waypoint.waypoint_container
    #     self.table.setRowCount(len(wpc))

    #     for wp_idx, wp_value in enumerate(wpc):
    #         cell_text = str(wp_value.x) + ' ' + str(wp_value.y)
    #         cell_widget = QLabel()
    #         cell_widget = QPushButton()
    #         cell_widget.clicked.connect(lambda: self.canvas_instance.delete_specific_waypoint(wp_idx))
            



    #         # cell_widget.setText(cell_text)
    #         self.table.setCellWidget(wp_idx, 0, cell_widget)

    # def refresh_specific_waypoint(self, wp_idx):
    #     wp = Waypoint.waypoint_container[wp_idx]
    #     cell_text = str(wp.x) + ' ' + str(wp.y)
    #     cell_widget = QLabel()
    #     cell_widget.setText(cell_text)
    #     self.table.setCellWidget(wp_idx, 0, cell_widget)

