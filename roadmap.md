# NeuralNet Designer - Визуальный конструктор нейронных сетей

Приложение на PyQt для визуального проектирования, обучения и экспорта нейронных сетей.

## Основная функциональность

### Главное меню (Menu Bar)

**File:**
- `New Project` - Создать новый проект
- `Open Project` - Открыть проект (.nnd файл)
- `Save Project` - Сохранить проект
- `Export` → 
  - Код модели
  - Код обучения
  - Код тестирования
  - Полный проект
  - Веса модели (.pth, .onnx)
- `Settings` - Настройки (тема, путь к Python)
- `Exit` - Выход

**Edit:**
- `Undo` (Ctrl+Z)
- `Redo` (Ctrl+Y)
- `Delete` - Удалить выбранный блок
- `Select All` - Выделить все

**View:**
- `Zoom In/Out`
- `Fit to Screen`
- `Toggle Grid` - Сетка
- `Dark/Light Theme`

**Help:**
- `Documentation`
- `About`

---

## ️ Вкладки приложения

### Вкладка 1: Архитектура (Architecture)

**Панель слева:**
- Поле поиска
- Список доступных блоков:
  - Input Layers
  - Dense/Linear
  - Convolutional (Conv1D/2D/3D)
  - Pooling (Max/Avg)
  - Activation (ReLU, Sigmoid, Softmax и др.)
  - Dropout
  - BatchNorm
  - Flatten
  - Output
- Пользовательские блоки - из группировки блоков

**Центральная область:**
- Canvas для drag-and-drop
- Соединение блоков линиями
- Отображение размерностей тензоров
- Визуальная валидация соединений
- Выделение блоков
- Zoom in/out
- Визуализация активного блока
- Валидация графа
  - Проверка связности графа
  - Проверка совместимости слоев
  - Проверка наличия Input/Output

**Панель справа (Properties):**
- Настройка параметров выбранного блока
- Имя слоя
- Размеры, функции активации
- Dropout rate и др.

---

### Вкладка 2: Данные и Обучение (Data & Training)

**Секция "Датасет":**
- Выбор предзагруженных (MNIST, CIFAR-10, FashionMNIST)
- Загрузка своего датасета:
  - Изображения (папки) - проверить размеры, предложить изменять shape, определить метки из названий
  - CSV/Excel таблицы - проверить количество колонок, определить метки
- Настройка препроцессинга:
  - Нормализация
  - Аугментация данных?
  - Train/Val/Test split

**Секция "Параметры обучения":**
- Оптимизатор (SGD, Adam, RMSprop)
- Learning Rate + Scheduler
- Функция потерь (Loss Function)
- Метрики (Accuracy, F1, Precision, Recall)
- Batch Size
- Количество эпох
- Device (CPU/CUDA/MPS) - проверить наличие

**Секция "Callbacks":**
- Early Stopping
- Model Checkpoint
- Reduce LR on Plateau
- TensorBoard logging

---

### Вкладка 3: Запуск и Результаты (Run & Monitor)

**Панель управления:**
- Кнопка `Start Training`
- Кнопка `Pause/Resume`
- Кнопка `Stop`
- Индикатор прогресса

**Графики (Real-time):**
- Loss (Train/Val)
- Accuracy/Metrics
- Learning Rate
- Confusion Matrix

**Логи:**
- Консоль вывода процесса обучения
- Таблица с метриками по эпохам
- Время обучения

**Визуализация предсказаний:**
- Примеры изображений с предсказаниями
- Сравнение Ground Truth vs Prediction
- Confidence scores

---

### Вкладка 4: Экспорт (Export)

**Экспорт кода:**
- Код модели (model.py)
- Код обучения (train.py)
- Код инференса (predict.py)
- Полный проект (ZIP) + requirements.txt + README с инструкцией

**Экспорт весов модели:**
- PyTorch (.pth)
- ONNX (.onnx)

**Настройки экспорта:**
- Включение/выключение комментариев
- Стиль кода (скрипт/классы)

---

## Технические особенности

### Архитектура:
- **GUI Framework:** PyQt5
- **Graph Editor:** QGraphicsView/Scene или NodeGraphQt
- **Plotting:** pyqtgraph / matplotlib
- **Code Generation:** Jinja2 templates
- **Backend:** PyTorch

### Многопоточность:
- Обучение в отдельном QThread
- Обновление UI через pyqtSignal
- Non-blocking интерфейс

### Сохранение проектов:
- Формат: JSON
- Структура:
  ```json
  {
    "architecture": {...},
    "parameters": {...},
    "dataset_config": {...}
  }
  ```
### Дополнительно:
- requirements.txt
- README с инструкцией