import config.project

package_name = config.project.project_name

console_scripts = [
    "pysvgview=pysvgview.main:main",
]

install_requires = [
    "PyQt5",
    "pytconf",
    "pylogconf",
]

test_requires = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "pymakehelper",
]

dev_requires = [
    "pyclassifiers",
    "pypitools",
    "pydmt",
    "Sphinx",
    "PyQt5-stubs",
]

python_requires = ">=3.9"
test_os = ["ubuntu-20.04"]
test_python = ["3.9"]
