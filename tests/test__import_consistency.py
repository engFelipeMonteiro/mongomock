"""Verify no mongomock_ng strings leak past imports in any test file."""

from unittest import TestCase


class ImportConsistencyTest(TestCase):
    def test__no_mongomock_ng_outside_imports(self):
        import ast
        from pathlib import Path

        tests_dir = Path(__file__).parent
        allowed_files = {'conftest.py', 'test__import_consistency.py'}
        allowed_imports = {
            'test__database_api.py': {
                'from mongomock_ng.command_cursor import CommandCursor',
            },
        }
        issues = []
        for pyfile in sorted(tests_dir.rglob('*.py')):
            if pyfile.name in allowed_files:
                continue
            text = pyfile.read_text()
            if 'mongomock_ng' not in text:
                continue
            tree = ast.parse(text)
            lines = text.splitlines()
            import_lines = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == 'mongomock_ng' and alias.asname != 'mongomock':
                            issues.append(
                                f'{pyfile}:L{node.lineno} — '
                                f'import mongomock_ng must use "as mongomock" alias'
                            )
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_lines.add(node.lineno)
                if (
                    isinstance(node, ast.ImportFrom)
                    and node.module is not None
                    and 'mongomock_ng' in node.module
                ):
                    line_text = lines[node.lineno - 1].strip()
                    file_allowed = allowed_imports.get(pyfile.name, set())
                    if line_text not in file_allowed:
                        issues.append(
                            f'{pyfile}:L{node.lineno} — '
                            f'from mongomock_ng import not allowed, use from mongomock import'
                        )
            for lineno, line in enumerate(lines, 1):
                if 'mongomock_ng' in line and lineno not in import_lines:
                    issues.append(
                        f'{pyfile}:L{lineno} — mongomock_ng outside import: {line.strip()}'
                    )
        self.assertFalse(issues, '\n'.join(issues))

    def test__conftest_sys_modules(self):
        import sys

        import mongomock_ng

        self.assertIs(sys.modules.get('mongomock'), mongomock_ng)

    def test__mongomock_alias_resolves_submodules(self):
        from mongomock import ConfigurationError  # noqa: F401
        from mongomock import Database  # noqa: F401
        from mongomock import helpers  # noqa: F401
        from mongomock import read_concern  # noqa: F401
        from mongomock.collection import Collation  # noqa: F401
        from mongomock.collection import ReturnDocument  # noqa: F401
        from mongomock.helpers import get_value_by_dot  # noqa: F401
        from mongomock.helpers import hashdict  # noqa: F401
        from mongomock.helpers import RE_TYPE  # noqa: F401
        from mongomock.read_concern import ReadConcern  # noqa: F401
        from mongomock.store import RWLock  # noqa: F401
        from mongomock.write_concern import WriteConcern  # noqa: F401

        self.assertTrue(True)

    def test__mock_patch_still_works(self):
        from unittest import mock

        import mongomock_ng as mongomock

        with mock.patch('mongomock.utcnow') as m:
            mongomock.utcnow()
            m.assert_called_once()
