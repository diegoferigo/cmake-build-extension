import importlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools.command.build_ext import build_ext

from .build_ext_option import BuildExtOption, add_new_build_ext_option
from .cmake_extension import CMakeExtension

custom_options = [
    BuildExtOption(
        variable="define=",
        short="D",
        help="Create or update CMake cache "
        "(concatenate options with '-DBAR=b;FOO=f')",
    )
]

for o in custom_options:
    add_new_build_ext_option(option=o, override=True)


class BuildExtension(build_ext):
    """
    Setuptools build extension handler.
    It processes all the extensions listed in the 'ext_modules' entry.
    """

    def initialize_options(self):

        # Initialize base class
        build_ext.initialize_options(self)

        # Override define. This is supposed to pass C preprocessor macros, but we use it
        # to pass custom options to CMake.
        self.define = None

    def finalize_options(self):

        # Parse the custom CMake options and store them in a new attribute
        defines = self.define.split(";") if self.define is not None else []
        self.cmake_defines = [f"-D{define}" for define in defines]

        # Call base class
        build_ext.finalize_options(self)

    def run(self) -> None:
        """
        Process all the registered extensions executing only the CMakeExtension objects.
        """

        # Filter the CMakeExtension objects
        cmake_extensions = [e for e in self.extensions if isinstance(e, CMakeExtension)]

        if len(cmake_extensions) == 0:
            raise ValueError("No CMakeExtension objects found")

        # Check that CMake is installed
        if shutil.which("cmake") is None:
            raise RuntimeError("Required command 'cmake' not found")

        # Check that Ninja is installed
        if shutil.which("ninja") is None:
            raise RuntimeError("Required command 'ninja' not found")

        for ext in cmake_extensions:
            self.build_extension(ext)

    def build_extension(self, ext: CMakeExtension) -> None:
        """
        Build a CMakeExtension object.

        Args:
            ext: The CMakeExtension object to build.
        """

        if self.inplace and ext.disable_editable:
            print(f"Editable install recognized. Extension '{ext.name}' disabled.")
            return

        # Export CMAKE_PREFIX_PATH of all the dependencies
        for pkg in ext.cmake_depends_on:

            try:
                importlib.import_module(pkg)
            except ImportError:
                raise ValueError(f"Failed to import '{pkg}'")

            init = importlib.util.find_spec(pkg).origin
            BuildExtension.extend_cmake_prefix_path(path=str(Path(init).parent))

        # The ext_dir directory can be thought as a temporary site-package folder.
        #
        # Case 1: regular installation.
        #   ext_dir is the folder that gets compressed to make the wheel archive. When
        #   installed, the archive is extracted in the active site-package directory.
        # Case 2: editable installation.
        #   ext_dir is the in-source folder containing the Python packages. In this case,
        #   the CMake project is installed in-source.
        ext_dir = Path(self.get_ext_fullpath(ext.name)).parent.absolute()
        cmake_install_prefix = ext_dir / ext.install_prefix

        # CMake configure arguments
        configure_args = [
            "-GNinja",
            f"-DCMAKE_BUILD_TYPE={ext.cmake_build_type}",
            f"-DCMAKE_INSTALL_PREFIX:PATH={cmake_install_prefix}",
        ]

        # Extend the configure arguments with those passed from the extension
        configure_args += ext.cmake_configure_options

        # CMake build arguments
        build_args = ["--config", ext.cmake_build_type]

        if platform.system() == "Windows":

            configure_args += []

        elif platform.system() in {"Linux", "Darwin"}:

            configure_args += []

        else:
            raise RuntimeError(f"Unsupported '{platform.system()}' platform")

        # Parse the optional CMake options. They can be passed as:
        #
        # python setup.py build_ext -D"BAR=Foo;VAR=TRUE"
        # python setup.py bdist_wheel build_ext -D"BAR=Foo;VAR=TRUE"
        # python setup.py install build_ext -D"BAR=Foo;VAR=TRUE"
        # python setup.py install -e build_ext -D"BAR=Foo;VAR=TRUE"
        # pip install --global-option="build_ext" --global-option="-DBAR=Foo;VAR=TRUE" .
        #
        configure_args += self.cmake_defines

        # Get the absolute path to the build folder
        build_folder = str(Path(".").absolute() / f"{self.build_temp}_{ext.name}")

        # Make sure that the build folder exists
        Path(build_folder).mkdir(exist_ok=True, parents=True)

        # 1. Compose CMake configure command
        configure_command = [
            "cmake",
            "-S",
            ext.source_dir,
            "-B",
            build_folder,
        ] + configure_args

        # 2. Compose CMake build command
        build_command = ["cmake", "--build", build_folder] + build_args

        # 3. Compose CMake install command
        install_command = ["cmake", "--install", build_folder]
        if ext.cmake_component is not None:
            install_command.extend(["--component", ext.cmake_component])

        print("")
        print("==> Configuring:")
        print(f"$ {' '.join(configure_command)}")
        print("")
        print("==> Building:")
        print(f"$ {' '.join(build_command)}")
        print("")
        print("==> Installing:")
        print(f"$ {' '.join(install_command)}")
        print("")

        # Call CMake
        subprocess.check_call(configure_command)
        subprocess.check_call(build_command)
        subprocess.check_call(install_command)

        # Write content to the top-level __init__.py
        if ext.write_top_level_init is not None:
            with open(file=cmake_install_prefix / "__init__.py", mode="w") as f:
                f.write(ext.write_top_level_init)

        # Write content to the bin/__main__.py magic file to expose binaries
        if len(ext.expose_binaries) > 0:
            bin_dirs = {str(Path(d).parents[0]) for d in ext.expose_binaries}

            import inspect

            main_py = inspect.cleandoc(
                f"""
                from pathlib import Path
                import subprocess
                import sys

                def main():

                    binary_name = Path(sys.argv[0]).name
                    prefix = Path(__file__).parent.parent
                    bin_dirs = {str(bin_dirs)}

                    binary_path = ""

                    for dir in bin_dirs:
                        path = prefix / Path(dir) / binary_name
                        if path.is_file():
                            binary_path = str(path)
                            break

                        path = Path(str(path) + ".exe")
                        if path.is_file():
                            binary_path = str(path)
                            break

                    if not Path(binary_path).is_file():
                        name = binary_path if binary_path != "" else binary_name
                        raise RuntimeError(f"Failed to find binary: {{ name }}")

                    sys.argv[0] = binary_path

                    result = subprocess.run(args=sys.argv, capture_output=False)
                    exit(result.returncode)

                if __name__ == "__main__" and len(sys.argv) > 1:
                    sys.argv = sys.argv[1:]
                    main()"""
            )

            bin_folder = cmake_install_prefix / "bin"
            Path(bin_folder).mkdir(exist_ok=True, parents=True)
            with open(file=bin_folder / "__main__.py", mode="w") as f:
                f.write(main_py)

    @staticmethod
    def extend_cmake_prefix_path(path: str) -> None:

        abs_path = Path(path).absolute()

        if not abs_path.exists():
            raise ValueError(f"Path {abs_path} does not exist")

        if "CMAKE_PREFIX_PATH" in os.environ:
            os.environ[
                "CMAKE_PREFIX_PATH"
            ] = f"{str(path)}:{os.environ['CMAKE_PREFIX_PATH']}"
        else:
            os.environ["CMAKE_PREFIX_PATH"] = str(path)
