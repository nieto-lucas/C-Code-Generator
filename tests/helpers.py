from pathlib import Path

from pycparser import c_ast, c_generator
from pycparser.c_parser import CParser

from c_generator.c_seed import CSeed 


MIXED = """
int a(int x) { return x + 1; }
int b(int x) { return x - 1; }
int c(int x) { return x * 2; }
int m(int x) { return a(x) + b(x); }
int root(int x) { return m(x) + c(x); }
"""

CHAIN = """
int leaf(int x) { return x + 1; }
int mid(int x) { return leaf(x) * 2; }
int root(int x) { return mid(x); }
"""

DIAMOND = """
int d(int x) { return x; }
int b(int x) { return d(x) + 1; }
int c(int x) { return d(x) + 2; }
int root(int x) { return b(x) + c(x); }
"""

BRANCHING = """
int a(int x) { return x + 1; }
int b(int x) { return x - 1; }
int root(int x) { return a(x) + b(x); }
"""


def parse(code: str) -> c_ast.FileAST:
    return CParser().parse(code)


def to_c(node: c_ast.Node) -> str:
    return c_generator.CGenerator().visit(node)


def seed_from(tmp_path: Path, code: str, root: str = "root") -> CSeed:
    path = tmp_path / "seed.c"
    path.write_text(code)
    return CSeed(str(path), root)


def funcs_from_ast(ast: c_ast.FileAST) -> dict[str, c_ast.FuncDef]:
    return {
        func.decl.name: func for func in ast.ext if isinstance(func, c_ast.FuncDef)
    }


def to_func(code: str, func_name: str) -> c_ast.FuncDef:
    ast = parse(code)
    functions = funcs_from_ast(ast)
    return functions[func_name]


def func_names(ast: c_ast.FileAST) -> list[str]:
    return [func.decl.name for func in ast.ext if isinstance(func, c_ast.FuncDef)]
