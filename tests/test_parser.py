# Description: Unit tests for the Parser singleton (expression parsing, module injection, config).

import json
import os

import numpy as np
import pytest

from iplotProcessing.common.errors import InvalidExpression


class TestSingletonContract:

    def test_two_constructions_yield_same_instance(self, isolated_parser_config):
        from iplotProcessing.tools.parsers import Parser
        a = Parser()
        b = Parser()
        assert a is b


class TestStaticHelpers:

    def test_get_var_expression_extracts_all_variables(self):
        from iplotProcessing.tools.parsers import Parser
        assert Parser.get_var_expression("${a} + ${b} - ${c}") == ["a", "b", "c"]

    def test_get_var_expression_returns_empty_list_when_no_markers(self):
        from iplotProcessing.tools.parsers import Parser
        assert Parser.get_var_expression("just a string") == []

    def test_get_member_list_returns_dict_of_attributes(self):
        from iplotProcessing.tools.parsers import Parser
        members = Parser.get_member_list(np)
        assert "sin" in members
        assert "cos" in members

    def test_alias_map_envelope_has_expected_keys(self):
        from iplotProcessing.tools.parsers import Parser
        m = Parser.add_alias_map_envelope()
        assert set(m.keys()) == {"time", "dmin", "dmax", "davg"}
        assert m["time"]["independent"] is True

    def test_alias_map_contour_has_expected_keys(self):
        from iplotProcessing.tools.parsers import Parser
        m = Parser.add_alias_map_contour()
        assert set(m.keys()) == {"r", "z", "psi"}
        assert m["r"]["independent"] is True
        assert m["z"]["independent"] is True


class TestSyntaxValidation:

    def test_balanced_markers_pass_syntax_check(self, isolated_parser_config):
        assert isolated_parser_config.is_syntax_valid("${x} + ${y}") is True

    def test_unbalanced_markers_fail_syntax_check(self, isolated_parser_config):
        assert isolated_parser_config.is_syntax_valid("${x + ${y}") is False


class TestSetExpressionPureLiteral:

    def test_literal_without_markers_is_stored_unchanged(self, isolated_parser_config):
        p = isolated_parser_config
        p.set_expression("just a static string")
        assert p.expression == "just a static string"
        assert p.is_valid is False


class TestSetExpressionWithVariables:

    def test_variable_substitution_replaces_markers_with_keys(self, isolated_parser_config):
        p = isolated_parser_config
        p.set_expression("${x} + ${y}")
        assert p.is_valid is True
        assert "${" not in p.expression

    def test_substitution_appends_data_accessor_by_default(self, isolated_parser_config):
        p = isolated_parser_config
        p.set_expression("${x} + ${y}")
        assert ".data" in p.expression


class TestPreCompileValidation:

    def test_double_star_operator_is_rejected(self, isolated_parser_config):
        p = isolated_parser_config
        with pytest.raises(InvalidExpression):
            p.set_expression("${x}**2")

    def test_for_loop_is_rejected(self, isolated_parser_config):
        p = isolated_parser_config
        with pytest.raises(InvalidExpression):
            p.set_expression("for i in ${x}", is_expression=True)

    def test_dunder_access_is_rejected(self, isolated_parser_config):
        p = isolated_parser_config
        with pytest.raises(InvalidExpression):
            p.set_expression("${x}.__class__", is_expression=True)


class TestPostCompileValidation:

    def test_undefined_name_raises_invalid_expression(self, isolated_parser_config):
        p = isolated_parser_config
        with pytest.raises(InvalidExpression):
            p.set_expression("undefined_func(${x})")


class TestTimeUnitTokens:

    def test_set_expression_translates_time_units_to_timedelta(self, isolated_parser_config):
        p = isolated_parser_config
        p.set_expression("${x} + 5ms", is_expression=True)
        assert p.has_time_units is True
        assert "np.timedelta64" in p.expression


class TestClearExpression:

    def test_clear_resets_state(self, isolated_parser_config):
        p = isolated_parser_config
        p.set_expression("${x} + ${y}")
        p.clear_expr()
        assert p.expression == ""
        assert p.is_valid is False
        assert p.var_map == {}
        assert p._var_counter == 0
        assert p.has_time_units is False


