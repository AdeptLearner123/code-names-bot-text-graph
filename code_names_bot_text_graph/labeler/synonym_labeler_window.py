from .labeler_window import LabelerWindow

class SynonymLabelerWindow(LabelerWindow):
    def _render_text(self):
        text_content = f"<p>{self._definition}</p>"
        text_content += "<ul>"
        for i, token in enumerate(self._tokens):
            token_text = f"{token}"
            if i == self._current:
                token_text = f"<u>{token_text}</u>"
            text_content += f"<li>{token_text}</li>"
        text_content += "</ul>"

        self._text.setText(text_content)

    def get_tokens(self):
        return self._tokens

    def set_text(self, title, definition, tokens, senses, definitions, labels, predicted_senses):
        self._definition = definition
        super().set_text(title, tokens, senses, definitions, labels, predicted_senses)