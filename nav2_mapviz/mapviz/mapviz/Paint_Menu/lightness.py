#!/usr/bin/python3

# External lib
import numpy as np

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.Qt import Qt, QColor

# Python
import logging

# Source files
from mapviz.Helpers.simple_focus_out_widgets import FocusOutSpinBox, FocusOutDoubleSpinBox
from mapviz.Helpers.colors_helpers import calculate_lightness, change_lightness

# Constants
from mapviz.Helpers.magic_gui_numbers import default_max_speed, default_target_speed

logger = logging.getLogger("mapviz")


class Lightness(QWidget):  # used for speed restrictions
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignTop)

        self.max_speed_spin = FocusOutDoubleSpinBox(canvas_instance)
        self.max_speed_spin.setRange(1, 100)
        self.max_speed_spin.setSingleStep(0.1)
        self.max_speed_spin.setValue(default_max_speed)
        self.max_speed_label = QLabel()
        self.max_speed_label.setText("m/s max speed (optional)")

        self.target_speed_spin = FocusOutDoubleSpinBox(canvas_instance)
        self.target_speed_spin.setRange(1, 100)
        self.target_speed_spin.setSingleStep(0.01)
        self.target_speed_spin.setValue(default_target_speed)
        self.target_speed_label = QLabel()
        self.target_speed_label.setText("m/s target speed (optional)")

        self.label_light = QLabel()
        self.label_light.setText('% of max speed')

        self.spin_light = FocusOutSpinBox(canvas_instance)
        self.spin_light.setRange(0, 100)

        # set default color lightness
        self.spin_light.setValue(round(np.interp(calculate_lightness(
            self.canvas_instance.const_paintColor), [0, 255], [0, 100])))

        def lightness_changed():
            lightness_value = np.interp(self.spin_light.value(), [0, 100], [0, 255])
            _r, _g, _b, _ = QColor(self.canvas_instance.const_paintColor).getRgb()
            rgb = _r, _g, _b
            changed_rgb = change_lightness(rgb, lightness_value)
            self.canvas_instance.paintColor = QColor(*changed_rgb)
            self.target_speed_spin.setValue((self.spin_light.value()/100)*self.max_speed_spin.value())

            logger.debug("Lightness changed to: " + str(lightness_value))

        def change_lightness_percentage():
            maximal_speed = float(self.max_speed_spin.value())
            target_speed = float(self.target_speed_spin.value())
            self.spin_light.setValue(round(100*(target_speed/maximal_speed)))

        self.spin_light.valueChanged.connect(lightness_changed)
        self.max_speed_spin.valueChanged.connect(change_lightness_percentage)
        self.target_speed_spin.valueChanged.connect(change_lightness_percentage)

        self.grid.addWidget(self.spin_light, 0, 0)
        self.grid.addWidget(self.label_light, 0, 1)

        self.grid.addWidget(self.max_speed_spin, 1, 0)
        self.grid.addWidget(self.max_speed_label, 1, 1)

        self.grid.addWidget(self.target_speed_spin, 2, 0)
        self.grid.addWidget(self.target_speed_label, 2, 1)

        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
