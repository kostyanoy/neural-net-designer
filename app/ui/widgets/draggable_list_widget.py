from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QListWidget


class DraggableListWidget(QListWidget):
    """Кастомный QListWidget с поддержкой перетаскивания (Drag & Drop) элементов."""

    NODE_MIME_TYPE = "application/x-nodegraph-node-id"

    def startDrag(self, supportedActions):
        """Переопределяет метод базового класса QListWidget для кастомизации данных"""
        indexes = self.selectedIndexes()
        if not indexes:
            return

        index = indexes[0]
        item = self.itemFromIndex(index)

        node_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not node_id:
            return

        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        mime_data.setData(self.NODE_MIME_TYPE, node_id.encode("utf-8"))

        drag.setMimeData(mime_data)
        drag.exec_(supportedActions)