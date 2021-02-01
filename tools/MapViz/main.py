#!/usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import os
import cv2
import sys
from collections import namedtuple
from helpers import *

# globals:
available_resolution = None  # calculated in main()
dimensions = namedtuple('dimensions', 'width height')
load_button_dimensions = dimensions(width=80, height=80)
save_button_dimensions = dimensions(width=80, height=80)
canvas_min_dim = dimensions(width=400, height=400)
canvas_height_offset = 50


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
        self.setText("Save")


class SizeSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super(SizeSlider, self).__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setOrientation(Qt.Horizontal)
        self.setDisabled(True)


class RotationSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super(RotationSlider, self).__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setOrientation(Qt.Horizontal)
        self.setRange(0, 360)
        self.setDisabled(True)


class LeftVerticalMenu(QWidget):
    def __init__(self):
        super().__init__()
        print('LeftMenu')
        self.load_button = LoadButton()
        self.save_button = SaveButton()
        self.size_slider = SizeSlider()
        self.rotation_slider = RotationSlider()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.load_button)
        self.vbox.addWidget(self.save_button)
        self.vbox.addWidget(self.size_slider)
        self.vbox.addWidget(self.rotation_slider)
        self.vbox.setAlignment(Qt.AlignTop)
        self.setLayout(self.vbox)


class Canvas(QLabel):
    def __init__(self):
        super().__init__()
        print('Canvas')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("QLabel {background-color: red;}")
        self.setAlignment(Qt.AlignLeft)


class Panel(QWidget):
    def __init__(self, parent=None):
        super(Panel, self).__init__(parent=None)
        print('Panel')
        self.panel_lay = QGridLayout(self)
        self.left_menu = LeftVerticalMenu()
        self.canvas = Canvas()
        self.panel_lay.addWidget(self.left_menu, 0, 0)
        self.panel_lay.addWidget(self.canvas, 0, 1)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        print('MainWindow')
        self.default_dim = dimensions(width=800, height=600)
        self.default_window_x = 0
        self.default_window_y = 0
        self.angle = 0  # counter-clockwise
        self.setGeometry(self.default_window_x, self.default_window_y, self.default_dim.width, self.default_dim.height)
        self.initUi()

    def initUi(self):
        self.panel = Panel(self)
        self.setCentralWidget(self.panel)

        # defaults
        self.left_menu_dim = dimensions(width=self.panel.left_menu.sizeHint().width(),
                                        height=self.panel.left_menu.sizeHint().height())
        self.canvas_max_dim = dimensions(width=available_resolution.width - self.left_menu_dim.width,
                                         height=available_resolution.height - canvas_height_offset)

        # bind sliders
        self.panel.left_menu.size_slider.valueChanged.connect(self.resizeWithSlider)
        self.panel.left_menu.rotation_slider.valueChanged.connect(self.rotateWithSlider)

        # bind load button with load_yaml
        self.panel.left_menu.load_button.clicked.connect(self.load_yaml)

    def updateCanvas(self, updated_pixmap):
        self.panel.canvas.setPixmap(updated_pixmap)
        self.setFixedSize(self.panel.sizeHint())

    def resizeCanvas(self, const_image, target_canvas_w, target_canvas_h):
        temp_pixmap = const_image.scaled(target_canvas_w, target_canvas_h)
        self.updateCanvas(temp_pixmap)

    def resizeWithSlider(self):
        # guaranteed to execute after Load (slider is locked)
        slider_value = self.panel.left_menu.size_slider.value()
        self.interp_canvas_width = int(np.interp(slider_value, (0, 99), [canvas_min_dim.width, self.new_image_dim.width]))
        self.interp_canvas_height = int(self.interp_canvas_width / self.const_image_width_height_ratio)

        # rotation is done again on const image so the quality of image does not degrade
        rotated_pixmap = rotation(self.const_image, self.angle)
        self.rotated_image_dim = scaleToFit(canvas_w=self.interp_canvas_width, canvas_h=self.interp_canvas_height,
                                            image_w=rotated_pixmap.width(), image_h=rotated_pixmap.height())
        self.resizeCanvas(rotated_pixmap, self.rotated_image_dim.width, self.rotated_image_dim.height)

    def rotateWithSlider(self):
        # guaranteed to execute after Load (slider is locked)
        slider_value = self.panel.left_menu.rotation_slider.value()
        self.angle = slider_value

        rotated_pixmap = rotation(self.const_image, self.angle)
        self.rotated_image_dim = scaleToFit(canvas_w=self.interp_canvas_width, canvas_h=self.interp_canvas_height,
                                            image_w=rotated_pixmap.width(), image_h=rotated_pixmap.height())
        self.resizeCanvas(rotated_pixmap, self.rotated_image_dim.width, self.rotated_image_dim.height)

    def load_yaml(self):
        # TODO: drag and drop file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Load YAML", "", "YAML(*.yaml)", options=options)
        print(file_name)

        if file_name:
            yaml_directory, yaml_name = os.path.split(file_name)
            os.chdir(yaml_directory)
            parsed_yaml = parse_map_yaml(yaml_name)
            if type(parsed_yaml) is list:
                # error parsing branch
                # TODO: Notify user about YAML parsing error via some widget
                print(parsed_yaml)
            else:
                self.const_image = QPixmap(parsed_yaml['image'])
                self.const_image_dim = dimensions(width=self.const_image.width(), height=self.const_image.height())
                self.const_image_width_height_ratio = self.const_image.width() / self.const_image.height()

                # scale image so it maximally uses resolution, while keeping sides ratio
                self.new_image_dim = scaleToFit(canvas_w=self.canvas_max_dim.width, canvas_h=self.canvas_max_dim.height,
                                                image_w=self.const_image_dim.width, image_h=self.const_image_dim.height)

                # update canvas
                self.resizeCanvas(self.const_image, self.new_image_dim.width, self.new_image_dim.height)

                # update sliders
                self.panel.left_menu.size_slider.setValue(99)
                self.panel.left_menu.size_slider.setEnabled(True)
                self.panel.left_menu.rotation_slider.setValue(0)
                self.panel.left_menu.rotation_slider.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    available_screen = screen.availableGeometry()
    global available_resolution
    available_resolution = dimensions(available_screen.width(), available_screen.height())
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
