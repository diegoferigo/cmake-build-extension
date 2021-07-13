# cmake-build-extension

[![Version](https://img.shields.io/pypi/v/cmake-build-extension.svg)][pypi]
[![Python versions](https://img.shields.io/pypi/pyversions/cmake-build-extension.svg)][pypi]
[![Status](https://img.shields.io/pypi/status/cmake-build-extension.svg)][pypi]
[![Format](https://img.shields.io/pypi/format/cmake-build-extension.svg)][pypi]
[![License](https://img.shields.io/pypi/l/cmake-build-extension.svg)][pypi]
[![Python CI/CD](https://github.com/diegoferigo/cmake-build-extension/workflows/Python%20CI/CD/badge.svg)][ci_cd]

[pypi]: https://pypi.org/project/cmake-build-extension/
[ci_cd]: https://github.com/diegoferigo/cmake-build-extension/actions/workflows/python.yml

**Setuptools extension to build and package CMake projects.**

This projects aims to simplify the integration of C++ projects based on CMake with Python packaging tools.
CMake provides out-of-the-box support to either [SWIG][swig] and [pybind11][pybind11],
that are two among the most used projects to create Python bindings from C++ sources.

[swig]: https://github.com/swig/swig
[pybind11]: https://github.com/pybind/pybind11

If you have any experience with these hybrid projects, you know the challenges to make packaging right!
This project takes inspiration from pre-existing examples 
([`pybind/cmake_example`][pybind11_example], among many others)
and provides a simple, flexible, and reusable setuptools extension with the following features:

- Bridge between CMake projects and Python packaging.
- Configure and build the CMake project from `setup.py`. 
- Install the CMake project in the resulting Python package.
- Allow passing custom CMake options.
- Allow creating a top-level `__init__.py`.
- Expose C++ executables to the Python environment.
- Provide a context manager to import reliably CPython modules on all major OSs.
- Disable the C++ extension in editable installations (requiring to manually call CMake to install the C++ project).

[pybind11_example]: https://github.com/pybind/cmake_example

Have a look to the [example](example/) for an overview of what can be done with this extension.
It shows how to create SWIG and pybind11 bindings for a project composed by a small C++ library with NumPy support 
and an executable. 

### Advanced features

1. This extension supports creating packages [PEP517] and [PEP518] compliant ([more details][pyproject]).
2. If the CMake project [exports the targets][export_targets], downstream projects can:
   1. Extend their `CMAKE_MODULE_PATH` with the root of your installed Python package,
      that could be obtained with:
      ```bash
      python -c "import <pkg>, pathlib; print(pathlib.Path(<pkg>.__file__).parent)"
      ```
      and consume the exported CMake targets.
   1. Use `cmake-build-extension` with the `cmake_depends_on` option and link against the exported CMake targets
      during the downstream packaging.

Note that the second feature allows distributing C++ dependencies through PyPI.
The resulting package structure is similar to other projects like [pybind11][pybind11_pypi] and [CasADi][casadi_pypi].
Be aware that ensuring ABI compatibility could be problematic in edge cases, 
and the usage of a proper [compatible release pattern][pep440] (`~=`) could be necessary.

[pep440]: https://www.python.org/dev/peps/pep-0440/#compatible-release
[pep517]: https://www.python.org/dev/peps/pep-0517/
[pep518]: https://www.python.org/dev/peps/pep-0518/

[pyproject]: https://snarky.ca/what-the-heck-is-pyproject-toml/
[export_targets]: https://cmake.org/cmake/help/git-stage/guide/importing-exporting/index.html

[pybind11_pypi]: https://pypi.org/project/pybind11/
[casadi_pypi]: https://pypi.org/project/casadi/

## Installation

From PyPI:

```bash
pip install cmake-build-extension
```

From the repository:

```bash
pip install git+https://github.com/diegoferigo/cmake-build-extension
```

## Usage

Once both CMake project and `setup.py|setup.cfg|pyproject.toml` of your hybrid package are correctly configured
to use the resources provided by cmake-build-extension, the following commands can be used:

```bash
# ============
# Create sdist
# ============

# Calling setup.py
python setup.py sdist

# Using pypa/build
python -m build --sdist

# ============
# Create wheel
# ============

# Calling setup.py
python setup.py bdist_wheel

# Using pip
pip wheel -w dist/ .

# Using pypa/build
python -m build --wheel

# ==========================================================
# Create wheel or install package passing additional options
# ==========================================================

# Calling setup.py
python setup.py {bdist_wheel|install} build_ext -D"BAR=Foo;VAR=TRUE"

# Using pip
pip {wheel|install} --global-option="build_ext" --global-option="-DBAR=Foo;VAR=TRUE" .

# Using pypa/build (only wheel creation)
python -m build --wheel "-C--global-option=build_ext" "-C--global-option=-DBAR=Foo;VAR=TRUE"
```

## Caveats

### `manylinux*` support

This extension, beyond packaging the hybrid C++ / Python project, 
also allows the inclusion of the exported CMake targets in the resulting wheel.
This result depends on how the CMake project is configured, 
and whether the [exported targets][exp_imp_wiki] are installed together with the other files.

[exp_imp_wiki]: https://gitlab.kitware.com/cmake/community/-/wikis/doc/tutorials/Exporting-and-Importing-Targets

Such hybrid packages can then be uploaded to PyPI. 
Though, on GNU/Linux, the generated wheel is not compliant by default with any [`manylinux*`][manylinux] standard.
Tools such [auditwheel][auditwheel] exist to fix these wheels, but they require running on selected distributions.
Luckily, other projects like [cibuildwheel][cibuildwheel] greatly simplify the process in CI.

[manylinux]: https://github.com/pypa/manylinux
[auditwheel]: https://github.com/pypa/auditwheel
[cibuildwheel]: https://github.com/joerick/cibuildwheel

This being said, `manylinux*` guidelines could still work against you.
In fact, wheels supporting `manylinux2010|manylinux2014` are built [with gcc4][pep599_manylinux2014] 
that does not support the new C++11 ABIs.
In few words, this means that the exported libraries bundled in the wheel cannot 
be imported in a downstream project using relatively new C++ standards!
For more details visit [robotology/idyntree#776](https://github.com/robotology/idyntree/issues/776). 

[pep599_manylinux2014]: https://www.python.org/dev/peps/pep-0599/#the-manylinux2014-policy

Luckily, the situation changed thanks to the finalization of [PEP600][pep600], i.e. `manylinuxX_YY` :tada: 
If you build a PEP600 compliant wheel (nowadays compatible with most of the commonly used distributions), 
your exported CMake project bundled in the wheel can be successfully imported downstream.
If you want to support this use case, make sure to produce and distribute wheels compliant with PEP600.

[pep600]: https://www.python.org/dev/peps/pep-0600/

### Loading CPython modules in Windows

Python 3.8 [changed][changelog_3_8] how DLL are resolved.
By default, modules that could be imported in Python 3.7 stopped working, and using the new 
[`os.add_dll_directory`][add_dll_directory] is now necessary.

In order to streamline the process, `cmake-build-extension` implements a context manager that can be used 
to import reliably the bindings module:

```python
import cmake_build_extension

with cmake_build_extension.build_extension_env():
    from . import bindings
```

It will take care to temporarily fix the search path.

For more details, refer to [#8][windows_import_issue] and [#12][windows_import_pr].

[changelog_3_8]: https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew
[add_dll_directory]: https://docs.python.org/3/library/os.html#os.add_dll_directory
[windows_import_issue]: https://github.com/diegoferigo/cmake-build-extension/issues/8
[windows_import_pr]: https://github.com/diegoferigo/cmake-build-extension/pull/12

### `setup.py|setup.cfg|pyproject.toml` files in subfolder

Sometimes hybrid projects are C++ centric, and keeping these files in the top-level folder is not desirable.
In this setup, however, problems occur if the main `CMakeLists.txt` is kept in the top-level folder 
(see [pypa/build#322][sdist_issue]).
To solve this problem, `cmake-build-extension` provides custom commands to create source distribution.
You can use one of the following custom `sdist` options in `setup.py`:

```python
setuptools.setup(
    cmdclass=dict(
        # [...]
        # Pack the whole git folder:
        sdist=cmake_build_extension.GitSdistFolder,
        # Pack only the git tree:
        sdist=cmake_build_extension.GitSdistTree,
        # Or, inherit from cmake_build_extension.sdist_command.GitSdistABC and
        # make your own custom sdist including only the files you are interested
    ),
)
```

[sdist_issue]: https://github.com/pypa/build/issues/322

## Downstream projects

If the provided example is not enough complex, find here below a list of projects using `cmake-build-extension`: 

- [`robotology/idyntree`](https://github.com/robotology/idyntree/)
- [`robotology/yarp`](https://github.com/robotology/yarp/)
- [`robotology/ycm`](https://github.com/robotology/ycm/)
- [`diegoferigo/gazebo-yarp-synchronizer`](https://github.com/diegoferigo/gazebo-yarp-synchronizer)
- [`robotology/gym-ignition@scenario`](https://github.com/robotology/gym-ignition/tree/devel/scenario)
- [`dic-iit/gazebo-scenario-plugins`](https://github.com/dic-iit/gazebo-scenario-plugins/)
- [`dic-iit/bipedal-locomotion-framework`](https://github.com/dic-iit/bipedal-locomotion-framework)
- [`artivis/manif`](https://github.com/artivis/manif)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
