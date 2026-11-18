import os
import re
import pathlib
import sysconfig
from typing import Dict
from platform import python_version
from functools import lru_cache

from ._qt import __version__ as pyside_version


@lru_cache(maxsize=None)
def load_version() -> str:
    # so much code to get the version number :(
    pyproject = pathlib.Path(__file__).parent.parent / 'pyproject.toml'
    version = re.search(r'version = "(.*)"', pyproject.read_text())
    version = version[1] if version else 'unknown'
    os.environ['VIMDCC_VERSION'] = version
    return version


def about() -> Dict[str, str]:
    """Return a dictionary with information about the application."""
    return {
        'version': load_version(),
        'python': python_version(),
        'pyside': pyside_version,
        'machine': sysconfig.get_platform(),
        'user': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
    }
