from setuptools import setup, find_packages

setup(
    name="rever-sql-query-builder",
    version="0.1.0",
    description="SQL Query builder for Rever python applications",
    author="Giovanni",
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy>=1.4"
    ],
    license="MIT",
    python_requires=">=3.7",
    url="https://github.com/reverscore/rever-python-query-builder",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
