import time
from pathlib import Path

import torch
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QThread, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QSplitter, QGroupBox, QHBoxLayout, QPushButton, QFormLayout, \
    QProgressBar, QGridLayout, QTabWidget, QTextEdit, QHeaderView, QTableView
from pyqtgraph import PlotWidget

from core.training.training_worker import TrainingWorker
from ui.widgets.metric_table_model import MetricsTableModel


class MonitorTab(QWidget):
    """Вкладка для запуска обучения и мониторинга метрик в реальном времени."""

    training_started = pyqtSignal()
    training_paused = pyqtSignal()
    training_resumed = pyqtSignal()
    training_stopped = pyqtSignal()
    training_finished = pyqtSignal()
    load_model_request = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._epoch_offset = 0
        self._elapsed_time = 0
        self._start_time = None
        self._pause_start_time = None
        self._is_training = False
        self._is_paused = False
        self._selected_metrics = ["Accuracy"]
        self._training_worker: TrainingWorker = None
        self._training_thread: QThread = None
        self._training_data = None
        self.trained_model = None
        self.trained_input_shape = None

        self._metrics_buffer = []
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._flush_metrics)
        self._update_timer.start(500)

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
        self.start_btn.setEnabled(False)

        self.pause_btn = QPushButton("⏸️ Пауза")
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.pause_btn.setEnabled(False)

        self.stop_btn = QPushButton("⏹️ Стоп")
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.stop_btn.setEnabled(False)

        self.load_weights_btn = QPushButton("📂 Загрузить веса (.pth)")
        self.load_weights_btn.clicked.connect(self._on_load_weights)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.load_weights_btn)

        progress_layout = QFormLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addRow(self.progress_bar)

        self.epoch_label = QLabel("Эпоха: 0/0")
        self.batch_label = QLabel("Batch: 0/0")
        self.time_label = QLabel("⏱️ 00:00 | ETA: --:--")
        progress_layout.addRow(self.epoch_label)
        progress_layout.addRow(self.batch_label)
        progress_layout.addRow(self.time_label)

        layout.addLayout(progress_layout)

        return group

    def _create_charts_area(self):
        """Создание области с графиками."""
        group = QGroupBox("📈 Графики")
        self.charts_layout = QGridLayout()
        group.setLayout(self.charts_layout)

        self.loss_plot = PlotWidget()
        self.loss_plot.setTitle("Loss")
        self.loss_plot.setLabel('left', 'Loss')
        self.loss_plot.setLabel('bottom', 'Эпоха')
        self.loss_plot.addLegend()
        self.loss_plot.showGrid(x=True, y=True, alpha=0.3)
        self.loss_plot.enableAutoRange(x=True, y=True)
        self.loss_plot_train = self.loss_plot.plot(pen='r', name='Train')
        self.loss_plot_test = self.loss_plot.plot(pen='b', name='Test')

        self.acc_plot = PlotWidget()
        self.acc_plot.setTitle("Accuracy")
        self.acc_plot.setLabel('left', 'Accuracy')
        self.acc_plot.setLabel('bottom', 'Эпоха')
        self.acc_plot.addLegend()
        self.acc_plot.showGrid(x=True, y=True, alpha=0.3)
        self.acc_plot.enableAutoRange(x=True, y=False)
        self.acc_plot.setYRange(0, 1)
        self.acc_plot_train = self.acc_plot.plot(pen='r', name='Train')
        self.acc_plot_test = self.acc_plot.plot(pen='b', name='Test')
        self.acc_plot.setVisible(True)

        self.charts_layout.addWidget(self.loss_plot, 0, 0)
        self.charts_layout.addWidget(self.acc_plot, 0, 1)

        self.charts_layout.setColumnStretch(0, 1)
        self.charts_layout.setColumnStretch(1, 1)

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

        self.metrics_model = MetricsTableModel(["Эпоха", "Train Loss", "Test Loss", "Train Accuracy", "Test Accuracy"])
        self.metrics_table = QTableView()
        self.metrics_table.setModel(self.metrics_model)
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.metrics_table.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.metrics_table.setAlternatingRowColors(False)
        self.metrics_table.setShowGrid(False)
        self.metrics_table.setSortingEnabled(False)

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

    def start_training(self, training_data):
        if self._is_training:
            return

        if self.history["loss"]["x"]:
            self._epoch_offset = self.history["loss"]["x"][-1]
        else:
            self._epoch_offset = 0
        training_data["epoch_offset"] = self._epoch_offset

        self._training_data = training_data
        self._training_worker = TrainingWorker(training_data)
        self._training_thread = QThread()
        self._training_worker.moveToThread(self._training_thread)

        self._training_worker.training_started.connect(self._on_training_started)
        self._training_worker.training_finished.connect(self._on_training_finished)
        self._training_worker.training_stopped.connect(self._on_training_stopped)
        self._training_worker.training_paused.connect(self._on_training_paused)
        self._training_worker.training_resumed.connect(self._on_training_resumed)
        self._training_worker.training_error.connect(self._on_training_error)
        self._training_worker.epoch_started.connect(self._on_epoch_started)
        self._training_worker.epoch_completed.connect(self._on_epoch_completed)
        self._training_worker.log_message.connect(self.append_log)
        self._training_worker.epoch_progress_updated.connect(self._on_update_epoch_progress)
        self._training_worker.batch_progress_updated.connect(self._on_batch_progress_updated)

        self._training_thread.started.connect(self._training_worker.run)
        self._training_thread.start()

        self._is_training = True
        self._is_paused = False

    def _connect_signals(self):
        """Подключение сигналов для обработки событий обучения."""
        pass

    def _on_training_started(self):
        """Обучение началось."""
        self._start_time = time.time()
        self._elapsed_time = 0
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.load_weights_btn.setEnabled(False)
        self.append_log("Обучение запущено")
        self.training_started.emit()

    def _on_training_finished(self):
        """Обучение завершено."""
        self._cleanup_training()
        if self._training_data and "model" in self._training_data:
            self.trained_model = self._training_data["model"]
            self.trained_input_shape = self._training_data["input_shape"]
            self.trained_model.eval()
        self.append_log("Обучение завершено")
        self.training_finished.emit()

    def _on_training_stopped(self):
        """Обучение остановлено."""
        self._cleanup_training()
        if self._training_data and "model" in self._training_data:
            self.trained_model = self._training_data["model"]
            self.trained_input_shape = self._training_data["input_shape"]
            self.trained_model.eval()
        self.append_log("Обучение остановлено")
        self.training_stopped.emit()

    def _on_training_paused(self):
        """Обучение на паузе."""
        self._is_paused = True
        self._pause_start_time = time.time()
        self.pause_btn.setText("▶️ Продолжить")
        self.append_log("Обучение на паузе")
        self.training_paused.emit()

    def _on_training_resumed(self):
        """Обучение продолжено."""
        self._is_paused = False
        self._start_time += time.time() - self._pause_start_time
        self.pause_btn.setText("⏸️ Пауза")
        self.append_log("Обучение продолжено")
        self.training_resumed.emit()

    def _on_training_error(self, error_msg: str):
        """Ошибка обучения."""
        self._cleanup_training()
        self.append_log(error_msg)

    def _on_epoch_started(self):
        """Начало эпохи."""
        pass

    def _on_epoch_completed(self, metrics: dict):
        """Завершение эпохи - обновление графиков и таблицы."""
        metrics["epoch"] += self._epoch_offset
        self.update_metrics(metrics)

    def _flush_metrics(self):
        if not self._metrics_buffer:
            return

        v_scroll = self.metrics_table.verticalScrollBar()
        was_at_bottom = v_scroll.value() > v_scroll.maximum() - 2

        self.metrics_table.setUpdatesEnabled(False)
        self.metrics_model.add_rows(self._metrics_buffer)
        self.metrics_table.setUpdatesEnabled(True)

        if was_at_bottom:
            self.metrics_table.scrollToBottom()

        self._metrics_buffer.clear()

    def _cleanup_training(self):
        """Очистка после завершения обучения."""
        self._is_training = False
        self._is_paused = False
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.load_weights_btn.setEnabled(True)
        self.pause_btn.setText("⏸️ Пауза")

        if self._training_thread and self._training_thread.isRunning():
            self._training_thread.quit()
            self._training_thread.wait(1000)

        self._training_thread = None
        self._training_worker = None

    def _on_load_weights(self):
        """Сигнла для загрузки предобученных весов в текущую архитектуру."""
        self.load_model_request.emit()

    def _on_start_clicked(self):
        """Обработка кнопки Старт."""
        if self._is_training and not self._is_paused:
            return

        if self._is_paused:
            if self._training_worker:
                self._training_worker.resume()
        else:
            if self._training_data:
                self.start_training(self._training_data)

    def _on_pause_clicked(self):
        """Обработка кнопки Пауза."""
        if not self._is_training:
            return

        if self._training_worker:
            if self._is_paused:
                self._training_worker.resume()
            else:
                self._training_worker.pause()

    def _on_stop_clicked(self):
        """Обработка кнопки Стоп."""
        if not self._is_training:
            return

        if self._training_worker:
            self._training_worker.stop()

    def _on_clear_log_clicked(self):
        """Очистка лога."""
        self.log_console.clear()
        self.append_log("Лог очищен")

    def _on_clear_table_clicked(self):
        """Очистка таблицы метрик."""
        self.metrics_model.reset_data()
        self.append_log("Таблица метрик очищена")

    def append_log(self, message: str):
        """Добавление сообщения в лог."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_console.append(f"[{timestamp}] {message}")
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def _on_update_epoch_progress(self, current: int, total: int):
        """Обновление прогресс-бара и меток эпох."""

        display_current = self._epoch_offset + current
        display_total = self._epoch_offset + total

        self.progress_bar.setValue(display_current)
        self.progress_bar.setMaximum(display_total)
        self.epoch_label.setText(f"Эпоха: {display_current}/{display_total}")

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

    def _on_batch_progress_updated(self, current: int, total: int):
        """Обновление метки текущего батча внутри эпохи."""
        self.batch_label.setText(f"Batch: {current}/{total}")

    def update_metrics(self, metrics: dict):
        """Обновление графиков и таблицы метрик."""
        table_data = {
            "Эпоха": metrics["epoch"],
            "Train Loss": metrics["train_loss"],
            "Test Loss": metrics["test_loss"]
        }
        self._update_loss_plot(metrics["epoch"], metrics["train_loss"], metrics["test_loss"])

        if "Accuracy" in self._selected_metrics:
            table_data["Train Accuracy"] = metrics["train_accuracy"]
            table_data["Test Accuracy"] = metrics["test_accuracy"]
            self._update_acc_plot(metrics["epoch"], metrics["train_accuracy"], metrics["test_accuracy"])
        if "Precision" in self._selected_metrics:
            table_data["Test Precision"] = metrics["precision"]
        if "Recall" in self._selected_metrics:
            table_data["Test Recall"] = metrics["recall"]
        if "F1-Score" in self._selected_metrics:
            table_data["Test F1-Score"] = metrics["f1_score"]

        self._metrics_buffer.append(table_data)

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

    def reset_ui_state(self):
        """Сброс графиков, таблицы, логов и прогресса без потери модели и training_data."""
        self._is_training = False
        self._is_paused = False
        self._start_time = None
        self._pause_start_time = None
        self._elapsed_time = 0
        self._epoch_offset = 0

        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸️ Пауза")
        self.stop_btn.setEnabled(False)

        self.progress_bar.setValue(0)
        self.epoch_label.setText("Эпоха: 0/0")
        self.batch_label.setText("Batch: 0/0")
        self.time_label.setText("⏱️ 00:00 | ETA: --:--")

        self.loss_plot_train.setData([], [])
        self.loss_plot_test.setData([], [])
        self.acc_plot_train.setData([], [])
        self.acc_plot_test.setData([], [])

        self.loss_plot.enableAutoRange(x=True, y=True)
        self.acc_plot.enableAutoRange(x=True, y=False)
        self.acc_plot.setYRange(0, 1)

        self.metrics_model.reset_data()
        self.log_console.clear()

        self.history = {
            "loss": {"x": [], "train": [], "test": []},
            "acc": {"x": [], "train": [], "test": []},
            "precision": {"x": [], "test": []},
            "recall": {"x": [], "test": []},
            "f1": {"x": [], "test": []},
        }

    def reset(self):
        """Сброс состояния вкладки."""
        self.reset_ui_state()
        self.trained_model = None
        self.trained_input_shape = None
        self.load_weights_btn.setEnabled(True)

    def set_metrics_config(self, metrics: list):
        """Установить конфигурацию отображаемых метрик"""
        self._selected_metrics = metrics
        self._reconfigure_ui()
        self.append_log(f"Метрики настроены: {', '.join(metrics)}")

    def _reconfigure_ui(self):
        """Перенастроить UI под выбранные метрики"""
        has_accuracy = "Accuracy" in self._selected_metrics
        self.acc_plot.setVisible(has_accuracy)
        self.charts_layout.setColumnStretch(1, int(has_accuracy))

        columns = ["Эпоха", "Train Loss", "Test Loss"]
        if "Accuracy" in self._selected_metrics:
            columns.extend(["Train Accuracy", "Test Accuracy"])
        if "Precision" in self._selected_metrics:
            columns.extend(["Test Precision"])
        if "Recall" in self._selected_metrics:
            columns.extend(["Test Recall"])
        if "F1-Score" in self._selected_metrics:
            columns.extend(["Test F1-Score"])

        self.metrics_model.set_headers(columns)

    def load_model(self, model, path, input_node):
        """Загрузка предобученных весов в текущую архитектуру."""
        try:
            if model is None:
                self.append_log("Текущий граф невалиден. Валидируйте архитектуру перед загрузкой весов.")
                return

            self.reset_ui_state()

            state_dict = torch.load(path, map_location="cpu")
            model.load_state_dict(state_dict)
            model.eval()
            model.cpu()

            self.trained_model = model
            if input_node:
                raw = input_node.get_property("input_shape")
                self.trained_input_shape = tuple(int(x.strip()) for x in raw.split(",") if x.strip())

            if self._training_data is not None:
                self._training_data["model"] = model
                if self.trained_input_shape:
                    self._training_data["input_shape"] = self.trained_input_shape
            if self._training_data is not None:
                self.start_btn.setEnabled(True)

            self.append_log(f"Веса успешно загружены: {Path(path).name}")
        except Exception as e:
            self.append_log(f"Ошибка загрузки весов: {str(e)}")

    def refresh_training_data(self, training_tab):
        """Обновить training_data после загрузки весов"""
        if not self._training_data:
            return
        model = self._training_data.get("model")
        if model is None:
            return
        # Получаем свежие параметры обучения (эпохи, батч, lr и т.д.)
        fresh_data = training_tab.get_training_object(model)
        if fresh_data:
            self._training_data.update(fresh_data)
            self.append_log("Оптимизатор и параметры обучения обновлены")

    def set_training_data(self, training_data: dict):
        """Установить данные для обучения."""
        self.reset()
        self._training_data = training_data
        self.start_btn.setEnabled(True)
        self.append_log("Данные для обучения загружены")

    def is_training_active(self):
        """Проверка, активно ли обучение."""
        return self._is_training and not self._is_paused

    def is_training_running(self):
        """Проверка, запущен ли процесс обучения (включая паузу)."""
        return self._is_training
