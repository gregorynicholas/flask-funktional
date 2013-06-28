#!/usr/bin/env python
"""
flask-funktional
~~~~~~~~~~~~~~~~

flask extension which hopes to make functional testing easier.

links
`````

* `documentation <http://gregorynicholas.github.io/flask-funktional>`_
* `package <http://packages.python.org/flask-funktional>`_
* `source <http://github.com/gregorynicholas/flask-funktional>`_
* `development version
  <http://github.com/gregorynicholas/flask-funktional>`_

"""
from setuptools import setup

with open("requirements.txt", "r") as f:
  requires = f.readlines()

with open("README.md", "r") as f:
  long_description = f.read()


setup(
  name="flask-funktional",
  version="0.0.1",
  url='http://github.com/gregorynicholas/flask-funktional',
  license='MIT',
  author='gregorynicholas',
  author_email='gn@gregorynicholas.com',
  description=__doc__,
  long_description=long_description,
  py_modules=['flask_funktional'],
  zip_safe=False,
  platforms='any',
  install_requires=requires,
  tests_require=[
    'blinker==1.2',
  ],
  test_suite='flask_funktional_tests',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)
