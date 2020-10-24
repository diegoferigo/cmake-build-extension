import sys
from pathlib import Path
from setuptools import setup
from cmake_build_extension import BuildExtension, CMakeExtension


with open(Path(__file__).parent.absolute() / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mymath',
    author="Diego Ferigo",
    author_email="dgferigo@gmail.com",
    description="Example to show how to use cmake-build-extension with CMake, SWIG and NumPy",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/diegoferigo/cmake-build-extension',
    keywords="setuptools extension cmake build package pypi swig",
    license="MIT",
    platforms=['any'],
    python_requires='>=3.6',
    ext_modules=[
        CMakeExtension(name='mymath',
                       install_prefix="mymath",
                       source_dir=str(Path(".").absolute()),
                       cmake_configure_options=[
                           f"-DPython3_ROOT_DIR={Path(sys.prefix)}",
                           "-DCALL_FROM_SETUP_PY:BOOL=ON",
                           "-DBUILD_SHARED_LIBS:BOOL=OFF",
                       ]),
    ],
    cmdclass=dict(build_ext=BuildExtension),
    zip_safe=False,
)
