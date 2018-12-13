from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from .PyQtHierarchicalHeaderView import PyQtHierarchicalHeaderView


class PyQtProxyModelWithHeaderModels(QtCore.QIdentityProxyModel):

    def __init__(self, parent = None):

        super().__init__(parent)

        self._headerModel = {Qt.Horizontal : None,
                             Qt.Vertical   : None}

    def data(self, index, role = Qt.DisplayRole):

        orientation = None
        if role == PyQtHierarchicalHeaderView.HorizontalHeaderDataRole:
            orientation = Qt.Horizontal
        if role == PyQtHierarchicalHeaderView.VerticalHeaderDataRole:
            orientation = Qt.Vertical

        if orientation:
            return self._headerModel[orientation]

        return super().data(index, role)

    def setHeaderModel(self, orientation, headerModel):
        self._headerModel[orientation] = headerModel

        cnt = self.sourceModel().columnCount() if orientation == Qt.Horizontal else self.sourceModel().rowCount()

        if cnt:
            self.headerDataChanged.emit(orientation, 0, cnt - 1)
