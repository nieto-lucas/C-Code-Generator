import pytest
import subprocess
import shutil

from c_generator.c_grows import grow
from c_generator.c_analysis import get_calls

from helpers import (
    CHAIN, 
    BRANCHING, 
    DIAMOND, 
    MIXED, 
    to_c, 
    funcs_from_ast, 
    seed_from, 
    func_names
)


def gcc_ok(code: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gcc", "-fsyntax-only", "-Wall", "-Werror", "-x", "c", "-"],
        input=code, capture_output=True, text=True
    )


needs_gcc = pytest.mark.skipif(
    shutil.which("gcc") is None, reason="sin gcc"
)


class TestGrow:
    def test_zero_generations_is_identical_copy(self, tmp_path) -> None:
        seed = seed_from(tmp_path, CHAIN)
        out = grow(seed, 0)
        assert out is not seed.ast
        assert to_c(out) == to_c(seed.ast)

    def test_root_without_calls_is_unchanged(self, tmp_path) -> None:
        code = "int root(void) { return 0; }"
        seed = seed_from(tmp_path, code)
        out = grow(seed, 4)
        assert to_c(out) == to_c(seed.ast)
 
    def test_does_not_mutate_seed(self, tmp_path) -> None:
        seed = seed_from(tmp_path, CHAIN)
        before = to_c(seed.ast)
        grow(seed, 3)
        assert to_c(seed.ast) == before
 
    def test_branching_expands_every_terminal(self, tmp_path) -> None:
        seed = seed_from(tmp_path, BRANCHING)
        out = grow(seed, 1)
        funcs = funcs_from_ast(out)
        # a y b terminales -> cada una adopta el cuerpo de root
        assert get_calls(funcs["a"]) == {"a_a", "b_a"}
        assert get_calls(funcs["b"]) == {"a_b", "b_b"}

    @pytest.mark.parametrize("code", [CHAIN, BRANCHING, DIAMOND, MIXED],
                             ids=["chain", "branching", "diamond", "mixed"])
    @pytest.mark.parametrize("n", range(6))
    def test_function_count_formula(self, tmp_path, code: str, n: int) -> None:
        # el número de funciones es F(n) = F0 + K* (T + T^2 + ... + T^n), lo cuál
        # es F(n) = F0 + K* T*(T^n - 1) / (T - 1), con T: núm terminales, 
        # K: núm clasuras transitivas, F0: núm funciones base y n: núm generaciones
        seed = seed_from(tmp_path, code)
        t = len(seed.terminals)
        k = len(seed.closure)
        f0 = len(func_names(seed.ast))

        if t == 1:
            expected = f0 + k * n
        else:
            expected = f0 + k * t *(t**n - 1) // (t - 1)        

        out = grow(seed, n)
        assert len(func_names(out)) == expected


@needs_gcc
class TestCompiles:
    @pytest.mark.parametrize("code", [CHAIN, BRANCHING, DIAMOND, MIXED],
                             ids=["chain", "branching", "diamond", "mixed"])
    @pytest.mark.parametrize("n", range(6))
    def test_generated_code_compiles(self, tmp_path, code: str, n: int) -> None:
        seed = seed_from(tmp_path, code)
        out = grow(seed, n)
        result = gcc_ok(to_c(out))
        assert result.returncode == 0, result.stderr
 
    def test_semantics_preserved_at_root(self, tmp_path) -> None:
        # root llama a mid -> leaf. Tras crecer, root sigue igual
        seed = seed_from(tmp_path, CHAIN)
        out = grow(seed, 3)
        func = funcs_from_ast(out)["root"]
        assert to_c(func) == to_c(seed.root)
