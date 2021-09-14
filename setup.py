# -*- coding: utf-8 -*-
"""
可以通过下面命令安装
python3 setup.py install
"""
from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open('LICENSE', encoding='utf-8') as f:
    lic = f.read()

setup(
    name='flynnBot',

    version='0.1.1',

    description='A green trading robot',

    long_description=long_description,

    long_description_content_type="text/markdown",

    author='Flynn Ma',

    author_email='shmayunfei@qq.com',

    url='https://github.com/FlynnMa/quantBot',

    license=lic,

    packages=find_packages(
        include=['flynnBot', 'samples'],
        exclude=['tests', 'docs']
    ),
    install_requires=[
        'pandas>=1.0.0',
        'pandas_datareader>=0.8.0',
        'numpy>=1.18.0',
        'matplotlib >= 3.0.0'
    ],
    tests_require=['pytest'],
    test_suite='tests',
)
