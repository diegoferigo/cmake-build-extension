from pathlib import Path
from setuptools import find_packages, setup


with open(Path(__file__).parent.absolute() / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cmake-build-extension',
    author="Diego Ferigo",
    author_email="dgferigo@gmail.com",
    description="Setuptools extension to build and package CMake projects",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/diegoferigo/cmake-build-extension',
    keywords="setuptools extension cmake build package pypi",
    license="MIT",
    platforms=['any'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Packaging",
    ],
    use_scm_version=dict(local_scheme="dirty-tag"),
    setup_requires=['setuptools_scm'],
    python_requires='>=3.6',
    packages=find_packages("src"),
    package_dir={'': "src"},
    zip_safe=False,
)
