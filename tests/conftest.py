import importlib
import inspect
import json
from functools import lru_cache
from pathlib import Path
import pytest


@lru_cache(maxsize=32)
def module_path_root(module: str):
    if isinstance(module, str):
        module = importlib.import_module(module)

    assert module is not None
    return Path(inspect.getfile(module)).parents[0]


data_folder = module_path_root("tests") / "data"


@pytest.fixture()
def test_data_message():
    def load(path: str):
        return json.loads((data_folder / path).read_text(encoding="utf-8"))

    return load
