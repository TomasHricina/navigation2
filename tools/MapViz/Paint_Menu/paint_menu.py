#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from mapViz.Paint_Menu.crop import Crop
from mapViz.Paint_Menu.zoom import Zoom
from mapViz.Paint_Menu.paint_brush import PaintBrush
from mapViz.Paint_Menu.paint_rect import PaintRect
from mapViz.Paint_Menu.paint_line import PaintLine
from mapViz.Paint_Menu.lightness import Lightness
from mapViz.Paint_Menu.color_drop import ChangeColor
from mapViz.Paint_Menu.gray_canvas import GrayCanvas
from mapViz.Paint_Menu.angle_box import AngleBox

logger = logging.getLogger("MapViz")


class PaintMenu(QWidget):
    # contains all the painting capabilities
    # waypoint menu has to be passed in, in order to make exclusive buttons across two widgets
    def __init__(self, canvas_instance, waypoint_menu):
        super().__init__()
        logger.debug("Paint menu created")

        self.canvas_instance = canvas_instance
        self.waypoint = waypoint_menu
        self.grid = QGridLayout()

        self.crop = Crop(canvas_instance)

        self.zoom = Zoom(canvas_instance)

        self.brush = PaintBrush(canvas_instance)
        self.paint_rect = PaintRect(canvas_instance)
        self.paint_line = PaintLine(canvas_instance)

        self.light = Lightness(canvas_instance)
        self.color = ChangeColor(canvas_instance)

        self.gray = GrayCanvas(canvas_instance)

        self.grid.setContentsMargins(0, 0, 0, 0)

        def toggle_except(button):
            group = {
                'brush': self.brush,
                'line': self.paint_line,
                'paint_rect': self.paint_rect,
                'waypoint': self.waypoint,
                'crop': self.crop,
                'zoom': self.zoom
            }
            group[button].toggle_state()
            group.pop(button)
            for but in group.values():
                if but.button.isChecked():
                    but.toggle_state()
                    but.button.setChecked(False)

            self.canvas_instance.change_waypoint_movable()
            logger.debug("Button group toggle off, except: " + str(button))

        self.brush.button.clicked.connect(lambda: toggle_except('brush'))
        self.paint_line.button.clicked.connect(lambda: toggle_except('line'))
        self.paint_rect.button.clicked.connect(lambda: toggle_except('paint_rect'))
        self.waypoint.button.clicked.connect(lambda: toggle_except('waypoint'))
        self.crop.button.clicked.connect(lambda: toggle_except('crop'))
        self.zoom.button.clicked.connect(lambda: toggle_except('zoom'))

        self.angle_box = AngleBox(canvas_instance)

        self.grid.addWidget(self.light, 0, 0, 3, 1)

        self.grid.addWidget(self.angle_box, 0, 1)
        self.grid.addWidget(self.crop, 1, 1)

        self.grid.addWidget(self.color, 0, 2)
        self.grid.addWidget(self.gray, 1, 2)
        self.grid.addWidget(self.zoom, 2, 2)

        self.grid.addWidget(self.brush, 0, 3, 1, 2)
        self.grid.addWidget(self.paint_line, 1, 3, 1, 2)
        self.grid.addWidget(self.paint_rect, 2, 3, 1, 2)

        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
