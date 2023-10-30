from .handler_parameters import HandlerParams


class Command:
    def execute(self, params: HandlerParams) -> bool:
        raise NotImplementedError
