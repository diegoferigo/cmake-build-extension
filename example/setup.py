import inspect
import sys
from pathlib import Path

from cmake_build_extension import BuildExtension, CMakeExtension
import setuptools

init_py = inspect.cleandoc(
    """
    from cmake_build_extension import build_extension_env

    with build_extension_env():
        from . import bindings
    """
)

setuptools.setup(
    ext_modules=[
        CMakeExtension(
            name="mymath",
            install_prefix="mymath",
            expose_binaries=["bin/print_answer"],
            write_top_level_init=init_py,
            source_dir=str(Path(__file__).parent.absolute()),
            cmake_configure_options=[
                f"-DPython3_ROOT_DIR={Path(sys.prefix)}",
                "-DCALL_FROM_SETUP_PY:BOOL=ON",
                "-DBUILD_SHARED_LIBS:BOOL=OFF",
                "-DEXAMPLE_WITH_SWIG:BOOL=ON",
            ],
        ),
    ],
    cmdclass=dict(build_ext=BuildExtension),
)
