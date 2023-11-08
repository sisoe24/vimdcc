from abc import ABC, abstractmethod

from .handler_parameters import HandlerParams


class BaseCommand:
    def execute(self, params: HandlerParams) -> bool:
        raise NotImplementedError


class MoveCommand(ABC):
    def execute(self, params: HandlerParams) -> bool:

        # The common pre-execution steps (if any) go here

        # Delegate the execution to the subclass
        result = self._do_execute(params)

        # Common post-execution steps
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
            params.cursor.movePosition(params.cursor.EndOfLine, params.cursor.KeepAnchor)

    def remove_selected_text(self, params: HandlerParams) -> None:
        if params.mode in ['DELETE', 'DELETE_INSERT']:
            params.cursor.removeSelectedText()

    def yank_selected_text(self, params: HandlerParams) -> None:
        if params.mode == 'YANK':
            params.cursor.clearSelection()
