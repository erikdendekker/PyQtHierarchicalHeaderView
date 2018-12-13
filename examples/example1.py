#! /usr/bin/env python3

import sys

from PyQt5 import QtCore,\
                  QtGui,\
                  QtWidgets
from PyQt5.QtCore import Qt

from PyQtHierarchicalHeaderView import PyQtHierarchicalHeaderView


class ExampleModel(QtCore.QAbstractTableModel):

    def __init__(self, parent = None):

        super().__init__(parent)

        self._horizontalHeaderModel = QtGui.QStandardItemModel()
        self._verticalHeaderModel   = QtGui.QStandardItemModel()

        self.fillHeaderModel(self._horizontalHeaderModel)
        self.fillHeaderModel(self._verticalHeaderModel)

    def fillHeaderModel(self, headerModel):

        rotatedTextCell = QtGui.QStandardItem("Rotated text")
        rotatedTextCell.setData(1, QtCore.Qt.UserRole)

        cell = QtGui.QStandardItem("level 2")
        cell.appendColumn([QtGui.QStandardItem("level 3")])
        cell.appendColumn([QtGui.QStandardItem("level 3")])

        rootItem = QtGui.QStandardItem("root")
        rootItem.appendColumn([rotatedTextCell])
        rootItem.appendColumn([cell])
        rootItem.appendColumn([QtGui.QStandardItem("level 2")])

        headerModel.setItem(0, 0, rootItem)

    def rowCount(self, parent = None):
        return 4

    def columnCount(self, parent = None):
        return 4

    def data(self, index, role):
        if role == PyQtHierarchicalHeaderView.HorizontalHeaderDataRole:
            return self._horizontalHeaderModel

        if role == PyQtHierarchicalHeaderView.VerticalHeaderDataRole:
            return self._verticalHeaderModel

        if role == Qt.DisplayRole and index.isValid():
            return 'index({}, {})'.format(index.row(),
                                          index.column())

        return None

    def flags(self, QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    em = ExampleModel()

    tv = QtWidgets.QTableView()
    hv = PyQtHierarchicalHeaderView(Qt.Horizontal, tv)
    hv.setHighlightSections(True)
    hv.setSectionsClickable(True)
    tv.setHorizontalHeader(hv)

    hv = PyQtHierarchicalHeaderView(Qt.Vertical, tv)
    hv.setHighlightSections(True)
    hv.setSectionsClickable(True)
    tv.setVerticalHeader(hv)

    tv.resizeColumnsToContents()
    tv.resizeRowsToContents()
    tv.setModel(em)
    tv.show()

    app.exec_()
