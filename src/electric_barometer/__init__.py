from __future__ import annotations

"""
electric-barometer — umbrella package for the Electric Barometer ecosystem.

This package intentionally contains minimal code. It provides a stable
namespace and installation extras that pull in:
- eb-metrics (core metrics)
- eb-evaluation (evaluation/orchestration)
- eb-adapters (model adapters)
"""

from importlib.metadata import PackageNotFoundError, version


def _resolve_version() -> str:
    try:
        return version("electric-barometer")
    except PackageNotFoundError:
        return "0.0.0"


__version__ = _resolve_version()

__all__ = ["__version__"]