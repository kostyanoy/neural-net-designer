import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QSplitter, QGroupBox, QHBoxLayout, QPushButton, QFormLayout, \
    QProgressBar, QGridLayout, QTabWidget, QTextEdit, QTableWidget, QHeaderView, QTableWidgetItem, QSizePolicy
from pyqtgraph import PlotWidget


class MonitorTab(QWidget):
    """Вкладка для запуска обучения и мониторинга метрик в реальном времени."""

    training_started = pyqtSignal()
    training_paused = pyqtSignal()
    training_resumed = pyqtSignal()
    training_stopped = pyqtSignal()
    training_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._elapsed_time = 0
        self._start_time = None
        self._pause_start_time = None
        self._is_training = False
        self._is_paused = False
        self.selected_metrics = ["Accuracy"]

        self._init_ui()
        self._connect_signals()

        self.history = {
            "loss": {"x": [], "train": [], "test": []},
            "acc": {"x": [], "train": [], "test": []},
            "precision": {"x": [], "test": []},
            "recall": {"x": [], "test": []},
            "f1": {"x": [], "test": []},
        }

    def _init_ui(self):
        """Инициализация всех UI элементов."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)
        layout.setStretchFactor(control_panel, 0)

        charts_area = self._create_charts_area()
        logs_area = self._create_logs_area()
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(charts_area)
        splitter.addWidget(logs_area)
        layout.addWidget(splitter)
        layout.setStretchFactor(splitter, 1)

    def _create_control_panel(self) -> QGroupBox:
        """Создание панели управления обучением."""
        group = QGroupBox("🎮 Управление обучением")
        layout = QHBoxLayout()
        group.setLayout(layout)

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
        progress_layout.addRow(self.epoch_label)
        progress_layout.addRow(self.time_label)

        layout.addLayout(progress_layout)

        return group

    def _create_charts_area(self):
        """Создание области с графиками."""
        group = QGroupBox("📈 Графики")
        layout = QGridLayout()
        group.setLayout(layout)

        self.loss_plot = PlotWidget()
        self.loss_plot.setTitle("Loss")
        self.loss_plot.setLabel('left', 'Loss')
        self.loss_plot.setLabel('bottom', 'Эпоха')
        self.loss_plot.addLegend()
        self.loss_plot.showGrid(x=True, y=True, alpha=0.3)
        self.loss_plot_train = self.loss_plot.plot(pen='r', name='Train')
        self.loss_plot_test = self.loss_plot.plot(pen='b', name='Test')

        self.acc_plot = PlotWidget()
        self.acc_plot.setTitle("Accuracy")
        self.acc_plot.setLabel('left', 'Accuracy')
        self.acc_plot.setLabel('bottom', 'Эпоха')
        self.acc_plot.addLegend()
        self.acc_plot.showGrid(x=True, y=True, alpha=0.3)
        self.acc_plot_train = self.acc_plot.plot(pen='r', name='Train')
        self.acc_plot_test = self.acc_plot.plot(pen='b', name='Test')
        self.acc_plot.setVisible(True)

        layout.addWidget(self.loss_plot, 0, 0)
        layout.addWidget(self.acc_plot, 0, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        return group

    def _create_logs_area(self):
        """Создание области с логами и таблицей метрик."""
        group = QGroupBox("📋 Логи и метрики")
        layout = QVBoxLayout()
        group.setLayout(layout)

        self.logs_tab_widget = QTabWidget()

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)

        log_btn_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("🗑️ Очистить")
        self.clear_log_btn.clicked.connect(self._on_clear_log_clicked)
        log_btn_layout.addWidget(self.clear_log_btn)
        log_btn_layout.addStretch()

        log_container = QWidget()
        log_layout = QVBoxLayout()
        log_container.setLayout(log_layout)
        log_layout.addWidget(self.log_console)
        log_layout.addLayout(log_btn_layout)

        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(5)
        self.metrics_table.setHorizontalHeaderLabels([
            "Эпоха", "Loss", "Test Loss", "Accuracy", "Test Accuracy"
        ])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.metrics_table.setAlternatingRowColors(True)

        table_btn_layout = QHBoxLayout()
        self.clear_table_btn = QPushButton("🗑️ Очистить")
        self.clear_table_btn.clicked.connect(self._on_clear_table_clicked)
        table_btn_layout.addWidget(self.clear_table_btn)
        table_btn_layout.addStretch()

        table_container = QWidget()
        table_layout = QVBoxLayout()
        table_container.setLayout(table_layout)
        table_layout.addWidget(self.metrics_table)
        table_layout.addLayout(table_btn_layout)

        self.logs_tab_widget.addTab(log_container, "📝 Логи")
        self.logs_tab_widget.addTab(table_container, "📊 Метрики")

        layout.addWidget(self.logs_tab_widget)

        return group

    def _connect_signals(self):
        # TODO обработать training_finished и т.д.
        pass

    def _on_start_clicked(self):
        """Обработка кнопки Старт."""
        if self._is_training and not self._is_paused:
            return

        self._is_training = True
        self._is_paused = False
        self._start_time = time.time()
        self._end_time = 0

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        self.append_log("Обучение запущено")
        self.training_started.emit()

    def _on_pause_clicked(self):
        """Обработка кнопки Пауза."""
        if not self._is_training:
            return

        if not self._is_paused:
            self._pause_start_time = time.time()
            self._is_paused = True
            self.pause_btn.setText("▶️ Продолжить")
            self.append_log("Обучение на паузе")
            self.training_paused.emit()
        else:
            pause_duration = int(time.time() - self._pause_start_time)
            self._start_time += pause_duration
            self._pause_start_time = None
            self._is_paused = False
            self.pause_btn.setText("⏸️ Пауза")
            self.append_log("Обучение продолжено")
            self.training_resumed.emit()

    def _on_stop_clicked(self):
        """Обработка кнопки Стоп."""
        if not self._is_training:
            return

        self._is_training = False
        self._is_paused = False
        self._start_time = None

        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸️ Пауза")
        self.stop_btn.setEnabled(False)

        self.append_log("Обучение остановлено")
        self.training_stopped.emit()

    def _on_clear_log_clicked(self):
        """Очистка лога."""
        self.log_console.clear()
        self.append_log("Лог очищен")

    def _on_clear_table_clicked(self):
        """Очистка таблицы метрик."""
        self.metrics_table.setRowCount(0)
        self.append_log("Таблица метрик очищена")

    def append_log(self, message: str):
        """Добавление сообщения в лог."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_console.append(f"[{timestamp}] {message}")
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def update_progress(self, current: int, total: int):
        """Обновление прогресс-бара и меток эпох."""
        self.progress_bar.setValue(current)
        self.progress_bar.setMaximum(total)
        self.epoch_label.setText(f"Эпоха: {current}/{total}")

        if self._start_time and not self._is_paused:
            elapsed = int(time.time() - self._start_time)
            self._elapsed_time = elapsed
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(self._elapsed_time))

            if current > 0:
                avg_time = elapsed / current
                remaining = avg_time * (total - current)
                eta_str = time.strftime("%H:%M:%S", time.gmtime(remaining))
            else:
                eta_str = "--:--"

            self.time_label.setText(f"⏱️ {elapsed_str} | ETA: {eta_str}")

    def update_metrics(self, metrics: dict):
        """Обновление графиков и таблицы метрик."""
        metric_values = []

        epoch = metrics.get("epoch", 0)
        loss = metrics.get("loss", 0)
        test_loss = metrics.get("test_loss", 0)
        metric_values.extend([epoch, loss, test_loss])
        self._update_loss_plot(epoch, loss, test_loss)

        if "Accuracy" in self.selected_metrics:
            acc = metrics.get("accuracy", 0)
            test_acc = metrics.get("test_accuracy", 0)
            metric_values.extend([acc, test_acc])
            self._update_acc_plot(epoch, acc, test_acc)

        if "Precision" in self.selected_metrics:
            precision = metrics.get("precision", 0)
            metric_values.append(precision)
        if "Recall" in self.selected_metrics:
            recall = metrics.get("recall", 0)
            metric_values.append(recall)
        if "F1-Score" in self.selected_metrics:
            f1 = metrics.get("f1-score", 0)
            metric_values.append(f1)

        self._add_metrics_row(metric_values)

    def _update_loss_plot(self, epoch: int, loss: float, test_loss: float):
        """Обновление графика Loss."""
        self.history["loss"]["x"].append(epoch)
        self.history["loss"]["train"].append(loss)
        self.history["loss"]["test"].append(test_loss)

        self.loss_plot_train.setData(self.history["loss"]["x"], self.history["loss"]["train"])
        self.loss_plot_test.setData(self.history["loss"]["x"], self.history["loss"]["test"])

    def _update_acc_plot(self, epoch: int, acc: float, test_acc: float):
        """Обновление графика Accuracy."""
        if not self.acc_plot.isVisible():
            return

        self.history["acc"]["x"].append(epoch)
        self.history["acc"]["train"].append(acc)
        self.history["acc"]["test"].append(test_acc)

        self.acc_plot_train.setData(self.history["acc"]["x"], self.history["acc"]["train"])
        self.acc_plot_test.setData(self.history["acc"]["x"], self.history["acc"]["test"])

    def _add_metrics_row(self, metric_values: list):
        """Добавление строки в таблицу метрик."""
        row = self.metrics_table.rowCount()
        self.metrics_table.insertRow(row)

        for i, metric in enumerate(self.selected_metrics):
            metric_value = metric_values[i]
            self.metrics_table.setItem(row, i, QTableWidgetItem(f"{metric_value:.4f}"))
        self.metrics_table.scrollToBottom()

    def setup_metrics(self, metrics_list: list):
        """Настройка таблицы под выбранные метрики."""
        columns = ["Эпоха", "Loss", "Test Loss"]

        if "Accuracy" in metrics_list:
            columns.extend(["Accuracy", "Test Accuracy"])
            self.acc_plot.setVisible(True)
        else:
            self.acc_plot.setVisible(False)

        self.metrics_table.setColumnCount(len(columns))
        self.metrics_table.setHorizontalHeaderLabels(columns)
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def reset(self):
        """Сброс состояния вкладки."""
        self._is_training = False
        self._is_paused = False
        self._start_time = None
        self._elapsed_time = 0

        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸️ Пауза")
        self.stop_btn.setEnabled(False)

        self.progress_bar.setValue(0)
        self.epoch_label.setText("Эпоха: 0/0")
        self.time_label.setText("⏱️ 00:00 | ETA: --:--")

        self.loss_plot_train.setData([], [])
        self.loss_plot_test.setData([], [])
        self.acc_plot_train.setData([], [])
        self.acc_plot_test.setData([], [])

        self.metrics_table.setRowCount(0)
        self.log_console.clear()

        self.history = {
            "loss": {"x": [], "train": [], "test": []},
            "acc": {"x": [], "train": [], "test": []},
            "precision": {"x": [], "test": []},
            "recall": {"x": [], "test": []},
            "f1": {"x": [], "test": []},
        }

    def set_metrics_config(self, metrics: list):
        """Установить конфигурацию отображаемых метрик"""
        self.selected_metrics = metrics
        self._reconfigure_ui()

    def _reconfigure_ui(self):
        """Перенастроить UI под выбранные метрики"""
        has_accuracy = "Accuracy" in self.selected_metrics
        self.acc_plot.setVisible(has_accuracy)

        columns = ["Эпоха", "Loss", "Test Loss"]
        if "Accuracy" in self.selected_metrics:
            columns.extend(["Accuracy", "Test Accuracy"])
        if "Precision" in self.selected_metrics:
            columns.extend(["Test Precision"])
        if "Recall" in self.selected_metrics:
            columns.extend(["Test Recall"])
        if "F1-Score" in self.selected_metrics:
            columns.extend(["Test F1-Score"])

        self.metrics_table.setColumnCount(len(columns))
        self.metrics_table.setHorizontalHeaderLabels(columns)
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.metrics_table.setRowCount(0)


