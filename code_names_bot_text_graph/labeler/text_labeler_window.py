from .labeler_window import LabelerWindow

class TextLabelerWindow(LabelerWindow):
    def _render_text(self):
        sentence_content = ""
        for i, token in enumerate(self._tokens):
            sentence_content += f"<u>{token}</u>" if i == self._current else token
            sentence_content += " "
        self._text.setText(sentence_content)
