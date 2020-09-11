import shutil
import platform
import subprocess
from pathlib import Path
from .cmake_extension import CMakeExtension
from setuptools.command.build_ext import build_ext


class BuildExtension(build_ext):
    """
    Setuptools build extension handler.
    It processes all the extensions listed in the 'ext_modules' entry.
    """

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

        # If the installation is editable (self.inplace is True), the plugin libraries
        # are installed in the source tree
        ext_dir = Path(self.get_ext_fullpath(ext.name)).parent.absolute()
        cmake_install_prefix = ext_dir / ext.name

        # CMake configure arguments
        configure_args = [
            f"-GNinja",
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
                # f"-A x64",
                f"-DCMAKE_BUILD_TYPE={ext.cmake_build_type}",
            ]

        elif platform.system() in {"Linux", "Darwin"}:

            configure_args += [
                f"-DCMAKE_BUILD_TYPE={ext.cmake_build_type}",
            ]

        else:
            raise RuntimeError(f"Unsupported '{platform.system()}' platform")

        # Get the absolute path to the build folder
        build_folder = str(Path('.').absolute() / self.build_temp)

        # Make sure that the build folder exists
        Path(build_folder).mkdir(exist_ok=True, parents=True)

        # Compose CMake configure command
        configure_command = \
            ['cmake', '-S', ext.source_dir, '-B', build_folder] + configure_args

        # Compose CMake build command
        build_command = ['cmake', '--build', build_folder] + build_args

        # Compose CMake install command
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
