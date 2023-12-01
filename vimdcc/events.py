"""Event manager.

This module implements a simple event manager that can be used to register an event
and emit it later. The event manager is implemented as a singleton.

XXX: I see this as a temporary solution until I figure out how to better custom events
from the controllers. For example, how a DCC can execute the code from the editor
when the user presses the enter key.

"""

from typing import Any, Callable
from collections import defaultdict

GenericEvent = Callable[..., Any]


class _EventManager:
    """Event manager singleton.

    This class is used to register and emit events. One can register multiple
    events to the same name and emit them later.

    NOTE: The class is pre-bound to the ``EventManager`` variable and
    you shouldn't instantiate it yourself.

    Example:
        >>> from .events import EventManager
        >>>
        >>> def handler(*args, **kwargs):
        ...     print('Hello world!')
        ...
        >>> EventManager.register('on_hello', handler)
        >>> EventManager.emit('on_hello')
        >>> Hello world!
        >>> EventManager.unregister('on_hello', handler)
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_EventManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.events: dict[str, list[GenericEvent]] = defaultdict(list)

    def register(self, event: str, handler: GenericEvent):
        self.events[event].append(handler)

    def unregister(self, event: str, handler: GenericEvent):
        self.events[event].remove(handler)

    def emit(self, event: str, *args: Any, **kwargs: Any):
        for handler in self.events[event]:
            handler(*args, **kwargs)


EventManager = _EventManager()
