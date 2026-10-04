# TOFIX

Findings from a code scan on 2026-10-04.

## High

- `src/pysvgview/svg_view.py:17` - `QSvgWidget` comes from PySide6 while every other Qt class (QApplication, QTabWidget, pyqtSignal, ...) comes from PyQt6. The two bindings cannot be mixed: `QTabWidget.addTab()` in `MainWindow.load()` (line 122) rejects the widget with `TypeError: argument 1 has unexpected type 'PySide6.QtSvgWidgets.QSvgWidget'` (reproduced in the repo venv), so the viewer cannot open any file. Import `QSvgWidget` from `PyQt6.QtSvgWidgets` (available in the installed PyQt6) and drop `PySide6` from `pyproject.toml:36`.
- `src/pysvgview/svg_view.py:82` - `wheelEvent` calls `evt.pos()`, which does not exist on Qt6 `QWheelEvent` (removed in Qt 6; `hasattr(QWheelEvent, "pos")` is False for both PyQt6 and PySide6), so every mouse-wheel zoom raises AttributeError. Use `evt.position()` (QPointF) here and at line 90; the `QMouseEvent.pos()` calls at lines 94-104 are deprecated in Qt6 too.
- `src/pysvgview/svg_view.py:150` - `QFileDialog.getOpenFileName()` returns a `(path, selected_filter)` tuple, so `if path:` is always true and `self.load(path)` passes a tuple to `SvgWidget`, breaking File > Open (and cancelling the dialog also "loads" `('', '')`). Unpack: `path, _ = QFileDialog.getOpenFileName(...)`.

## Medium

- `src/pysvgview/svg_view.py:195` - the Close action is added to the File menu twice (lines 195-196) and the Quit action, though created and connected (line 208), is never added to any menu; the second line should add `ActionTypes.QUIT`.
- `src/pysvgview/svg_view.py:179` - tabs are made closable (line 178) but the `tabCloseRequested` connection is commented out, so the close buttons on tabs do nothing. Connect it (to a handler that takes the tab index), or turn closable tabs off. All keyboard shortcuts (lines 160-172) are likewise commented out.

## Low

- `src/pysvgview/configs.py:9` - `ConfigDummy` ("Parameters for nothing") is never imported or used anywhere; remove the leftover module.
- `src/pysvgview/svg_view.py:1` - module docstring opens with four quotes (`""""`), so the docstring text starts with a stray `"`. Use three.
- `pyproject.toml:25` - classifier "Environment :: Console" for a Qt GUI application; use "Environment :: X11 Applications :: Qt".
