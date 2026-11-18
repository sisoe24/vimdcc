import os

import pytest

TEST_DATA = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(TEST_DATA, exist_ok=True)

# Set at import time: vimdcc.registers builds its global Registers when test
# modules are collected, before any fixture runs.
os.environ['REGISTER_DIR'] = TEST_DATA


@pytest.fixture(autouse=True, scope='function')
def tmp_register():
    register_path = os.path.join(TEST_DATA, 'registers.json')
    yield register_path
    if os.path.exists(register_path):
        os.remove(register_path)
