from PySide6 import QtWidgets
from PySide6.QtCore import Signal

class LabelerWindow(QtWidgets.QWidget):
    next_signal = Signal()
    prev_signal = Signal()

    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self._add_title()
        self._add_sentence()
        self._add_sense_list()
    
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

    def _render(self):
        sentence_content = ""
        for i, token in enumerate(self.tokens):
            sentence_content += f"<u>{token}</u>" if i == self.current else token
            sentence_content += " "
        self.sentence_widget.setText(sentence_content)

        senses = self.senses[self.current]
        definitions = self.definitions[self.current]
        senses_content = "<ul>"
        for sense, definition in zip(senses, definitions):
            senses_content += f"<li>{sense}:{definition}</li>"
        senses_content += "</ul>"
        self.sense_list.setText(senses_content)

    def _prev_term(self):
        self.current = max(0, self.current - 1)
        self._render()

    def _next_term(self):
        self.current = min(len(self.tokens) - 1, self.current + 1)
        self._render()
     
    def set_text(self, title, tokens, senses, definitions):
        self.current = 0
        self.tokens = tokens
        self.senses = senses
        self.definitions = definitions
        self.title.setText(f"<h1>{title}</h1>")
        self._render()
    
    def keyPressEvent(self, event):
        if event.key() == 16777237:  # Down
            print("Down")
            self.next_signal.emit()
            return
        elif event.key() == 16777235:  # Up
            print("Up")
            self.prev_signal.emit()
            return
        elif event.key() == 16777234:  # Left
            self._prev_term()
        elif event.key() == 16777236:  # Right
            self._next_term()
        self._render()