#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def read_requirements(filename):
    with open(filename) as requirements:
        return [requirement.strip() for requirement in requirements.readlines()]

config = {
    'name': 'Kjernekar',
    'version': '0.0.1',
    'description': 'A simple Slackbot for Kjerneteamet',
    'author': 'Sindre R. Bilden',
    'author_email': 'sindrebilden@gmail.com',
    'licence': 'LICENCE.md',
    'url': 'https://github.com/sindrebilden/kjernekar',
    'download': 'https://github.com/sindrebilden/kjernekar/releases',
    'install_requires': read_requirements('requirements.txt'),
    'scripts': ['bin/run.py']
}

setup(**config)
