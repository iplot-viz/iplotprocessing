# Description: Install library, example (entry-point named iprocapp) and unit tests
# Author: Jaswant Sai Panchumarti

import setuptools
import os
import sys

sys.path.append(os.getcwd())
import versioneer

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iplotProcessing",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Panchumarti Jaswant EXT",
    author_email="jaswant.panchumarti@iter.org",
    description="Data processing for applications using IDSs or CBS",
    long_description=long_description,
    url="https://github.com/iplot-viz/iplotprocessing.git",
    project_urls={
        "Bug Tracker": "https://jira.iter.org/issues/?jql=project+%3D+IDV+AND+component+%3D+Processing",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        "iplotLogging",
        "numpy >= 1.19.0",
        "scipy >= 1.5.4",
    ],
    entry_points={
        "console_scripts": ["iprocapp = iplotProcessing.example.__main__:main"]
    },
    package_data={
        "iplotProcessing.example": ["example_inp.csv"],
        "iplotProcessing.core": ["blueprint.json"],
        "iplotProcessing.tools": ["default_modules.json"]
    },
)
