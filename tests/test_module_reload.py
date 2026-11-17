"""A module of the user is imported again as its file is now, or taken out of expressions and of memory, without
restarting the application (mint#203)."""

import importlib
import sys
import textwrap

import pytest

ENTRY = 'coils203 as coils'


@pytest.fixture
def path_folder(tmp_path, monkeypatch):
    """Folders put on the path: each is called with the name and the code of a file to write in it."""
    written = set()

    def folder(name):
        root = tmp_path / name
        root.mkdir(exist_ok=True)
        monkeypatch.syspath_prepend(str(root))

        def write(file_name, code):
            path = root / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(code))
            written.add(file_name.split('/')[0].removesuffix('.py'))
        return write
    yield folder
    for name in written:
        for module in [module for module in sys.modules if module == name or module.startswith(name + '.')]:
            sys.modules.pop(module)


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

    def test_expressions_find_the_module_while_it_is_imported_again(self, parser, monkeypatch):
        # As a plot or a stream evaluated in another thread meanwhile.
        found = []
        import_module = importlib.import_module

        def finding(name, *args):
            found.append('gain' in parser.supported_members and 'gain' in parser._supported_member_names)
            return import_module(name, *args)

        monkeypatch.setattr(importlib, 'import_module', finding)
        parser.reload_module(ENTRY)
        assert found and all(found)

    def test_the_members_injected_stay(self, parser):
        parser.inject({'injected203': 1})
        parser.reload_module(ENTRY)
        assert parser.supported_members['injected203'] == 1


class TestSharedFiles:
    """Modules of the user that import the same file of theirs, as a helper."""

    @pytest.fixture
    def two(self, isolated_parser_config, path_folder):
        write = path_folder('mods')
        write('helpers203.py', 'VALUE = 1\n')
        for name in ('moda203', 'modb203'):
            write(f'{name}.py', '''\
                import helpers203


                def value():
                    return helpers203.VALUE
                ''')
        for entry in ('moda203', 'modb203'):
            isolated_parser_config.load_modules(entry)
            isolated_parser_config.add_module_to_config(entry)
        return isolated_parser_config, write

    def test_a_helper_is_read_again_for_both(self, two):
        parser, write = two
        write('helpers203.py', 'VALUE = 2\n')
        parser.reload_module('modb203')
        assert parser.supported_members['modb203'].value() == 2
        assert parser.supported_members['moda203'].value() == 2

    def test_a_reload_that_fails_leaves_both_as_they_were(self, two):
        parser, write = two
        write('helpers203.py', 'VALUE = 2\n')
        write('modb203.py', 'def value()\n')
        with pytest.raises(SyntaxError):
            parser.reload_module('modb203')
        assert parser.supported_members['modb203'].value() == 1
        assert parser.supported_members['moda203'].value() == 1
        assert sys.modules['helpers203'].VALUE == 1

    def test_the_other_module_stays_as_it_was_if_it_fails(self, two):
        parser, write = two
        write('helpers203.py', 'VALUE = 2\n')
        write('moda203.py', 'def value()\n')
        parser.reload_module('modb203')
        assert parser.supported_members['modb203'].value() == 2
        assert parser.supported_members['moda203'].value() == 1


def test_a_package_of_another_folder_of_the_path_is_not_imported_again(isolated_parser_config, path_folder,
                                                                         tmp_path):
    # As one on PYTHONPATH, or installed with pip --user: its code runs once, and its objects keep their class.
    runs = tmp_path / 'runs.txt'
    path_folder('site')('pkg203/__init__.py', f'''\
        with open({str(runs)!r}, 'a') as f:
            f.write('run\\n')


        class Gain:
            pass
        ''')
    path_folder('mods')('coils203.py', '''\
        import pkg203


        def gain():
            return pkg203.Gain()
        ''')
    parser = isolated_parser_config
    parser.load_modules('coils203')
    parser.add_module_to_config('coils203')
    package = sys.modules['pkg203']
    parser.reload_module('coils203')
    assert runs.read_text().count('run') == 1
    assert sys.modules['pkg203'] is package
    assert isinstance(parser.supported_members['coils203'].gain(), package.Gain)


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
