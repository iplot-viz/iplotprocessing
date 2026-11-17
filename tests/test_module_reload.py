"""A module of the user is imported again as its file is now, or taken out of expressions and of memory, without
restarting the application (mint#203)."""

import sys
import textwrap

import pytest

ENTRY = 'coils203 as coils'


@pytest.fixture
def user_module(tmp_path, monkeypatch):
    """A module of the user in a folder of the path, loaded and in the configuration. Call it with code to change its
    file."""
    monkeypatch.syspath_prepend(str(tmp_path))
    path = tmp_path / 'coils203.py'

    def write(code):
        path.write_text(textwrap.dedent(code))

    write('''\
        def gain(x):
            return x + 1


        def offset(x):
            return x - 1
        ''')
    yield write
    sys.modules.pop('coils203', None)


@pytest.fixture
def parser(isolated_parser_config, user_module):
    isolated_parser_config.load_modules(ENTRY)
    isolated_parser_config.add_module_to_config(ENTRY)
    return isolated_parser_config


class TestReload:

    def test_a_module_reloaded_runs_its_new_code_and_loses_what_it_no_longer_has(self, parser, user_module):
        assert parser.supported_members['coils'].gain(1) == 2
        user_module('''\
            def gain(x):
                return x + 10
            ''')
        parser.reload_module(ENTRY)
        assert parser.supported_members['coils'].gain(1) == 11
        assert parser.supported_members['gain'](1) == 11
        assert 'offset' not in parser.supported_members

    def test_a_change_of_the_same_size_in_the_same_second_is_read(self, parser, user_module):
        # Python reads a compiled module again only when the size or the second of its file changed.
        user_module('''\
            def gain(x):
                return x + 2


            def offset(x):
                return x - 1
            ''')
        parser.reload_module(ENTRY)
        assert parser.supported_members['coils'].gain(1) == 3

    def test_a_reload_that_fails_leaves_the_module_as_it_was(self, parser, user_module):
        user_module('''\
            def gain(x)
                return x
            ''')
        with pytest.raises(SyntaxError):
            parser.reload_module(ENTRY)
        assert parser.supported_members['coils'].gain(1) == 2
        assert 'coils203' in sys.modules


class TestRemove:

    def test_a_module_cleared_goes_out_of_expressions_and_of_memory(self, parser):
        parser.clear_modules([1])
        assert 'coils' not in parser.supported_members and 'gain' not in parser.supported_members
        assert 'coils203' not in sys.modules
        assert 'np' in parser.supported_members

    def test_clearing_all_keeps_the_default_modules(self, parser):
        parser.reset_modules()
        assert 'coils' not in parser.supported_members
        assert 'np' in parser.supported_members and 'numpy' in sys.modules
