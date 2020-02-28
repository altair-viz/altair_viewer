import io
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# ==============================================================================
# Utilities
# ==============================================================================


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def get_install_requirements(path):
    content = read(path)
    return [req for req in content.split("\n") if req != "" and not req.startswith("#")]


def version(path):
    """Obtain the packge version from a python file e.g. pkg/__init__.py

    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    version_file = read(path)
    version_match = re.search(
        r"""^__version__ = ['"]([^'"]*)['"]""", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


HERE = os.path.abspath(os.path.dirname(__file__))


# From https://github.com/jupyterlab/jupyterlab/blob/master/setupbase.py, BSD licensed
def find_packages(top=HERE):
    """
    Find all of the packages.
    """
    packages = []
    for d, dirs, _ in os.walk(top, followlinks=True):
        if os.path.exists(os.path.join(d, "__init__.py")):
            packages.append(os.path.relpath(d, top).replace(os.path.sep, "."))
        elif d != top:
            # Do not look for packages in subfolders if current is not a package
            dirs[:] = []
    return packages


setup(
    name="altair_viewer",
    version=version("altair_viewer/__init__.py"),
    description="Viewer for Altair and Vega-Lite visualizations.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Jake VanderPlas",
    author_email="jakevdp@google.com",
    url="http://github.com/altair-viz/altair_viewer/",
    download_url="http://github.com/altair-viz/altair_viewer/",
    license="BSD 3-clause",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_install_requirements("requirements.txt"),
    python_requires=">=3.6",
    entry_points={
        "altair.vegalite.v4.renderer": ["altair_viewer=altair_viewer:render"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
