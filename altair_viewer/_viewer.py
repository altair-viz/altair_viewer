import json
import pkgutil
from typing import Dict, Optional, Union
import uuid
import webbrowser

import altair as alt
from altair_data_server import Provider, Resource
from altair_viewer._scripts import get_bundled_script
from altair_viewer._event_provider import EventProvider, DataSource

CDN_URL = "https://cdn.jsdelivr.net/npm/{package}@{version}"

HTML = """
<html>
  <head>
    <title>Altair Viewer</title>
    <script src="{vega_url}"></script>
    <script src="{vegalite_url}"></script>
    <script src="{vegaembed_url}"></script>
    <style>
    div.altair-chart {{
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    }}
    </style>
  </head>
  <body>
    <div id="{output_div}" class="altair-chart"></div>
    <script type="text/javascript">
        var ws = new WebSocket("{websocket_url}");
        function showSpec(spec, embedOpt) {{
            const el = document.getElementById("{output_div}");
            vegaEmbed(el, spec, embedOpt)
                .catch(error => {{
                    el.innerHTML = ('<div class="error" style="color:red;">'
                                    + '<p>JavaScript Error: ' + error.message + '</p>'
                                    + "<p>This usually means there's a typo in your chart specification. "
                                    + "See the javascript console for the full traceback.</p>"
                                    + '</div>');
                    throw error;
                }});
        }}

        var eventSource = new EventSource("/stream/spec");

        eventSource.onmessage = function(event) {{
            console.log("message:", event);
            var data = JSON.parse(event.data);
            console.log(data["spec"]);
            console.log(data["embedOpt"]);
            showSpec(data["spec"], data["embedOpt"]);
        }};

        eventSource.onerror = function(event) {{
            console.log("error:", event);
        }};

        eventSource.onopen = function() {{
            console.log("open:", event);
        }};
    </script>
  </body>
</html>
"""

INLINE_HTML = r"""
<div id="{output_div}"></div>
<script type="text/javascript">
  (function(spec, embedOpt) {{
    const outputDiv = document.getElementById("{output_div}");
    const urls = {{
      "vega": "{vega_url}",
      "vega-lite": "{vegalite_url}",
      "vega-embed": "{vegaembed_url}",
    }};
    function loadScript(lib) {{
      return new Promise(function(resolve, reject) {{
        var s = document.createElement('script');
        s.src = urls[lib];
        s.async = true;
        s.onload = () => resolve(urls[lib]);
        s.onerror = () => reject(`Error loading script: ${{urls[lib]}}`);
        document.getElementsByTagName("head")[0].appendChild(s);
      }});
    }}
    function showError(err) {{
      outputDiv.innerHTML = `<div class="error" style="color:red;">${{err}}</div>`;
      throw err;
    }}
    function displayChart(vegaEmbed) {{
      vegaEmbed(outputDiv, spec, embedOpt)
        .catch(err => showError(`Javascript Error: ${{err.message}}<br>This usually means there's a typo in your chart specification. See the javascript console for the full traceback.`));
    }}

    if(typeof define === "function" && define.amd) {{
        // requirejs paths need '.js' extension stripped.
        const paths = Object.keys(urls).reduce(function(paths, package) {{
            paths[package] = urls[package].replace(/\.js$/, "");
            return paths
        }}, {{}})
        requirejs.config({{paths}});
        require(["vega-embed"], displayChart, err => showError(`Error loading script: ${{err.message}}`));
    }} else if (typeof vegaEmbed === "function") {{
        displayChart(vegaEmbed);
    }} else {{
        loadScript("vega")
            .then(() => loadScript("vega-lite"))
            .then(() => loadScript("vega-embed"))
            .catch(showError)
            .then(() => displayChart(vegaEmbed));
    }}
  }})({spec}, {embedOpt});
</script>
"""


class DisplayedChart:
    """Show information about displayed charts."""

    url: str

    def __init__(self, url: str):
        self.url = url

    def __repr__(self) -> str:
        return f"Displaying chart at {self.url}"

    def _repr_mimebundle_(self, include=None, exclude=None) -> Dict[str, str]:
        return {
            "text/plain": repr(self),
            "text/html": f"Displaying chart at <a href='{self.url}' target='_blank'>{self.url}</a>",
        }


