
from typing import List
from dataclasses import dataclass

import pytest

from vimdcc.registers import (Clipboard, RegistersData, RegisterFileInterface,
                              _Registers)


@dataclass
class ClipboardTest:
    initial_history: List[str]
    expected_history: List[str]


def test_clipboard():

    clipboard = Clipboard(['a'])
    clipboard.size = 3
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
    def save(self, registers: RegistersData):
        pass

    def load(self) -> RegistersData:
        return RegistersData(
            named={},
            clipboard=[],
            last_search='',
            marks={},
        )


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
