from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QImage, QPixmap, QKeyEvent, QMouseEvent, QWheelEvent, QShowEvent, QResizeEvent, QKeySequence
from PyQt5.QtCore import QPoint, QPointF, QRect, QRectF, QSize, QSizeF, pyqtSignal
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, QRubberBand)
import numpy as np
from helpers import clamp, calc_angle, rotation, scaleToFit, dirr

# ROI = Region of interest

unit_vectors = {
             'up': QPoint(0, 1),
             'down':QPoint(0, -1),
             'left': QPoint(1, 0),
             'right': QPoint(-1, 0),
             'upleft': QPoint(1, 1),
             'upright': QPoint(-1, 1),
             'downleft': QPoint(1, -1),
             'downright': QPoint(-1, -1)
             }


class ImageView(QGraphicsView):
    imageChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QGraphicsView.__init__(self, *args, **kwargs)
        scene = QGraphicsScene(self)
        self.scene_pos = self.mapToScene(QPoint(0, 0))
        self.cursor_widget_x, self.cursor_widget_y = 0, 0
        self.cursor_image_x, self.cursor_image_y = 0, 0
        self.cropped_image = None
        self.graphics_pixmap = QGraphicsPixmapItem()
        scene.addItem(self.graphics_pixmap)
        self.zoom_factor = 1.5
        self.setScene(scene)
        self.start_drag_ui = QPoint()
        self.rubberBand = None
        self.cropBand = None
        self.panning = False
        self.rotating = False
        self.first_show_occurred = False
        self.last_scene_roi = None
        self.angle = 0
        self.angle_at_cropping = 0
        self.pan_speed = 10
        self.pan_acceleration = 3  # this is const hard coded
        self.rotating_speed = 1
        self.rotating_acceleration = 1  # this is const hard coded
        self.pixmap_history = []  # first default pixmap is added here, then loaded const pixmap
        self.pixmap_history_current_idx = 0

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
                    raise TypeError(image)
            elif image.ndim == 2:
                if image_format is None:
                    image_format = QImage.Format_RGB888
                q_image = QImage(image.data, image.shape[1], image.shape[0], image_format)
                pixmap = QPixmap.fromImage(q_image)  # copy data from the QImage referencing original image
            else:
                raise ValueError(image)

        elif isinstance(image, QImage):
            pixmap = QPixmap.fromImage(image)
        elif isinstance(image, QPixmap):
            pixmap = image
        else:
            raise TypeError(image)   # TODO: catch it, do smt

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
        self.update()

    def zoomROITo(self, p, zoom_level_delta) -> None:
        pixmap = self.graphics_pixmap.pixmap()
        roi = self.current_scene_ROI
        roi_dims = QPointF(roi.width(), roi.height())
        roi_topleft = roi.topLeft()
        roi_scalef = 1
        if zoom_level_delta > 0:
            roi_scalef = 1/self.zoom_factor
        elif zoom_level_delta < 0:
            roi_scalef = self.zoom_factor
        nroi_dims = roi_dims * roi_scalef
        nroi_dims.setX(max(nroi_dims.x(), 1))
        nroi_dims.setY(max(nroi_dims.y(), 1))
        if nroi_dims.x() > self.pixmap.size().width() or nroi_dims.y() > self.pixmap.size().height():
            self.reset()
        else:
            prel_scaled_x = (p.x() - roi_topleft.x()) / roi_dims.x()
            prel_scaled_y = (p.y() - roi_topleft.y()) / roi_dims.y()
            nroi_topleft_x = p.x() - prel_scaled_x * nroi_dims.x()
            nroi_topleft_y = p.y() - prel_scaled_y * nroi_dims.y()

            nroi = QRectF(nroi_topleft_x, nroi_topleft_y, nroi_dims.x(), nroi_dims.y())
            self.fitInView(nroi, Qt.KeepAspectRatio)
            self.update()

    @property
    def current_scene_ROI(self):
        return self.last_scene_roi

    def _pan(self, start_point, end_point, vector_scale) -> None:
        pan_vector = end_point*vector_scale - start_point
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

    def mousePressEvent(self, event: QMouseEvent) -> None:

        if not ((0 <= self.cursor_image_x <= self.image.width()) and (0 <= self.cursor_image_y <= self.image.height())):
            # prevents user from event-clicking outside image (solves lot of issues later)
            # TODO: when map is rotated, the Zoom rubberband gives slightly wrong selection, but one can wheel zoom, which works perfectly
            return

        QGraphicsView.mousePressEvent(self, event)
        button = event.button()
        modifier = event.modifiers()
        self.start_drag_ui = event.pos()
        self.start_drag_image = QPoint(self.cursor_image_x, self.cursor_image_y)

        # pan
        if modifier == Qt.ControlModifier and button == Qt.LeftButton:
            self.panning = True

        # initiate/show ROI selection
        elif modifier == Qt.ShiftModifier and button == Qt.LeftButton:
            if self.rubberBand is None:
                self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.viewport())
            self.rubberBand.setGeometry(QRect(self.start_drag_ui, QSize()))
            self.rubberBand.show()

        elif modifier == Qt.AltModifier and button == Qt.LeftButton:
            if self.cropBand is None:
                self.cropBand = QRubberBand(QRubberBand.Rectangle, self.viewport())
            self.cropBand.setGeometry(QRect(self.start_drag_image, QSize()))
            self.angle_at_cropping = self.angle
            self.cropBand.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        QGraphicsView.mouseMoveEvent(self, event)
        # update selection display
        if self.rubberBand is not None:
            self.rubberBand.setGeometry(QRect(self.start_drag_ui, event.pos()).normalized())
            # print(self.rubberBand.geometry().x(), self.rubberBand.geometry().y(), self.rubberBand.geometry().width(), self.rubberBand.geometry().height())

        if self.cropBand is not None:
            # print(self.cursor_image_x, self.cursor_image_y)
            self.cropBand.setGeometry(QRect(self.start_drag_ui, event.pos()).normalized())
            # print(self.cropBand.geometry().x(), self.cropBand.geometry().y(), self.cropBand.geometry().width(), self.cropBand.geometry().height())
            pass

        if self.panning:
            end_drag_ui = event.pos()
            self._pan(self.start_drag_ui, end_drag_ui, 1)
            self.start_drag_ui = end_drag_ui

        self.update()

    def add_and_cull_history(self) -> None:
        self.pixmap_history_current_idx += 1
        self.pixmap_history = self.pixmap_history[:self.pixmap_history_current_idx]
        self.pixmap_history.append(self.pixmap)

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

        if self.cropBand is not None:
            self.cropBand.hide()
            roi_width = self.cursor_image_x - self.start_drag_image.x()
            roi_height = self.cursor_image_y - self.start_drag_image.y()
            roi_rect = QRect(self.start_drag_image.x(), self.start_drag_image.y(), roi_width, roi_height)
            self.pixmap = self.pixmap.copy(roi_rect)
            self.add_and_cull_history()
            self.cropBand = None

        if self.panning:
            self.panning = False

        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        dy = event.angleDelta().y()
        # adjust zoom
        if abs(dy) > 0:
            scene_pos = self.mapToScene(event.pos())
            sign = 1 if dy >= 0 else -1
            self.zoomROITo(scene_pos, sign)

    def angle_rotate(self) -> None:
        self.angle %= 360
        self.pixmap = rotation(self.pixmap_history[self.pixmap_history_current_idx], self.angle-self.angle_at_cropping)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # undo
        if event.matches(QKeySequence.Undo):
            if self.pixmap_history_current_idx >= 1:
                self.pixmap_history_current_idx -= 1
                self.pixmap = self.pixmap_history[self.pixmap_history_current_idx]

        # redo
        elif event.matches(QKeySequence.Redo):
            if self.pixmap_history_current_idx+1 < len(self.pixmap_history):
                self.pixmap_history_current_idx += 1
                self.pixmap = self.pixmap_history[self.pixmap_history_current_idx]

        # rotation
        elif event.key() == Qt.Key_1:  # clockwise rotation
            self.angle -= self.rotating_speed
            self.angle_rotate()

        elif event.key() == Qt.Key_2:  # counter clockwise rotation
            self.angle += self.rotating_speed
            self.angle_rotate()

        # change speed of rotation
        elif event.key() == Qt.Key_3:  # clockwise rotation
            self.rotating_speed += self.rotating_acceleration

        elif event.key() == Qt.Key_4:  # counter clockwise rotation
            self.rotating_speed -= self.rotating_acceleration

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

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        # when rotating by holding key, we want to count it as one routine (for undo-redo purposes)
        if event.key() == Qt.Key_1 and not event.isAutoRepeat():
            self.pixmap_history.append(('angle', self.angle))
            print(self.angle)
            self.reconstruct_from_history()

    def showEvent(self, event: QShowEvent) -> None:
        QGraphicsView.showEvent(self, event)
        if event.spontaneous():
            return
        if not self.first_show_occurred:
            self.first_show_occurred = True
            self.reset()

    def reset(self) -> None:
        self.setSceneDims()
        self.fitInView(self.image_scene_rect, Qt.KeepAspectRatio)
        self.update()

    def reconstruct_from_history(self):
        for history_idx, history_event in enumerate(reversed(self.pixmap_history)):
            if isinstance(history_event, QPixmap):
                latest_pixmap = history_event
                subsequent_routines = self.pixmap_history[-history_idx:]
                print(history_idx, self.pixmap_history)
                print('subse', subsequent_routines)
                print(latest_pixmap, latest_pixmap.size())
                break

    # override arbitrary and unwanted margins: https://bugreports.qt.io/browse/QTBUG-42331 - based on QT sources
    def fitInView(self, rect, flags=Qt.IgnoreAspectRatio):
        if self.scene() is None or rect.isNull():
            return
        self.last_scene_roi = rect
        unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        self.scale(1/unity.width(), 1/unity.height())
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
