from c_generator.c_analysis import get_calls
from c_generator.c_transform import (
    clone_function, 
    insert_before, 
    rename_calls, 
    rename_function
)

from helpers import parse, to_func, to_c, func_names, funcs_from_ast


class TestRenameFunction:
    def test_renames_decl_and_type(self) -> None:
        code = "int f(int x) { return x; }"
        func = to_func(code, "f")
        rename_function(func, "g")
        assert func.decl.name == "g"
        assert func.decl.type.type.declname == "g"
        assert "int g(int x)" in to_c(func)
 
    def test_pointer_return_type(self) -> None:
        code = "char *f(int x) { return 0; }"
        func = to_func(code, "f")
        rename_function(func, "g")
        assert func.decl.name == "g"
        assert "char *g(int x)" in to_c(func)
 
 
class TestRenameCalls:
    def test_renames_only_mapped(self) -> None:
        code = """
        int a(void);
        int b(void);
        int f(void) { return a() + b(); }
        """
        func = to_func(code, "f")
        rename_calls(func.body, {"a": "a2"})
        assert get_calls(func) == {"a2", "b"}
 
    def test_empty_mapping_is_noop(self) -> None:
        code = """
        int a(void);
        int f(void) { return a(); }
        """
        func = to_func(code, "f")
        before = to_c(func)
        rename_calls(func.body, {})
        assert to_c(func) == before
 
    def test_nested_calls(self) -> None:
        code = """
        int a(int x);
        int f(int x) { return a(a(x)); }
        """
        func = to_func(code, "f")
        rename_calls(func.body, {"a": "z"})
        assert get_calls(func) == {"z"}
        assert "z(z(x))" in to_c(func)
 
 
class TestCloneFunction:
    def test_clone_is_independent(self) -> None:
        code = "int f(int x) { return x; }"
        func = to_func(code, "f")
        clone = clone_function(func, "g")
        assert clone is not func
        assert func.decl.name == "f"
        assert clone.decl.name == "g"
 
    def test_without_args_is_plain_copy(self) -> None:
        code = "int f(int x) { return x; }"
        func = to_func(code, "f")
        clone = clone_function(func)
        assert to_c(clone) == to_c(func)
        assert clone is not func
 
    def test_renames_calls_in_clone_only(self) -> None:
        code = """
        int a(void);
        int f(void) { return a(); }
        """
        func = to_func(code, "f")
        clone = clone_function(func, "g", {"a": "b"})
        assert get_calls(clone) == {"b"}
        assert get_calls(func) == {"a"}
 
 
class TestInsertBefore:
    def test_inserts_right_before_node(self) -> None:
        code = """
        int a(void) { return 0; }
        int b(void) { return 0; }
        int c(void) { return 0; }
        """
        ast = parse(code)
        funcs = funcs_from_ast(ast)
        clone_x = clone_function(funcs["a"], "x")
        clone_y = clone_function(funcs["b"], "y")
        insert_before(ast, funcs["b"], [clone_x, clone_y])
        assert func_names(ast) == ["a", "x", "y", "b", "c"]
 
    def test_insert_at_start(self) -> None:
        code = "int a(void) { return 0; }"
        ast = parse(code)
        func = funcs_from_ast(ast)
        clone = clone_function(func["a"], "x")
        insert_before(ast, func["a"], [clone])
        assert func_names(ast) == ["x", "a"] 
