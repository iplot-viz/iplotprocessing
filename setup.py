# Description: Install library, example (entry-point named iprocapp) and unit tests
# Author: Jaswant Sai Panchumarti

import setuptools
from iplotProcessing._version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iplotProcessing",
    setup_requires=[
        "setuptools-git-versioning"
    ],
    version_config={
        "version_callback": __version__,
        "template": "{tag}",
        "dirty_template": "{tag}.dev{ccount}.{sha}",
    },
    author="Panchumarti Jaswant EXT",
    author_email="jaswant.panchumarti@iter.org",
    description="Data processing for applications using IDSs or CBS",
    long_description=long_description,
    url="https://git.iter.org/scm/vis/processing.git",
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
        "iplotLogging >= 0.0.0",
        "numpy >= 1.19.0",
        "pandas >= 1.1.4"
    ],
    entry_points={
        'console_scripts': ['iprocapp = iplotProcessing.example.__main__:main']
    },
    package_data = {
        "iplotProcessing.example": ["example_inp.csv"]
    }
)
