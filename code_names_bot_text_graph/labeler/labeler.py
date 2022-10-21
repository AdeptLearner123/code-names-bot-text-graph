import sys
import random
from abc import ABC, abstractmethod
from PySide6 import QtWidgets
from PySide6.QtCore import Slot


class Labeler(ABC):
    def __init__(self, window_type, save_labels_handler):
        self._window_type = window_type
        self._save_labels_handler = save_labels_handler
    
    @abstractmethod
    def _update(self, current_key):
        pass

    @abstractmethod
    def _save_labels(self, current_key):
        pass

    @Slot()
    def _next_handler(self):
        curr_key = self._keys[self._current]
        self._save_labels(curr_key)
        self._current = min(self._current + 1, len(self._keys) - 1)
        self._update(self._keys[self._current])

    @Slot()
    def _prev_handler(self):
        curr_key = self._keys[self._current]
        self._save_labels(curr_key)
        self._current = max(self._current - 1, 0)
        self._update(self._keys[self._current])

    def start(self, keys, start=0):
        self._keys = keys
        self._current = start

        app = QtWidgets.QApplication([])

        self._window = self._window_type()
        self._window.resize(800, 600)
        self._window.show()

        self._update(self._keys[self._current])
        self._window.next_signal.connect(self._next_handler)
        self._window.prev_signal.connect(self._prev_handler)
        sys.exit(app.exec())
