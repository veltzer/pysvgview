import setuptools


def get_readme():
    with open("README.rst") as f:
        return f.read()


setuptools.setup(
    # the first three fields are a must according to the documentation
    name="pysvgview",
    version="0.0.5",
    packages=[
        "pysvgview",
    ],
    # from here all is optional
    description="pysvgview is an SVG viewer",
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
    author="Mark Veltzer",
    author_email="mark.veltzer@gmail.com",
    maintainer="Mark Veltzer",
    maintainer_email="mark.veltzer@gmail.com",
    keywords=[
        "svg",
        "view",
        "qt",
    ],
    url="https://veltzer.github.io/pysvgview",
    download_url="https://github.com/veltzer/pysvgview",
    license="MIT",
    platforms=[
        "python3",
    ],
    install_requires=[
        "PyQt6",
        "PySide6",
        "pytconf",
        "pylogconf",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"console_scripts": [
        "pysvgview=pysvgview.main:main",
    ]},
)
