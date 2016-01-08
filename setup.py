from setuptools import setup, find_packages
import pybitx

setup(
    name='pybitx',
    version=pybitx.__version__,
    packages=find_packages(exclude=['tests']),
    description='A BitX API for Python',
    author='Cayle Sharrock',
    author_email='cayle@nimbustech.biz',
    scripts=['demo.py'],
    install_requires=[
        'nose>=1.3.7',
        'requests>=2.8.1',
        'pandas>=0.17.0'
    ],
    license='MIT',
    url='https://github.com/CjS77/pybitx',
    download_url='https://github.com/CjS77/pybitx/tarball/%s' % (pybitx.__version__, ),
    keywords='BitX Bitcoin exchange API',
    classifiers=[],
    test_suite='tests',
    tests_require=[
        'requests-mock>=0.7.0'
    ]
)
