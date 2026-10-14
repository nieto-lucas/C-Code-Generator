from pycparser import c_ast


class _CallExtractor(c_ast.NodeVisitor):
    def __init__(self) -> None:
        self.called: set[str] = set()

    def visit_FuncCall(self, node: c_ast.FuncCall) -> None:
        if isinstance(node.name, c_ast.ID):
            self.called.add(node.name.name)

        self.generic_visit(node)


def get_calls(function: c_ast.FuncDef) -> set[str]:
    """
    Recorre una función `function` y encuentra los nombres de las funciones
    llamadas dentro del cuerpo de la función.
    """
    extractor = _CallExtractor()
    extractor.visit(function)
    return extractor.called
