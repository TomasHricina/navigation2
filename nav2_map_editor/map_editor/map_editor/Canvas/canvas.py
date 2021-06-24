#!/usr/bin/python3

# External lib
import numpy as np
import qimage2ndarray

# PyQT
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent, QMouseEvent, QWheelEvent, QShowEvent, QResizeEvent
from PyQt5.QtGui import QKeySequence, QPen, QPainter, QBrush
from PyQt5.QtCore import QPoint, QPointF, QRect, QRectF, QSize, QSizeF, pyqtSignal
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QRubberBand

# Python
import logging

# Source files
from map_editor.Helpers.helpers import Routine, AddingPosition
from map_editor.Helpers.helpers import clamp, rotation, qimage2array, unit_vectors
from map_editor.Helpers.colors_helpers import calculate_lightness, colors, rgb2gray
from map_editor.Waypoint_Menu.waypoint_class import Waypoint

logger = logging.getLogger("map_editor")

# ROI = Region of interest


class ImageView(QGraphicsView):
    imageChanged = pyqtSignal()
    '''
    Canvas class 
    - access main by self.main_widget
    - outside of this module, access this class by self.canvas_instance
    '''

    def __init__(self, _default_image):
        QGraphicsView.__init__(self)
        # canvas
        self.main_scene = QGraphicsScene(self)
        self.scene_pos = self.mapToScene(QPoint(0, 0))
        self.cursor_widget_x, self.cursor_widget_y = 0, 0
        self.cursor_image_x, self.cursor_image_y = 0, 0
        self.graphics_pixmap = QGraphicsPixmapItem()
        self.main_scene.addItem(self.graphics_pixmap)
        self.setScene(self.main_scene)
        self.start_drag_ui = QPoint()
        self.last_scene_roi = None
        self.first_show_occurred = False

        # transformations
        self.transformations_enabled = True
        self.rubberBand = None; self.zooming_activated = False
        self.cropBand = None; self.cropping_allowed = True; self.cropping_activated = False
        self.panning = False
        self.rotating = False; self.rotating_allowed = True
        self.zoom_factor = 1.5
        self.angle = 0
        self.pan_speed = 10
        self.pan_acceleration = 3  # this is const hard coded
        self.rotating_speed = 1
        self.rotating_acceleration = 1  # this is const hard coded
        self.latest_pixmap = None  # inserted from the main
        self.history = []  # first default pixmap is added here, then loaded const pixmap
        self.history_current_idx = 0

        # map painting
        self.brushReady = False; self.drawing_brush = False
        self.paint_rectReady = False; self.drawing_rect = False
        self.paint_lineReady = False; self.drawing_line = False
        self.brushSize = 10
        self.const_paintColor = colors['Nav2-blue']
        self.paintColor = colors['Nav2-blue']
        self.paintLightness = np.interp(calculate_lightness(self.paintColor), [0, 255], [0, 100])
        self.adding_waypoint = False
        self.waypoint_adding_position = AddingPosition.END.value
        self.waypoints = []

    def update_light(self) -> None:
        self.main_widget.paint_menu.light.spin_light.setValue(round(np.interp(calculate_lightness(
            self.paintColor), [0, 255], [0, 100])))


    # Waypoint functions 

    def change_waypoint_movable(self) -> None:
        '''used for deciding, whether waypoints should be movable'''
        should_waypoint_move = not (self.rotating or self.panning or self.brushReady or self.paint_rectReady
                                    or self.paint_lineReady or self.adding_waypoint)
        Waypoint.change_movable(should_waypoint_move)
        logger.debug("Waypoints movable: " + str(should_waypoint_move))

    def add_waypoint(self) -> None:
        waypoint_x = self.cursor_image_x
        waypoint_y = self.cursor_image_y
        waypoint = Waypoint(self, waypoint_x, waypoint_y, self.angle)
        if self.waypoint_adding_position not in (AddingPosition.END.value, AddingPosition.START.value):
            next_wp_number = Waypoint.next_waypoint_number(self.waypoint_adding_position)
            Waypoint.waypoint_adding_position = next_wp_number
            self.main_widget.waypoint_menu.choices.radio3_line_edit.setText(str(next_wp_number))
        self.main_scene.addItem(waypoint)
        self.disable_transformations()

        waypoint.moveBy(waypoint_x, waypoint_y)
        self.populate_waypoint_table()

    def load_waypoint(self, x, y, theta, wp_id) -> None:
        loaded_waypoint = Waypoint(self, x, y, theta, wp_id)
        self.main_scene.addItem(loaded_waypoint)
        loaded_waypoint.moveBy(x, y)

    def populate_waypoint_table(self) -> None:
        '''used for updating waypoint table'''
        self.main_widget.waypoint_menu.waypoint_table.populate()

    def export_waypoints(self) -> str:
        # used for saving waypoints into YAML file
        result_string = '\n'
        Waypoint.reindex_waypoint()
        wpc = Waypoint.waypoint_container
        for wp in wpc:
            substring = 'wp_%s: [%s, %s, %s]' % (wp.id, wp.x, wp.y, self.angle)
            result_string += substring
            result_string += '\n'
        return result_string

    def delete_all_waypoints(self):
        wpc = Waypoint.waypoint_container
        if wpc:
            for wp in wpc:
                self.main_scene.removeItem(wp)
            Waypoint.waypoint_container = []
        self.main_widget.waypoint_menu.waypoint_table.populate()


    def delete_specific_waypoint(self, wp_id):
        wpc = Waypoint.waypoint_container
        for wp_idx, wp_value in enumerate(wpc):
            if wp_id == wp_value.id:
                self.main_scene.removeItem(wp_value)
                Waypoint.waypoint_container.pop(wp_idx)
                self.populate_waypoint_table()
                break

    # /Waypoint functions 


    def init_brush_paint(self, target_image):
        '''call it before starting paint with brush'''
        self.painter = QPainter(target_image)
        self.painter.setPen(QPen(self.paintColor, self.brushSize, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))

    def init_rect_paint(self, target_image):
        ''' call it before starting paint with rectangle'''
        self.painter = QPainter(target_image)
        brush = QBrush()
        brush.setColor(self.paintColor)
        brush.setStyle(Qt.SolidPattern)
        self.painter.setBrush(brush)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(self.paintColor)
        self.painter.setPen(pen)

    @property
    def pixmap(self):
        return self.graphics_pixmap.pixmap()

    @pixmap.setter
    def pixmap(self, image, image_format=None):
        # handle multiple input formats
        if isinstance(image, np.ndarray):
            if image.ndim == 3:
                if image.shape[2] == 3:
                    if image_format is None:
                        image_format = QImage.Format_RGB888
                    q_image = QImage(image.data, image.shape[1], image.shape[0], image_format)
                    pixmap = QPixmap.fromImage(q_image)  # copy data from the QImage referencing image original data
                elif image.shape[2] == 4:
                    if image_format is None:
                        image_format = QImage.Format_RGB32
                    q_image = QImage(image.data, image.shape[1], image.shape[0], image_format)
                    pixmap = QPixmap.fromImage(q_image)  # copy data from the QImage referencing image original data
                else:
                    logger.critical("Unknown format")
                    raise TypeError(image)
            elif image.ndim == 2:
                if image_format is None:
                    image_format = QImage.Format_RGB888
                q_image = QImage(image.data, image.shape[1], image.shape[0], image_format)
                pixmap = QPixmap.fromImage(q_image)  # copy data from the QImage referencing original image
            else:
                logger.critical("Unknown format")
                raise ValueError(image)

        elif isinstance(image, QImage):
            pixmap = QPixmap.fromImage(image)
        elif isinstance(image, QPixmap):
            pixmap = image
        else:
            logger.critical("Unknown format")
            raise TypeError(image)  # TODO

        self.graphics_pixmap.setPixmap(pixmap)
        self.setSceneDims()
        self.graphics_pixmap.update()
        self.imageChanged.emit()

    @property
    def image(self):
        return self.pixmap

    @image.setter
    def image(self, image) -> None:
        self.pixmap = image

    def setSceneDims(self) -> None:
        pixmap = self.pixmap
        self.setSceneRect(QRectF(QPointF(0, 0), QPointF(pixmap.width(), pixmap.height())))

    @property
    def image_scene_rect(self):
        return QRectF(self.graphics_pixmap.pos(), QSizeF(self.pixmap.size()))

    def resizeEvent(self, event: QResizeEvent) -> None:
        QGraphicsView.resizeEvent(self, event)
        self.setSceneDims()
        event.accept()
        self.fitInView(self.last_scene_roi, Qt.KeepAspectRatio)

    def zoomROITo(self, p, zoom_level_delta) -> None:
        pixmap = self.graphics_pixmap.pixmap()
        roi = self.current_scene_ROI
        roi_dims = QPointF(roi.width(), roi.height())
        roi_topleft = roi.topLeft()
        roi_scalef = 1
        if zoom_level_delta > 0:
            roi_scalef = 1 / self.zoom_factor
        elif zoom_level_delta < 0:
            roi_scalef = self.zoom_factor
        nroi_dims = roi_dims * roi_scalef
        nroi_dims.setX(max(nroi_dims.x(), 1))
        nroi_dims.setY(max(nroi_dims.y(), 1))
        if nroi_dims.x() > self.pixmap.size().width() or nroi_dims.y() > self.pixmap.size().height():
            self.reset_view()
        else:
            prel_scaled_x = (p.x() - roi_topleft.x()) / roi_dims.x()
            prel_scaled_y = (p.y() - roi_topleft.y()) / roi_dims.y()
            nroi_topleft_x = p.x() - prel_scaled_x * nroi_dims.x()
            nroi_topleft_y = p.y() - prel_scaled_y * nroi_dims.y()

            nroi = QRectF(nroi_topleft_x, nroi_topleft_y, nroi_dims.x(), nroi_dims.y())
            self.fitInView(nroi, Qt.KeepAspectRatio)

    @property
    def current_scene_ROI(self):
        return self.last_scene_roi

    def _pan(self, start_point, end_point, vector_scale):
        pan_vector = end_point * vector_scale - start_point
        scene2view = self.transform()
        sx = scene2view.m11()
        sy = scene2view.m22()
        scene_pan_vector = QPointF(pan_vector.x() / sx, pan_vector.y() / sy)
        roi = self.current_scene_ROI
        top_left = roi.topLeft()
        scene_rect = self.sceneRect()
        new_top_left = top_left - scene_pan_vector
        new_top_left.setX(clamp(new_top_left.x(), scene_rect.left(), scene_rect.right()))
        new_top_left.setY(clamp(new_top_left.y(), scene_rect.top(), scene_rect.bottom()))
        n_roi = QRectF(new_top_left, roi.size())
        self.fitInView(n_roi, Qt.KeepAspectRatio)

    def grayscale_canvas(self):
        logger.debug("Grayscaled")
        self.pixmap = QPixmap.fromImage(qimage2ndarray.array2qimage(rgb2gray(qimage2array(self.pixmap.toImage()))))
        self.add_routine_cull_history((Routine.GRAY.value, self.pixmap, self.angle))

    def disable_transformations(self, disable=True):
        # rotating and cropping only allowed at start, for now
        # if not self.transformations_enabled:
        #     return
        logger.debug("Transformations disabled")
        angle_box = self.main_widget.paint_menu.angle_box
        crop = self.main_widget.paint_menu.crop

        if not disable:
            angle_box.setVisible(True)
            self.rotating_allowed = True

            crop.setVisible(True)
            self.cropping_allowed = True

            self.transformations_enabled = True
        else:
            angle_box.setVisible(False)
            self.rotating_allowed = False

            crop.setVisible(False)
            self.cropping_allowed = False

            self.transformations_enabled = False

    def mousePressEvent(self, event: QMouseEvent) -> None:

        if not ((0 <= self.cursor_image_x <= self.image.width()) and (0 <= self.cursor_image_y <= self.image.height())):
            # prevents user from event-clicking outside image (solves lot of issues later)
            # TODO: when map is rotated, the Zoom rubberband gives slightly wrong selection, but one can wheel zoom, which works perfectly
            return

        logger.debug("Mouse event pressed")
        QGraphicsView.mousePressEvent(self, event)
        button = event.button()
        modifier = event.modifiers()
        self.start_drag_ui = event.pos()
        self.start_drag_image = QPoint(self.cursor_image_x, self.cursor_image_y)
        self.current_image_pos = QPoint(self.scene_pos.x(), self.scene_pos.y())

        # pan
        if modifier == Qt.ControlModifier and button == Qt.LeftButton:
            self.panning = True

        # initiate/show ROI selection
        elif (modifier == Qt.ShiftModifier or self.zooming_activated) and button == Qt.LeftButton:
            if self.rubberBand is None:
                self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.viewport())
            self.rubberBand.setGeometry(QRect(self.start_drag_ui, QSize()))
            self.rubberBand.show()

        elif self.cropping_allowed and (modifier == Qt.AltModifier or self.cropping_activated) and button == Qt.LeftButton:
            if self.cropBand is None:
                self.cropBand = QRubberBand(QRubberBand.Rectangle, self.viewport())
            self.cropBand.setGeometry(QRect(self.start_drag_image, QSize()))
            self.cropBand.show()
            self.delete_all_waypoints()

        elif self.brushReady and event.button() == Qt.LeftButton:
            logger.debug("Paint brush started")
            self.drawing_brush = True
            self.paint_pixmap = self.pixmap.copy()
            self.init_brush_paint(self.paint_pixmap)
            self.lastPoint = QPoint(self.scene_pos.x(), self.scene_pos.y())
            self.painter.drawPoint(self.lastPoint)
            self.pixmap = self.paint_pixmap
            self.disable_transformations()

        elif self.paint_lineReady and event.button() == Qt.LeftButton:
            logger.debug("Paint line started")
            self.drawing_line = True
            self.const_pixmap = self.pixmap.copy()
            self.lastPoint = QPoint(self.scene_pos.x(), self.scene_pos.y())
            self.disable_transformations()

        elif self.paint_rectReady and event.button() == Qt.LeftButton:
            logger.debug("Paint rect started")
            self.drawing_rect = True
            self.const_pixmap = self.pixmap.copy()
            self.rect = QRect(self.start_drag_image, self.start_drag_image)
            self.lastPoint = QPoint(self.scene_pos.x(), self.scene_pos.y())
            self.disable_transformations()

        elif self.adding_waypoint and event.button() == Qt.LeftButton:
            self.add_waypoint()

        elif event.button() == Qt.RightButton:
            if self.main_widget.waypoint_menu.choices.button.isChecked():
                self.main_widget.waypoint_menu.choices.button.setChecked(False)
                self.main_widget.waypoint_menu.choices.toggle_state()
                Waypoint.change_movable(True)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        QGraphicsView.mouseMoveEvent(self, event)
        # self.current_cursor_pos = self.scene_pos.x(), self.scene_pos.y()

        # update selection display
        if self.rubberBand is not None:
            self.rubberBand.setGeometry(QRect(self.start_drag_ui, event.pos()).normalized())

        elif self.cropBand is not None:
            self.cropBand.setGeometry(QRect(self.start_drag_ui, event.pos()).normalized())

        elif self.panning:
            end_drag_ui = event.pos()
            self._pan(self.start_drag_ui, end_drag_ui, 1)
            self.start_drag_ui = end_drag_ui

        elif self.drawing_brush:
            current_point = QPoint(self.scene_pos.x(), self.scene_pos.y())
            self.painter.drawPoint(current_point)
            self.pixmap = self.paint_pixmap

        elif self.drawing_line:
            current_point = QPoint(self.scene_pos.x(), self.scene_pos.y())
            self.pixmap = self.const_pixmap.copy()
            self.paint_pixmap = self.const_pixmap.copy()
            self.init_brush_paint(self.paint_pixmap)
            self.painter.drawLine(self.start_drag_image, current_point)
            self.painter.end()
            self.pixmap = self.paint_pixmap

        elif self.drawing_rect:
            current_point = QPoint(self.scene_pos.x(), self.scene_pos.y())
            self.rect = QRect(self.start_drag_image, current_point)
            self.pixmap = self.const_pixmap.copy()
            self.paint_pixmap = self.const_pixmap.copy()
            self.init_rect_paint(self.paint_pixmap)
            self.painter.drawRect(self.rect)
            self.painter.end()
            self.pixmap = self.paint_pixmap

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        QGraphicsView.mouseReleaseEvent(self, event)
        # consume rubber band selection
        if self.rubberBand is not None:
            self.rubberBand.hide()
            # set view to ROI
            rect = self.rubberBand.geometry().normalized()
            if rect.width() > 5 and rect.height() > 5:
                roi = QRectF(self.mapToScene(rect.topLeft()), self.mapToScene(rect.bottomRight()))
                self.fitInView(roi, Qt.KeepAspectRatio)
            self.rubberBand = None

        elif self.cropBand is not None:
            self.angle = 0
            self.cropBand.hide()
            roi_width = self.cursor_image_x - self.start_drag_image.x()
            roi_height = self.cursor_image_y - self.start_drag_image.y()
            roi_rect = QRect(self.start_drag_image.x(), self.start_drag_image.y(), roi_width, roi_height)
            self.pixmap = self.pixmap.copy(roi_rect)
            self.latest_pixmap = self.pixmap
            self.add_routine_cull_history((Routine.CROP.value, self.latest_pixmap, 0))
            self.cropBand = None
            self.reset_view()

        elif self.panning:
            self.panning = False

        elif self.drawing_brush:
            logger.debug("Paint brush ended")
            self.drawing_brush = False
            self.painter.end()
            self.add_routine_cull_history((Routine.PAINT_BRUSH.value, self.paint_pixmap, self.angle))
            # self.latest_pixmap = self.paint_pixmap

        elif self.drawing_line:
            logger.debug("Paint line ended")
            self.drawing_line = False
            self.add_routine_cull_history((Routine.PAINT_LINE.value, self.paint_pixmap, self.angle))

        elif self.drawing_rect:
            logger.debug("Paint rect ended")
            self.drawing_rect = False
            self.add_routine_cull_history((Routine.PAINT_RECT.value, self.paint_pixmap, self.angle))
            # self.latest_pixmap = self.paint_pixmap

    def wheelEvent(self, event: QWheelEvent) -> None:
        dy = event.angleDelta().y()
        # adjust zoom
        if abs(dy) > 0:
            scene_pos = self.mapToScene(event.pos())
            sign = 1 if dy >= 0 else -1
            self.zoomROITo(scene_pos, sign)

    def add_routine_cull_history(self, added_routine) -> None:
        ''' prevents branching of history, when you Undo and make new, you cannot return '''
        logger.debug("Add and cull history")
        self.history_current_idx += 1
        self.history = self.history[:self.history_current_idx]
        self.history.append(added_routine)
        self.populate_history_table()

    def populate_history_table(self):
        ''' updates history table '''
        self.main_widget.left_menu.history_table.history = self.history
        self.main_widget.left_menu.history_table.populate()

    def angle_rotate(self, angle) -> None:
        self.delete_all_waypoints()
        self.angle %= 360
        self.pixmap = rotation(self.latest_pixmap, angle)
        self.main_widget.paint_menu.angle_box.angle_entry.setText(str(self.angle))
        # self.reset_view()

    def undo_redo_disable_transformations(self, current_history):
        ''' enabling and disabling transformations after undo/redo '''
        for event in current_history:  
            event_type = event[0]
            if event_type not in (Routine.LOAD.value, Routine.ANGLE.value, Routine.CROP.value):
                self.disable_transformations(True)
                break
        else:
            self.disable_transformations(False)

    def execute_latest_history(self, history_current_idx):
        ''' goes through the stack of routines in history and executes them in order '''
        current_history = self.history[:history_current_idx]
        self.undo_redo_disable_transformations(current_history)
        for history_idx, last_history_event in enumerate(reversed(current_history)):
            history_event_routine = last_history_event[0]
            history_event_pixmap = last_history_event[1]
            history_event_angle = last_history_event[2]
            if history_event_routine != Routine.ANGLE.value:
                previous_pixmap = history_event_pixmap
                self.latest_pixmap = previous_pixmap
                routines = current_history[len(current_history) - history_idx:]
                if routines:
                    previous_angle = routines[-1][2]
                    self.angle = previous_angle
                    previous_pixmap = rotation(previous_pixmap, previous_angle)
                else:
                    # no routines means the last is pixmap
                    self.angle = 0

                self.main_widget.paint_menu.angle_box.angle_entry.setText(str(self.angle))
                self.pixmap = previous_pixmap
                # self.reset_view()
                break

    def undo(self):
        if self.history_current_idx >= 1:
            self.execute_latest_history(self.history_current_idx)
            self.history_current_idx -= 1
        else:
            # WARNING: Already at the oldest change
            logger.info("Already at the oldest change")
        self.populate_history_table()

    def redo(self):
        redo_index = self.history_current_idx + 1
        current_history = self.history[:redo_index + 1]
        self.undo_redo_disable_transformations(current_history)
        if redo_index < len(self.history):
            last_history_event = self.history[redo_index]
            history_event_routine = last_history_event[0]
            history_event_pixmap = last_history_event[1]
            history_event_angle = last_history_event[2]

            if history_event_routine == Routine.ANGLE.value:
                self.pixmap = rotation(self.latest_pixmap, history_event_angle)
            else:
                self.latest_pixmap = history_event_pixmap
                self.pixmap = self.latest_pixmap

            self.angle = history_event_angle
            self.history_current_idx += 1
        else:
            # WARNING: Already at the newest change
            logger.info("Already at the newest change")
        self.populate_history_table()
        # self.reset_view()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.Undo):
            self.undo()
        elif event.matches(QKeySequence.Redo):
            self.redo()

        elif event.key() == Qt.Key_G:
            self.grayscale_canvas()

        # rotation
        elif self.rotating_allowed and (event.key() == Qt.Key_1):  # clockwise rotation
            self.angle -= self.rotating_speed
            self.angle_rotate(self.angle)

        elif self.rotating_allowed and (event.key() == Qt.Key_2):  # counter clockwise rotation
            self.angle += self.rotating_speed
            self.angle_rotate(self.angle)

        # panning with keyboard W,A,S,D + diagonal Q,E,Z(Y),X(C)
        elif event.key() == Qt.Key_W:
            self._pan(QPoint(0, 0), unit_vectors['up'], self.pan_speed)
        elif event.key() == Qt.Key_S:
            self._pan(QPoint(0, 0), unit_vectors['down'], self.pan_speed)
        elif event.key() == Qt.Key_A:
            self._pan(QPoint(0, 0), unit_vectors['left'], self.pan_speed)
        elif event.key() == Qt.Key_D:
            self._pan(QPoint(0, 0), unit_vectors['right'], self.pan_speed)
        elif event.key() == Qt.Key_Q:
            self._pan(QPoint(0, 0), unit_vectors['upleft'], self.pan_speed)
        elif event.key() == Qt.Key_E:
            self._pan(QPoint(0, 0), unit_vectors['upright'], self.pan_speed)
        elif event.key() == Qt.Key_Z or event.key() == Qt.Key_Y:
            self._pan(QPoint(0, 0), unit_vectors['downleft'], self.pan_speed)
        elif event.key() == Qt.Key_X or event.key() == Qt.Key_C:
            self._pan(QPoint(0, 0), unit_vectors['downright'], self.pan_speed)

        # pan speed
        elif event.key() == Qt.Key_R:
            self.pan_speed += self.pan_acceleration
        elif event.key() == Qt.Key_F:
            self.pan_speed -= self.pan_acceleration

        elif event.key() == Qt.Key_H:
            Waypoint.sort_waypoints_by_id()

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if (event.key() == Qt.Key_1 and not event.isAutoRepeat()) or (
                event.key() == Qt.Key_2 and not event.isAutoRepeat()):
            self.add_routine_cull_history((Routine.ANGLE.value, self.pixmap, self.angle))

    def showEvent(self, event: QShowEvent) -> None:
        QGraphicsView.showEvent(self, event)
        if event.spontaneous():
            return
        if not self.first_show_occurred:
            self.first_show_occurred = True
            self.reset_view()

    def reset_view(self) -> None:
        logger.debug("View reset")
        self.main_widget.paint_menu.angle_box.angle_entry.setText(str(self.angle))
        self.main_widget.canvas.updateStatusBar()
        self.setSceneDims()
        self.fitInView(self.image_scene_rect, Qt.KeepAspectRatio)

    def fitInView(self, rect, flags=Qt.IgnoreAspectRatio):
        if self.scene() is None or rect.isNull():
            return
        self.last_scene_roi = rect
        unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        view_rect = self.viewport().rect()
        scene_rect = self.transform().mapRect(rect)
        x_ratio = view_rect.width() / scene_rect.width()
        y_ratio = view_rect.height() / scene_rect.height()
        if flags == Qt.KeepAspectRatio:
            x_ratio = y_ratio = min(x_ratio, y_ratio)
        elif flags == Qt.KeepAspectRatioByExpanding:
            x_ratio = y_ratio = max(x_ratio, y_ratio)
        self.scale(x_ratio, y_ratio)
        self.centerOn(rect.center())
