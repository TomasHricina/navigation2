#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from map_editor.Helpers.simple_focus_out_widgets import FocusOutButton

logger = logging.getLogger("map_editor")


class PaintLine(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignTop)

        self.button = FocusOutButton(canvas_instance)
        self.button.setText('Draw Line')
        self.button.setCheckable(True)

        self.grid.addWidget(self.button, 0, 0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

    def toggle_state(self):
        self.canvas_instance.paint_lineReady = not self.canvas_instance.paint_lineReady
        logger.debug("Paint line toggled to: " + str(self.canvas_instance.paint_lineReady))
