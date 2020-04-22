#!/usr/bin/env python
from setuptools import setup

requirements = None
with open("requirements.txt", r) as _f:
    requirements = _f.readlines()

setup(
    name="application",
    packages=["application"],
    include_package_data=True,
    install_requires=requirements,
)
