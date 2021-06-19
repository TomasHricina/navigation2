#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.Qt import Qt

# Python
import logging

# Source files
from mapviz.Left_Menu.history_table import HistoryTable
from mapviz.Left_Menu.yaml_box import YamlBox
from mapviz.Left_Menu.path_box import PathBox

logger = logging.getLogger("mapviz")


class LeftMenu(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()
        logger.debug("LeftMenu created")

        self.canvas_instance = canvas_instance
        self.path_box = PathBox(self)
        self.yaml_box = YamlBox(self)
        self.yaml_box.insert_yaml_into_entries()  # inserting default YAML

        self.history_table = HistoryTable(self)
        self.grid = QGridLayout()
        self.grid.addWidget(self.path_box)
        self.grid.addWidget(self.yaml_box)
        self.grid.addWidget(self.history_table)

        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
