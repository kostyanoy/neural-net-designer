from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPlainTextEdit

from ui.widgets.syntax_highlighter import PythonSyntaxHighlighter


class CodeEditor(QPlainTextEdit):
    """Редактор кода с подсветкой синтаксиса Python."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_editor()
        self.highlighter = PythonSyntaxHighlighter(self.document())

    def _init_editor(self):
        """Настройка редактора."""
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        # self.line_number_area = LineNumberArea(self)

        self.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #1E1E1E;
                        color: #D4D4D4;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPlainTextEdit:focus {
                        border: 1px solid #007ACC;
                    }
                """)

    def set_code(self, code: str):
        """Установить код в редактор."""
        self.setPlainText(code)

    def get_code(self) -> str:
        """Получить код из редактора."""
        return self.toPlainText()

    def clear(self):
        """Очистить редактор."""
        self.clear()