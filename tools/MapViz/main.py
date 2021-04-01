
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget, QLineEdit, QSlider, QPushButton
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QTableWidget
from PyQt5.QtWidgets import QStyledItemDelegate, QDialog, QAbstractItemView, QTableView, QRadioButton
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QKeyEvent, QFont, QIntValidator, QStandardItemModel, QStandardItem
from PyQt5.QtGui import QTextCursor, QBrush, QFocusEvent
from PyQt5.QtCore import QPoint, QPointF, QRect, QRectF, QSize, QSizeF, pyqtSignal
from PyQt5.Qt import Qt
import yaml  # pip pyaml
from canvas20 import ImageView
import os, sys
from collections import namedtuple
from helpers import Routine, dict2str
from re import compile, match


# TODO: Drag and drop
# TODO: Fix bottom-up crop
# TODO: Add image names in history box
# TODO: https://www.learnpyqt.com/tutorials/qtableview-modelviews-numpy-pandas/

__version__ = "1.0.3"
__title__ = "Nav2-MapViz"
__uri__ = "https://github.com/TomasHricina/navigation2"
__author__ = "Tomáš Hričina"
__maintainer__ = __author__
__credits__ = ["Steve Macenski", ]
__email__ = "t.hri@seznam.cz"
__license__ = None

available_resolution = None  # calculated in main()
default_yaml = None  # loaded in main()
dimensions = namedtuple('dimensions', 'width height')

valid_filename_regex = compile(r'^[^<>:;,?"*|/]+$')
list_sanitizer_regex = compile(r'[0-9., \[\]+-]*$')

error_background = "QLineEdit{background:red;}"
warning_background = "QLineEdit{background:yellow;}"
success_background = "QLineEdit{background:white;}"

# GUI-specific magic numbers
top_menu_button_width, top_menu_button_height = 90, 60
left_menu_width = 222
history_box_total_height = 300
history_box_row_height = 23
angle_button_width, angle_button_height = 25, 25
yaml_button_width, yaml_button_height = 25, 25
canvas_minimum_dimensions = dimensions(width=820, height=800)
canvas_height_offset = 50

top_menu_button_dimensions = dimensions(width=top_menu_button_width, height=top_menu_button_height)
load_button_dimensions = top_menu_button_dimensions
save_button_dimensions = top_menu_button_dimensions
undo_button_dimensions = top_menu_button_dimensions
redo_button_dimensions = top_menu_button_dimensions
help_button_dimensions = top_menu_button_dimensions
about_button_dimensions = top_menu_button_dimensions

angle_button_dimensions = dimensions(width=angle_button_width, height=angle_button_height)
yaml_button_dimensions = dimensions(width=yaml_button_width, height=yaml_button_height)


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


# ----------Top menu widgets----------

class LoadButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(LoadButton, self).__init__(*args, **kwargs)
        self.setFixedSize(*load_button_dimensions)
        self.setText("Load Yaml")


class SaveButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(SaveButton, self).__init__(*args, **kwargs)
        self.setFixedSize(*save_button_dimensions)
        self.setText("Save As")


class UndoButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(UndoButton, self).__init__(*args, **kwargs)
        self.setFixedSize(*undo_button_dimensions)
        self.setText("Undo")


class RedoButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(RedoButton, self).__init__(*args, **kwargs)
        self.setFixedSize(*redo_button_dimensions)
        self.setText("Redo")


class HelpButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(HelpButton, self).__init__(*args, **kwargs)
        self.setFixedSize(*help_button_dimensions)
        self.setText("Help")


class AboutButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(AboutButton, self).__init__(*args, **kwargs)
        self.setFixedSize(*about_button_dimensions)
        self.setText("About")


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Help")
        self.layout = QGridLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.setLayout(self.layout)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("About")
        self.layout = QGridLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.setLayout(self.layout)


class TopMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.load_button = LoadButton()
        self.save_button = SaveButton()
        self.undo_button = UndoButton()
        self.redo_button = RedoButton()
        self.help_button = HelpButton()
        self.about_button = AboutButton()

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.load_button)
        self.hbox.addWidget(self.save_button)
        self.hbox.addWidget(self.undo_button)
        self.hbox.addWidget(self.redo_button)
        self.hbox.addWidget(self.help_button)
        self.hbox.addWidget(self.about_button)
        self.hbox.setAlignment(Qt.AlignLeft)
        self.setLayout(self.hbox)

# ----------/Top menu widgets----------


# ----------Left menu widgets----------

class FocusOutLineEdit(QLineEdit):
    # Inherited class makes sure, that after entry is filled, canvas is brought into focus
    def __init__(self, left_menu):
        super().__init__()
        self.left_menu = left_menu

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super(FocusOutLineEdit, self).focusOutEvent(event)
        self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)


class AngleBox(QWidget):
    def __init__(self, left_menu):
        super().__init__()

        self.left_menu = left_menu
        self.hbox = QHBoxLayout()
        self.label = QLabel()
        self.label.setText('Angle')

        self.angle_entry = FocusOutLineEdit(left_menu)
        self.angle_entry.setText('0')
        self.angle_entry.setValidator(QIntValidator(-9999, 9999))
        self.angle_entry.setAlignment(Qt.AlignCenter)

        self.button_default = QPushButton()
        self.button_default.setText('D')
        self.button_default.setFixedSize(*angle_button_dimensions)

        self.button_0 = QPushButton()
        self.button_0.setText('0°')
        self.button_0.setFixedSize(*angle_button_dimensions)

        self.button_plus = QPushButton()
        self.button_plus.setText('+')
        self.button_plus.setFont(QFont('Arial', 17))
        self.button_plus.setFixedSize(*angle_button_dimensions)

        self.button_minus = QPushButton()
        self.button_minus.setText('–')
        self.button_minus.setFont(QFont('Arial', 19))
        self.button_minus.setFixedSize(*angle_button_dimensions)

        self.button_plus_90 = QPushButton()
        self.button_plus_90.setText('+90°')
        self.button_0.setFixedSize(*angle_button_dimensions)

        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.angle_entry)
        self.hbox.addWidget(self.button_0)
        self.hbox.addWidget(self.button_plus_90)
        self.hbox.addWidget(self.button_minus)
        self.hbox.addWidget(self.button_plus)

        self.setFixedWidth(left_menu_width)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.hbox)

        self.angle_entry.editingFinished.connect(lambda: self.angle_set(int(self.angle_entry.text())))
        self.button_0.clicked.connect(lambda: self.angle_set(0))
        self.button_plus_90.clicked.connect(lambda: self.angle_increment(+90))
        self.button_plus.clicked.connect(lambda: self.angle_increment(+1))
        self.button_minus.clicked.connect(lambda: self.angle_increment(-1))

    def angle_set(self, angle_amount) -> None:
        if self.left_menu.canvas_instance.angle != angle_amount:
            angle_amount %= 360
            self.left_menu.canvas_instance.angle_rotate(angle_amount)
            self.left_menu.canvas_instance.add_and_cull_history((Routine.ANGLE.value, angle_amount))
            self.left_menu.canvas_instance.angle = angle_amount
            self.left_menu.canvas_instance.updateStatusBar()
            self.left_menu.angle_box.angle_entry.setText(str(angle_amount))
            self.left_menu.history_table.history = self.left_menu.canvas_instance.history
            self.left_menu.history_table.populate()

    def angle_increment(self, increment) -> None:
        entry_val = int(self.left_menu.angle_box.angle_entry.text())
        entry_val += increment
        self.angle_set(entry_val)


