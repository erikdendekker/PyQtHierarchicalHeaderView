from PyQt5 import QtCore,\
                  QtGui,\
                  QtWidgets
from PyQt5.QtCore import Qt


class private_data:

    def __init__(self):
        self.headerModel = None

    def initFromNewModel(self, orientation, model):
        self.headerModel = model.data(QtCore.QModelIndex(), (PyQtHierarchicalHeaderView.HorizontalHeaderDataRole if orientation == Qt.Horizontal else PyQtHierarchicalHeaderView.VerticalHeaderDataRole))

    def findRootIndex(self, index):
        while index.parent().isValid():
            index = index.parent()
        return index

    def parentIndexes(self, index):
        indexes = []
        while index.isValid():
            indexes.insert(0, index)
            index = index.parent()
        return indexes

    def findLeaf(self, curentIndex, sectionIndex, curentLeafIndex):
        if curentIndex.isValid():
            childCount = curentIndex.model().columnCount(curentIndex)
            if childCount:
                for i in range(childCount):
                    MI, curentLeafIndex = self.findLeaf(curentIndex.child(0, i), sectionIndex, curentLeafIndex)
                    res = QtCore.QModelIndex(MI)
                    if res.isValid():
                        return res, curentLeafIndex
            else:
                curentLeafIndex += 1
                if curentLeafIndex == sectionIndex:
                    return curentIndex, curentLeafIndex
        return QtCore.QModelIndex(), curentLeafIndex

    def leafIndex(self, sectionIndex):
        if self.headerModel:
            curentLeafIndex = -1
            for i in range(self.headerModel.columnCount()):
                MI, curentLeafIndex = self.findLeaf(self.headerModel.index(0, i), sectionIndex, curentLeafIndex)
                res = QtCore.QModelIndex(MI)
                if res.isValid():
                    return res
        return QtCore.QModelIndex()

    def searchLeafs(self, curentIndex):
        res = []
        if (curentIndex.isValid()):
            childCount = curentIndex.model().columnCount(curentIndex)
            if childCount:
                for i in range(childCount):
                    res += self.searchLeafs(curentIndex.child(0, i))
            else:
                res.append(curentIndex)
        return res

    def leafs(self, searchedIndex):
        leafs = []
        if searchedIndex.isValid():
            childCount = searchedIndex.model().columnCount(searchedIndex)
            for i in range(childCount):
                leafs += self.searchLeafs(searchedIndex.child(0, i))
        return leafs

    def setForegroundBrush(self, opt, index):
        foregroundBrush = index.data(Qt.ForegroundRole)
        if isinstance(foregroundBrush, QtGui.QBrush):
            opt.palette.setBrush(QtGui.QPalette.ButtonText, foregroundBrush)

    def setBackgroundBrush(self, opt, index):
        backgroundBrush = index.data(Qt.BackgroundRole)
        if isinstance(backgroundBrush, QtGui.QBrush):
            opt.palette.setBrush(QtGui.QPalette.Button, backgroundBrush)
            opt.palette.setBrush(QtGui.QPalette.Window, backgroundBrush)

    def cellSize(self, leafIndex, hv, styleOptions):
        res = QtCore.QSize()
        vS = leafIndex.data(Qt.SizeHintRole)
        if vS and isinstance(vS, QtCore.QSize):
            res = vS
        fnt = QtGui.QFont(hv.font())
        vF = leafIndex.data(Qt.FontRole)
        if vF and isinstance(vF, QtGui.QFont):
            fnt = vF
        fnt.setBold(True)
        fm = QtGui.QFontMetrics(fnt)
        size = QtCore.QSize(fm.size(0, str(leafIndex.data(Qt.DisplayRole))))
        if leafIndex.data(Qt.UserRole) != None:
            size.transpose()
        decorationsSize = QtCore.QSize(hv.style().sizeFromContents(QtWidgets.QStyle.CT_HeaderSection, styleOptions, QtCore.QSize(), hv))
        emptyTextSize = QtCore.QSize(fm.size(0, ''))
        return res.expandedTo(size + decorationsSize - emptyTextSize)

    def currentCellWidth(self, searchedIndex, leafIndex, sectionIndex, hv):
        leafsList = self.leafs(searchedIndex)
        if len(leafsList) == 0:
            return hv.sectionSize(sectionIndex)
        width = 0
        firstLeafSectionIndex = sectionIndex - leafsList.index(leafIndex)
        for i in range(len(leafsList)):
            width += hv.sectionSize(firstLeafSectionIndex + i)
        return width

    def currentCellLeft(self, searchedIndex, leafIndex, sectionIndex, left, hv):
        leafsList = self.leafs(searchedIndex)
        if len(leafsList) > 0:
            n = leafsList.index(leafIndex)
            firstLeafSectionIndex = sectionIndex - n
            n -= 1
            while n >= 0:
                left -= hv.sectionSize(firstLeafSectionIndex + n)
                n -= 1
        return left

    def paintHorizontalCell(self, painter, hv, cellIndex, leafIndex, logicalLeafIndex, styleOptions, sectionRect, top):
        uniopt = QtWidgets.QStyleOptionHeader(styleOptions)
        self.setForegroundBrush(uniopt, cellIndex)
        self.setBackgroundBrush(uniopt, cellIndex)
        height = self.cellSize(cellIndex, hv, uniopt).height()
        if cellIndex == leafIndex:
            height = sectionRect.height() - top
        left  = self.currentCellLeft (cellIndex, leafIndex, logicalLeafIndex, sectionRect.left(), hv)
        width = self.currentCellWidth(cellIndex, leafIndex, logicalLeafIndex, hv)

        r = QtCore.QRect(left, top, width, height)
        uniopt.text = str(cellIndex.data(Qt.DisplayRole))
        painter.save()
        uniopt.rect = r
        if cellIndex.data(Qt.UserRole) != None:
            hv.style().drawControl(QtWidgets.QStyle.CE_HeaderSection, uniopt, painter, hv)
            painter.rotate(-90)
            new_r = QtCore.QRect(0, 0, r.height(), r.width())
            new_r.moveCenter(QtCore.QPoint(-r.center().y(), r.center().x()))
            uniopt.rect = new_r
            hv.style().drawControl(QtWidgets.QStyle.CE_HeaderLabel, uniopt, painter, hv)
        else:
            hv.style().drawControl(QtWidgets.QStyle.CE_Header, uniopt, painter, hv)
        painter.restore()
        return top + height

    def paintHorizontalSection(self, painter, sectionRect, logicalLeafIndex, hv, styleOptions, leafIndex):
        oldBO = QtCore.QPointF(painter.brushOrigin())
        top = sectionRect.y()
        indexes = self.parentIndexes(leafIndex)
        for i in range(len(indexes)):
            realStyleOptions = QtWidgets.QStyleOptionHeader(styleOptions)
            # if i<len(indexes)-1 and ( realStyleOptions.state.testFlag(QtGui.QStyle.State_Sunken) or realStyleOptions.state.testFlag(QtGui.QStyle.State_On)):
            #  t = QtGui.QStyle.State(QtGui.QStyle.State_Sunken | QtGui.QStyle.State_On)
            #  realStyleOptions.state&=(~t)
            top = self.paintHorizontalCell(painter, hv, indexes[i], leafIndex, logicalLeafIndex, realStyleOptions,sectionRect, top)
        painter.setBrushOrigin(oldBO)

    def paintVerticalCell(self, painter, hv, cellIndex, leafIndex, logicalLeafIndex, styleOptions, sectionRect, left):
        uniopt = QtWidgets.QStyleOptionHeader(styleOptions)
        self.setForegroundBrush(uniopt, cellIndex)
        self.setBackgroundBrush(uniopt, cellIndex)
        width = self.cellSize(cellIndex, hv, uniopt).width()
        if cellIndex == leafIndex:
            width = sectionRect.width() - left
        top = self.currentCellLeft(cellIndex, leafIndex, logicalLeafIndex, sectionRect.top(), hv)
        height = self.currentCellWidth(cellIndex, leafIndex, logicalLeafIndex, hv)
        r = QtCore.QRect(left, top, width, height)
        uniopt.text = str(cellIndex.data(Qt.DisplayRole))
        painter.save()
        uniopt.rect = r
        if cellIndex.data(Qt.UserRole) != None:
            hv.style().drawControl(QtWidgets.QStyle.CE_HeaderSection, uniopt, painter, hv)
            painter.rotate(-90)
            new_r = QtCore.QRect(0, 0, r.height(), r.width())
            new_r.moveCenter(QtCore.QPoint(-r.center().y(), r.center().x()))
            uniopt.rect = new_r
            hv.style().drawControl(QtWidgets.QStyle.CE_HeaderLabel, uniopt, painter, hv)
        else:
            hv.style().drawControl(QtWidgets.QStyle.CE_Header, uniopt, painter, hv)
        painter.restore()
        return left + width

    def paintVerticalSection(self, painter, sectionRect, logicalLeafIndex, hv, styleOptions, leafIndex):
        oldBO = QtCore.QPointF(painter.brushOrigin())
        left = sectionRect.x()
        indexes = self.parentIndexes(leafIndex)
        for i in range(len(indexes)):
            realStyleOptions = QtWidgets.QStyleOptionHeader(styleOptions)
            # if(   i<indexes.size()-1
            #    &&
            #      (   realStyleOptions.state.testFlag(QStyle::State_Sunken)
            #       || realStyleOptions.state.testFlag(QStyle::State_On)))
            # {
            #    QStyle::State t(QStyle::State_Sunken | QStyle::State_On)
            #    realStyleOptions.state&=(~t)
            # }
            left = self.paintVerticalCell(painter, hv, indexes[i], leafIndex, logicalLeafIndex, realStyleOptions, sectionRect, left)
        painter.setBrushOrigin(oldBO)


