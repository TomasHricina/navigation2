#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from mapviz.Helpers.simple_focus_out_widgets import FocusOutSpinBox, FocusOutButton

logger = logging.getLogger("mapviz")


class PaintBrush(QWidget):
    # after user clicks on Draw brush button, brushReady variable is set to True
    # if brushReady is True and user clicks on the canvas, the brush painting starts

    def __init__(self, canvas_instance):
        super().__init__()

        self.canvas_instance = canvas_instance
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignTop)

        self.label_brush_size = QLabel()
        self.label_brush_size.setText('BrushSize')

        self.spin_brush_size = FocusOutSpinBox(canvas_instance)
        self.spin_brush_size.setValue(5)
        self.spin_brush_size.setRange(0, 300)
        self.button = FocusOutButton(canvas_instance)
        self.button.setCheckable(True)
        self.button.setText('Draw brush')

        def brushSizeChange(brush_size):
            self.canvas_instance.brushSize = brush_size
            logger.debug("Brush size changed")

        self.spin_brush_size.valueChanged.connect(lambda: brushSizeChange(self.spin_brush_size.value()))
        self.grid.addWidget(self.spin_brush_size, 0, 0)
        self.grid.addWidget(self.button, 0, 1)

        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

    def toggle_state(self):
        self.canvas_instance.brushReady = not self.canvas_instance.brushReady
        logger.debug("Brush toggled to: " + str(self.canvas_instance.brushReady))
