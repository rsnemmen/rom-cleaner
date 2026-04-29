from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
KEEP_TOP_PATH = REPO_ROOT / "keep-top.py"
PARSE_DIRS_PATH = REPO_ROOT / "parse-dirs.sh"


@pytest.fixture
def load_keep_top_module(monkeypatch):
    def _load(file_matching):
        monkeypatch.setitem(
            sys.modules,
            "fuzzycp",
            types.SimpleNamespace(file_matching=file_matching),
        )
        spec = importlib.util.spec_from_file_location(
            "keep_top_under_test",
            KEEP_TOP_PATH,
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    return _load


@pytest.fixture
def parse_dirs_script() -> Path:
    return PARSE_DIRS_PATH
