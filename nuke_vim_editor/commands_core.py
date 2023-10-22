from ._types import EventParams


class Command:
    def execute(self, params: EventParams) -> bool:
        raise NotImplementedError
