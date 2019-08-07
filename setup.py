import os.path
import re
import setuptools


# Find the version number
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(here, *parts), 'r', encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Load README
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zkviz",
    version=find_version("zkviz", "__init__.py"),
    author="Alexandre Chabot-Leclerc",
    author_email="github@alexchabot.net",
    description="Zettel Network Visualizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zettelkasten-Method/zkviz",
    packages=setuptools.find_packages(),
    install_requires=[
        'graphviz',
        'plotly',
        'numpy',
        'scipy',
        'networkx',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'zkviz = zkviz.zkviz:main'
        ]
    }
)
