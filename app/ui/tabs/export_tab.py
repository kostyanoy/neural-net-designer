from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QComboBox, QPushButton

from ui.dialog.message_boxes import choose_code_file, choose_weights_file
from ui.widgets.code_editor import CodeEditor


class ExportTab(QWidget):
    """Вкладка для экспорта кода модели и весов."""

    generate_code_requested = pyqtSignal(str) # type
    export_code_requested = pyqtSignal(str, str) # type, path
    export_weights_requested = pyqtSignal(str) # path

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_code_type = "model"
        self._generated_code = {
            "model": "",
            "dataset": "",
            "training_config": "",
            "training": "",
        }

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Инициализация всех UI элементов."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        control_group = self._create_control_panel()
        main_layout.addWidget(control_group)

        editor_group = self._create_editor_area()
        main_layout.addWidget(editor_group)
        main_layout.setStretchFactor(editor_group, 1)

        export_group = self._create_export_panel()
        main_layout.addWidget(export_group)

    def _create_control_panel(self) -> QGroupBox:
        """Панель выбора типа кода для генерации."""
        group = QGroupBox("📝 Тип кода")
        layout = QHBoxLayout()
        group.setLayout(layout)

        label = QLabel("Выберите тип кода для генерации:")
        layout.addWidget(label)

        self.code_type_combo = QComboBox()
        self.code_type_combo.addItems([
            "Код модели (класс)",
            "Код загрузки датасета",
            "Код настройки обучения",
            "Код обучения (train loop)"
        ])
        self.code_type_combo.setCurrentIndex(0)
        self.code_type_combo.currentIndexChanged.connect(self._on_code_type_changed)
        layout.addWidget(self.code_type_combo)

        layout.addStretch()

        self.generate_btn = QPushButton("Загрузить / Сгенерировать")
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        layout.addWidget(self.generate_btn)

        return group

    def _create_editor_area(self) -> QGroupBox:
        """Область с редактором кода."""
        group = QGroupBox("📄 Предпросмотр кода")
        layout = QVBoxLayout()
        group.setLayout(layout)

        self.code_editor = CodeEditor()
        self.code_editor.setPlaceholderText(
            "Нажмите «Загрузить / Сгенерировать» для получения кода...\n"
            "Вы можете редактировать код перед экспортом."
        )
        self.code_editor.textChanged.connect(self._on_code_changed)
        layout.addWidget(self.code_editor)

        info_layout = QHBoxLayout()
        self.status_label = QLabel("Готов к генерации")
        info_layout.addWidget(self.status_label)

        info_layout.addStretch()

        self.char_count_label = QLabel("0 символов")
        info_layout.addWidget(self.char_count_label)
        layout.addLayout(info_layout)

        return group

    def _create_export_panel(self) -> QGroupBox:
        """Панель кнопок экспорта."""
        group = QGroupBox("💾 Экспорт")
        layout = QHBoxLayout()
        group.setLayout(layout)

        self.export_code_btn = QPushButton("📁 Экспортировать код в файл")
        self.export_code_btn.clicked.connect(self._on_export_code_clicked)
        self.export_code_btn.setEnabled(False)
        layout.addWidget(self.export_code_btn)

        self.export_weights_btn = QPushButton("⚖️ Экспортировать веса модели (.pth)")
        self.export_weights_btn.clicked.connect(self._on_export_weights_clicked)
        # self.export_weights_btn.setEnabled(False)
        layout.addWidget(self.export_weights_btn)

        layout.addStretch()

        return group

    def _connect_signals(self):
        """Подключение внутренних сигналов."""
        pass

    def _on_code_type_changed(self, index: int):
        """Обработка изменения типа кода."""
        code_types = ["model", "dataset", "training_config", "training"]
        self.current_code_type = code_types[index]
        self.status_label.setText(f"Выбран тип: {self.code_type_combo.currentText()}")

        if self._generated_code.get(self._current_code_type):
            self.code_editor.set_code(self._generated_code[self._current_code_type])

    def _on_generate_clicked(self):
        """Обработка кнопки генерации кода."""
        self.status_label.setText("Генерация кода...")
        self.generate_code_requested.emit(self._current_code_type)

        # TODO генерирвоать код по шаблонам

    def _on_code_changed(self):
        """Обработка изменения кода в редакторе."""
        code = self.code_editor.get_code()
        char_count = len(code)
        self.char_count_label.setText(f"{char_count} символов")

        self.export_code_btn.setEnabled(char_count > 0)

    def _on_export_code_clicked(self):
        """Обработка кнопки экспорта кода."""
        code = self.code_editor.get_code()
        if not code:
            return

        file_types = {
            "model": "Python Files (*.py)",
            "dataset": "Python Files (*.py)",
            "training_config": "Python Files (*.py)",
            "training": "Python Files (*.py)"
        }

        default_name = {
            "model": "model.py",
            "dataset": "dataset.py",
            "training_config": "training_config.py",
            "training": "train.py"
        }

        path, _ = choose_code_file(self, default_name[self._current_code_type], file_types[self._current_code_type])
        if path:
            if not path.endswith(".py"):
                path += ".py"
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            self.status_label.setText(f"✅ Код сохранён: {path}")

    def _on_export_weights_clicked(self):
        """Обработка кнопки экспорта весов."""
        path, _ = choose_weights_file(self)
        if path:
            self.export_weights_requested.emit(path)
            # TODO: сохранение весов

    def set_generated_code(self, code_type: str, code: str):
        """Установить сгенерированный код."""
        if code_type in self._generated_code:
            self._generated_code[code_type] = code
            self.status_label.setText("✅ Код сгенерирован")
            if self._current_code_type == code_type:
                self.code_editor.set_code(code)

    def enable_weights_export(self, enabled: bool):
        """Активировать/деактивировать кнопку экспорта весов."""
        self.export_weights_btn.setEnabled(enabled)

    def get_current_code(self) -> str:
        """Получить текущий код из редактора."""
        return self.code_editor.get_code()

    def get_current_code_type(self) -> str:
        """Получить текущий тип кода."""
        return self._current_code_type