class PyQtHierarchicalHeaderView(QtWidgets.QHeaderView):

    HorizontalHeaderDataRole = Qt.UserRole
    VerticalHeaderDataRole   = Qt.UserRole + 1

    def __init__(self, orientation, parent = None):
        super().__init__(orientation, parent)

        self._pd = private_data()

        self.sectionResized.connect(self.on_sectionResized)

    def styleOptionForCell(self, logicalIndex):
        opt = QtWidgets.QStyleOptionHeader()
        self.initStyleOption(opt)
        if (self.window().isActiveWindow()):
            opt.state |= QtWidgets.QStyle.State_Active
        opt.textAlignment = Qt.AlignCenter
        opt.iconAlignment = Qt.AlignVCenter
        opt.section = logicalIndex

        visualIndex = self.visualIndex(logicalIndex)

        if self.count() == 1:
            opt.position = QtWidgets.QStyleOptionHeader.OnlyOneSection
        elif visualIndex == 0:
            opt.position = QtWidgets.QStyleOptionHeader.Beginning
        elif visualIndex == self.count() - 1:
            opt.position = QtWidgets.QStyleOptionHeader.End
        else:
            opt.position = QtWidgets.QStyleOptionHeader.Middle

        if self.sectionsClickable() and self.highlightSections() and self.selectionModel():
            if self.orientation() == Qt.Horizontal:
                if self.selectionModel().columnIntersectsSelection(logicalIndex, self.rootIndex()):
                    opt.state |= QtWidgets.QStyle.State_On
                if self.selectionModel().isColumnSelected(logicalIndex, self.rootIndex()):
                    opt.state |= QtWidgets.QStyle.State_Sunken
            else:
                if self.selectionModel().rowIntersectsSelection(logicalIndex, self.rootIndex()):
                    opt.state |= QtWidgets.QStyle.State_On
                if self.selectionModel().isRowSelected(logicalIndex, self.rootIndex()):
                    opt.state |= QtWidgets.QStyle.State_Sunken

        if self.selectionModel():
            previousSelected = False
            if self.orientation() == Qt.Horizontal:
                previousSelected = self.selectionModel().isColumnSelected(self.logicalIndex(visualIndex - 1), self.rootIndex())
            else:
                previousSelected = self.selectionModel().isRowSelected(self.logicalIndex(visualIndex - 1), self.rootIndex())

            nextSelected = False
            if self.orientation() == Qt.Horizontal:
                nextSelected = self.selectionModel().isColumnSelected(self.logicalIndex(visualIndex + 1), self.rootIndex())
            else:
                nextSelected = self.selectionModel().isRowSelected(self.logicalIndex(visualIndex + 1), self.rootIndex())

            if previousSelected and nextSelected:
                opt.selectedPosition = QtWidgets.QStyleOptionHeader.NextAndPreviousAreSelected
            else:
                if previousSelected:
                    opt.selectedPosition = QtWidgets.QStyleOptionHeader.PreviousIsSelected
                else:
                    if nextSelected:
                        opt.selectedPosition = QtWidgets.QStyleOptionHeader.NextIsSelected
                    else:
                        opt.selectedPosition = QtWidgets.QStyleOptionHeader.NotAdjacent
        return opt

    # protected??
    def paintSection(self, painter, rect, logicalIndex):
        if rect.isValid():
            leafIndex = QtCore.QModelIndex(self._pd.leafIndex(logicalIndex))
            if leafIndex.isValid():
                if self.orientation() == Qt.Horizontal:
                    self._pd.paintHorizontalSection(painter, rect, logicalIndex, self, self.styleOptionForCell(logicalIndex), leafIndex)
                else:
                    self._pd.paintVerticalSection  (painter, rect, logicalIndex, self, self.styleOptionForCell(logicalIndex), leafIndex)
                return

        super().paintSection(painter, rect, logicalIndex)

    def sectionSizeFromContents(self, logicalIndex):
        if self._pd.headerModel:

            curLeafIndex = QtCore.QModelIndex(self._pd.leafIndex(logicalIndex))
            if curLeafIndex.isValid():
                styleOption = QtWidgets.QStyleOptionHeader(self.styleOptionForCell(logicalIndex))
                s = QtCore.QSize(self._pd.cellSize(curLeafIndex, self, styleOption))
                curLeafIndex = curLeafIndex.parent()
                while curLeafIndex.isValid():
                    if self.orientation() == Qt.Horizontal:
                        s.setHeight(s.height() + self._pd.cellSize(curLeafIndex, self, styleOption).height())
                    else:
                        s.setWidth (s.width()  + self._pd.cellSize(curLeafIndex, self, styleOption).width())
                    curLeafIndex = curLeafIndex.parent()
                return s

        return super().sectionSizeFromContents(logicalIndex)

    def setModel(self, model):
        self._pd.initFromNewModel(self.orientation(), model)
        super().setModel(model)

        cnt = (model.columnCount() if self.orientation() == Qt.Horizontal else model.rowCount())
        if cnt:
            self.initializeSections(0, cnt - 1)

    # slot
    def on_sectionResized(self, logicalIndex):

        if self.isSectionHidden(logicalIndex):
            return

        leafIndex = QtCore.QModelIndex(self._pd.leafIndex(logicalIndex))
        if leafIndex.isValid():

            leafsList = self._pd.leafs(self._pd.findRootIndex(leafIndex))
            if not leafIndex in leafsList:
                return

            for n in range(leafsList.index(leafIndex), 1, -1):  # (int n=leafsList.indexOf(leafIndex); n>0; --n)
                logicalIndex -= 1
                w = self.viewport().width()
                h = self.viewport().height()
                pos = self.sectionViewportPosition(logicalIndex)
                r = QtCore.QRect(pos, 0, w - pos, h)
                if self.orientation() == Qt.Vertical:
                    r.setRect(0, pos, w, h - pos)
                elif self.isRightToLeft():
                    r.setRect(0, 0, pos + self.sectionSize(logicalIndex), h)

                self.viewport().update(r.normalized())
