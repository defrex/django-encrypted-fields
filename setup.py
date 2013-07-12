#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
import re
import os
import sys


name = 'django-encrypted-fields'
package = 'encrypted_fields'
description = ''
url = 'http://github.com/defrex/django-encrypted-fields/'
author = 'Aron Jones'
author_email = 'aron.jones@gmail.com'
license = 'BSD'

with open('requirements.txt', 'r') as requirements:
    requires = [line.strip() for line in requirements.readlines()]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(get_version(package)))
    print("  git push --tags")
    sys.exit()


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    packages=['encrypted_fields'],
    install_requires=requires,
)
