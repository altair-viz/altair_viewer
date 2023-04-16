# Altair Viewer Change Log

## Version 0.5.0 (unreleased)

- add bundled Vega v5.24.0
- add bundled Vega-Lite v5.7.0
- add bundled Vega-Embed v6.21.3
- add entrypoint ``altair.vegalite.v5.renderer``

## Version 0.4.0

- add bundled Vega v5.21.0
- add bundled Vega-Lite v4.17.0
- add bundled Vega-Embed v6.20.0

## Version 0.3.0

- Add bundled Vega v5.10.1
- Add bundled Vega-Lite v4.8.1
- Add bundled Vega-Embed v6.5.2

## Version 0.2.1

- Update bundled Vega to v5.9.2
- Update bundled Vega-embed to v6.2.2

## Version 0.2.0

- Update bundled Vega to v5.9.1 (#23)
- Add websocket connection monitor to avoid opening multiple windows and to terminate
  processes more cleanly (#22)
- Fix project metadata (#18, #19)

## Version 0.1.2

Bug: fix URLs for inline mode in JupyterLab and other non-requirejs-based renderers (#19)

## Version 0.1.1

Bug: fix URLs for inline mode for Jupyter Notebook and other requirejs-based renderers (#18).

## Version 0.1.0

Initial release: basic Altair viewer functionality.

Basic functionality:

- ``altair_viewer.show``
- ``altair_viewer.display``

Entrypoints:

- ``altair.vegalite.v4.renderer``