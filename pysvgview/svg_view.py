import enum
import os
import signal
import socket
import sys
from typing import List

from PyQt6 import QtSvg, QtCore, QtWidgets, QtGui, QtNetwork


class ActionTypes(enum.Enum):
    OPEN = 1
    CLOSE = 2
    QUIT = 3
    CENTER = 4
    RELOAD = 5
    NEXT = 6
    PREV = 7


class SignalWakeupHandler(QtNetwork.QAbstractSocket):

    def __init__(self, parent=None):
        super().__init__(QtNetwork.QAbstractSocket.UdpSocket, parent)
        self.old_fd = None
        # Create a socket pair
        self.write_sock, self.read_sock = socket.socketpair(type=socket.SOCK_DGRAM)
        # Let Qt listen on the one end
        # noinspection PyTypeChecker
        self.setSocketDescriptor(self.read_sock.fileno())
        # And let Python write on the other end
        self.write_sock.setblocking(False)
        self.old_fd = signal.set_wakeup_fd(self.write_sock.fileno())
        # First Python code executed gets any exception from
        # the signal handler, so add a dummy handler first
        self.readyRead.connect(lambda: None, None)
        # Second handler does the real handling
        # noinspection PyUnresolvedReferences
        self.readyRead.connect(self._read_signal, None)

    def __del__(self):
        # Restore any old handler on deletion
        if self.old_fd is not None and signal and signal.set_wakeup_fd:
            signal.set_wakeup_fd(self.old_fd)

    def _read_signal(self):
        # Read the written byte.
        # Note: readyRead is blocked from occurring again until readData()
        # was called, so call it, even if you don't need the value.
        data = self.readData(1)
        # Emit a Qt signal for convenience
        self.signalReceived.emit(data[0])

    signalReceived = QtCore.pyqtSignal(int)


class SvgWidget(QtSvg.QSvgWidget):
    location_changed = QtCore.pyqtSignal(QtCore.QPointF)

    def update_view_box(self, size):
        w = self.scale * size.width()
        h = self.scale * size.height()
        r = QtCore.QRectF(self.center_x - w / 2, self.center_y - h / 2,
                          w, h)
        self.renderer().setViewBox(r)

    def center(self):
        self.scale = max(float(self.defViewBox.width()) / self.width(),
                         float(self.defViewBox.height()) / self.height())
        self.center_x = self.defViewBox.center().x()
        self.center_y = self.defViewBox.center().y()
        self.update_view_box(self.size())
        self.repaint()

    def reload(self):
        QtSvg.QSvgWidget.load(self, self.path)
        self.defViewBox = self.renderer().viewBoxF()
        self.update_view_box(self.size())

    def resizeEvent(self, evt):
        self.update_view_box(evt.size())
        QtSvg.QSvgWidget.resizeEvent(self, evt)

    def __init__(self, path):
        QtSvg.QSvgWidget.__init__(self)
        self.path = path
        self.watch = QtCore.QFileSystemWatcher(self)
        self.watch.addPath(self.path)
        self.watch.fileChanged.connect(self.reload, None)

        self.setMouseTracking(True)
        self.ds = None
        self.scale = 0
        self.center_x = 0
        self.center_y = 0
        self.start_center_x = 0
        self.start_center_y = 0
        self.setPalette(QtGui.QPalette(QtCore.Qt.white))
        self.setAutoFillBackground(True)
        QtSvg.QSvgWidget.load(self, path)
        self.defViewBox = self.renderer().viewBoxF()
        self.center()

    def update_location(self, pos):
        self.location_changed.emit(QtCore.QPointF(
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


class MainWindow(QtWidgets.QMainWindow):

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
        path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            filter="Svg documents (*.svg);;Any files (*.*)"
        )
        if path:
            self.load(path)

    def create_actions(self):
        self.actions[ActionTypes.OPEN] = QtWidgets.QAction(self)
        self.actions[ActionTypes.OPEN].setShortcuts(QtGui.QKeySequence.Open)
        self.actions[ActionTypes.QUIT] = QtWidgets.QAction(self)
        self.actions[ActionTypes.QUIT].setShortcuts(QtGui.QKeySequence.Quit)
        self.actions[ActionTypes.CLOSE] = QtWidgets.QAction(self)
        self.actions[ActionTypes.CLOSE].setShortcuts(QtGui.QKeySequence.Close)
        self.actions[ActionTypes.CENTER] = QtWidgets.QAction(self)
        self.actions[ActionTypes.CENTER].setShortcuts(QtGui.QKeySequence("Space"))
        self.actions[ActionTypes.RELOAD] = QtWidgets.QAction(self)
        self.actions[ActionTypes.RELOAD].setShortcuts(QtGui.QKeySequence("F5"))
        self.actions[ActionTypes.NEXT] = QtWidgets.QAction(self)
        self.actions[ActionTypes.NEXT].setShortcuts(QtGui.QKeySequence("Page Down"))
        self.actions[ActionTypes.PREV] = QtWidgets.QAction(self)
        self.actions[ActionTypes.PREV].setShortcuts(QtGui.QKeySequence("Page Up"))

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tab_close, None)
        self.setCentralWidget(self.tabs)
        self.resize(800, 600)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.actions = {}

        self.menubar = QtWidgets.QMenuBar(self)
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuEdit = QtWidgets.QMenu(self.menubar)
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

        self.actionCenter.triggered.connect(self.center)
        self.actionReload.triggered.connect(self.reload)
        self.actionNext.triggered.connect(self.tab_next)
        self.actionPrev.triggered.connect(self.tab_prev)
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self.open)
        self.actionClose.triggered.connect(self.tab_close)

        self.setWindowTitle("Svg Viewer")
        self.menuFile.setTitle("&File")
        self.menuEdit.setTitle("&Edit")
        self.actionOpen.setText("&Open")
        self.actionClose.setText("&Close Tab")
        self.actionQuit.setText("&Quit")
        self.actionCenter.setText("&Center")
        self.actionReload.setText("&Reload")
        self.actionNext.setText("&Next Tab")
        self.actionPrev.setText("&Prev Tab")


def view_svgs(filenames: List[str]):
    app = QtWidgets.QApplication(sys.argv)
    SignalWakeupHandler(app)
    signal.signal(signal.SIGINT, lambda sig, _: app.quit())

    window = MainWindow()
    window.show()

    for filename in filenames:
        window.load(filename)

    sys.exit(app.exec_())
