import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mdfreader-helper",
    version="0.0.1",
    author="H.Yu",
    author_email="haoyang_yu123@yahoo.com",
    description="Extention to the python lib 'mdfreader', for finding/parsing/preprocessing the data from .dat/.mdf files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Siuuuu7/mdfreader-helper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)