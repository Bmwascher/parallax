"""AST-based repository checker for the "discard blanks, then count
survivors" defect class.

Task 11 (2026-08-01 lane-credential-and-lock plan) replaced nine call
sites that all wrote

    lines = [l for l in text.splitlines() if l.strip()]
    assert len(lines) == 1

with the shared `accept_exactly_one_nonempty_line()` helper
(evals/tools/exact_line.py). That idiom discards blank lines BEFORE
counting, so a reply with a blank-line separator satisfies "exactly one
line" when the frozen contract requires it to be rejected. Three
independent sweeps for that idiom each missed at least one instance
before it was swept mechanically; this script is that mechanical sweep,
run in the eval gate so a tenth instance cannot be reintroduced silently.

It flags an assignment `name = [x for x in <line split> if COND]` where
COND filters on truthiness (any non-comparison test, e.g. `x.strip()`) or
on inequality with the empty string (`x != ""` / `x.strip() != ""`) ONLY
WHEN `name` is later compared to `len(name) == 1` or `len(name) != 1` in
the same lexical scope. Both halves are required: a comprehension that
filters blank lines for a legitimate multi-record result (never tested
for length one) is NOT flagged.

A <line split> is `.splitlines()` OR `.split(<sep>)` where <sep> is a
string literal containing a newline. The SEPARATOR is what makes it a
line split, not the method name - `.split(",")` is a field parse and is
deliberately not matched.

WIDENED 2026-08-03, and the reason is this gate's own miss. Until then it
keyed on the attribute name `splitlines` alone, and a fresh instance of
the defect class written `raw.split("\\n")` shipped straight past it into
evals/multi-model-verify/test_home_skill_canary.py. A whole-branch review
caught it; CI did not. That makes four spellings of this class that a
sweep has missed, counting the three hand sweeps recorded above.

LIMIT, stated once here and nowhere overstated: this checker recognizes
one SYNTACTIC shape - a list comprehension over a line split with a
truthiness/"!= \"\"" filter, whose target is later measured for length
one. It cannot prove that an arbitrarily-written parser is semantically equivalent
to `accept_exactly_one_nonempty_line()`, and a clean run of this script
must never be described as proving the defect class is gone - only that
this one syntactic idiom was not found. A `for` loop that appends, a
`filter()` call, a regex split, or a separator built at runtime are all
still invisible to it.
"""
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SKIP_DIR_NAMES = {".git", "__pycache__", ".venv", "venv", "node_modules"}


def _len_call_name(node):
    """If `node` is `len(<name>)`, return <name>; else None."""
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "len" and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)):
        return node.args[0].id
    return None


def _length_one_test_name(node):
    """If `node` is a Compare testing `len(<name>) == 1` or `!= 1`, in
    either operand order, return <name>; else None."""
    if len(node.ops) != 1 or not isinstance(node.ops[0], (ast.Eq, ast.NotEq)):
        return None
    if len(node.comparators) != 1:
        return None
    left, right = node.left, node.comparators[0]
    left_name = _len_call_name(left)
    right_name = _len_call_name(right)
    if left_name and isinstance(right, ast.Constant) and right.value == 1:
        return left_name
    if right_name and isinstance(left, ast.Constant) and left.value == 1:
        return right_name
    return None


def _is_risky_filter(expr):
    """True if `expr` is a comprehension `if` clause that filters on
    truthiness (anything that is not a comparison) or on inequality with
    the empty string."""
    if isinstance(expr, ast.Compare):
        return (len(expr.ops) == 1 and isinstance(expr.ops[0], ast.NotEq)
                and len(expr.comparators) == 1
                and isinstance(expr.comparators[0], ast.Constant)
                and expr.comparators[0].value == "")
    return True


_NEWLINE_SEPARATORS = ("\n", "\r\n", "\r")


def _is_line_split(call):
    """True if `call` splits text into LINES: `.splitlines()`, or
    `.split(<sep>)` where <sep> is a string literal containing a newline.

    THE SEPARATOR IS WHAT MATTERS, NOT THE METHOD NAME. Keying on
    `splitlines` alone is how this gate stayed green over a fresh instance
    of its own defect class on 2026-08-03: the same discard-then-count
    idiom written `raw.split("\\n")` was invisible to it, and a review
    caught what CI could not.

    `.split(",")` is deliberately NOT matched. That is a field parse, no
    contract there promises one LINE, and a gate that fired on it would
    cry wolf on correct code - and a gate that cries wolf gets suppressed.
    """
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)):
        return False
    if call.func.attr == "splitlines":
        return True
    if call.func.attr != "split":
        return False
    if len(call.args) != 1 or call.keywords:
        return False
    arg = call.args[0]
    return (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
            and arg.value in _NEWLINE_SEPARATORS)


