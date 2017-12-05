import os
import re

from setuptools import setup, find_packages


# Extract the version from the main package __init__ file
PATTERN = '__version__\s+=\s+(?P<version>.*)'
BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, 'pybitx/__init__.py'), 'r') as f:
  match = re.search(PATTERN, f.read())

if match is None:
    raise ValueError("failed to extract package version")

version = match.groupdict()['version']


setup(
    name='pybitx',
    version=version,
    packages=find_packages(exclude=['tests']),
    description='A BitX API for Python',
    author='Cayle Sharrock',
    author_email='cayle@nimbustech.biz',
    scripts=['demo.py'],
    install_requires=[
        'futures>=3.0.3',
        'nose>=1.3.7',
        'requests>=2.8.1',
        'pandas>=0.17.0'
    ],
    license='MIT',
    url='https://github.com/CjS77/pybitx',
    download_url='https://github.com/CjS77/pybitx/tarball/%s' % (version, ),
    keywords='BitX Bitcoin exchange API',
    classifiers=[],
    test_suite='tests',
    extras_require={'dev': ['requests-mock>=0.7.0']}
)
