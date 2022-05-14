import config.project

package_name = config.project.project_name

console_scripts = [
    "pysvgview=pysvgview.main:main",
]
dev_requires = [
    "pyclassifiers",
    "pypitools",
    "pydmt",
    "Sphinx",
]
install_requires = [
    # "PyQt6-stubs",
    "PyQt6",
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

python_requires = ">=3.10"

test_os = ["ubuntu-22.04"]
test_python = ["3.10"]
