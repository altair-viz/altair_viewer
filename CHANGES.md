# Altair Viewer Change Log

## Version 0.3.0 (unreleased)

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