import glob
from os.path import basename, dirname, isfile


def __list_all_commands():
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    return [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]


ALL_COMMANDS = sorted(__list_all_commands())
__all__ = ALL_COMMANDS + ["ALL_COMMANDS"]