def _is_risky_listcomp(value):
    """True if `value` is `[... for x in <line split> if COND]` with COND
    matching `_is_risky_filter` (a truthiness or "!= \"\"" filter)."""
    if not isinstance(value, ast.ListComp) or len(value.generators) != 1:
        return False
    gen = value.generators[0]
    if getattr(gen, "is_async", 0):
        return False
    if not _is_line_split(gen.iter):
        return False
    return any(_is_risky_filter(f) for f in gen.ifs)


class _ScopeCollector(ast.NodeVisitor):
    """Collects candidate risky assignments and length-one tests within
    ONE lexical scope (a module body or a single function body), never
    descending into a nested function/class/lambda's own body - those are
    separate scopes, visited on their own by the driver below."""

    _SCOPE_BOUNDARY = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)

    def __init__(self):
        self.assigns = {}          # name -> [Assign node, ...]
        self.length_one_tests = {}  # name -> [lineno, ...]

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, self._SCOPE_BOUNDARY):
                continue
            self.visit(child)

    def visit_Assign(self, node):
        if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and _is_risky_listcomp(node.value)):
            name = node.targets[0].id
            self.assigns.setdefault(name, []).append(node)
        self.generic_visit(node)

    def visit_Compare(self, node):
        name = _length_one_test_name(node)
        if name:
            self.length_one_tests.setdefault(name, []).append(node.lineno)
        self.generic_visit(node)


def _scope_roots(tree):
    """Yield every lexical scope root in `tree`: the module itself, plus
    every function (at any nesting depth)."""
    yield tree
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def find_violations(source, filename="<string>"):
    """Return a list of (lineno, name) for every risky assignment in
    `source` whose assigned name is later tested for length one in the
    same scope."""
    tree = ast.parse(source, filename=filename)
    violations = []
    for scope in _scope_roots(tree):
        collector = _ScopeCollector()
        collector.generic_visit(scope)
        for name, assign_nodes in collector.assigns.items():
            test_linenos = collector.length_one_tests.get(name, [])
            if not test_linenos:
                continue
            for assign_node in assign_nodes:
                if any(t > assign_node.lineno for t in test_linenos):
                    violations.append((assign_node.lineno, name))
    violations.sort()
    return violations


def _iter_python_files(root):
    for path in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(root).parts[:-1]):
            continue
        yield path


def check_repository(root):
    """Return a list of (path, lineno, name) violations across every
    tracked-looking .py file under `root`."""
    findings = []
    unmeasured = []
    for path in _iter_python_files(root):
        # A file this gate cannot read or parse is NOT a clean file. It used
        # to `continue` on all three failures, so an unmeasurable file was
        # silently indistinguishable from one that passed, inside a gate
        # built because three human sweeps each missed an instance.
        try:
            source = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            unmeasured.append((path, type(exc).__name__))
            continue
        try:
            for lineno, name in find_violations(source, filename=str(path)):
                findings.append((path, lineno, name))
        except SyntaxError as exc:
            unmeasured.append((path, "SyntaxError: %s" % exc.msg))
    return findings, unmeasured


def main():
    findings, unmeasured = check_repository(REPO_ROOT)
    if not findings and not unmeasured:
        return 0
    for path, lineno, name in findings:
        rel = path.relative_to(REPO_ROOT)
        print(f"{rel}:{lineno}: '{name}' is built by discarding blank "
              f"lines from splitlines() and then tested for length one - "
              f"use accept_exactly_one_nonempty_line() instead "
              f"(evals/tools/exact_line.py)")
    for path, why in unmeasured:
        rel = path.relative_to(REPO_ROOT)
        print(f"{rel}: NOT MEASURED ({why}) - this gate refuses rather than "
              f"reporting a file it could not read or parse as clean")
    return 1


if __name__ == "__main__":
    sys.exit(main())
