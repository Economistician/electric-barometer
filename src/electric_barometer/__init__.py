"""
Public facade for the Electric Barometer ecosystem.

This distribution coordinates compatible leaf versions and re-exports the
production governance surface so callers can import from ``electric_barometer``.
"""

from __future__ import annotations

from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Literal, cast

import numpy as np

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
from eb_optimization import enforce_snapping as _enforce_snapping

_EnforceMode = Literal["snap", "raise", "ignore"]
_SnapMode = Literal["ceil", "floor", "nearest"]

DQC = DQCClass
FPC = FPCClass
FAS = FASClass
RAL = RALPolicy


def enforce_snapping(
    y_hat: Sequence[float] | np.ndarray,
    *,
    dqc: Any,
    enforce: _EnforceMode = "snap",
    mode: _SnapMode = "ceil",
    tol: float = 1e-6,
) -> np.ndarray:
    """Production snap enforcement aligned with ``apply_ral`` (default ``ceil``).

    ``enforce="ignore"`` is not part of this facade and always raises.
    """
    if enforce == "ignore":
        raise ValueError(
            "electric_barometer.enforce_snapping does not support enforce='ignore'. "
            "Use electric_barometer.apply_ral with a governance decisions table."
        )
    return _enforce_snapping(
        y_hat,
        dqc=dqc,
        enforce=cast(Any, enforce),
        mode=mode,
        tol=tol,
    )


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
