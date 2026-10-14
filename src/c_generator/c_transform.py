"""Clona y tranforma funciones de un c_ast"""

import copy
from pycparser import c_ast


def insert_before(
    ast: c_ast.FileAST, node: c_ast.Node, nodes: list[c_ast.Node]
) -> None:
    """
    Inserta `nodes` en el nivel superior de `ast`, justo antes de `node`
    """
    pos = ast.ext.index(node)
    ast.ext[pos:pos] = nodes


def clone_function(
    function: c_ast.FuncDef,
    new_name: str | None = None,
    call_map: dict[str, str] | None = None,
) -> c_ast.FuncDef:
    """
    Copia `function` con otro nombre y con sus llamadas renombradas según `mapping`
    """
    clone = copy.deepcopy(function)
    if new_name is not None:
        rename_function(clone, new_name)

    if call_map is not None:
        rename_calls(clone.body, call_map)

    return clone


def rename_function(function: c_ast.FuncDef, new_name: str) -> None:
    """
    Renombra una función `function` según un nombre `new_name`
    """
    function.decl.name = new_name

    type_decl = function.decl.type
    while not isinstance(type_decl, c_ast.TypeDecl):
        type_decl = type_decl.type

    type_decl.declname = new_name


class _CallRenamer(c_ast.NodeVisitor):
    def __init__(self, mapping: dict[str, str]) -> None:
        self._mapping = mapping

    def visit_FuncCall(self, node: c_ast.FuncCall) -> None:
        if isinstance(node.name, c_ast.ID) and node.name.name in self._mapping:
            node.name.name = self._mapping[node.name.name]

        self.generic_visit(node)


def rename_calls(node: c_ast.Node, mapping: dict[str, str]) -> None:
    """
    Renombra in-place cada FuncCall de `node` según `mapping` (si aplica)
    """
    _CallRenamer(mapping).visit(node)
