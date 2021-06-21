#!/usr/bin/python3

# PyQT
from PyQt5.QtWidgets import QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox
from PyQt5.QtGui import QFocusEvent
from PyQt5.Qt import Qt


class FocusOutLineEdit(QLineEdit):
    # Makes sure, that after entry is filled, canvas is brought into focus
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.returnPressed.connect(lambda: self.canvas_instance.setFocus(Qt.OtherFocusReason))

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super(FocusOutLineEdit, self).focusOutEvent(event)
        self.canvas_instance.setFocus(Qt.OtherFocusReason)


class FocusOutButton(QPushButton):
    # Makes sure, that after button click, canvas is brought into focus
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.clicked.connect(lambda: self.canvas_instance.setFocus(Qt.OtherFocusReason))


class FocusOutSpinBox(QSpinBox):
    # Makes sure, that after spinbox is changed, canvas is brought into focus
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.editingFinished.connect(lambda: self.canvas_instance.setFocus(Qt.OtherFocusReason))


class FocusOutDoubleSpinBox(QDoubleSpinBox):
    # Makes sure, that after spinbox is changed, canvas is brought into focus
    def __init__(self, canvas_instance):
        super().__init__()
        self.canvas_instance = canvas_instance
        self.editingFinished.connect(lambda: self.canvas_instance.setFocus(Qt.OtherFocusReason))

