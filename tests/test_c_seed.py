import pytest

from c_generator.c_seed import CSeed

from helpers import seed_from, CHAIN, BRANCHING, DIAMOND


def closure_seed(seed: CSeed) -> set[str]:
    return {func.decl.name for func in seed.closure}


def terminals_seed(seed: CSeed) -> set[str]:
    return {func.decl.name for func in seed.terminals}


class TestCSeed:
    def test_chain(self, tmp_path) -> None:
        seed = seed_from(tmp_path, CHAIN)
        assert seed.root.decl.name == "root"
        assert closure_seed(seed) == {"mid", "leaf"}
        assert terminals_seed(seed) == {"leaf"}

    def test_closure_excludes_root(self, tmp_path) -> None:
        seed = seed_from(tmp_path, CHAIN)
        assert "root" not in closure_seed(seed)
 
    def test_branching_terminals(self, tmp_path):
        seed = seed_from(tmp_path, BRANCHING)
        assert closure_seed(seed) == {"a", "b"}
 
    def test_unreachable_function_not_in_closure(self, tmp_path) -> None:
        code = CHAIN + "int orphan(int x) { return x; }"
        seed = seed_from(tmp_path, code)
        assert "orphan" not in closure_seed(seed)
 
    def test_diamond_visited_once(self, tmp_path) -> None:
        seed = seed_from(tmp_path, DIAMOND)
        closure = list(closure_seed(seed))
        assert sorted(closure) == ["b", "c", "d"]
        assert terminals_seed(seed) == {"d"}
 
    def test_root_without_calls(self, tmp_path) -> None:
        code = "int root(void) { return 0; }"
        seed = seed_from(tmp_path, code)
        assert seed.closure == []
        assert seed.terminals == set()
 
    def test_ignores_external_calls(self, tmp_path) -> None:
        code = """
        int ext(int);
        int leaf(int x) { return ext(x); }
        int root(int x) { return leaf(x); }
        """
        seed = seed_from(tmp_path, code)
        assert terminals_seed(seed) == {"leaf"}
 
    def test_unknown_root_raises(self, tmp_path) -> None:
        with pytest.raises(ValueError):
            seed_from(tmp_path, CHAIN, root="nope")
