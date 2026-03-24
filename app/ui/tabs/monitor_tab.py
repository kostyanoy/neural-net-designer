from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QSplitter, QGroupBox, QHBoxLayout, QPushButton, QFormLayout, \
    QProgressBar


class MonitorTab(QWidget):
    """Вкладка для запуска обучения и мониторинга метрик в реальном времени."""

    training_started = pyqtSignal()
    training_paused = pyqtSignal()
    training_resumed = pyqtSignal()
    training_stopped = pyqtSignal()

    update_progress = pyqtSignal(int, int) # cur_epoch / total_epochs
    update_metrics = pyqtSignal(dict)
    append_log = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.elapsed_time = 0
        self.start_time = None
        self._is_training = False
        self.is_paused = False
        self._init_ui()
        self._connect_signals()


    def _init_ui(self):
        """Инициализация всех UI элементов."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)

        charts_area = self._create_charts_area()
        logs_area = self._create_logs_area()
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(charts_area)
        splitter.addWidget(logs_area)
        layout.addWidget(splitter)

    def _create_control_panel(self) -> QGroupBox:
        """Создание панели управления обучением."""
        group = QGroupBox("🎮 Управление обучением")
        layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ Старт")
        self.start_btn.clicked.connect(self._on_start_clicked)

        self.pause_btn = QPushButton("⏸️ Пауза")
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.pause_btn.setEnabled(False)

        self.stop_btn = QPushButton("⏹️ Стоп")
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.stop_btn.setEnabled(False)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)

        progress_layout = QFormLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addRow(self.progress_bar)

        self.epoch_label = QLabel("Эпоха 0/0")
        self.time_label = QLabel("⏱️ 00:00 | ETA: --:--")


        return group

    def _create_charts_area(self):
        """Создание области с графиками."""
        pass
    def _create_logs_area(self):
        """Создание области с логами и таблицей метрик."""
        pass

    def _connect_signals(self):
        """Подключение внутренних сигналов."""
        pass

    def _on_start_clicked(self):
        """Обработка кнопки Старт."""
        pass

    def _on_pause_clicked(self):
        """Обработка кнопки Пауза."""
        pass

    def _on_stop_clicked(self):
        """Обработка кнопки Стоп."""
        pass

    def _on_clear_log_clicked(self):
        """Очистка лога."""
        pass

    def _on_clear_table_clicked(self):
        """Очистка таблицы метрик."""
        pass




