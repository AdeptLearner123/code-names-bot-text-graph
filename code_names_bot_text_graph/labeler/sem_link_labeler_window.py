from .labeler_window import LabelerWindow

class SemLinkLabelerWindow(LabelerWindow):
    def _render_text(self):
        token = self._tokens[0]
        text_content = f"<p>{token}</p>"
        text_content += "<ul>"
        for example in self._examples:
            text_content += f"<li>{example}</li>"
        text_content += "<ul>"
        self._text.setText(text_content)

    def get_label(self):
        return self._labels[0]

    def set_text(self, title, token, senses, definitions, label, predicted_sense, examples):
        self._examples = examples
        super().set_text(title, [token], [senses], [definitions], [label], [predicted_sense])