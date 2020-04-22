#!/usr/bin/env python
from setuptools import setup

setup(
    name="application",
    packages=["application"],
    include_package_data=True,
    install_requires=[
        "Flask==1.1.1",
        "pandas==1.0.3",
        "requests==2.23.0",
        "xlrd==1.2.0",
    ],
)
