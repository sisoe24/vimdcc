from abc import ABC, abstractmethod

from nuke_vim_editor.registers import Registers

from .handler_parameters import HandlerParams


class BaseCommand:
    def execute(self, params: HandlerParams) -> bool:
        raise NotImplementedError


class MoveCommand(ABC):
    def execute(self, params: HandlerParams) -> bool:
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

    def remove_selected_text(self, params: HandlerParams) -> None:
        if params.mode in ['DELETE', 'DELETE_INSERT']:
            Registers.push(params.cursor.selectedText())
            params.cursor.removeSelectedText()

    def yank_selected_text(self, params: HandlerParams) -> None:
        if params.mode == 'YANK':
            Registers.push(params.cursor.selectedText())
            params.cursor.clearSelection()
