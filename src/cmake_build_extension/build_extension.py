import shutil
import platform
import subprocess
from pathlib import Path
from .cmake_extension import CMakeExtension
from setuptools.command.build_ext import build_ext
from .build_ext_option import add_new_build_ext_option, BuildExtOption


custom_options = [
    BuildExtOption(variable="define=", short="D",
                   help="Create or update CMake cache "
                        "(concatenate options with '-DBAR=b;FOO=f')")
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
            raise RuntimeError(f"Required command 'cmake' not found")

        # Check that Ninja is installed
        if shutil.which("ninja") is None:
            raise RuntimeError(f"Required command 'ninja' not found")

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
            f"-GNinja",
            f"-DCMAKE_BUILD_TYPE={ext.cmake_build_type}",
            f"-DCMAKE_INSTALL_PREFIX:PATH={cmake_install_prefix}",
        ]

        # Extend the configure arguments with those passed from the extension
        configure_args += ext.cmake_configure_options

        # CMake build arguments
        build_args = [
            '--config', ext.cmake_build_type
        ]

        # CMake install target
        install_target = "install"

        if platform.system() == "Windows":

            configure_args += [
            ]

        elif platform.system() in {"Linux", "Darwin"}:

            configure_args += [
            ]

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
        build_folder = str(Path('.').absolute() / f"{self.build_temp}_{ext.name}")

        # Make sure that the build folder exists
        Path(build_folder).mkdir(exist_ok=True, parents=True)

        # 1. Compose CMake configure command
        configure_command = \
            ['cmake', '-S', ext.source_dir, '-B', build_folder] + configure_args

        # 2. Compose CMake build command
        build_command = ['cmake', '--build', build_folder] + build_args

        # 3. Compose CMake install command
        install_command = ['cmake', '--build', build_folder, '--target', install_target]

        print(f"")
        print(f"==> Configuring:")
        print(f"$ {' '.join(configure_command)}")
        print(f"")
        print(f"==> Building:")
        print(f"$ {' '.join(build_command)}")
        print(f"")
        print(f"==> Installing:")
        print(f"$ {' '.join(install_command)}")
        print("")

        # Call CMake
        subprocess.check_call(configure_command)
        subprocess.check_call(build_command)
        subprocess.check_call(install_command)
