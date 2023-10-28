from typing import Any, Callable

from PySide2.QtWidgets import QPlainTextEdit

HandlerType = Callable[[QPlainTextEdit], Any]
