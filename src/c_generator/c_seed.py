"""Recibe una función root e indentifica terminales y clausura transitiva"""

from pycparser import c_ast, parse_file

from .c_analysis import get_calls


class CSeed:
    """
    Programa C base para las expansiones recursivas de funciones terminales
    """

    def __init__(self, filepath: str, root: str) -> None:
        self.ast: c_ast.FileAST = parse_file(filepath, use_cpp=False)

        functions = {
            func.decl.name: func
            for func in self.ast.ext
            if isinstance(func, c_ast.FuncDef)
        }
        if root not in functions:
            raise ValueError(
                f"La función root: {root!r} no esta definida en {filepath}"
            )

        calls = {
            name: sorted(get_calls(func)) & functions.keys()
            for name, func in functions.items()
        }
        if any(root in called for called in calls.values()):
            raise ValueError(f"La función root: {root!r}, no debe ser llamada")

        self.root: c_ast.FuncDef = functions[root]

        reachable: set[str] = set()
        pending = list(calls[root])

        while pending:
            name = pending.pop()
            if name not in reachable:
                reachable.add(name)
                pending.extend(calls[name])

        self.closure: list[c_ast.FuncDef] = [
            func for name, func in functions.items() if name in reachable
        ]

        self.terminals: set[c_ast.FuncDef] = {
            func for func in self.closure if not calls[func.decl.name]
        }
