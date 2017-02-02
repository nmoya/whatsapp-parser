#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    import codecs
    long_description = codecs.open('README.rst', 'r', encoding='utf-8').read()

version = '1.0.0'

setup(
    name='whatsapp parser',
    version=version,
    author='Nikolas Moya',
    author_email='nikolasmoya@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/nmoya/whatsapp-parser',
    license='MIT',
    description='',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'wp_parser=wp_parser.chat:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
