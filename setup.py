import os
import re
import shutil
import sys

from setuptools import setup


def read_file(*paths):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, *paths)) as f:
        return f.read()


def get_version():
    version_file = read_file('pgmanager', '__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Get long_description from index.rst:
long_description = read_file('README.md')

requirements = read_file('requirements.txt')

setup(
    name='pgmanager',
    version=get_version(),
    description='Administrate a Postgres Multi-Tenancy Server',
    long_description=long_description,
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='Administrate a Postgres Multi-Tenancy Server',
    author='Nielson Santana',
    author_email='nielsonnas@gmail.com',
    maintainer='',
    license='MIT',
    py_modules=['pgmanager'],
    packages=['pgmanager'],
    install_requires=[
        requirements
    ],
    entry_points={
        'console_scripts': ['pgmanager=pgmanager:main'],
    },
    zip_safe=False,
)
