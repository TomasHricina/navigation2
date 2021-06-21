#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSlot

# Python
import logging

# Source files
from map_editor.Helpers.helpers import Routine, rotation

# Constants
from map_editor.Helpers.magic_gui_numbers import left_menu_width, history_box_column_width

logger = logging.getLogger("map_editor")


class HistoryCell(QWidget):
    """
    Widget that allows for pixmap + text to be shown in history cell
    """
    def __init__(self, pixmap, text, angle, parent=None):
        QWidget.__init__(self, parent)

        self.pixmap = pixmap
        self.text = text
        self.angle = angle

        self.setLayout(QHBoxLayout())
        self.lbPixmap = QLabel(self)
        self.lbText = QLabel(self)
        self.lbText.setAlignment(Qt.AlignCenter)

        self.layout().addWidget(self.lbPixmap)
        self.layout().addWidget(self.lbText)

        self.initUi()

    def initUi(self):
        self.lbPixmap.setPixmap(self.pixmap.scaled(self.lbPixmap.size(), Qt.KeepAspectRatio))
        self.lbText.setText(self.text)


class HistoryTable(QTableWidget):
    def __init__(self, left_menu):
        super().__init__()
        logger.debug("HistoryTable created")
        self.left_menu = left_menu
        self.horizontalHeader().setVisible(False)

        self.setFixedWidth(left_menu_width)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setColumnCount(1)
        self.setColumnWidth(0, history_box_column_width)

        self.cellClicked.connect(self.onCellClicked)
        self.cellDoubleClicked.connect(self.onCellClicked)

    @pyqtSlot(int)
    def onCellClicked(self, row):
        logger.debug("HistoryTable cell clicked")
        cell_value = self.cellWidget(row, 0)
        angle = cell_value.angle
        self.left_menu.canvas_instance.angle = angle
        self.left_menu.canvas_instance.execute_latest_history(row + 1)
        self.left_menu.canvas_instance.history_current_idx = row
        self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

    def populate(self):
        logger.debug("HistoryTable populated")
        self.setRowCount(len(self.history))

        for history_idx, history_event in enumerate(self.history):
            event_routine = history_event[0]
            event_pixmap = history_event[1]
            event_angle = history_event[2]

            if event_routine == Routine.ANGLE.value:
                cell_text = Routine.ANGLE.name + ' ' + str(event_angle) + '°'

            elif event_routine == Routine.LOAD.value:
                cell_text = Routine.LOAD.name + ' ' + str(event_pixmap.width()) + 'x' + str(event_pixmap.height())

            elif event_routine == Routine.CROP.value:
                cell_text = Routine.CROP.name + ' ' + str(event_pixmap.width()) + 'x' + str(event_pixmap.height())

            elif event_routine == Routine.PAINT_BRUSH.value:
                cell_text = Routine.PAINT_BRUSH.name
                event_pixmap = rotation(event_pixmap, event_angle)

            elif event_routine == Routine.PAINT_LINE.value:
                cell_text = Routine.PAINT_LINE.name

            elif event_routine == Routine.PAINT_RECT.value:
                cell_text = Routine.PAINT_RECT.name
                event_pixmap = rotation(event_pixmap, event_angle)

            elif event_routine == Routine.GRAY.value:
                cell_text = Routine.GRAY.name

            cell_widget = HistoryCell(event_pixmap, cell_text, event_angle)
            self.setCellWidget(history_idx, 0, cell_widget)

        self.resizeRowsToContents()
        self.selectRow(self.left_menu.canvas_instance.history_current_idx)
