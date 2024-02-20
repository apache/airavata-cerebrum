import os

from setuptools import setup, find_packages


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='cybershuttle-neuro-lib',
    long_description_content_type="text/markdown",
    version='0.0.1',
    packages=find_packages(),
    package_data={'': ['*.pem','*.md']},
    include_package_data=True,
    url='https://neuroscience.cybershuttle.org/',
    license='Apache License 2.0',
    author='Cybershuttle Developers',
    author_email='dev@airavata.apache.org',
    install_requires=['airavata-python-sdk==1.1.6', 'ipywidgets'],
    description='Cybershuttle neuroscience libraries',
    long_description=long_description,
)