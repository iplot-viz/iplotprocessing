import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proc",
    version="0.0.1",
    author="Abadie Lana EXT",
    author_email="lana.abadie@iter.org",
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
    packages=setuptools.find_namespace_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        "logging2 >= 0.0.1",
        "numpy >= 1.20.0",
    ]
)
