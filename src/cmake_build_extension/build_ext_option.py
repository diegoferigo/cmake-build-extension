from typing import NamedTuple

from setuptools.command.build_ext import build_ext


class BuildExtOption(NamedTuple):
    """
    NamedTuple that stores the metadata of a custom build_ext option.

    Example:

        The following option:

        BuildExtOption(variable="define=", short="D", help="New compiler define")

        is displayed as follows:

        $ python setup.py build_ext --help
        ...
        Options for 'BuildExtension' command:
          ...
          --define (-D)     New compiler define
          ...
    """

    variable: str
    short: str
    help: str = ""


def add_new_build_ext_option(option: BuildExtOption, override: bool = True):
    """
    Workaround to add an existing option shown in python setup.py build_ext -h.

    Args:
        option: The new option to add.
        override: Delete the option if it already exists.
    """

    if override:
        build_ext.user_options = [
            o for o in build_ext.user_options if o[1] is not option.short
        ]
    else:
        for o in build_ext.user_options:
            if o[1] == option.short:
                raise ValueError(f"Short option '{o[1]}' already exists")

    build_ext.user_options.append(tuple(option))
