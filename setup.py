import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="zkviz",
    version="0.1",
    author="Alexandre Chabot-Leclerc",
    author_email="github@alexchabot.net",
    description="Zettel Network Visualizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zettelkasten-Method/zkviz",
    packages=setuptools.find_packages(),
    install_requires=[
        'graphviz',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
