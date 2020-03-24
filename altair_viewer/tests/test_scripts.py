import pytest

from altair_viewer import get_bundled_script, NoMatchingVersions


@pytest.mark.parametrize("package", ["vega", "vega-lite", "vega-embed"])
def test_get_bundled_script(package: str) -> None:
    script = get_bundled_script(package)
    assert script.startswith("!function(")


@pytest.mark.parametrize(
    "package,version", [("vega", "5"), ("vega-lite", "4"), ("vega-embed", "6")]
)
def test_get_bundled_script_with_version(package: str, version: str) -> None:
    script = get_bundled_script(package)
    assert script.startswith("!function(")


def test_get_bundled_script_error() -> None:
    with pytest.raises(NoMatchingVersions) as err:
        get_bundled_script("vega-lite", "1.0")
    assert str(err.value).startswith("No matches for version='1.0'")

    with pytest.raises(ValueError) as err:
        get_bundled_script("vega-light")
    assert str(err.value).startswith("package 'vega-light' not recognized.")
