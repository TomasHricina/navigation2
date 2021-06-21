#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from map_editor.Helpers.simple_focus_out_widgets import FocusOutButton

logger = logging.getLogger("map_editor")


class Zoom(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        self.grid = QGridLayout()
        self.canvas_instance = canvas_instance
        self.button = FocusOutButton(canvas_instance)
        self.button.setText("Zoom")
        self.button.setCheckable(True)
        self.button.setToolTip("Shift+Mouse drag")
        self.grid.addWidget(self.button)
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

    def toggle_state(self):
        self.canvas_instance.zooming_activated = not self.canvas_instance.zooming_activated
