#!/usr/bin/python3

# External lib
import yaml  # pip pyaml

# PyQT
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtWidgets import QFileDialog, QLabel
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QPixmap, QMouseEvent, QKeyEvent, QIcon
from PyQt5.Qt import Qt

# Python
import os
import sys
import signal
from collections import namedtuple

# Source files
from map_editor.Helpers.helpers import Routine
from map_editor.Helpers.helpers import create_logger, dict2str
from map_editor.Helpers.helpers import correct_image_path
from map_editor.Helpers.magic_gui_numbers import default_image_name
from map_editor.Helpers.default_map import default_image


from map_editor.Canvas.canvas import ImageView
from map_editor.Left_Menu.left_menu import LeftMenu
from map_editor.Paint_Menu.paint_menu import PaintMenu
from map_editor.Waypoint_Menu.waypoint_menu import WaypointMenu

log_level = "INFO"
logger = create_logger("map_editor")
logger.setLevel(log_level)
signal.signal(signal.SIGINT, signal.SIG_DFL) # Allows CTRL+C to end the program


# TODO: Drag and drop
# TODO: Bottom-up crop

__version__ = "1.0.6"
__title__ = "Nav2-map_editor"
__uri__ = "https://github.com/TomasHricina/navigation2"
__author__ = "Tomáš Hričina"
__maintainer__ = __author__
__credits__ = ["Steve Macenski", "Alexey Merzlyakov" ]
__email__ = "t.hri@seznam.cz"
__license__ = None


available_resolution = None  # calculated in main()
dimensions = namedtuple('dimensions', 'width height')


class AppImageView(ImageView):
    def __init__(self, _default_image):
        logger.debug("Canvas created")
        ImageView.__init__(self, _default_image)

    def updateStatusBar(self) -> None:
        status_msg = '   ui: %d,%d  |  image: %d,%d' \
                     % (self.cursor_widget_x, self.cursor_widget_y,
                        self.cursor_image_x, self.cursor_image_y)
        self.main_widget.statusBar().showMessage(status_msg)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        ImageView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        ImageView.mouseMoveEvent(self, event)
        pos = event.pos()
        self.scene_pos = self.mapToScene(pos)
        self.cursor_widget_x, self.cursor_widget_y = pos.x(), pos.y()
        self.cursor_image_x, self.cursor_image_y = round(self.scene_pos.x()), round(self.scene_pos.y())
        self.updateStatusBar()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        ImageView.keyPressEvent(self, event)
        self.cursor_image_x, self.cursor_image_y = round(self.scene_pos.x()), round(self.scene_pos.y())
        self.updateStatusBar()


