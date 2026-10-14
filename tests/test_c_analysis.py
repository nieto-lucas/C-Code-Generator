from c_generator.c_analysis import get_calls

from helpers import to_func


class TestReturnsCalls:
    def test_return_call(self) -> None:
        code = """
        int g(void);
        int f(void) { return g(); }
        """
        func = to_func(code, "f")
        assert get_calls(func) == {"g"}
 
    def test_no_calls(self) -> None:
        code = "int f(void) { return 1; }"
        func = to_func(code, "f")
        assert get_calls(func) == set()
 
    def test_nested_and_multiple_calls(self) -> None:
        code = """
        int g(int);
        int h(int);
        int f(int x) { return g(h(x)) + g(x); }
        """
        func = to_func(code, "f")
        assert get_calls(func) == {"g", "h"}
 
    def test_ignores_indirect_calls(self) -> None:
        # `p()` es ID, así que se reporta; (*p)() no es ID y se ignora
        code1 = "int f(int (*p)(void)) { return p(); }"
        code2 = "int f(int (*p)(void)) { return (*p)(); }"
        func1 = to_func(code1, "f")
        func2 = to_func(code2, "f")
        assert get_calls(func1) == {"p"}
        assert get_calls(func2) == set()
 
    def test_collects_non_return_calls(self) -> None:
        code = """
        void g(void);
        int f(void) { g(); return 1; }
        """
        func = to_func(code, "f")
        assert get_calls(func) == {"g"}
