#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QTableWidget
from PyQt5.Qt import Qt

# Python
import logging
from map_editor.Helpers.simple_focus_out_widgets import FocusOutButton

# Source files
from map_editor.Waypoint_Menu.waypoint_class import Waypoint

# Constants
from map_editor.Helpers.magic_gui_numbers import waypoint_menu_width, waypoint_column_width

logger = logging.getLogger("map_editor")


class WaypointCell(QWidget):
    """Cell widget in waypoint table"""
    def __init__(self, canvas_instance, wp_value, parent=None):
        QWidget.__init__(self, parent)

        self.canvas_instance = canvas_instance
        cell_layout = QHBoxLayout()

        cell_text = str(wp_value.x) + 'x' + str(wp_value.y)
        self.cell_text_label = QLabel(self)
        self.cell_text_label.setText(cell_text)

        self.delete_button = FocusOutButton(canvas_instance)
        self.delete_button.setFixedWidth(16)
        self.delete_button.setFixedHeight(16)
        self.delete_button.setText("X")

        def delete():
            logger.debug("Waypoint with id: " + str(wp_value.id) + " deleted")
            self.canvas_instance.delete_specific_waypoint(wp_value.id)

        self.delete_button.clicked.connect(delete)

        cell_layout.addWidget(self.cell_text_label)
        cell_layout.addWidget(self.delete_button)
        cell_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(cell_layout)


class WaypointTable(QTableWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        logger.debug("Waypoint table created")
        self.canvas_instance = canvas_instance
        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.setMinimumWidth(waypoint_menu_width)
        self.setMaximumWidth(waypoint_menu_width)
        self.setColumnWidth(0, waypoint_column_width)


    def populate(self):
        logger.debug("Populate waypoint table")
        Waypoint.sort_waypoints_by_id()
        wpc = Waypoint.waypoint_container
        self.setRowCount(len(wpc))

        for wp_idx, wp_value in enumerate(wpc):
            def cell(wp_idx=wp_idx, wp_value=wp_value):
                # this function is needed for capturing value each iteration
                _cell_widget = WaypointCell(self.canvas_instance, wp_value=wp_value)
                return _cell_widget          
            self.setCellWidget(wp_idx, 0, cell())

        self.scrollToBottom()

    # def refresh_specific_waypoint(self, wp_idx):
    #     wp = Waypoint.waypoint_container[wp_idx]
    #     cell_text = str(wp.x) + ' ' + str(wp.y)
    #     cell_widget = QLabel()
    #     cell_widget.setText(cell_text)
    #     self.setCellWidget(wp_idx, 0, cell_widget)