class PathBox(QWidget):
    def __init__(self, left_menu):
        super().__init__()

        self.left_menu = left_menu
        self.title = QLabel()
        self.title.setText('______Yaml and Image Path:_____')
        self.parent_vbox = QVBoxLayout()
        self.parent_vbox.addWidget(self.title)

        self.yaml_widget = QWidget()
        self.yaml_hbox = QHBoxLayout()

        self.yaml_entry = FocusOutLineEdit(left_menu)
        self.yaml_entry.setReadOnly(True)
        self.yaml_entry.setText('../default_yaml.yaml')
        self.yaml_hbox.addWidget(self.yaml_entry)
        self.yaml_hbox.setContentsMargins(0, 0, 0, 0)
        self.yaml_widget.setLayout(self.yaml_hbox)

        self.img_widget = QWidget()
        self.img_hbox = QHBoxLayout()

        self.img_entry = FocusOutLineEdit(left_menu)
        self.img_entry.setReadOnly(True)
        self.img_entry.setText('../default_map.pgm')
        self.img_hbox.addWidget(self.img_entry)
        self.img_hbox.setContentsMargins(0, 0, 0, 0)
        self.img_widget.setLayout(self.img_hbox)

        self.save_as_widget = QWidget()
        self.save_as_hbox = QHBoxLayout()

        self.save_as_title = QLabel()
        self.save_as_title.setFont(QFont('Arial', 8))
        self.save_as_title.setText('Save path as:  ')
        self.save_as_hbox.addWidget(self.save_as_title)

        self.save_as_relative_radio = QRadioButton()
        self.save_as_relative_radio.setChecked(True)
        self.save_as_relative_radio.setFont(QFont('Arial', 10))
        self.save_as_relative_radio.setText('Relative')
        self.save_as_hbox.addWidget(self.save_as_relative_radio)

        self.save_as_absolute_radio = QRadioButton()
        self.save_as_absolute_radio.setFont(QFont('Arial', 10))
        self.save_as_absolute_radio.setText('Absolute')
        self.save_as_hbox.addWidget(self.save_as_absolute_radio)

        self.save_as_hbox.setContentsMargins(0, 0, 0, 0)
        self.save_as_widget.setLayout(self.save_as_hbox)

        self.parent_vbox.addWidget(self.yaml_widget)
        self.parent_vbox.addWidget(self.img_widget)
        self.parent_vbox.addWidget(self.save_as_widget)
        self.setFixedWidth(left_menu_width)
        self.parent_vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.parent_vbox)


class YamlSingleRow(QWidget):
    def __init__(self, label, left_menu):
        super().__init__()

        self.hbox = QHBoxLayout()
        self.label = QLabel()
        self.label.setText(label)
        self.entry = QLineEdit()

        self.entry = FocusOutLineEdit(left_menu)
        # self.entry.setAlignment(Qt.AlignRight)

        self.button = QPushButton()
        self.button.setText('D')
        self.button.setFixedSize(*yaml_button_dimensions)

        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.entry)
        self.hbox.addWidget(self.button)
        self.setFixedWidth(left_menu_width)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        # self.hbox.setAlignment(Qt.AlignCenter)
        self.setLayout(self.hbox)


