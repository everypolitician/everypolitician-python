from os.path import join, dirname
from setuptools import setup, find_packages

with open(join(dirname(__file__), 'README.rst')) as f:
    readme_text = f.read()

setup(
    name = "everypolitician",
    version = "0.0.12",
    packages = find_packages(),
    author = "Mark Longair",
    author_email = "mark@mysociety.org",
    description = "Navigate countries and legislatures from EveryPolitician",
    long_description = readme_text,
    license = "AGPL",
    keywords = "politics data civic-tech",
    install_requires = [
        'requests',
        'six >= 1.9.0',
        'everypolitician-popolo >= 0.0.10',
    ]
)