class MainWindow(QMainWindow):
    def __init__(self, image, input_path):
        QMainWindow.__init__(self)
        logger.debug("MainWindow created")

        self.image = image
        self.canvas = AppImageView(default_image)
        self.canvas.image = self.image
        self.canvas.main_widget = self
        self.setGeometry(400, 400, 1200, 1200)

        # self.setMinimumSize(*canvas_minimum_dimensions)
        # self.showMaximized()

        # ----------Menu----------
        menu_bar = self.menuBar()
        menu_bar_file = menu_bar.addMenu('&File')
        menu_bar_edit = menu_bar.addMenu('&Edit')

        # File
        save_act = QAction(QIcon('save.png'), '&Save as', self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('Save YAML and image')
        save_act.triggered.connect(self.save_as)
        menu_bar_file.addAction(save_act)

        load_act = QAction(QIcon('load.png'), '&Load YAML', self)
        load_act.setShortcut('Ctrl+L')
        load_act.setStatusTip('Load YAML and image')
        load_act.triggered.connect(self.load_yaml)
        menu_bar_file.addAction(load_act)

        # Undo Redo
        undo_act = QAction(QIcon('undo.png'), '&Undo', self)
        undo_act.setShortcut('Ctrl+Z')
        undo_act.setStatusTip('Undo action')
        undo_act.triggered.connect(self.canvas.undo)
        menu_bar_edit.addAction(undo_act)

        redo_act = QAction(QIcon('redo.png'), '&Redo', self)
        redo_act.setShortcut('Ctrl+Shift+Z')
        redo_act.setStatusTip('Redo action')
        redo_act.triggered.connect(self.canvas.redo)
        menu_bar_edit.addAction(redo_act)

        # ----------/Menu----------

        self.input_path = input_path
        self.image_path_in_yaml = ''

        self.canvas.setMouseTracking(True)

        self.map_editor_logo = QLabel()
        map_editor_logo_path = correct_image_path('map_editor_logo.png')
        self.map_editor_logo.setStyleSheet("background-image : url(" + map_editor_logo_path + ")" )

        self.waypoint_logo = QLabel()
        wp_logo = QPixmap(correct_image_path('waypoint_logo.png')).scaled(100, 100)
        self.waypoint_logo.setPixmap(wp_logo)
        self.waypoint_logo.setAlignment(Qt.AlignCenter)

        self.left_menu = LeftMenu(self.canvas)

        self.waypoint_menu = WaypointMenu(self.canvas)

        self.paint_menu = PaintMenu(self.canvas, self.waypoint_menu.choices)

        padding = self.frameGeometry().size() - self.geometry().size()
        self.resize(image.size() + padding)
        self.central = QWidget(self)
        self.main_layout = QtWidgets.QGridLayout(self.central)

        self.main_layout.addWidget(self.map_editor_logo, 0, 0)
        self.main_layout.addWidget(self.paint_menu, 0, 1)
        self.main_layout.addWidget(self.left_menu, 1, 0)
        self.main_layout.addWidget(self.canvas, 1, 1)
        self.main_layout.addWidget(self.waypoint_logo, 0, 2)
        self.main_layout.addWidget(self.waypoint_menu, 1, 2)

        self.main_layout.setColumnStretch(1, 2)
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(self.central)
        screen = QDesktopWidget().screenGeometry(self)
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 4), int((screen.height() - size.height()) / 4))
        self.update_view()
        self.canvas.reset_view()

    def update_view(self) -> None:
        default_pixmap = QPixmap.fromImage(self.image)
        self.canvas.latest_pixmap = default_pixmap
        self.canvas.history.append((Routine.LOAD.value, default_pixmap, 0))
        self.canvas.populate_history_table()
        self.window_title()
        self.canvas.setFocus(Qt.OtherFocusReason)

    def file_title(self):
        return os.path.basename(self.input_path)

    def window_title(self) -> None:
        self.setWindowTitle('%s %s                file: %s' % (__title__, __version__, self.file_title()))

    def load_yaml(self) -> None:
        logger.debug("Load initiated")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Load YAML", "", filter="YAML(*.yaml)", options=options)
        try:
            os.chdir(os.path.dirname(file_path))
            with open(file_path, 'r') as stream:
                logger.debug("File open")
                parsed_yaml = yaml.safe_load(stream)
                image_path = parsed_yaml['image']
                split_path = os.path.split(image_path)
                self.image_path_in_yaml = split_path[0]
                if self.image_path_in_yaml in ('', '..'):
                    self.left_menu.path_box.save_as_relative_radio.setChecked(True)
                else:
                    self.left_menu.path_box.save_as_absolute_radio.setChecked(True)
                image_basename = split_path[1]
                parsed_yaml['image'] = image_basename
                self.left_menu.yaml_box.latest_yaml = parsed_yaml
                self.left_menu.yaml_box.insert_yaml_into_entries()
                self.canvas.clear_waypoints()
                for i in parsed_yaml:
                    if i.startswith('wp_'):
                        wp_id = int(i.split('_')[1])
                        wp_x, wp_y, wp_theta = parsed_yaml[i]
                        self.canvas.load_waypoint(wp_x, wp_y, wp_theta, wp_id)

                self.canvas.change_waypoint_movable()
                self.canvas.populate_waypoint_table()
        except (FileNotFoundError, KeyError):
            return
        else:
            logger.debug("Load successful")
            self.left_menu.path_box.yaml_entry.setText(file_path)
            latest_yaml_name = os.path.basename(file_path)
            logger.debug("Loaded: " + file_path)
            self.left_menu.yaml_box.latest_yaml_name = latest_yaml_name
            self.left_menu.yaml_box.entry_yaml.entry.setText(latest_yaml_name)
            self.left_menu.path_box.img_entry.setText(image_path)
            loaded_pixmap = QPixmap(image_path)
            self.input_path = file_path
            self.window_title()
            self.canvas.pixmap = loaded_pixmap
            self.canvas.latest_pixmap = loaded_pixmap
            self.canvas.angle = 0
            self.canvas.history.append((Routine.LOAD.value, loaded_pixmap, 0))
            self.canvas.history_current_idx += 1
            self.canvas.populate_history_table()
            self.canvas.reset_view()
            self.canvas.disable_transformations(False)

    def save_as(self) -> None:
        logger.debug("Save initiated")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # 'directory=' serves as default name for Dialog
        future_yaml_name = self.left_menu.yaml_box.entry_yaml.entry.text()
        future_image_name = self.left_menu.yaml_box.entry_image.entry.text()

        self.left_menu.yaml_box.update_flags()

        if False in self.left_menu.yaml_box.flags.values():
            logger.debug("Save failed")
            return

        if '' in (future_yaml_name, future_image_name):
            logger.debug("Save failed")
            return

        yaml_extension = '.yaml'
        if not future_yaml_name.endswith(yaml_extension):
            future_yaml_name += yaml_extension

        image_default_extension = '.pgm'
        if '.' not in future_image_name:
            future_image_name += image_default_extension

        file_path, _ = QFileDialog.getSaveFileName(self, "Save YAML", directory=future_yaml_name,
                                                   options=options, filter="YAML(*.yaml)")

        if '' == file_path:
            logger.debug("Save failed")
            return

        is_path_relative = self.left_menu.path_box.save_as_relative_radio.isChecked()
        self.left_menu.yaml_box.harvest_entry_into_latest_yaml()
        saved_yaml = self.left_menu.yaml_box.latest_yaml

        ordered_saved_yaml = dict()

        if is_path_relative:
            ordered_saved_yaml['image'] = future_image_name
        else:
            if self.image_path_in_yaml in ('', '..'):
                default_to_cwd = os.path.dirname(file_path)
                ordered_saved_yaml['image'] = os.path.join(default_to_cwd, future_image_name)
            else:
                ordered_saved_yaml['image'] = os.path.join(self.image_path_in_yaml, future_image_name)

        saved_yaml.pop('image', None)
        ordered_saved_yaml.update(saved_yaml)
        export_string = dict2str(ordered_saved_yaml)

        # add waypoint data
        export_string += self.canvas.export_waypoints()

        with open(file_path, 'w', encoding="utf-8") as yaml_file:
            yaml_file.write(export_string)

        self.canvas.grayscale_canvas()
        self.canvas.pixmap.save(future_image_name)
        logger.debug("Save succeeded")


def main_entry_point():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    available_screen = screen.availableGeometry()
    global available_resolution
    available_resolution = dimensions(available_screen.width(), available_screen.height())
    window = MainWindow(default_image, default_image_name)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main_entry_point()
