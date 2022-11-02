from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt

class LabelerWindow(QtWidgets.QWidget):
    next_signal = Signal()
    prev_signal = Signal()

    INPUT_KEYS = "0123456789abcdefghijklmnopqrstuvwxyz"

    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)

        self._add_title()
        self._add_text()
        self._add_sense_list()
        self._add_sense_input()
    
    def _add_title(self):
        self._title = QtWidgets.QLabel()
        self._layout.addWidget(self._title)
    
    def _add_text(self):
        text = QtWidgets.QLabel()
        self._layout.addWidget(text)
        self._text = text

    def _add_sense_list(self):
        sense_list = QtWidgets.QLabel()
        self._layout.addWidget(sense_list)
        self._sense_list = sense_list
    
    def _add_sense_input(self):
        sense_input = QtWidgets.QLineEdit()
        self._layout.addWidget(sense_input)
        self._sense_input = sense_input
        self._sense_input.setVisible(False)

    def _render(self):
        self._render_text()
        self._render_sense_list()

    def _render_text(self):
        pass

    def _render_sense_list(self):
        senses = self._senses[self._current]
        definitions = self._definitions[self._current]
        label = self._labels[self._current]
        predicted_sense = self._predicted_senses[self._current]
        senses_content = "<ul>"
        label_style = "style=\"color:green;\""
        predicted_style = "style=\"color:yellow\""
        for i, (sense, definition) in enumerate(zip(senses, definitions)):
            is_label = sense == label
            is_predicted = sense == predicted_sense
            style = label_style if is_label else predicted_style if is_predicted else ''
            input_key = self.INPUT_KEYS[i] if i < len(self.INPUT_KEYS) else ""
            senses_content += f"<li {style}>[{input_key}]  {sense}:  {definition}</li>"
        if label is not None and label not in senses:
            senses_content += f"<li {label_style}>{label}</li>"
        senses_content += "</ul>"
        self._sense_list.setText(senses_content)

    def _prev_term(self):
        self._current = max(0, self._current - 1)
        self._render()

    def _next_term(self):
        self._current = min(len(self._tokens) - 1, self._current + 1)
        self._render()
    
    def get_labels(self):
        return self._labels
    
    def set_text(self, title, tokens, senses, definitions, labels, predicted_senses):
        self._current = 0
        self._tokens = tokens
        self._senses = senses
        self._definitions = definitions
        self._labels = labels
        self._predicted_senses = predicted_senses
        self._title.setText(f"<h1>{title}</h1>")
        self._render()
    
    def keyPressEvent(self, event):
        if event.key() == 16777237:  # Down
            self.next_signal.emit()
            return
        elif event.key() == 16777235:  # Up
            self.prev_signal.emit()
            return
        elif event.key() == 16777234:  # Left
            self._prev_term()
        elif event.key() == 16777236:  # Right
            self._next_term()
        elif event.key() == Qt.Key_Return:  # Enter
            if self._sense_input.isVisible():
                input_text = self._sense_input.text()
                self._labels[self._current] = None if len(input_text) == 0 else input_text
                self._sense_input.setVisible(False)
                self._sense_input.clearFocus()
            else:
                self._sense_input.setVisible(True)
                self._sense_input.setFocus()
        elif event.key() == 16777219:  # Backspace
            self._labels[self._current] = None
            self._render()
        elif event.text() in self.INPUT_KEYS:
            input_index = self.INPUT_KEYS.index(event.text())
            self._labels[self._current] = self._senses[self._current][input_index]
        self._render()