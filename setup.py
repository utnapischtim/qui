import os

from setuptools import find_packages, setup

install_requires = [
    "click",
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("qui", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="qui",
    version=version,
    packages=packages,
    entry_points={
        "console_scripts": [
            "qui = qui.cli:qui",
        ]
    },
    install_requires=install_requires,
)
