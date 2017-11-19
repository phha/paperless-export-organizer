#!/usr/bin/env python
from setuptools import setup

setup(
    name='paperless_export_organizer',
    version='0.1.0',
    py_modules=['paperless_export_organizer'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        paperless_export_organizer=paperless_export_organizer:paperless_export_organizer''',
)
