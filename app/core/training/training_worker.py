import time

import torch
from PyQt5.QtCore import QObject, pyqtSignal
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from torch import nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader


class TrainingWorker(QObject):
    """Рабочий поток для обучения модели."""
    epoch_started = pyqtSignal(int)
    epoch_completed = pyqtSignal(dict)  # metrics
    training_started = pyqtSignal()
    training_paused = pyqtSignal()
    training_resumed = pyqtSignal()
    training_stopped = pyqtSignal()
    training_finished = pyqtSignal(dict)  # final metrics
    training_error = pyqtSignal(str)
    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int, int)  # current, total

    def __init__(self, training_data):
        super().__init__()
        self._training_data = training_data
        self._is_running = False
        self._is_paused = False
        self._should_stop = False
        self._pause_lock = None
        self._best_loss = float("inf")
        self._history = {
            'train_loss': [],
            'test_loss': [],
            'train_accuracy': [],
            'test_accuracy': []
        }

    def run(self):
        """Основной цикл обучения."""
        try:
            self._is_running = True
            self._should_stop = False
            self._is_paused = False

            model = self._training_data["model"]
            train_loader = self._training_data["train_loader"]
            test_loader = self._training_data["test_loader"]
            optimizer = self._training_data["optimizer"]
            loss_fn = self._training_data["loss_fn"]
            params = self._training_data["params"]
            device = self._training_data["device"]

            epochs = params["epochs"]
            metrics_list = params["metrics"]

            self.training_started.emit()

            for epoch in range(epochs):
                if self._should_stop:
                    return

                while self._is_paused:
                    if self._should_stop:
                        return
                    time.sleep(0.1)

                self.epoch_started.emit(epoch + 1)
                self.progress_updated.emit(epoch + 1, epochs)

                train_metrics = self._train_epoch(
                    model, train_loader, optimizer, loss_fn, device
                )
                test_metrics = self._validate_epoch(
                    model, test_loader, loss_fn, device
                )

                if self._should_stop:
                    return

                self._history["train_loss"].append(train_metrics["loss"])
                self._history["test_loss"].append(test_metrics["loss"])
                self._history["train_accuracy"].append(train_metrics["accuracy"])
                self._history["test_accuracy"].append(test_metrics["accuracy"])

                metrics = {
                    "epoch": epoch + 1,
                    "train_loss": train_metrics["loss"],
                    "test_loss": test_metrics["loss"],
                    "train_accuracy": train_metrics["accuracy"],
                    "test_accuracy": test_metrics["accuracy"],
                    "precision": train_metrics["precision"],
                    "recall": train_metrics["recall"],
                    "f1_score": train_metrics["f1_score"],
                }
                self.epoch_completed.emit(metrics)
                epoch_offset = self._training_data["epoch_offset"]
                self.log_message.emit(
                    f"Эпоха {epoch_offset + epoch + 1}/{epoch_offset + epochs} | "
                    f"Train Loss: {metrics['train_loss']:.4f} | "
                    f"Test Loss: {metrics['test_loss']:.4f} | "
                    f"Train Acc: {metrics['train_accuracy']:.4f} | "
                    f"Test Acc: {metrics['test_accuracy']:.4f}"
                )

                if metrics["test_loss"] < self._best_loss:
                    self._best_loss = metrics["test_loss"]
                    self.log_message.emit(f"Новый лучший результат: {metrics['test_loss']:.4f}")

            final_metrics = {
                "best_loss": self._best_loss,
                "history": self._history,
                "final_epoch": epochs
            }
            self.training_finished.emit(final_metrics)
        except Exception as e:
            error_msg = f"Ошибка обучения: {str(e)}"
            self.training_error.emit(error_msg)
        finally:
            self._is_running = False

    def _train_epoch(self, model: nn.Module, loader: DataLoader, optimizer: Optimizer, loss_fn: nn.Module, device) -> dict:
        """Одна эпоха обучения."""
        model.train()
        total_loss = 0.0
        all_pred = []
        all_targets = []
        batches_processed = 0

        for data, target in loader:
            if self._should_stop:
                break

            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = loss_fn(output, target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            pred = output.argmax(dim=1)
            all_pred.extend(pred.cpu().numpy())
            all_targets.extend(target.cpu().numpy())
            batches_processed += 1

        avg_loss = total_loss / max(batches_processed, 1)
        metrics = self._calculate_metrics(all_pred, all_targets)
        metrics["loss"] = avg_loss
        return metrics

    def _validate_epoch(self, model: nn.Module, loader: DataLoader, loss_fn: nn.Module, device) -> dict:
        """Одна эпоха валидации."""
        model.eval()
        total_loss = 0.0
        all_pred = []
        all_targets = []
        batches_processed = 0

        with torch.no_grad():
            for data, target in loader:
                if self._should_stop:
                    break

                data, target = data.to(device), target.to(device)
                output = model(data)
                loss = loss_fn(output, target)
                total_loss += loss.item()

                pred = output.argmax(dim=1)
                all_pred.extend(pred.cpu().numpy())
                all_targets.extend(target.cpu().numpy())
                batches_processed += 1

        avg_loss = total_loss / max(batches_processed, 1)
        metrics = self._calculate_metrics(all_pred, all_targets)
        metrics["loss"] = avg_loss
        return metrics

    def _calculate_metrics(self, preds, targets):
        """Вычисление метрик."""
        metrics = {}
        if len(preds) == 0:
            return metrics

        metrics["accuracy"] = accuracy_score(targets, preds)
        metrics["precision"] = precision_score(targets, preds, average="weighted", zero_division=0)
        metrics["recall"] = recall_score(targets, preds, average="weighted", zero_division=0)
        metrics["f1_score"] = f1_score(targets, preds, average="weighted", zero_division=0)
        return metrics

    def pause(self):
        """Поставить обучение на паузу."""
        if self._is_running and not self._is_paused:
            self._is_paused = True
            self.training_paused.emit()

    def resume(self):
        """Продолжить обучение."""
        if self._is_paused:
            self._is_paused = False
            self.training_resumed.emit()

    def stop(self):
        """Остановить обучение."""
        self._should_stop = True
        self._is_paused = False
        self.training_stopped.emit()

