""""
svg_view.py
"""


import enum
import os
import sys
import typing

# pylint cannot introspect the Qt compiled extension modules, so every name
# imported from them reads as missing. Keep this disable above the whole Qt
# import block — import sorting will not separate it from what it covers.
from PyQt6.QtCore import QFileSystemWatcher, QPoint, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QAction, QColorConstants, QMouseEvent, QPalette, QResizeEvent, QWheelEvent
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMenu, QMenuBar, QStatusBar, QTabWidget


class ActionTypes(enum.Enum):
    OPEN = 1
    CLOSE = 2
    QUIT = 3
    CENTER = 4
    RELOAD = 5
    NEXT = 6
    PREV = 7


class SvgWidget(QSvgWidget):
    location_changed = pyqtSignal(QPointF, arguments=["location"])

    def update_view_box(self, size):
        w = self.scale * size.width()
        h = self.scale * size.height()
        r = QRectF(self.center_x - w / 2, self.center_y - h / 2, w, h)
        renderer = self.renderer()
        if renderer is not None:
            renderer.setViewBox(r)

    def _load_def_view_box(self):
        renderer = self.renderer()
        if renderer is not None:
            self.defViewBox = renderer.viewBoxF()

    def center(self):
        self.scale = max(float(self.defViewBox.width()) / self.width(),
                         float(self.defViewBox.height()) / self.height())
        self.center_x = self.defViewBox.center().x()
        self.center_y = self.defViewBox.center().y()
        self.update_view_box(self.size())
        self.repaint()

    def reload(self):
        QSvgWidget.load(self, self.path)
        self._load_def_view_box()
        self.update_view_box(self.size())

    @typing.override
    def resizeEvent(self, a0: QResizeEvent | None):
        if a0 is not None:
            self.update_view_box(a0.size())
        QSvgWidget.resizeEvent(self, a0)

    def __init__(self, path):
        QSvgWidget.__init__(self)
        self.path = path
        self.watch = QFileSystemWatcher(self)
        self.watch.addPath(self.path)
        self.watch.fileChanged.connect(self.reload)

        self.setMouseTracking(True)
        self.ds: QPoint | None = None
        self.scale = 0.0
        self.center_x = 0.0
        self.center_y = 0.0
        self.start_center_x = 0.0
        self.start_center_y = 0.0
        self.setPalette(QPalette(QColorConstants.White))
        self.setAutoFillBackground(True)
        QSvgWidget.load(self, path)
        self.defViewBox = QRectF()
        self._load_def_view_box()
        self.center()

    def update_location(self, pos):
        self.location_changed.emit(QPointF(
            (pos.x() - self.width() / 2) * self.scale + self.center_x,
            (pos.y() - self.height() / 2) * self.scale + self.center_y))

    @typing.override
    def wheelEvent(self, a0: QWheelEvent | None):
        evt = a0
        if evt is None:
            return
        dx = evt.position().toPoint().x() - self.width() / 2
        dy = evt.position().toPoint().y() - self.height() / 2
        center_x = self.center_x + dx * self.scale
        center_y = self.center_y + dy * self.scale
        self.scale = self.scale * 1.0025 ** (-evt.angleDelta().y())
        self.center_x = center_x - dx * self.scale
        self.center_y = center_y - dy * self.scale
        self.update_view_box(self.size())
        self.update_location(evt.position().toPoint())
        self.repaint()

    @typing.override
    def mousePressEvent(self, a0: QMouseEvent | None):
        evt = a0
        if evt is None:
            return
        self.ds = evt.pos()
        self.start_center_x = self.center_x
        self.start_center_y = self.center_y

    @typing.override
    def mouseMoveEvent(self, a0: QMouseEvent | None):
        evt = a0
        if evt is None:
            return
        self.update_location(evt.pos())
        if not self.ds:
            return
        dx = evt.pos().x() - self.ds.x()
        dy = evt.pos().y() - self.ds.y()
        self.center_x = self.start_center_x - dx * self.scale
        self.center_y = self.start_center_y - dy * self.scale
        self.update_view_box(self.size())
        self.repaint()

    @typing.override
    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        self.mouseMoveEvent(a0)
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
        view = self.tabs.currentWidget()
        if isinstance(view, SvgWidget):
            view.center()

    def reload(self):
        view = self.tabs.currentWidget()
        if isinstance(view, SvgWidget):
            view.reload()

    def tab_next(self):
        if not self.tabs.currentWidget():
            return
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def tab_prev(self):
        if not self.tabs.currentWidget():
            return
        self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % self.tabs.count())

    def open(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            filter="Svg documents (*.svg);;Any files (*.*)"
        )
        if path:
            self.load(path)

    def create_actions(self):
        self.action_map[ActionTypes.OPEN] = QAction(self)
        self.action_map[ActionTypes.QUIT] = QAction(self)
        self.action_map[ActionTypes.CLOSE] = QAction(self)
        self.action_map[ActionTypes.CENTER] = QAction(self)
        self.action_map[ActionTypes.RELOAD] = QAction(self)
        self.action_map[ActionTypes.NEXT] = QAction(self)
        self.action_map[ActionTypes.PREV] = QAction(self)

    def __init__(self):
        QMainWindow.__init__(self)
        self.tabs = QTabWidget(self)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.setCentralWidget(self.tabs)
        self.resize(800, 600)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.action_map: dict[ActionTypes, QAction] = {}

        self.menubar = QMenuBar(self)
        self.menuFile = QMenu(self.menubar)
        self.menuEdit = QMenu(self.menubar)
        self.setMenuBar(self.menubar)

        self.create_actions()

        self.menuFile.addAction(self.action_map[ActionTypes.OPEN])
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_map[ActionTypes.CLOSE])
        self.menuFile.addAction(self.action_map[ActionTypes.CLOSE])
        self.menuEdit.addAction(self.action_map[ActionTypes.CENTER])
        self.menuEdit.addAction(self.action_map[ActionTypes.RELOAD])
        self.menuEdit.addAction(self.action_map[ActionTypes.NEXT])
        self.menuEdit.addAction(self.action_map[ActionTypes.PREV])
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.action_map[ActionTypes.CENTER].triggered.connect(self.center)
        self.action_map[ActionTypes.RELOAD].triggered.connect(self.reload)
        self.action_map[ActionTypes.NEXT].triggered.connect(self.tab_next)
        self.action_map[ActionTypes.PREV].triggered.connect(self.tab_prev)
        self.action_map[ActionTypes.QUIT].triggered.connect(self.close)
        self.action_map[ActionTypes.OPEN].triggered.connect(self.open)
        self.action_map[ActionTypes.CLOSE].triggered.connect(self.tab_close)

        self.setWindowTitle("Svg Viewer")
        self.menuFile.setTitle("&File")
        self.menuEdit.setTitle("&Edit")
        self.action_map[ActionTypes.OPEN].setText("&Open")
        self.action_map[ActionTypes.CLOSE].setText("&Close Tab")
        self.action_map[ActionTypes.QUIT].setText("&Quit")
        self.action_map[ActionTypes.CENTER].setText("&Center")
        self.action_map[ActionTypes.RELOAD].setText("&Reload")
        self.action_map[ActionTypes.NEXT].setText("&Next Tab")
        self.action_map[ActionTypes.PREV].setText("&Prev Tab")


def view_svgs(filenames: list[str]):
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    for filename in filenames:
        window.load(filename)

    sys.exit(app.exec())
