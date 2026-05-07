import json
import os

import numpy as np
import pytest


@pytest.fixture
def reset_parser_singleton():
    """Wipe the Parser singleton so each test starts from a clean slate."""
    from iplotProcessing.tools.parsers import Parser
    Parser._instance = None
    yield
    Parser._instance = None


@pytest.fixture
def isolated_parser_config(tmp_path, monkeypatch, reset_parser_singleton):
    """Redirect default_modules.json to a temp directory and return the Parser."""
    cfg_dir = tmp_path / "parser_cfg"
    cfg_dir.mkdir()
    cfg_file = cfg_dir / "default_modules.json"
    cfg_file.write_text(json.dumps({"modules": ["numpy as np"], "user_modules": []}))
    monkeypatch.setenv("IPLOT_PMODULE_PATH", str(cfg_dir))

    # parsers.py reads IPLOT_PMODULE_PATH at import time, so we reload it.
    import importlib

    from iplotProcessing.tools import parsers as parsers_mod
    importlib.reload(parsers_mod)
    yield parsers_mod.Parser()
    # Rebind DEFAULT_PYTHON_MODULES_JSON to ROOT now that monkeypatch has
    # cleared IPLOT_PMODULE_PATH; otherwise it stays pinned to a deleted tmp_path.
    importlib.reload(parsers_mod)


@pytest.fixture
def buffer_factory():
    """Factory to build BufferObject instances quickly."""
    from iplotProcessing.core.bobject import BufferObject

    def _make(values, unit=""):
        return BufferObject(input_arr=np.asarray(values), unit=unit)

    return _make


@pytest.fixture
def simple_signal(buffer_factory):
    """Build a Signal with a 1D time/data pair populated."""
    from iplotProcessing.core.signal import Signal

    s = Signal()
    s.data_store[0] = buffer_factory([0.0, 1.0, 2.0, 3.0], unit="s")
    s.data_store[1] = buffer_factory([10.0, 20.0, 30.0, 40.0], unit="V")
    return s


@pytest.fixture
def envelope_signal(buffer_factory):
    """Build a Signal with the envelope alias map (time, dmin, dmax, davg)."""
    from iplotProcessing.core.signal import Signal

    s = Signal()
    s._alias_map = {
        "time": {"idx": 0, "independent": True},
        "dmin": {"idx": 1},
        "dmax": {"idx": 2},
        "davg": {"idx": 3},
    }
    s._data.append(s._data[0].__class__())
    s._data[0] = buffer_factory([0.0, 1.0, 2.0], unit="s")
    s._data[1] = buffer_factory([0.0, 0.0, 0.0], unit="V")
    s._data[2] = buffer_factory([1.0, 2.0, 3.0], unit="V")
    s._data[3] = buffer_factory([0.5, 1.0, 1.5], unit="V")
    return s
