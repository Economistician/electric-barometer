"""
Smoke tests for the Electric Barometer ecosystem.

Validates that the umbrella facade imports cleanly and that optional
ecosystem packages do not introduce import-time failures when present.
"""

import importlib
import importlib.util
from pathlib import Path


def _can_import(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def test_smoke_imports_and_public_surface():
    import electric_barometer as eb  # type: ignore[reportMissingImports]

    assert hasattr(eb, "__version__")
    assert eb.__file__ is not None
    assert Path(eb.__file__).with_name("py.typed").is_file()

    required = (
        "run_governance_workflow_df",
        "evaluate_governance_panel_df",
        "apply_ral",
        "decide_governance",
        "DQC",
        "FPC",
        "FAS",
        "RAL",
        "enforce_snapping",
        "classify_dqc",
        "classify_fpc",
        "build_fas_surface",
    )
    assert set(required) <= set(eb.__all__)
    for name in required:
        assert getattr(eb, name) is not None

    optional = [
        "eb_evaluation",
        "eb_adapters",
        "eb_features",
    ]

    for name in optional:
        if _can_import(name):
            importlib.import_module(name)
