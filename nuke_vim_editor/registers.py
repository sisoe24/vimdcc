from typing import Dict


def increment(index: int) -> str:
    return chr(ord('a') + index - 9) if index >= 9 else str(index + 1)


class Registers:
    _registers: Dict[str, str] = {}
    _register_index = 0

    @classmethod
    def get(cls, name: str):
        return cls._registers.get(name, "")

    @classmethod
    def get_all(cls):
        return cls._registers.copy()
    
    @classmethod
    def clear(cls):
        cls._registers.clear()
        cls._register_index = 0

    @classmethod
    def add(cls, text: str):
        z_index = 34
        if cls._register_index >= z_index:
            cls._register_index = 0

        if cls._registers.get(increment(cls._register_index - 1)) != text:
            cls._registers[increment(cls._register_index)] = text
            cls._register_index += 1
