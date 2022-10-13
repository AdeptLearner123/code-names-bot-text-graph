from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt

class LabelerWindow(QtWidgets.QWidget):
    next_signal = Signal()
    prev_signal = Signal()

    INPUT_KEYS = "0123456789abcdefghijklmnopqrstuvwxyz"

    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self._add_title()
        self._add_sentence()
        self._add_sense_list()
        self._add_sense_input()
    
    def _add_title(self):
        self.title = QtWidgets.QLabel()
        self.layout.addWidget(self.title)
    
    def _add_sentence(self):
        sentence_widget = QtWidgets.QLabel()
        self.layout.addWidget(sentence_widget)
        self.sentence_widget = sentence_widget

    def _add_sense_list(self):
        sense_list = QtWidgets.QLabel()
        self.layout.addWidget(sense_list)
        self.sense_list = sense_list
    
    def _add_sense_input(self):
        sense_input = QtWidgets.QLineEdit()
        self.layout.addWidget(sense_input)
        self.sense_input = sense_input
        self.sense_input.setVisible(False)

    def _render(self):
        sentence_content = ""
        for i, token in enumerate(self.tokens):
            sentence_content += f"<u>{token}</u>" if i == self.current else token
            sentence_content += " "
        self.sentence_widget.setText(sentence_content)

        senses = self.senses[self.current]
        definitions = self.definitions[self.current]
        label = self.labels[self.current]
        senses_content = "<ul>"
        label_style = "style=\"color:green;\""
        for i, (sense, definition) in enumerate(zip(senses, definitions)):
            is_label = sense == label
            senses_content += f"<li {label_style if is_label else ''}>[{self.INPUT_KEYS[i]}]  {sense}:  {definition}</li>"
        if label is not None and label not in senses:
            senses_content += f"<li {label_style}>{label}</li>"
        senses_content += "</ul>"
        self.sense_list.setText(senses_content)

    def _prev_term(self):
        self.current = max(0, self.current - 1)
        self._render()

    def _next_term(self):
        self.current = min(len(self.tokens) - 1, self.current + 1)
        self._render()
    
    def get_labels(self):
        return self.labels
    
    def set_text(self, title, tokens, senses, definitions, labels):
        self.current = 0
        self.tokens = tokens
        self.senses = senses
        self.definitions = definitions
        self.labels = labels
        self.title.setText(f"<h1>{title}</h1>")
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
            if self.sense_input.isVisible():
                input_text = self.sense_input.text()
                self.labels[self.current] = None if len(input_text) == 0 else input_text
                self.sense_input.setVisible(False)
                self.sense_input.clearFocus()
            else:
                self.sense_input.setVisible(True)
                self.sense_input.setFocus()
        elif event.text() in self.INPUT_KEYS:
            input_index = self.INPUT_KEYS.index(event.text())
            self.labels[self.current] = self.senses[self.current][input_index]
        self._render()