class ChartViewer:
    _provider: Optional[Provider]
    _resources: Dict[str, Resource]
    _stream: Optional[DataSource]
    _use_bundled_js: bool
    _versions: Dict[str, Optional[str]]

    def __init__(
        self,
        use_bundled_js: bool = True,
        vega_version: Optional[str] = alt.VEGA_VERSION,
        vegalite_version: Optional[str] = alt.VEGALITE_VERSION,
        vegaembed_version: Optional[str] = alt.VEGAEMBED_VERSION,
    ):
        self._provider = None
        self._resources = {}
        self._stream = None
        self._use_bundled_js = use_bundled_js
        self._versions = {
            "vega": vega_version,
            "vega-lite": vegalite_version,
            "vega-embed": vegaembed_version,
        }

    def _websocket_url(self) -> str:
        if self._provider is None:
            raise RuntimeError(
                "Internal: _websocket_url() called before initialization."
            )
        base_url = self._provider.url.split("//", 1)[1]
        return f"ws://{base_url}/websocket"

    def _package_url(self, package: str) -> str:
        if self._use_bundled_js:
            return self._resources[package].url
        else:
            return CDN_URL.format(package=package, version=self._versions.get(package))

    def _initialize(self) -> None:
        """Initialize the viewer."""
        if self._provider is None:
            self._provider = EventProvider()
            if self._use_bundled_js:
                for package in ["vega", "vega-lite", "vega-embed"]:
                    self._resources[package] = self._provider.create(
                        content=get_bundled_script(
                            package, self._versions.get(package)
                        ),
                        route=f"scripts/{package}.js",
                    )

            favicon = pkgutil.get_data("altair_viewer", "static/favicon.ico")
            if favicon is not None:
                self._resources["favicon.ico"] = self._provider.create(
                    content=favicon, route="favicon.ico"
                )
            self._resources["main"] = self._provider.create(
                content=HTML.format(
                    output_div="altair-chart",
                    vega_url=self._package_url("vega"),
                    vegalite_url=self._package_url("vega-lite"),
                    vegaembed_url=self._package_url("vega-embed"),
                    websocket_url=self._websocket_url(),
                ),
                route="",
            )
            self._stream = self._provider.create_stream("spec")

    def stop(self) -> None:
        if self._provider is not None:
            self._provider.stop()
            self._provider = None

    @property
    def url(self) -> str:
        """Return the main chart URL."""
        if "main" not in self._resources:
            self._initialize()
        return self._resources["main"].url

    def _inline_html(
        self, chart: Union[dict, alt.TopLevelMixin], embed_opt: Optional[dict] = None
    ) -> str:
        """Return inline HTML representation of the chart."""
        if isinstance(chart, alt.TopLevelMixin):
            chart = chart.to_dict()
        assert isinstance(chart, dict)

        return INLINE_HTML.format(
            output_div=f"altair-chart-{uuid.uuid4().hex}",
            vega_url=self._package_url("vega"),
            vegalite_url=self._package_url("vega-lite"),
            vegaembed_url=self._package_url("vega-embed"),
            spec=json.dumps(chart),
            embedOpt=json.dumps(embed_opt or {}),
        )

    def display(
        self,
        chart: Union[dict, alt.TopLevelMixin],
        inline: bool = False,
        embed_opt: Optional[dict] = None,
        open_browser: Optional[bool] = None,
    ) -> Optional[DisplayedChart]:
        """Display an Altair, Vega-Lite, or Vega chart.

        Parameters
        ----------
        chart : alt.Chart or dict
            The chart or chart specification to display.
        inline : bool
            If False (default) then open a new window to display the chart.
            If True, then display the chart inline in the Jupyter notebook.
        embed_opt : dict (optional)
            The Vega embed options that control the dispay of the chart.
        open_browser : bool (optional)
            Specify whether a browser window should be opened when inline=False.
            If not specified, a browser window will be opened only if the server is
            not already connected to a browser.

        See Also
        --------
        render : Jupyter renderer for chart.
        show : display a chart and start event loop.
        """
        if isinstance(chart, alt.TopLevelMixin):
            chart = chart.to_dict()
        assert isinstance(chart, dict)
        self._initialize()
        if self._stream is None:
            raise RuntimeError("Internal: _stream is not defined.")
        if inline:
            from IPython import display

            display.display(display.HTML(self._inline_html(chart, embed_opt)))
            return None

        self._stream.send(json.dumps({"spec": chart, "embedOpt": embed_opt or {}}))
        if self._provider is None:
            raise RuntimeError("Internal: provider is None")

        if open_browser or (open_browser is None and not self._provider._connections):
            self._provider._disconnect_event.clear()
            webbrowser.open(self.url)
        return DisplayedChart(self.url)

    def render(
        self,
        chart: Union[dict, alt.TopLevelMixin],
        inline: bool = False,
        embed_opt: Optional[dict] = None,
        open_browser: Optional[bool] = None,
    ) -> Dict[str, str]:
        """Jupyter renderer for Altair/Vega charts.

        Use this to display a chart within a Jupyter or IPython session.

        Parameters
        ----------
        chart : alt.Chart or dict
            The chart or chart specification to display.
        inline : bool
            If False (default) then open a new browser window with the chart.
            If True, then render the chart inline in the notebook.
        embed_opt : dict (optional)
            The Vega embed options that control the dispay of the chart.
        open_browser : bool (optional)
            Specify whether a browser window should be opened when inline=False.
            If not specified, a browser window will be opened only if the server is
            not already connected to a browser.

        Returns
        -------
        mimebundle : dict
            Mimebundle dictating what is displayed in IPython/Juputer outputs.

        See Also
        --------
        display : display a chart.
        show : display a chart and pause execution.
        """
        if inline:
            self._initialize()
            return {"text/html": self._inline_html(chart, embed_opt)}
        else:
            out = self.display(
                chart, embed_opt=embed_opt, open_browser=open_browser, inline=inline
            )
            return out._repr_mimebundle_() if out is not None else {}

    def show(
        self,
        chart: Union[dict, alt.TopLevelMixin],
        embed_opt: Optional[dict] = None,
        open_browser: Optional[bool] = None,
    ) -> None:
        """Show chart and prompt to pause execution.

        Use this to show a chart within a stand-alone script, to prevent the Python process
        from ending when the script finishes.

        Parameters
        ----------
        chart : alt.Chart or dict
            The chart or chart specification to display.
        embed_opt : dict (optional)
            The Vega embed options that control the dispay of the chart.
        open_browser : bool (optional)
            Specify whether a browser window should be opened. If not specified,
            a browser window will be opened only if the server is not already
            connected to a browser.

        See Also
        --------
        display : Display a chart without pausing execution.
        render : Jupyter renderer for chart.
        """
        msg = self.display(chart, embed_opt=embed_opt, open_browser=open_browser)
        print(msg)
        if self._provider is not None:
            self._provider._disconnect_event.wait()
