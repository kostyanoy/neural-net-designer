from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, QModelIndex


class MetricsTableModel(QAbstractTableModel):
    def __init__(self, headers=None):
        super().__init__()
        self._headers = headers or []
        self._data = []

    def rowCount(self, parent = QModelIndex()):
        return len(self._data)

    def columnCount(self, parent = QModelIndex()):
        return len(self._headers)

    def data(self, index: QModelIndex, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        value = self._data[index.row()][index.column()]
        if value is None:
            return None
        if self._headers[index.column()] == "Эпоха":
            return str(int(value))
        return f"{value:.4f}"

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def add_row(self, row_data):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        row = [row_data.get(h) for h in self._headers]
        self._data.append(row)
        self.endInsertRows()

    def add_rows(self, rows_data: list[dict]):
        if not rows_data:
            return
        start_row = self.rowCount()
        end_row = self.rowCount() + len(rows_data) - 1
        self.beginInsertRows(QModelIndex(), start_row, end_row)
        for row_data in rows_data:
            row = [row_data.get(h) for h in self._headers]
            self._data.append(row)
        self.endInsertRows()

    def reset_data(self):
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()

    def set_headers(self, headers: list):
        self.beginResetModel()
        self._headers = headers
        self._data.clear()
        self.endResetModel()