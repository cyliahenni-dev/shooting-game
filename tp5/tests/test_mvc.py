"""Tests of the MVC organisation. They read the source files: no window needed."""
import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _files(folder):
    return sorted((ROOT / folder).glob("*.py"))


def _imported_packages(path):
    names = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_the_three_packages_exist():
    for folder in ("model", "view", "controller"):
        assert (ROOT / folder / "__init__.py").exists(), folder


def test_model_does_not_know_view_or_controller():
    for f in _files("model"):
        assert not ({"view", "controller"} & _imported_packages(f)), f.name


def test_model_has_no_drawing_code():
    for f in _files("model"):
        text = f.read_text()
        functions = {n.name for n in ast.walk(ast.parse(text)) if isinstance(n, ast.FunctionDef)}
        assert "draw" not in functions, f.name
        assert "pygame.draw" not in text and "display" not in text, f.name


def test_view_does_not_know_controller():
    for f in _files("view"):
        assert "controller" not in _imported_packages(f), f.name


def test_only_the_controller_reads_the_input():
    for f in _files("model") + _files("view"):
        text = f.read_text()
        assert "pygame.event" not in text and "pygame.key" not in text, f.name