class YamlBox(QWidget):
    def __init__(self, left_menu):
        super().__init__()

        self.vbox = QVBoxLayout()
        self.title = QLabel()
        self.left_menu = left_menu
        self.latest_yaml_name = 'default_yaml.yaml'
        self.latest_yaml = default_yaml
        self.flags = {   # used for disabling Save, when input is invalid, call self.update_flags()
            'yaml': True,
            'image': True,
            'resolution': True,
            'origin': True,
            'occupied_thresh': True,
            'free_thresh': True,
            'negate': True,
            'mode': True}

        self.title.setText('________Edit Yaml file:________')
        self.entry_yaml = YamlSingleRow('yaml', left_menu)
        self.entry_image = YamlSingleRow('image', left_menu)
        self.entry_resolution = YamlSingleRow('resolution', left_menu)
        self.entry_origin = YamlSingleRow('origin', left_menu)
        self.entry_occupied_thresh = YamlSingleRow('occupied_thresh', left_menu)
        self.entry_free_thresh = YamlSingleRow('free_thresh', left_menu)
        self.entry_negate = YamlSingleRow('negate', left_menu)
        self.entry_mode = YamlSingleRow('mode', left_menu)

        def yaml_entry_func() -> None:
            yaml_value = self.entry_yaml.entry.text()
            valid_filename = match(valid_filename_regex, yaml_value)
            if os.path.isfile(yaml_value):
                self.entry_yaml.entry.setStyleSheet(success_background)
                self.flags['yaml'] = True
            else:
                if valid_filename:
                    self.entry_yaml.entry.setStyleSheet(warning_background)
                    self.flags['yaml'] = True
                else:
                    self.entry_yaml.entry.setStyleSheet(error_background)
                    self.flags['yaml'] = False

        def image_entry_func() -> None:
            image_value = self.entry_image.entry.text()
            valid_filename = match(valid_filename_regex, image_value)
            if os.path.isfile(image_value):
                self.entry_image.entry.setStyleSheet(success_background)
                self.flags['image'] = True
            else:
                if valid_filename:
                    self.entry_image.entry.setStyleSheet(warning_background)
                    self.flags['image'] = True
                else:
                    self.entry_image.entry.setStyleSheet(error_background)
                    self.flags['image'] = False

        def resolution_entry_func() -> None:
            resolution_value = self.entry_resolution.entry.text()
            try:
                resolution_value = float(resolution_value)
                0 / resolution_value  # cant be zero
                self.entry_resolution.entry.setStyleSheet(success_background)
                self.flags['resolution'] = True
            except (KeyError, ValueError, ZeroDivisionError):
                self.entry_resolution.entry.setStyleSheet(error_background)
                self.flags['resolution'] = False

        def origin_entry_func() -> None:
            origin_value = self.entry_origin.entry.text()
            sanitized = match(list_sanitizer_regex, origin_value)
            if not sanitized:
                self.entry_origin.entry.setStyleSheet(error_background)
                self.flags['origin'] = False
            else:
                try:
                    origin_value = eval(origin_value)
                    if all(isinstance(n, (int, float)) for n in origin_value) and len(origin_value) == 3:
                        self.entry_origin.entry.setStyleSheet(success_background)
                        self.flags['origin'] = True
                    else:
                        self.entry_origin.entry.setStyleSheet(error_background)
                        self.flags['origin'] = False
                except (NameError, SyntaxError, TypeError):
                    self.entry_origin.entry.setStyleSheet(error_background)
                    self.flags['origin'] = False

        def occupied_thresh_entry_func() -> None:
            try:
                occupied_thresh_value = float(self.entry_occupied_thresh.entry.text())
            except ValueError:
                self.entry_occupied_thresh.entry.setStyleSheet(error_background)
                self.flags['occupied_thresh'] = False
            else:
                if 0 <= occupied_thresh_value <= 1:
                    self.entry_occupied_thresh.entry.setStyleSheet(success_background)
                    self.flags['occupied_thresh'] = True
                else:
                    self.entry_occupied_thresh.entry.setStyleSheet(error_background)
                    self.flags['occupied_thresh'] = False

        def free_thresh_entry_func() -> None:
            try:
                free_thresh_value = float(self.entry_free_thresh.entry.text())
            except ValueError:
                self.entry_free_thresh.entry.setStyleSheet(error_background)
                self.flags['free_thresh'] = False
            else:
                if 0 <= free_thresh_value <= 1:
                    self.entry_free_thresh.entry.setStyleSheet(success_background)
                    self.flags['free_thresh'] = True
                else:
                    self.entry_free_thresh.entry.setStyleSheet(error_background)
                    self.flags['free_thresh'] = False

        def negate_entry_func() -> None:
            negate_value = self.entry_negate.entry.text()
            if negate_value == '0' or negate_value == '1':
                self.entry_negate.entry.setStyleSheet(success_background)
                self.flags['negate'] = True
            else:
                self.entry_negate.entry.setStyleSheet(error_background)
                self.flags['negate'] = False

        def mode_entry_func() -> None:
            mode_value = self.entry_mode.entry.text()
            if mode_value in ('', 'trinary', 'scale', 'raw'):
                self.entry_mode.entry.setStyleSheet(success_background)
                self.flags['mode'] = True
            else:
                self.entry_mode.entry.setStyleSheet(error_background)
                self.flags['mode'] = False

        self.entry_yaml.entry.textChanged.connect(yaml_entry_func)
        self.entry_image.entry.textChanged.connect(image_entry_func)
        self.entry_resolution.entry.textChanged.connect(resolution_entry_func)
        self.entry_origin.entry.textChanged.connect(origin_entry_func)
        self.entry_occupied_thresh.entry.textChanged.connect(occupied_thresh_entry_func)
        self.entry_free_thresh.entry.textChanged.connect(free_thresh_entry_func)
        self.entry_negate.entry.textChanged.connect(negate_entry_func)
        self.entry_mode.entry.textChanged.connect(mode_entry_func)

        def yaml_default_button_func() -> None:
            self.entry_yaml.entry.setText(self.latest_yaml_name)
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def image_default_button_func() -> None:
            self.entry_image.entry.setText(str(self.latest_yaml['image']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def resolution_default_button_func() -> None:
            self.entry_resolution.entry.setText(str(self.latest_yaml['resolution']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def origin_default_button_func() -> None:
            self.entry_origin.entry.setText(str(self.latest_yaml['origin']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def occupied_thresh_default_button_func() -> None:
            self.entry_occupied_thresh.entry.setText(str(self.latest_yaml['occupied_thresh']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def free_thresh_default_button_func() -> None:
            self.entry_free_thresh.entry.setText(str(self.latest_yaml['free_thresh']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def negate_default_button_func() -> None:
            self.entry_negate.entry.setText(str(self.latest_yaml['negate']))
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        def mode_default_button_func() -> None:
            try:
                # optional
                self.entry_mode.entry.setText(str(self.latest_yaml['mode']))
            except KeyError:
                self.entry_mode.entry.setText('')
            self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

        self.entry_yaml.button.clicked.connect(yaml_default_button_func)
        self.entry_image.button.clicked.connect(image_default_button_func)
        self.entry_resolution.button.clicked.connect(resolution_default_button_func)
        self.entry_origin.button.clicked.connect(origin_default_button_func)
        self.entry_occupied_thresh.button.clicked.connect(occupied_thresh_default_button_func)
        self.entry_free_thresh.button.clicked.connect(free_thresh_default_button_func)
        self.entry_negate.button.clicked.connect(negate_default_button_func)
        self.entry_mode.button.clicked.connect(mode_default_button_func)

        self.vbox.addWidget(self.title)
        self.vbox.addWidget(self.entry_yaml)
        self.vbox.addWidget(self.entry_image)
        self.vbox.addWidget(self.entry_resolution)
        self.vbox.addWidget(self.entry_origin)
        self.vbox.addWidget(self.entry_occupied_thresh)
        self.vbox.addWidget(self.entry_free_thresh)
        self.vbox.addWidget(self.entry_negate)
        self.vbox.addWidget(self.entry_mode)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

    def insert_yaml_into_entries(self) -> None:
        self.entry_yaml.entry.setText(self.latest_yaml_name)
        self.entry_image.entry.setText(str(self.latest_yaml['image']))
        self.entry_resolution.entry.setText(str(self.latest_yaml['resolution']))
        self.entry_origin.entry.setText(str(self.latest_yaml['origin']))
        self.entry_occupied_thresh.entry.setText(str(self.latest_yaml['occupied_thresh']))
        self.entry_free_thresh.entry.setText(str(self.latest_yaml['free_thresh']))
        self.entry_negate.entry.setText(str(self.latest_yaml['negate']))
        try:
            # optional
            self.entry_mode.entry.setText(str(self.latest_yaml['mode']))
        except KeyError:
            self.entry_mode.entry.setText('')

    def harvest_entry_into_latest_yaml(self) -> None:
        self.latest_yaml['image'] = self.entry_image.entry.text()
        self.latest_yaml['resolution'] = self.entry_resolution.entry.text()
        self.latest_yaml['origin'] = self.entry_origin.entry.text()
        self.latest_yaml['occupied_thresh'] = self.entry_occupied_thresh.entry.text()
        self.latest_yaml['free_thresh'] = self.entry_free_thresh.entry.text()
        self.latest_yaml['negate'] = self.entry_negate.entry.text()

        mode_value = self.entry_mode.entry.text()
        if mode_value == '':
            self.latest_yaml.pop('mode', None)
        else:
            self.latest_yaml['mode'] = mode_value

    def update_flags(self) -> None:
        self.left_menu.yaml_box.flags = self.flags


class HistoryTable(QTableWidget):
    def __init__(self, left_menu):
        super().__init__()

        self.left_menu = left_menu
        self.setFixedWidth(left_menu_width)
        self.table = QTableView(self)
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['History'])
        self.table.setModel(self.model)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFixedWidth(left_menu_width)
        self.table.setFixedHeight(history_box_total_height)

        self.history = []
        self.table.doubleClicked.connect(self.on_click)
        self.populate()

    def on_click(self, signal) -> None:
        row = signal.row()
        cell_dict = self.model.itemData(signal)
        cell_value = cell_dict.get(0)
        self.left_menu.canvas_instance.execute_latest_history(row+1)
        self.left_menu.canvas_instance.history_current_idx = row
        self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)

    def populate(self) -> None:
        self.model.clear()
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['History'])
        self.table.setModel(self.model)

        for history_idx, history_event in enumerate(self.history):
            event_type = history_event[0]
            event_value = history_event[1]

            if event_type == Routine.ANGLE.value:
                cell = Routine.ANGLE.name + ' ' + str(event_value) + '°'

            elif event_type == Routine.LOAD.value:
                cell = Routine.LOAD.name + ' ' + str(event_value.width()) + 'x' + str(event_value.height())

            elif event_type == Routine.CROP.value:
                cell = Routine.CROP.name + ' ' + str(event_value.width()) + 'x' + str(event_value.height())

            self.model.appendRow(QStandardItem(cell.lower()))
            self.table.setColumnWidth(history_idx, left_menu_width)
            self.table.setRowHeight(history_idx, history_box_row_height)
            self.table.scrollToBottom()

        self.left_menu.canvas_instance.setFocus(Qt.OtherFocusReason)
        # self.table.clearSelection()
        self.table.selectRow(self.left_menu.canvas_instance.history_current_idx)


class LeftMenu(QWidget):
    def __init__(self, canvas_instance):
        super().__init__()

        self.canvas_instance = canvas_instance
        self.angle_box = AngleBox(self)
        self.path_box = PathBox(self)
        self.yaml_box = YamlBox(self)
        self.yaml_box.insert_yaml_into_entries()  # inserting default YAML

        self.history_table = HistoryTable(self)
        self.grid = QGridLayout()
        self.grid.addWidget(self.angle_box)
        self.grid.addWidget(self.path_box)
        self.grid.addWidget(self.yaml_box)
        self.grid.addWidget(self.history_table)

        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

# ----------/Left menu widgets----------


class MainWindow(QMainWindow):
    def __init__(self, image, input_path):
        QMainWindow.__init__(self)

        self.setMinimumSize(*canvas_minimum_dimensions)
        # self.showMaximized()

        self.image = image
        self.input_path = input_path
        self.image_path_in_yaml = ''
        self.canvas = AppImageView()
        self.canvas.main_widget = self
        self.canvas.setMouseTracking(True)
        self.top_menu = TopMenu()
        self.left_menu = LeftMenu(self.canvas)

        padding = self.frameGeometry().size() - self.geometry().size()
        self.resize(image.size() + padding)
        self.central = QWidget(self)
        self.main_layout = QtWidgets.QGridLayout(self.central)

        self.main_layout.addWidget(self.top_menu, 0, 1)
        self.main_layout.addWidget(self.canvas, 1, 1)
        self.main_layout.addWidget(self.left_menu, 1, 0)
        self.main_layout.setColumnStretch(1, 2)

        self.setCentralWidget(self.central)
        screen = QDesktopWidget().screenGeometry(self)
        size = self.geometry()
        self.move(int((screen.width()-size.width())/4), int((screen.height()-size.height())/4))
        self.update_view()
        self.canvas.reset()
        self.top_menu_bind_buttons()

    def update_view(self) -> None:
        self.canvas.image = self.image
        default_pixmap = QPixmap.fromImage(self.image)
        self.canvas.const_pixmap = default_pixmap
        self.canvas.latest_pixmap = default_pixmap
        self.canvas.history.append((Routine.LOAD.value, default_pixmap))
        self.canvas.populate_history_table()
        self.window_title()

    def top_menu_bind_buttons(self) -> None:
        self.top_menu.load_button.clicked.connect(self.load_yaml)
        self.top_menu.save_button.clicked.connect(self.save_as)
        self.top_menu.undo_button.clicked.connect(self.canvas.undo)
        self.top_menu.redo_button.clicked.connect(self.canvas.redo)
        self.top_menu.help_button.clicked.connect(lambda: HelpDialog().exec_())
        self.top_menu.about_button.clicked.connect(lambda: AboutDialog().exec_())

    def file_title(self):
        return os.path.basename(self.input_path)

    def window_title(self) -> None:
        self.setWindowTitle('%s %s                file: %s' % (__title__, __version__, self.file_title()))

    def load_yaml(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Load YAML", "", filter="YAML(*.yaml)", options=options)
        try:
            os.chdir(os.path.dirname(file_path))
            with open(file_path, 'r') as stream:
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
        except (FileNotFoundError, KeyError):
            return
        else:
            self.left_menu.path_box.yaml_entry.setText(file_path)
            latest_yaml_name = os.path.basename(file_path)
            self.left_menu.yaml_box.latest_yaml_name = latest_yaml_name
            self.left_menu.yaml_box.entry_yaml.entry.setText(latest_yaml_name)
            self.left_menu.path_box.img_entry.setText(image_path)
            loaded_pixmap = QPixmap(image_path)
            self.input_path = file_path
            self.window_title()
            self.canvas.const_pixmap = loaded_pixmap
            self.canvas.pixmap = loaded_pixmap
            self.canvas.latest_pixmap = loaded_pixmap
            self.canvas.angle = 0
            self.canvas.history.append((Routine.LOAD.value, loaded_pixmap))
            self.canvas.history_current_idx += 1
            self.canvas.populate_history_table()

    def save_as(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # 'directory=' serves as default name for Dialog
        future_yaml_name = self.left_menu.yaml_box.entry_yaml.entry.text()
        future_image_name = self.left_menu.yaml_box.entry_image.entry.text()

        self.left_menu.yaml_box.update_flags()

        if False in self.left_menu.yaml_box.flags.values():
            return

        if '' in (future_yaml_name, future_image_name):
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

        with open(file_path, 'w', encoding="utf-8") as yaml_file:
            yaml_file.write(export_string)
        self.canvas.pixmap.save(future_image_name)


def main():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    available_screen = screen.availableGeometry()
    global available_resolution
    available_resolution = dimensions(available_screen.width(), available_screen.height())
    default_image_name = 'default_map.pgm'
    global default_yaml
    try:
        with open('default_yaml.yaml', 'r') as stream:
            default_yaml = yaml.safe_load(stream)
    except FileNotFoundError:
        pass

    image = QImage()
    image.load(default_image_name)
    window = MainWindow(image, default_image_name)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
