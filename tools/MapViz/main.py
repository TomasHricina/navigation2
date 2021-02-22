
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget, QLineEdit, QSlider, QPushButton
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QKeyEvent
from PyQt5.QtCore import QPoint, QPointF, QRect, QRectF, QSize, QSizeF, pyqtSignal
from PyQt5.Qt import Qt
from canvas import ImageView
import os, sys
from collections import namedtuple
from helpers import scaleToFit, parse_map_yaml


#TODO: Drag and drop
#TODO: Undo Redo - in progress

__version__ = "1.1.0"
__title__ = "MapViz"
__uri__ = "https://github.com/TomasHricina/navigation2"
__author__ = "Tomas Hričina"
__maintainer__ = __author__
__credits__ = ["Steve Macenski", ]
__email__ = "t.hri@seznam.cz"
__license__ = None

available_resolution = None  # calculated in main()
dimensions = namedtuple('dimensions', 'width height')
load_button_dimensions = dimensions(width=80, height=80)
save_button_dimensions = dimensions(width=80, height=80)
canvas_min_dim = dimensions(width=400, height=400)
canvas_height_offset = 50


class AppImageView(ImageView):
    def __init__(self, *args, **kwargs):
        ImageView.__init__(self, *args, **kwargs)

    def updateStatusBar(self) -> None:
        status_msg = 'ui: %d,%d | image: %d,%d | angle: %d | rotation_speed: %d | pan_speed: %d'\
                     % (self.cursor_widget_x, self.cursor_widget_y,
                        self.cursor_image_x, self.cursor_image_y,
                        self.angle, self.rotating_speed, self.pan_speed)
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

class LoadButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(LoadButton, self).__init__(*args, **kwargs)
        print('Load')
        self.setFixedSize(*load_button_dimensions)
        self.setText("Load Yaml")


class SaveButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(SaveButton, self).__init__(*args, **kwargs)
        print('Save')
        self.setFixedSize(*save_button_dimensions)
        self.setText("Save As")


class TopMenu(QWidget):
    def __init__(self):
        super().__init__()
        print('TopMenu')
        self.load_button = LoadButton()
        self.save_button = SaveButton()
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.load_button)
        self.hbox.addWidget(self.save_button)
        self.hbox.setAlignment(Qt.AlignTop)
        self.setLayout(self.hbox)


class ImageViewerWindow(QMainWindow):
    def __init__(self, image, input_path):
        QMainWindow.__init__(self)
        self.image = image
        self.input_path = input_path
        self.image_view = AppImageView(self)
        self.image_view.main_widget = self
        self.top_menu = TopMenu()

        padding = self.frameGeometry().size() - self.geometry().size()
        self.resize(image.size() + padding)
        self.central = QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.central)
        self.image_view.setMouseTracking(True)
        self.verticalLayout.addWidget(self.top_menu)
        self.verticalLayout.addWidget(self.image_view)

        self.setCentralWidget(self.central)
        screen = QDesktopWidget().screenGeometry(self)
        size = self.geometry()
        self.move(int((screen.width()-size.width())/4), int((screen.height()-size.height())/4))
        # self.setStyleSheet('background: red')
        self.update_view()
        self.image_view.reset()

        self.top_menu.load_button.clicked.connect(self.load_yaml)

    def update_view(self):
        self.image_view.image = self.image
        self.image_view.const_pixmap = QPixmap.fromImage(self.image)
        self.image_view.pixmap_history.append(QPixmap.fromImage(self.image))     # this is for default image
        self.setWindowTitle('MapViz  file: ' + self.make_window_title())

    def make_window_title(self):
        return os.path.basename(self.input_path)

    def load_yaml(self):
        # TODO: drag and drop file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Load YAML", "", "YAML(*.yaml)", options=options)

        if file_name:
            parsed_yaml = parse_map_yaml(file_name)
            if type(parsed_yaml) is list:
                # TODO: Notify user about YAML parsing error
                # error parsing branch
                print(parsed_yaml)
            else:
                # success parsing branch

                self.const_pixmap = QPixmap(parsed_yaml['image'])
                self.image_view.const_pixmap = self.const_pixmap
                self.image_view.pixmap = self.const_pixmap
                self.image_view.pixmap_history.append(self.const_pixmap)
                self.image_view.angle = 0


def main():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    available_screen = screen.availableGeometry()
    global available_resolution
    available_resolution = dimensions(available_screen.width(), available_screen.height())
    input_image = 'map.png'
    image = QImage()
    image.load(input_image)
    window = ImageViewerWindow(image, input_image)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
