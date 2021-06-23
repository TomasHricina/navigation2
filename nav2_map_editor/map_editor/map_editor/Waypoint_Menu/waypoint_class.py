#!/usr/bin/python3

# PyQT
from PyQt5.QtGui import QMouseEvent
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QBrush

# Python
import logging

# Source files
from map_editor.Helpers.helpers import AddingPosition
from map_editor.Helpers.magic_gui_numbers import default_color_text, default_color_shape_inside, default_color_shape_outline

logger = logging.getLogger("map_editor")


class Waypoint(QGraphicsItemGroup):
    waypoint_container = []
    waypoint_adding_position = AddingPosition.END.value
    waypoint_size = 2
    waypoint_showing_text = True
    waypoint_text_size = 3
    waypoint_movable = False
    waypoint_currently_moved_idx = None

    def __init__(self, canvas_instance, x, y, theta, passed_id=None):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.x, self.y = x, y
        if passed_id:
            self.id = passed_id
        else:
            self.id = self.generate_id(Waypoint.waypoint_adding_position)

        size = Waypoint.waypoint_size
        self.shape = QGraphicsEllipseItem(size / 2.0, size / 2.0, size, size)
        self.shape.setBrush(QBrush(default_color_shape_inside))
        self.shape.setPen(QPen(default_color_shape_outline))

        if Waypoint.waypoint_showing_text:
            self.text = QGraphicsTextItem(str(self.id), parent=self.shape)
        else:
            self.text = QGraphicsTextItem("", parent=self.shape)

        self.text.setScale(Waypoint.waypoint_text_size)
        self.text.setDefaultTextColor(default_color_text)
        br = self.shape.boundingRect()
        br_x = br.right() - 2
        br_y = br.top() - 5
        self.text.setPos(br_x, br_y)

        self.addToGroup(self.shape)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        Waypoint.waypoint_container.append(self)

    @classmethod
    def generate_id(cls, adding_position):
        wpc = Waypoint.waypoint_container
        if not wpc:
            return 1
        if adding_position == AddingPosition.START.value:
            lowest_id_waypoint = min(wpc, key=lambda wp: wp.id)
            return lowest_id_waypoint.id - 1
        elif adding_position == AddingPosition.END.value:
            highest_id_waypoint = max(wpc, key=lambda wp: wp.id)
            return highest_id_waypoint.id + 1
        else:
            return Waypoint.next_waypoint_number(adding_position)

    @staticmethod
    def next_waypoint_number(num):
        str_num = str(num)
        if '.' not in str_num:
            return float(str_num + '.1')
        last_digit = str_num[-1]
        if last_digit == '9':
            return float(str_num + '1')
        else:
            return float(str_num[:-1:] + str(int(last_digit) + 1))

    @classmethod
    def reindex_waypoint(cls):
        wpc = Waypoint.waypoint_container
        wpc = sorted(wpc, key=lambda _wp: _wp.id)
        Waypoint.waypoint_container = wpc
        for idx, wp in enumerate(wpc):
            wp.id = idx+1
            if Waypoint.waypoint_showing_text:
                wp.text.setPlainText(str(idx+1))
            else:
                wp.text.setPlainText("")

    @classmethod
    def change_movable(cls, movable):
        wpc = Waypoint.waypoint_container
        Waypoint.waypoint_movable = movable
        for wp in wpc:
            wp.setFlag(QGraphicsItem.ItemIsMovable, movable)

    @classmethod
    def show_indexes(cls, does_show):
        wpc = Waypoint.waypoint_container
        if does_show:
            for wp in wpc:
                wp.text.setPlainText(str(wp.id))
        else:
            for wp in wpc:
                wp.text.setPlainText("")


    @classmethod
    def change_waypoint_text_size(cls, size_value):
        wpc = Waypoint.waypoint_container
        for wp in wpc:
            wp.text.setScale(size_value)
            Waypoint.waypoint_text_size = size_value

    @classmethod
    def sort_waypoints_by_id(cls):
        wpc = Waypoint.waypoint_container
        Waypoint.waypoint_container = sorted(wpc, key=lambda x: x.id)


    def mousePressEvent(self, event: QMouseEvent) -> None:
        button = event.button()
        wpc = Waypoint.waypoint_container
        for idx, wp in enumerate(wpc):  # find waypoint idx
            if wp.id == self.id:
                Waypoint.waypoint_currently_moved_idx = idx
                break

        if button == Qt.RightButton:
            self.canvas_instance.main_scene.removeItem(self)
            wpc.pop(idx)
            self.canvas_instance.main_widget.waypoint_menu.waypoint_table.populate()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)
        if Waypoint.waypoint_movable:  # update waypoint table
            self.x = round(self.canvas_instance.scene_pos.x())
            self.y = round(self.canvas_instance.scene_pos.y())
            self.canvas_instance.main_widget.waypoint_menu.refresh_specific_waypoint(Waypoint.waypoint_currently_moved_idx)