class TestModuleConfigManagement:

    def test_get_modules_returns_default_plus_user(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["user_modules"] = ["pandas as pd"]
        assert p.get_modules() == ["numpy as np", "pandas as pd"]

    def test_add_module_to_config_appends_to_user_modules(self, isolated_parser_config):
        p = isolated_parser_config
        p.add_module_to_config("pandas as pd")
        assert "pandas as pd" in p.config["user_modules"]

    def test_add_module_skips_duplicates(self, isolated_parser_config):
        p = isolated_parser_config
        p.add_module_to_config("pandas as pd")
        p.add_module_to_config("pandas as pd")
        assert p.config["user_modules"].count("pandas as pd") == 1

    def test_remove_module_drops_from_user_list(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["user_modules"] = ["pandas as pd"]
        p.remove_module_from_config("pandas as pd")
        assert "pandas as pd" not in p.config["user_modules"]

    def test_reset_modules_clears_user_modules(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["user_modules"] = ["pandas as pd", "scipy as sp"]
        p.reset_modules()
        assert p.config["user_modules"] == []

    def test_format_modules_drops_user_entries_already_in_default(self, isolated_parser_config, tmp_path, monkeypatch):
        from iplotProcessing.tools import parsers as parsers_mod
        cfg_file = parsers_mod.DEFAULT_PYTHON_MODULES_JSON
        with open(cfg_file, "w") as f:
            json.dump({"modules": ["numpy as np"], "user_modules": ["numpy as np", "pandas as pd"]}, f)

        p = isolated_parser_config
        p.format_modules()
        assert p.config["user_modules"] == ["pandas as pd"]

    def test_get_total_default_modules_counts_default_list(self, isolated_parser_config):
        p = isolated_parser_config
        assert p.get_total_default_modules() == len(p.config["modules"])


class TestModuleNameParsing:

    def test_get_modules_names_extracts_from_default_and_user(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["user_modules"] = ["pandas as pd"]
        names = p.get_modules_names()
        assert "numpy" in names
        assert "pandas" in names

    def test_get_modules_names_handles_dotted_paths(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["user_modules"] = ["from scipy import signal"]
        names = p.get_modules_names()
        assert any("scipy" in n for n in names)


class TestLoadModulesPattern:

    def test_invalid_import_syntax_raises_value_error(self, isolated_parser_config):
        p = isolated_parser_config
        with pytest.raises(ValueError):
            p.load_modules("!!! not python !!!")


class TestInjectMembers:

    def test_inject_adds_to_supported_members(self, isolated_parser_config):
        p = isolated_parser_config
        p.inject({"my_func": lambda x: x})
        assert "my_func" in p.supported_members
        assert "my_func" in p._supported_member_names

    def test_inject_returns_self_for_chaining(self, isolated_parser_config):
        p = isolated_parser_config
        out = p.inject({"foo": 1})
        assert out is p


class TestEvalExpression:

    def test_eval_with_simple_expression_binds_signal_directly(self, isolated_parser_config, buffer_factory):
        from iplotProcessing.core.signal import Signal
        p = isolated_parser_config
        p.set_expression("${x}", is_expression=True)

        sig = Signal()
        sig.data_store[0] = buffer_factory([0.0, 1.0])
        sig.data_store[1] = buffer_factory([10.0, 20.0])
        p.substitute_var({"x": sig})

        # Without dict_result the signal is bound directly so the auto-appended .data
        # accessor resolves through the signal's own alias_map.
        assert p.locals[p.var_map["x"]] is sig

        p.eval_expr()
        assert p.result is sig.data_store[1]

    def test_eval_dotted_data_returns_buffer_when_no_realignment(self, isolated_parser_config, buffer_factory):
        # Regression for #110: ${alias}.data must yield the underlying BufferObject, not
        # the signal object itself. Otherwise downstream consumers that check
        # isinstance(val, np.ndarray) reject the result and arrays stay empty.
        from iplotProcessing.core.bobject import BufferObject
        from iplotProcessing.core.signal import Signal

        p = isolated_parser_config
        p.set_expression("${psi}.data", is_expression=True)

        psi = Signal()
        psi.data_store[0] = buffer_factory([0.0, 1.0])
        psi.data_store[1] = buffer_factory([[1.0, 2.0], [3.0, 4.0]])

        p.substitute_var({"psi": psi})
        p.eval_expr()

        assert isinstance(p.result, BufferObject)
        assert p.result.shape == (2, 2)
        assert p.result is psi.data_store[1]

    def test_eval_with_type_error_raises_invalid_variable(self, isolated_parser_config):
        from iplotProcessing.common.errors import InvalidVariable
        p = isolated_parser_config
        p._compiled_obj = compile("None + 5", "<string>", "eval")
        with pytest.raises(InvalidVariable):
            p.eval_expr()


class TestHasAccessToConfig:

    def test_returns_true_when_access_was_granted(self, isolated_parser_config):
        assert isolated_parser_config.has_access_to_config() is True

    def test_returns_false_when_write_failed(self, isolated_parser_config):
        p = isolated_parser_config
        p._access_to_config = False
        assert p.has_access_to_config() is False


class TestLoadConfigFromJson:

    def test_invalid_json_falls_back_to_writing_a_fresh_config(self, isolated_parser_config):
        from iplotProcessing.tools import parsers as parsers_mod
        with open(parsers_mod.DEFAULT_PYTHON_MODULES_JSON, "w") as f:
            f.write("{ not valid json")

        p = isolated_parser_config
        p.load_config_from_json()

        with open(parsers_mod.DEFAULT_PYTHON_MODULES_JSON) as f:
            recovered = json.load(f)
        assert "modules" in recovered
        assert "user_modules" in recovered

    def test_missing_file_falls_back_to_writing_a_fresh_config(self, isolated_parser_config):
        from iplotProcessing.tools import parsers as parsers_mod
        os.remove(parsers_mod.DEFAULT_PYTHON_MODULES_JSON)

        p = isolated_parser_config
        p.load_config_from_json()

        assert os.path.exists(parsers_mod.DEFAULT_PYTHON_MODULES_JSON)


class TestInitModulesErrorHandling:

    def test_init_modules_drops_modules_that_fail_to_load(self, isolated_parser_config):
        from iplotProcessing.tools import parsers as parsers_mod
        cfg = {
            "modules": ["numpy as np"],
            "user_modules": ["nonexistent_pkg_xyz123 as bad"],
        }
        with open(parsers_mod.DEFAULT_PYTHON_MODULES_JSON, "w") as f:
            json.dump(cfg, f)

        p = isolated_parser_config
        p.config = cfg.copy()
        p.config["user_modules"] = list(cfg["user_modules"])
        p.init_modules()
        assert "nonexistent_pkg_xyz123 as bad" not in p.config["user_modules"]


class TestRemoveModuleFromDefault:

    def test_removes_module_present_in_default_list(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["modules"] = ["numpy as np", "pandas as pd"]
        p.remove_module_from_config("pandas as pd")
        assert "pandas as pd" not in p.config["modules"]


class TestClearModules:

    def test_clear_modules_removes_user_entries_at_given_indices(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["modules"] = ["numpy as np"]
        p.config["user_modules"] = ["pandas as pd", "scipy as sp"]
        deleted = p.clear_modules([1, 2])
        assert deleted == [1, 2]
        assert p.config["user_modules"] == []

    def test_clear_modules_ignores_indices_pointing_to_default_entries(self, isolated_parser_config):
        p = isolated_parser_config
        p.config["modules"] = ["numpy as np"]
        p.config["user_modules"] = ["pandas as pd"]
        deleted = p.clear_modules([0])
        assert deleted == []


class TestSyntaxValidationOrdering:

    def test_invalid_marker_order_returns_false(self, isolated_parser_config):
        p = isolated_parser_config
        assert p.is_syntax_valid("${a} ${b} } ${c} ${d}") is False


class TestSignalProxyConstruction:

    def test_default_construction_keeps_base_alias_map(self, isolated_parser_config):
        from iplotProcessing.tools.parsers import SignalProxy
        proxy = SignalProxy()
        assert "time" in proxy.alias_map
        assert "data" in proxy.alias_map

    def test_dict_result_populates_default_two_slot_data_store(self, isolated_parser_config, buffer_factory):
        from iplotProcessing.tools.parsers import SignalProxy
        dict_result = {
            "time": buffer_factory([0.0, 1.0, 2.0]),
            "data": buffer_factory([10.0, 20.0, 30.0]),
        }
        proxy = SignalProxy(dict_result=dict_result)
        np.testing.assert_array_equal(proxy.data_store[0], [0.0, 1.0, 2.0])
        np.testing.assert_array_equal(proxy.data_store[1], [10.0, 20.0, 30.0])

    def test_envelope_mode_swaps_alias_map_and_appends_four_buffers(self, isolated_parser_config, buffer_factory):
        from iplotProcessing.tools.parsers import Parser, SignalProxy
        env_map = Parser.add_alias_map_envelope()
        dict_result = {
            "time": buffer_factory([0.0, 1.0]),
            "dmin": buffer_factory([0.0, 0.0]),
            "dmax": buffer_factory([1.0, 2.0]),
            "davg": buffer_factory([0.5, 1.0]),
        }
        proxy = SignalProxy(dict_result=dict_result, env_alias_map=env_map, envelope=True)
        assert set(proxy.alias_map.keys()) == {"time", "dmin", "dmax", "davg"}
        assert len(proxy.data_store) == 4


class TestSubstituteVarWithDictResult:

    def test_dict_result_keys_become_signal_proxies(self, isolated_parser_config, buffer_factory):
        from iplotProcessing.tools.parsers import SignalProxy
        p = isolated_parser_config
        p.set_expression("${a} + ${b}")

        a_payload = {
            "time": buffer_factory([0.0, 1.0]),
            "data": buffer_factory([10.0, 20.0]),
        }
        p.substitute_var({"a": None, "b": "fallback"}, dict_result={"a": a_payload})

        assert isinstance(p.locals[p.var_map["a"]], SignalProxy)
        assert p.locals[p.var_map["b"]] == "fallback"
