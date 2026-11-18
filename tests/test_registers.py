
from typing import List
from dataclasses import dataclass

import pytest

from vimdcc.settings import Settings
from vimdcc.registers import (Clipboard, RegisterFile, RegistersData,
                              RegisterFileInterface, _Registers)


@dataclass
class ClipboardTest:
    initial_history: List[str]
    expected_history: List[str]


def test_clipboard(monkeypatch: pytest.MonkeyPatch):

    monkeypatch.setattr(Settings, 'clipboard_size', 3)
    clipboard = Clipboard(['a'])
    assert clipboard.history == ['a']
    assert clipboard.get(0) == 'a'

    clipboard.add('b')
    assert clipboard.history == ['b', 'a']

    # does not add duplicate
    clipboard.add('b')
    assert clipboard.history == ['b', 'a']

    clipboard.add('c')
    assert clipboard.history == ['c', 'b', 'a']

    # max 3 items
    clipboard.add('d')
    assert clipboard.history == ['d', 'c', 'b']


class RegisterFileMock(RegisterFileInterface):
    def __init__(self):
        self.data = RegistersData()

    def save(self, registers: RegistersData):
        self.data = registers

    def load(self) -> RegistersData:
        return self.data


def test_registers_add():
    register = _Registers(RegisterFileMock())
    register.add('a')
    register.add('b')
    assert register.registers.clipboard == ['b', 'a']


def test_registers_add_named():
    register = _Registers(RegisterFileMock())

    register.set_named_register('a')
    register.add('a')

    assert register.registers.clipboard == ['a']
    assert register.registers.named == {'a': 'a'}
    assert register._named_register is None


def test_register_get_named_value():
    register = _Registers(RegisterFileMock())

    register.set_named_register('a')
    register.add('a')

    assert register.get_named_register_value() == 'a'


def test_register_set_last_search():
    register = _Registers(RegisterFileMock())
    register.add_last_search('a')
    register.set_named_register('/')
    assert register.get_named_register_value() == 'a'


def test_register_get_numbered_value():
    register = _Registers(RegisterFileMock())
    register.add('a')
    register.add('b')

    assert register.get_numbered_register_value(0) == 'b'
    assert register.get_numbered_register_value(1) == 'a'
    assert register.get_numbered_register_value(2) is None


def test_register_add_mark():
    register = _Registers(RegisterFileMock())
    register.add_mark('a', 'b', 1)

    assert register.registers.marks == {'a': {'position': 1, 'line': 'b'}}
    assert register.get_mark('a') == {'position': 1, 'line': 'b'}


def test_register_add_space():
    register = _Registers(RegisterFileMock())

    register.set_named_register('a')
    register.add('\u2029')

    assert register.registers.clipboard == []
    assert register.get_numbered_register_value(0) is None
    assert register.get_named_register_value() is None


def test_register_paste_empty_clipboard():
    register = _Registers(RegisterFileMock())
    assert register.get_named_register_value() is None


def test_register_search_does_not_touch_clipboard():
    register = _Registers(RegisterFileMock())
    register.add('yanked')
    register.add_last_search('searched')
    assert register.get_named_register_value() == 'yanked'


def test_register_file_corrupt(tmp_path):
    path = tmp_path / 'registers.json'
    path.write_text('{"clipboard": ["a"')  # truncated write
    assert RegisterFile(path).load() == RegistersData()


def test_register_file_old_schema(tmp_path):
    path = tmp_path / 'registers.json'
    path.write_text('{"clipboard": ["a"], "removed_key": 1}')
    assert RegisterFile(path).load().clipboard == ['a']


def test_register_file_roundtrip(tmp_path):
    path = tmp_path / 'registers.json'
    data = RegistersData(clipboard=['a'], named={'x': 'y'})
    RegisterFile(path).save(data)
    assert RegisterFile(path).load() == data
    assert not path.with_suffix('.tmp').exists()


def test_registers_shared_between_sessions(tmp_path):
    path = tmp_path / 'registers.json'
    session_a = _Registers(RegisterFile(path))
    session_b = _Registers(RegisterFile(path))
    session_a.add('from a')
    session_b.add('from b')
    assert session_b.get_clipboard() == ['from b', 'from a']
