import operator
import random
from typing import Any, Callable, Dict, List, Tuple, Union

import pytest

from altair_viewer._utils import Version, find_version


OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


@pytest.mark.parametrize(
    "version_string,expected",
    [
        ("4", Version(4)),
        ("4.2", Version(4, 2)),
        ("4.2.0", Version(4, 2, 0)),
        ("4.alpha", Version(4, None, None, ".alpha")),
        ("4.2-beta", Version(4, 2, None, "-beta")),
        ("4.2.0.dev0", Version(4, 2, 0, ".dev0")),
        ("4.2.0-dev.0", Version(4, 2, 0, "-dev.0")),
    ],
)
def test_version_parsing(version_string: str, expected: Version) -> None:
    version = Version(version_string)
    assert version == expected
    assert str(version) == version_string


@pytest.mark.parametrize(
    "sorted_sequence",
    [
        ["1", "3", "5"],
        ["1.0", "1.0.1", "1.1", "1.1.1"],
        ["2.0.dev0", "2.0.dev1", "2.0"],
        ["1", "1.0", "1.0.1", "1.0.2.dev0", "1.0.2", "2", "2.1", "3.5.9"],
    ],
)
def test_version_ordering(sorted_sequence: List[str]) -> None:
    sequence = sorted_sequence[:]
    random.shuffle(sequence)
    out = [str(v) for v in sorted(map(Version, sequence))]
    assert out == sorted_sequence


@pytest.mark.parametrize(
    "version, candidates, strict_micro, expected",
    [
        ("4.0.0", ["4.0.0", "4.0.1", "4.0.2"], True, "4.0.0"),
        ("4.0.0", ["4.0.0", "4.0.1", "4.0.2"], False, "4.0.2"),
        ("4.0.0.dev0", ["4.0.0.dev0", "4.0.1.dev0", "4.0.2.dev0"], True, "4.0.0.dev0"),
        ("4.0.0.dev0", ["4.0.0.dev0", "4.0.1.dev0", "4.0.2.dev0"], False, "4.0.0.dev0"),
    ],
)
def test_version_matches(
    version: str, candidates: List[str], strict_micro: bool, expected: str
) -> None:
    result = find_version(version, candidates, strict_micro=strict_micro)
    assert result == expected


@pytest.mark.parametrize(
    "args,errstring",
    [
        (
            ("3.1", 2),
            "If passing a string to Version, no other arguments should be used.",
        ),
        (("ABC",), "Cannot parse version: 'ABC'"),
    ],
)
def test_version_instantitation_errors(
    args: Tuple[Union[str, int]], errstring: str
) -> None:
    with pytest.raises(ValueError) as err:
        Version(*args)
    assert str(err.value) == errstring


@pytest.mark.parametrize(
    "expr,result",
    [
        ("3.1 < 3.2", True),
        ("3.1 > 3.2", False),
        ("3.1 <= 3.2", True),
        ("3.1 >= 3.2", False),
        ("3.1 == 3.2", False),
        ("3.1 != 3.2", True),
        ("2.0 < 2.0", False),
        ("2.0 > 2.0", False),
        ("2.0 <= 2.0", True),
        ("2.0 >= 2.0", True),
        ("2.0 == 2.0", True),
        ("2.0 != 2.0", False),
    ],
)
def test_version_comp(expr: str, result: bool) -> None:
    lhs, op, rhs = expr.split()
    assert OPERATORS[op](Version(lhs), rhs) is result
    assert OPERATORS[op](lhs, Version(rhs)) is result


def test_version_inequality() -> None:
    assert Version("3.0") != 0


@pytest.mark.parametrize("op", ["<", ">", "<=", ">="])
def test_version_comp_err(op: str) -> None:
    with pytest.raises(TypeError) as err:
        OPERATORS[op](Version("1.0"), None)
    assert str(err.value).startswith(f"{op!r} not supported between instances")


@pytest.mark.parametrize("version", ["3", "3.1", "3.2", "3.2.0", "3.2.0.dev0"])
def test_version_repr(version: str) -> None:
    v = Version(version)
    assert eval(repr(v)) == v


@pytest.mark.parametrize("version", ["3", "3.1", "3.2", "3.2.0", "3.2.0.dev0"])
def test_version_str(version: str) -> None:
    v = Version(version)
    assert str(v) == version
