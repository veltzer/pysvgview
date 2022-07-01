import enum
import os
import sys
from typing import List

# pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QMenuBar, QMenu, QMainWindow, QFileDialog, QStatusBar, QTabWidget, QApplication
from PyQt6.QtCore import pyqtSignal, QPointF, QRectF, QFileSystemWatcher
from PyQt6.QtGui import QAction, QPalette, QColorConstants


class ActionTypes(enum.Enum):
    OPEN = 1
    CLOSE = 2
    QUIT = 3
    CENTER = 4
    RELOAD = 5
    NEXT = 6
    PREV = 7


class SvgWidget(QSvgWidget):
    location_changed = pyqtSignal(QPointF)

    def update_view_box(self, size):
        w = self.scale * size.width()
        h = self.scale * size.height()
        r = QRectF(self.center_x - w / 2, self.center_y - h / 2, w, h)
        self.renderer().setViewBox(r)

    def center(self):
        self.scale = max(float(self.defViewBox.width()) / self.width(),
                         float(self.defViewBox.height()) / self.height())
        self.center_x = self.defViewBox.center().x()
        self.center_y = self.defViewBox.center().y()
        self.update_view_box(self.size())
        self.repaint()

    def reload(self):
        QSvgWidget.load(self, self.path)
        self.defViewBox = self.renderer().viewBoxF()
        self.update_view_box(self.size())

    def resizeEvent(self, evt):
        self.update_view_box(evt.size())
        QSvgWidget.resizeEvent(self, evt)

    def __init__(self, path):
        QSvgWidget.__init__(self)
        self.path = path
        self.watch = QFileSystemWatcher(self)
        self.watch.addPath(self.path)
        self.watch.fileChanged.connect(self.reload, None)

        self.setMouseTracking(True)
        self.ds = None
        self.scale = 0
        self.center_x = 0
        self.center_y = 0
        self.start_center_x = 0
        self.start_center_y = 0
        self.setPalette(QPalette(QColorConstants.White))
        self.setAutoFillBackground(True)
        QSvgWidget.load(self, path)
        self.defViewBox = self.renderer().viewBoxF()
        self.center()

    def update_location(self, pos):
        self.location_changed.emit(QPointF(
            (pos.x() - self.width() / 2) * self.scale + self.center_x,
            (pos.y() - self.height() / 2) * self.scale + self.center_y))

    def wheelEvent(self, evt):
        dx = evt.pos().x() - self.width() / 2
        dy = evt.pos().y() - self.height() / 2
        center_x = self.center_x + dx * self.scale
        center_y = self.center_y + dy * self.scale
        self.scale = self.scale * 1.0025 ** (-evt.angleDelta().y())
        self.center_x = center_x - dx * self.scale
        self.center_y = center_y - dy * self.scale
        self.update_view_box(self.size())
        self.update_location(evt.pos())
        self.repaint()

    def mousePressEvent(self, evt):
        self.ds = evt.pos()
        self.start_center_x = self.center_x
        self.start_center_y = self.center_y

    def mouseMoveEvent(self, evt):
        # print(dir(evt))
        self.update_location(evt.pos())
        if not self.ds:
            return
        dx = evt.pos().x() - self.ds.x()
        dy = evt.pos().y() - self.ds.y()
        self.center_x = self.start_center_x - dx * self.scale
        self.center_y = self.start_center_y - dy * self.scale
        self.update_view_box(self.size())
        self.repaint()

    def mouseReleaseEvent(self, evt):
        self.mouseMoveEvent(evt)
        self.ds = None


