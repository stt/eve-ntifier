#!/usr/bin/env python

from setuptools import setup, find_packages
DESCRIPTION = ("Simply easy declarative HTTP events for Eve")
with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

install_requires = [
    'Eve>=0.6.3'
]

setup(
    name='eve-ntifier',
    version='0.0.1',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Samuli Tuomola',
    author_email='sanuli.tuomola@gmail.com',
    url='https://github.com/stt/eve-ntifier',
    license='BSD',
    platforms=["any"],
    packages=find_packages(),
    #test_suite="eve_ntifier.tests",
    install_requires=install_requires,
    tests_require=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
