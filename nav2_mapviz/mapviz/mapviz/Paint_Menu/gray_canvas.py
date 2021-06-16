#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from mapviz.Helpers.simple_focus_out_widgets import FocusOutButton

logger = logging.getLogger("mapviz")


class GrayCanvas(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignTop)

        self.button = FocusOutButton(canvas_instance)
        self.button.setText('Grayscale')
        self.button.clicked.connect(self.canvas_instance.grayscale_canvas)

        self.grid.addWidget(self.button, 0, 0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
