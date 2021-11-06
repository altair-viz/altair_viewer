"""Altair viewer provides offline viewing for Altair charts."""

__version__ = "0.4.0"
__all__ = [
    "ChartViewer",
    "NoMatchingVersions",
    "display",
    "render",
    "show",
    "get_bundled_script",
]

from altair_viewer._viewer import ChartViewer
from altair_viewer._scripts import get_bundled_script
from altair_viewer._utils import NoMatchingVersions

_global_viewer = ChartViewer()
display = _global_viewer.display
render = _global_viewer.render
show = _global_viewer.show
