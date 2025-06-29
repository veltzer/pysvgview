""" python deps for this project """

scripts: dict[str,str] = {
    "pysvgview": "pysvgview.main:main",
}

config_requires: list[str] = [
    "pyclassifiers",
]
install_requires: list[str] = [
    # "PyQt6-stubs",
    "PyQt6",
    "PySide6",
    "pytconf",
    "pylogconf",
]
build_requires: list[str] = [
    "hatch",
    "pydmt",
    "pymakehelper",
    "pycmdtools",
]
test_requires: list[str] = [
    "pylint",
    "pytest",
    "mypy",
    "ruff",
]
requires = config_requires + install_requires + build_requires + test_requires