class MainWindow(QMainWindow):

    def show_location(self, point):
        self.statusbar.showMessage(f"{point.x()} {point.y()}")

    def load(self, path):
        view = SvgWidget(path)
        self.tabs.setCurrentIndex(self.tabs.addTab(view, os.path.basename(path)))

    def tab_close(self):
        if not self.tabs.currentWidget():
            return
        self.tabs.removeTab(self.tabs.currentIndex())

    def center(self):
        if not self.tabs.currentWidget():
            return
        self.tabs.currentWidget().center()

    def reload(self):
        if not self.tabs.currentWidget():
            return
        self.tabs.currentWidget().reload()

    def tab_next(self):
        if not self.tabs.currentWidget():
            return
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def tab_prev(self):
        if not self.tabs.currentWidget():
            return
        self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % self.tabs.count())

    def open(self):
        path = QFileDialog.getOpenFileName(
            self,
            "Open File",
            filter="Svg documents (*.svg);;Any files (*.*)"
        )
        if path:
            self.load(path)

    def create_actions(self):
        self.actions[ActionTypes.OPEN] = QAction(self)
        # self.actions[ActionTypes.OPEN].setShortcuts(QKeySequence("Open"))
        self.actions[ActionTypes.QUIT] = QAction(self)
        # self.actions[ActionTypes.QUIT].setShortcuts(QKeySequence("Quit"))
        self.actions[ActionTypes.CLOSE] = QAction(self)
        # self.actions[ActionTypes.CLOSE].setShortcuts(QKeySequence("Close"))
        self.actions[ActionTypes.CENTER] = QAction(self)
        # self.actions[ActionTypes.CENTER].setShortcuts(QKeySequence("Space"))
        self.actions[ActionTypes.RELOAD] = QAction(self)
        # self.actions[ActionTypes.RELOAD].setShortcuts(QKeySequence("F5"))
        self.actions[ActionTypes.NEXT] = QAction(self)
        # self.actions[ActionTypes.NEXT].setShortcuts(QKeySequence("Page Down"))
        self.actions[ActionTypes.PREV] = QAction(self)
        # self.actions[ActionTypes.PREV].setShortcuts(QKeySequence("Page Up"))

    def __init__(self):
        QMainWindow.__init__(self)
        self.tabs = QTabWidget(self)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        # self.tabs.tabCloseRequested.connect(self.tab_close, None)
        self.setCentralWidget(self.tabs)
        self.resize(800, 600)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.actions = {}

        self.menubar = QMenuBar(self)
        self.menuFile = QMenu(self.menubar)
        self.menuEdit = QMenu(self.menubar)
        self.setMenuBar(self.menubar)

        self.create_actions()

        self.menuFile.addAction(self.actions[ActionTypes.OPEN])
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actions[ActionTypes.CLOSE])
        self.menuFile.addAction(self.actions[ActionTypes.CLOSE])
        self.menuEdit.addAction(self.actions[ActionTypes.CENTER])
        self.menuEdit.addAction(self.actions[ActionTypes.RELOAD])
        self.menuEdit.addAction(self.actions[ActionTypes.NEXT])
        self.menuEdit.addAction(self.actions[ActionTypes.PREV])
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.actions[ActionTypes.CENTER].triggered.connect(self.center)
        self.actions[ActionTypes.RELOAD].triggered.connect(self.reload)
        self.actions[ActionTypes.NEXT].triggered.connect(self.tab_next)
        self.actions[ActionTypes.PREV].triggered.connect(self.tab_prev)
        self.actions[ActionTypes.QUIT].triggered.connect(self.close)
        self.actions[ActionTypes.OPEN].triggered.connect(self.open)
        self.actions[ActionTypes.CLOSE].triggered.connect(self.tab_close)

        self.setWindowTitle("Svg Viewer")
        self.menuFile.setTitle("&File")
        self.menuEdit.setTitle("&Edit")
        self.actions[ActionTypes.OPEN].setText("&Open")
        self.actions[ActionTypes.CLOSE].setText("&Close Tab")
        self.actions[ActionTypes.QUIT].setText("&Quit")
        self.actions[ActionTypes.CENTER].setText("&Center")
        self.actions[ActionTypes.RELOAD].setText("&Reload")
        self.actions[ActionTypes.NEXT].setText("&Next Tab")
        self.actions[ActionTypes.PREV].setText("&Prev Tab")


def view_svgs(filenames: List[str]):
    app = QApplication(sys.argv)
    # SignalWakeupHandler(app)
    # signal.signal(signal.SIGINT, lambda sig, _: app.quit())

    window = MainWindow()
    window.show()

    for filename in filenames:
        window.load(filename)

    sys.exit(app.exec())
