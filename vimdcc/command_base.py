from abc import ABC, abstractmethod

from .registers import Registers
from .handler_parameters import HandlerParams


class BaseCommand(ABC):
    """Interface for all commands."""

    @abstractmethod
    def execute(self, params: HandlerParams) -> bool:
        """Execute the command."""


class MoveCommand(ABC):
    """Interface for all move commands.

    A move command is similar to a BaseCommand, but it performs a pre and post
    actions based on the mode.

    """
    initial_position = None

    def execute(self, params: HandlerParams) -> bool:
        self.initial_position = params.cursor.position()
        result = self._do_execute(params)
        self._post_execute(params)
        return result

    @abstractmethod
    def _do_execute(self, params: HandlerParams) -> bool:
        """The actual execution logic to be implemented by subclasses."""

    def _post_execute(self, params: HandlerParams) -> None:
        self.select_entire_line(params)
        self.yank_selected_text(params)
        self.remove_selected_text(params)

    def select_entire_line(self, params: HandlerParams) -> None:
        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(params.cursor.StartOfLine, params.cursor.KeepAnchor)
            params.cursor.movePosition(params.cursor.EndOfLine, params.cursor.KeepAnchor)

    def remove_selected_text(self, params: HandlerParams) -> None:
        if params.mode in ['DELETE', 'CHANGE']:
            Registers.add(params.cursor.selectedText())
            params.cursor.removeSelectedText()

    def yank_selected_text(self, params: HandlerParams) -> None:
        if params.mode == 'YANK':
            Registers.add(params.cursor.selectedText())
            params.cursor.clearSelection()

            # Restore the cursor position to the initial position
            if self.initial_position is not None:
                params.cursor.setPosition(self.initial_position)
