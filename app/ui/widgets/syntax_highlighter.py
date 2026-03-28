from typing import Tuple

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса для Python кода."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._formats = {}
        self._rules: list[Tuple[QRegularExpression, QTextCharFormat]] = []

        self._init_formats()
        self._init_rules()

    def _init_formats(self):
        """Инициализация форматов для разных элементов кода."""
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # Синий
        keyword_format.setFontWeight(QFont.Bold)
        self._formats["keyword"] = keyword_format

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#4EC9B0"))  # Бирюзовый
        self._formats["builtin"] = builtin_format

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Оранжевый
        self._formats["string"] = string_format

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Зелёный
        comment_format.setFontItalic(True)
        self._formats["comment"] = comment_format

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))  # Светло-зелёный
        self._formats["number"] = number_format

        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))  # Бирюзовый
        class_format.setFontWeight(QFont.Bold)
        self._formats["class"] = class_format

        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))  # Жёлтый
        self._formats["function"] = function_format

        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#C586C0"))  # Фиолетовый
        self._formats["decorator"] = decorator_format

    def _init_rules(self):
        """Инициализация правил для подсветки."""

        # Ключевые слова
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "finally", "for", "from",
            "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
            "or", "pass", "raise", "return", "try", "while", "with", "yield",
            "True", "False", "None"
        ]
        for kw in keywords:
            self._rules.append((
                QRegularExpression("\\b" + kw + "\\b"),
                self._formats["keyword"]
            ))

        # Встроенные функции
        builtins = [
            "print", "len", "range", "str", "int", "float", "list", "dict",
            "set", "tuple", "open", "file", "input", "type", "isinstance",
            "super", "getattr", "setattr", "hasattr", "iter", "next", "map",
            "filter", "zip", "enumerate", "sorted", "reversed", "sum", "min", "max"
        ]
        for bi in builtins:
            self._rules.append((
                QRegularExpression("\\b" + bi + "\\b"),
                self._formats["builtin"]
            ))

        # Числа
        self._rules.append((
            QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"),
            self._formats["number"]
        ))

        # Классы и функции
        self._rules.append((
            QRegularExpression("\\bclass\\s+(\\w+)"),
            self._formats["class"]
        ))
        self._rules.append((
            QRegularExpression("\\bdef\\s+(\\w+)"),
            self._formats["function"]
        ))

        # Декораторы
        self._rules.append((
            QRegularExpression("@\\w+"),
            self._formats["decorator"]
        ))

        # Комментарии
        self._rules.append((
            QRegularExpression("#[^\n]*"),
            self._formats["comment"]
        ))

        # Строки
        # Тройные кавычки
        self._rules.append((
            QRegularExpression("\"\"\".*?\"\"\""),
            self._formats["string"]
        ))
        self._rules.append((
            QRegularExpression("\'\'\'.*?\'\'\'"),
            self._formats["string"]
        ))
        # Одинарные и двойные кавычки
        self._rules.append((
            QRegularExpression("\"(?:[^\"\\\\]|\\\\.)*\""),
            self._formats["string"]
        ))
        self._rules.append((
            QRegularExpression("\'(?:[^\'\\\\]|\\\\.)*\'"),
            self._formats["string"]
        ))

    def highlightBlock(self, text):
        """Применение подсветки к строке текста."""
        for expression, fmt in self._rules:
            match = expression.match(text)
            while match.hasMatch():
                index = match.capturedStart()
                length = match.capturedLength()

                if expression.captureCount() > 0:
                    index = match.capturedStart(1)
                    length = match.capturedLength(1)

                if index >= 0 and length > 0:
                    self.setFormat(index, length, fmt)

                match = expression.match(text, index + length)


