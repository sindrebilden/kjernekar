#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

config = {
    "name": "Kjernekar",
    "version": "1.0",
    "description": "The good guy on your team",
    "author": "Sindre Rannem Bilden",
    "author_email": "sindrebilden@gmail.com",
    "license": "LICENSE.md",
    "url": "https://github.com/sindrebilden/kjernekar",
    "download_url": "https://github.com/sindrebilden/kjernekar/",
    "install_requires": ["slack_sdk", "urllib3"],
    "packages": find_packages(exclude=["tests"]),
}

setup(**config)
