from PyQt5.QtWidgets import QMessageBox

from app.config import APP_NAME, ORGANIZATION, VERSION, AUTHOR


def show_documentation(parent=None):
    """Показать окно с документацией по вкладкам."""
    text = (
        f"<h2>{APP_NAME} – Документация</h2>"
        "<p><b>🏗️ Архитектура</b><br>"
        "Визуальное проектирование нейронной сети. Перетаскивайте блоки из левой панели на холст, "
        "соединяйте их. В правой панели настраивайте параметры выбранного слоя. "
        "Кнопка «Валидировать граф» проверяет корректность архитектуры.</p>"
        "<p><b>⚙️ Обучение</b><br>"
        "Выбор датасета (предустановленные или свой CSV/папка с изображениями), настройка "
        "препроцессинга, гиперпараметров обучения (эпохи, batch size, оптимизатор, функция потерь, метрики).</p>"
        "<p><b>📊 Мониторинг</b><br>"
        "Запуск, пауза и остановка обучения. В реальном времени отображаются графики loss и accuracy, "
        "таблица метрик и логи.</p>"
        "<p><b>💾 Экспорт</b><br>"
        "Генерация Python-кода модели и обучения, экспорт весов в форматах .pth или .onnx.</p>"
        "<p>Горячие клавиши доступны в меню.</p>"
    )
    QMessageBox.information(parent, "Документация", text)


def show_about(parent=None):
    """Показать окно «О программе»."""
    text = (
        f"<h2>{APP_NAME}</h2>"
        f"<p>Версия {VERSION}</p>"
        f"<p>Визуальный конструктор и среда обучения нейронных сетей.</p>"
        f"<p><b>Автор:</b> {AUTHOR}<br>"
        f"<b>Организация:</b> {ORGANIZATION}</p>"
        f"<p>© 2026</p>"
    )
    QMessageBox.about(parent, "О программе", text)


def wrong_input(parent, arch_input_shape, dataset_input_shape):
    QMessageBox.warning(
        parent,
        "Несовместимость данных",
        f"Размерность входного слоя архитектуры {arch_input_shape} "
        f"не совпадает с размерностью датасета {dataset_input_shape}.\n"
        "Измените входной слой или выберите другой датасет."
    )


def wrong_output(parent, arch_output_shape, dataset_num_classes):
    QMessageBox.warning(
        parent,
        "Несовместимость данных",
        f"Размерность выходного слоя архитектуры {arch_output_shape} "
        f"не совпадает с количеством классов в датасете {dataset_num_classes}.\n"
        "Измените выходной слой или выберите другой датасет."
    )
