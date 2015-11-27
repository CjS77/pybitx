from setuptools import setup, find_packages
import pybitx

setup(
    name='mypackage',
    version=pybitx.__version__,
    packages=find_packages(),
    description='A BitX API for Python',
    author='Cayle Sharrock',
    author_email='cayle@nimbustech.biz',
    url='https://github.com/CjS77/pybitx',  # use the URL to the github repo
    download_url='https://github.com/CjS77/pybitx/tarball/0.1',  # I'll explain this in a second
    keywords=['BitX', 'Bitcoin', 'exchange', 'API'],  # arbitrary keywords
    classifiers=[],
)
