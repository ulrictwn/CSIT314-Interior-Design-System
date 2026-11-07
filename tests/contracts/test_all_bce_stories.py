"""Validate all public story interfaces against the updated Word BCE diagrams."""
import ast
from importlib import import_module
import inspect
import json
from pathlib import Path
import types
import typing

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = json.loads(Path(__file__).with_name('bce_contracts.json').read_text())['stories']


def uml_type(annotation):
    if annotation is None or annotation is type(None):
        return 'void'
    origin = typing.get_origin(annotation)
    if origin in (types.UnionType, typing.Union):
        members = [a for a in typing.get_args(annotation) if a is not type(None)]
        return uml_type(members[0]) if len(members) == 1 else '|'.join(map(uml_type, members))
    if origin is list:
        return 'list[' + uml_type(typing.get_args(annotation)[0]) + ']'
    return getattr(annotation, '__name__', str(annotation))


@pytest.mark.parametrize('contract', CONTRACTS, ids=[f"story{c['story']:02d}" for c in CONTRACTS])
def test_each_story_matches_its_diagram_names_parameters_types_and_void_displays(contract):
    for layer in ('boundary', 'controller', 'entity'):
        expected = contract[layer]
        if expected is None:
            continue
        cls = getattr(import_module(expected['module']), expected['name'])
        assert cls.__name__ == expected['name']
        for name, method in expected['methods'].items():
            operation = getattr(cls, name)
            signature = inspect.signature(operation)
            hints = typing.get_type_hints(operation)
            parameters = [p for p in signature.parameters.values() if p.name not in ('self', 'cls')]
            allowed = expected.get('allowed_keyword_only', [])
            parameters = [p for p in parameters if not (p.kind is inspect.Parameter.KEYWORD_ONLY and p.name in allowed)]
            assert [p.name for p in parameters] == list(method['parameters']), (contract['story'], layer, name)
            for parameter, data_type in method['parameters'].items():
                assert uml_type(hints[parameter]) == data_type, (contract['story'], layer, name, parameter)
            assert uml_type(hints['return']) == method['returns'], (contract['story'], layer, name, 'return')


def test_manifest_covers_every_story_and_records_the_approved_password_free_exception():
    assert [c['story'] for c in CONTRACTS] == list(range(1, 49))
    exceptions = [c['story'] for c in CONTRACTS if c.get('exception')]
    assert exceptions == [6]


@pytest.mark.parametrize('layer,forbidden', [
    ('boundary', ('sqlalchemy', 'infrastructure.database')),
    ('control', ('boundary', 'flask', 'sqlalchemy', 'infrastructure.database')),
    ('entity', ('boundary', 'control', 'flask')),
])
def test_layers_do_not_import_input_validation_http_or_database_concerns_from_the_wrong_layer(layer, forbidden):
    for path in (ROOT / layer).rglob('*.py'):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            modules = [node.module or ''] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            for module in modules:
                assert not any(module == name or module.startswith(name+'.') for name in forbidden), (path, module)
