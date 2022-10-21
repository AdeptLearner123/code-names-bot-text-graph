from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt
from .labeler_window import LabelerWindow

class SemLinkLabelerWindow(LabelerWindow):
    def _render_text(self):
        text_content = f"<p>{self._definition}</p>"
        text_content += "<ul>"
        for i, (token, token_type) in enumerate(zip(self._tokens, self._token_types)):
            token_text = f"[{token_type}]  {token}"
            if i == self._current:
                token_text = f"<u>{token_text}</u>"
            text_content += f"<li>{token_text}</li>"

        self._text.setText(text_content)

    def get_tokens(self):
        return self._tokens
    
    def get_token_types(self):
        return self._token_types

    def set_text(self, title, definition, tokens, token_types, senses, definitions, labels, predicted_senses):
        self._definition = definition
        self._token_types = token_types
        super().set_text(title, tokens, senses, definitions, labels, predicted_senses)