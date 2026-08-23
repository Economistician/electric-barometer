"""
Public facade for the Electric Barometer ecosystem.

This distribution coordinates compatible leaf versions and re-exports the
production governance surface so callers can import from ``electric_barometer``.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from eb_evaluation import (
    DQCClass,
    DQCResult,
    DQCThresholds,
    FASClass,
    FASThresholds,
    FPCClass,
    FPCResult,
    FPCThresholds,
    RALPolicy,
    apply_ral,
    build_fas_surface,
    classify_dqc,
    classify_fpc,
    decide_governance,
    evaluate_governance_panel_df,
    run_governance_workflow_df,
)
from eb_optimization import enforce_snapping

DQC = DQCClass
FPC = FPCClass
FAS = FASClass
RAL = RALPolicy


def _resolve_version() -> str:
    """Return the installed version of the electric-barometer distribution."""
    try:
        return version("electric-barometer")
    except PackageNotFoundError:
        return "0.0.0"


__version__ = _resolve_version()

__all__ = [
    "DQC",
    "FAS",
    "FPC",
    "RAL",
    "DQCClass",
    "DQCResult",
    "DQCThresholds",
    "FASClass",
    "FASThresholds",
    "FPCClass",
    "FPCResult",
    "FPCThresholds",
    "RALPolicy",
    "__version__",
    "apply_ral",
    "build_fas_surface",
    "classify_dqc",
    "classify_fpc",
    "decide_governance",
    "enforce_snapping",
    "evaluate_governance_panel_df",
    "run_governance_workflow_df",
]
