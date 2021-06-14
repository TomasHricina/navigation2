#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QIntValidator
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from mapViz.Helpers.simple_focus_out_widgets import FocusOutLineEdit
from mapViz.Helpers.helpers import Routine

# Constants
from mapViz.Helpers.magic_gui_numbers import angle_button_dimensions, left_menu_width

logger = logging.getLogger("MapViz")


class AngleBox(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        logger.debug("AngleBox created")

        self.canvas_instance = canvas_instance
        self.hbox = QHBoxLayout()
        self.label = QLabel()
        self.label.setText('Angle')

        self.angle_entry = FocusOutLineEdit(canvas_instance)
        self.angle_entry.setText('0')
        self.angle_entry.setValidator(QIntValidator(-9999, 9999))
        self.angle_entry.setAlignment(Qt.AlignCenter)

        self.button_0 = QPushButton()
        self.button_0.setText('0°')
        self.button_0.setFixedSize(*angle_button_dimensions)

        self.button_plus_90 = QPushButton()
        self.button_plus_90.setText('+90°')
        self.button_0.setFixedSize(*angle_button_dimensions)

        self.button_minus_90 = QPushButton()
        self.button_minus_90.setText('-90°')
        self.button_0.setFixedSize(*angle_button_dimensions)

        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.angle_entry)
        self.hbox.addWidget(self.button_0)
        self.hbox.addWidget(self.button_plus_90)
        self.hbox.addWidget(self.button_minus_90)

        self.setFixedWidth(left_menu_width)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.hbox)

        self.angle_entry.editingFinished.connect(lambda: self.angle_set(int(self.angle_entry.text())))
        self.button_0.clicked.connect(lambda: self.angle_set(0))
        self.button_plus_90.clicked.connect(lambda: self.angle_increment(+90))
        self.button_minus_90.clicked.connect(lambda: self.angle_increment(-90))

    def angle_set(self, angle_amount) -> None:

        if self.canvas_instance.angle != angle_amount:
            angle_amount %= 360
            self.canvas_instance.angle_rotate(angle_amount)
            self.canvas_instance.add_routine_cull_history(
                (Routine.ANGLE.value, self.canvas_instance.pixmap, angle_amount))
            self.canvas_instance.angle = angle_amount
            self.canvas_instance.updateStatusBar()
            self.angle_entry.setText(str(angle_amount))

    def angle_increment(self, increment) -> None:
        entry_val = int(self.angle_entry.text())
        entry_val += increment
        self.angle_set(entry_val)
