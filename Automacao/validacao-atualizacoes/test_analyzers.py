"""R01/R02: fontes sintéticas temporárias; somente parsing, nunca execução."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import test_updates as fixtures
from atualizacoes import Updates, sha
from atualizacao_receita import relative_python_resources


class JavaScriptModuleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='stacknauta-r01-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.engine = Updates(self.root, runtime={})

    def put(self, path, data):
        target = self.root/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def check(self, extension, source, configs=None, path=None):
        path = path or 'Skills/Frontend/fixture/scripts/example'+extension
        for name, data in (configs or {}).items():
            self.put(name, data)
        self.put(path, source)
        self.engine.check_changed_scripts(self.root, {path:source}, {})
        self.assertEqual((self.root/path).read_bytes(),source)
        for name,data in (configs or {}).items():self.assertEqual((self.root/name).read_bytes(),data)

    def test_js_without_type_accepts_node_syntax_detection(self):
        self.check('.js', b'export const value = 1; throw new Error("never execute");\n')

    def test_mjs_uses_modules_even_under_commonjs(self):
        self.check('.mjs', b'export const value = 1;\n', {'Skills/Frontend/fixture/package.json':b'{"type":"commonjs"}'})

    def test_cjs_uses_commonjs_even_under_module(self):
        self.check('.cjs', b'return;\n', {'Skills/Frontend/fixture/package.json':b'{"type":"module"}'})

    def test_explicit_module_accepts_esm(self):
        self.check('.js', b'export const value = 1;\n', {'Skills/Frontend/fixture/package.json':b'{"type":"module"}'})

    def test_explicit_commonjs_accepts_commonjs(self):
        self.check('.js', b'return;\n', {'Skills/Frontend/fixture/package.json':b'{"type":"commonjs"}'})

    def test_no_type_accepts_commonjs(self):
        self.check('.js', b'module.exports = 1;\n')

    def test_typeless_package_preserves_node_detection(self):
        self.check('.js', b'export const value = 1;\n', {'Skills/Frontend/fixture/package.json':b'{"name":"fixture"}'})

    def test_nearest_ancestor_package_applies(self):
        self.check('.js', b'export const value = 1;\n', {'Skills/package.json':b'{"type":"module"}'})

    def test_nested_package_overrides_ancestor(self):
        configs={'Skills/package.json':b'{"type":"module"}', 'Skills/Frontend/fixture/package.json':b'{"type":"commonjs"}'}
        with self.assertRaisesRegex(ValueError, 'Sintaxe'):
            self.check('.js', b'export const value = 1;\n', configs)

    def test_nested_module_overrides_commonjs_ancestor(self):
        self.check('.js',b'export const value = 1;\n',{
            'Skills/package.json':b'{"type":"commonjs"}',
            'Skills/Frontend/fixture/package.json':b'{"type":"module"}'})

    def test_context_change_rechecks_unchanged_script(self):
        path='Skills/Frontend/fixture/scripts/example.js';source=b'export const value = 1;\n'
        self.put(path,source)
        self.put('Skills/Frontend/fixture/package.json',b'{"type":"commonjs"}')
        with self.assertRaisesRegex(ValueError,'Sintaxe'):
            self.engine.check_changed_scripts(self.root,{path:source},{path:{'sha256':sha(source)}})

    def test_typeless_nested_package_stops_type_inheritance(self):
        self.check('.js', b'export const value = 1;\n', {
            'Skills/package.json':b'{"type":"commonjs"}', 'Skills/Frontend/fixture/package.json':b'{}'})

    def test_invalid_syntax_is_rejected_in_all_formats(self):
        for extension in ('.mjs','.cjs','.js'):
            with self.subTest(extension=extension), self.assertRaisesRegex(ValueError,'Sintaxe'):
                self.check(extension,b'const broken = ;\n')

    def test_esm_is_rejected_in_explicit_commonjs_and_cjs(self):
        for extension in ('.js','.cjs'):
            with self.subTest(extension=extension), self.assertRaisesRegex(ValueError,'Sintaxe'):
                self.check(extension,b'export const value = 1;\n',{'Skills/Frontend/fixture/package.json':b'{"type":"commonjs"}'})

    def test_malformed_package_has_context_diagnostic(self):
        with self.assertRaisesRegex(ValueError, 'Contexto.*package.json'):
            self.check('.js',b'const value = 1;\n',{'Skills/Frontend/fixture/package.json':b'{"type":'})

    def test_unsafe_package_context_is_rejected(self):
        sentinel=self.root/'outside.json';sentinel.write_bytes(b'{"type":"module"}')
        package=self.root/'Skills/Frontend/fixture/package.json'
        package.parent.mkdir(parents=True)
        package.symlink_to(sentinel)
        with self.assertRaises((ValueError,OSError)):
            self.check('.js',b'export const value = 1;\n')

    def test_parser_failure_is_not_misreported_as_syntax(self):
        with patch('atualizacoes.subprocess.run',return_value=SimpleNamespace(returncode=1,stderr='unexpected parser failure',stdout='')):
            with self.assertRaisesRegex(ValueError,'inconclusiva'):
                self.check('.js',b'const value = 1;\n')


class PythonAssignmentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='stacknauta-r02-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def check(self, initializer, names='helper', import_text=None, extra=None):
        files={'pkg/__init__.py':initializer, **(extra or {})}
        for name, data in files.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        source=import_text or ('from . import '+names).encode()
        return relative_python_resources(source,'pkg/main.py',files,lambda name:(self.root/name).read_bytes())

    def test_tuple_export_is_recognized(self):
        self.assertIn('pkg/__init__.py',self.check(b'helper, other = 1, 2\n'))

    def test_simple_assignment(self):
        self.assertIn('pkg/__init__.py',self.check(b'helper = 1\n'))

    def test_list_assignment(self):
        self.check(b'[helper, other] = values\n')

    def test_nested_destructuring(self):
        self.check(b'a, (helper, c) = values\n')

    def test_starred_and_chained_targets(self):
        self.check(b'[a, *helper] = values\n')
        self.check(b'helper = other = values\n')

    def test_annotation_with_value_defines_name(self):
        self.check(b'helper: int = 1\n')

    def test_annotation_without_value_does_not_define_export(self):
        with self.assertRaises(ValueError):self.check(b'helper: int\n')

    def test_attribute_and_subscript_do_not_define_owner(self):
        for text in (b'helper.value = 1\n',b'helper[0] = 1\n',b'helper += 1\n'):
            with self.subTest(text=text),self.assertRaises(ValueError):self.check(text)

    def test_export_is_not_a_physical_module(self):
        with self.assertRaisesRegex(ValueError,'Dependência local'):
            self.check(b'helper, other = 1, 2\n',import_text=b'from .helper import tool\n')

    def test_missing_symbol_is_still_rejected(self):
        with self.assertRaisesRegex(ValueError,'Dependência local'):
            self.check(b'a, other = 1, 2\n')

    def test_invalid_python_still_rejected(self):
        with self.assertRaises(SyntaxError):self.check(b'helper, =\n')

    def test_relative_import_and_tuple_export_without_execution(self):
        initializer=b'from .utils import helper\nprimeiro, segundo = helper, None\n'
        extra={'pkg/utils.py':b'raise RuntimeError("never execute")\n'}
        self.check(initializer,names='primeiro, segundo',extra=extra)
        self.assertIn('pkg/utils.py',relative_python_resources(initializer,'pkg/__init__.py',
            {'pkg/__init__.py':initializer,**extra},lambda name:(self.root/name).read_bytes()))

    def test_missing_relative_dependency_is_still_rejected(self):
        source=b'from .utils import helper\nprimeiro, segundo = helper, None\n'
        with self.assertRaisesRegex(ValueError,'Dependência local'):
            relative_python_resources(source,'pkg/__init__.py',{'pkg/__init__.py':source},lambda _:source)
