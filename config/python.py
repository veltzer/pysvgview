from typing import List


console_scripts: List[str] = [
    "pysvgview=pysvgview.main:main",
]
config_requires: List[str] = []
dev_requires: List[str] = [
    "pypitools",
]
install_requires: List[str] = [
    # "PyQt6-stubs",
    "PyQt6",
    "PySide6",
    "pytconf",
    "pylogconf",
]
make_requires: List[str] = [
    "pyclassifiers",
    "pydmt",
    "pymakehelper",
]
test_requires: List[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "mypy",
]
requires = config_requires + install_requires + make_requires + test_requires
