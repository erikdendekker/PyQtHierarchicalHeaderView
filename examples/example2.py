#! /usr/bin/env python3

import sys

from PyQt5 import QtGui,\
                  QtWidgets
from PyQt5.QtCore import Qt

from PyQtHierarchicalHeaderView import PyQtProxyModelWithHeaderModels,\
                                       PyQtHierarchicalHeaderView


def BuildDataModel(model):
    cellText = "cell({0}, {1})"
    for i in range(4):
        l = []
        for j in range(4):
            cell = QtGui.QStandardItem(cellText.format(i, j))
            l.append(cell)
        model.appendRow(l)


def BuildHeaderModel(headerModel):
    rotatedTextCell = QtGui.QStandardItem("Rotated\n text")
    rotatedTextCell.setData(1, Qt.UserRole)

    cell = QtGui.QStandardItem("level 2")
    cell.appendColumn([QtGui.QStandardItem("level 3")])
    cell.appendColumn([QtGui.QStandardItem("level 3")])

    rootItem = QtGui.QStandardItem("root")
    rootItem.appendColumn([rotatedTextCell])
    rootItem.appendColumn([cell])
    rootItem.appendColumn([QtGui.QStandardItem("level 2")])

    headerModel.setItem(0, 0, rootItem)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    dataModel = QtGui.QStandardItemModel()
    BuildDataModel(dataModel)

    headerModel = QtGui.QStandardItemModel()
    BuildHeaderModel(headerModel)

    model = PyQtProxyModelWithHeaderModels()
    model.setHeaderModel(Qt.Horizontal, headerModel)
    model.setHeaderModel(Qt.Vertical,   headerModel)
    model.setSourceModel(dataModel)

    tv = QtWidgets.QTableView()
    tv.setHorizontalHeader(PyQtHierarchicalHeaderView(Qt.Horizontal, tv))
    tv.setVerticalHeader  (PyQtHierarchicalHeaderView(Qt.Vertical,   tv))
    tv.setModel(model)
    tv.resizeColumnsToContents()
    tv.resizeRowsToContents()
    tv.show()

    app.exec_()
