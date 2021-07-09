import inspect
import sys
from pathlib import Path

import cmake_build_extension
import setuptools

init_py = inspect.cleandoc(
    """
    import cmake_build_extension

    with cmake_build_extension.build_extension_env():
        from . import bindings
    """
)

setuptools.setup(
    ext_modules=[
        cmake_build_extension.CMakeExtension(
            name="SwigBindings",
            install_prefix="mymath_swig",
            expose_binaries=["bin/print_answer"],
            write_top_level_init=init_py,
            source_dir=str(Path(__file__).parent.absolute()),
            cmake_configure_options=[
                f"-DPython3_ROOT_DIR={Path(sys.prefix)}",
                "-DCALL_FROM_SETUP_PY:BOOL=ON",
                "-DBUILD_SHARED_LIBS:BOOL=OFF",
                "-DEXAMPLE_WITH_SWIG:BOOL=ON",
                "-DEXAMPLE_WITH_PYBIND11:BOOL=OFF",
            ],
        ),
        cmake_build_extension.CMakeExtension(
            name="Pybind11Bindings",
            install_prefix="mymath_pybind11",
            cmake_depends_on=["pybind11"],
            expose_binaries=["bin/print_answer"],
            write_top_level_init=init_py,
            source_dir=str(Path(__file__).parent.absolute()),
            cmake_configure_options=[
                f"-DPython3_ROOT_DIR={Path(sys.prefix)}",
                "-DCALL_FROM_SETUP_PY:BOOL=ON",
                "-DBUILD_SHARED_LIBS:BOOL=OFF",
                "-DEXAMPLE_WITH_SWIG:BOOL=OFF",
                "-DEXAMPLE_WITH_PYBIND11:BOOL=ON",
            ],
        ),
    ],
    cmdclass=dict(build_ext=cmake_build_extension.BuildExtension),
)
