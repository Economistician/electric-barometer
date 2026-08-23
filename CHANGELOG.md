# Changelog

All notable changes to the Electric Barometer ecosystem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Leaf package changelogs are the source of truth. This macro changelog is
synthesized by ``scripts/sync_changelogs.py`` and must not drift from the
leaf entries for a given release date.

## [Unreleased]

## [System Release 0.2.9] - 2026-08-23

### Added

- Public facade re-exports `run_governance_workflow_df`, `evaluate_governance_panel_df`, `apply_ral`, `decide_governance`, DQC/FPC/FAS/RAL taxonomies, and `enforce_snapping` from `electric_barometer`.
- `py.typed` marker for PEP 561 compliance.

### Changed

- Package version is `0.2.9`, matching this system release header.
- Development Status classifier is `4 - Beta`.
- Sibling dependencies are exact pins for System Release 0.2.9.
- README Python badge specifies `>=3.11`; copyright year is 2026.
- Removed conversational docs index outro; fixed RELEASING.md format note.

### Fixed

- Resolved ruff formatting/import-sort issues and Pyright import resolution for smoke tests.
- Declared runtime dependencies on `eb-contracts` and `eb-optimization`.

### eb-evaluation 0.2.8

- Fail-closed governance, snap, DQC parse, injected-decision reconciliation, and finite-coverage gates.
- Root re-exports of DQC, FPC, FAS, and governance diagnostics.
- Exact sibling pins (`eb-metrics==0.2.8`, `eb-adapters==0.2.4`).

### eb-optimization 0.2.6

- `compute_dqc` delegates the full series to `eb_evaluation.classify_dqc`.
- Fail-closed DQC enforcement, snap arithmetic aligned with evaluation, exact sibling pins.

### eb-metrics 0.2.8

- Added zero-allocation scalar fast paths for unweighted cwsl, nsl, ud, and hr_at_tau.
- Added 67 property-based stress tests verifying scale invariance, monotonicity, and exact zero limits.
- Exported py.typed marker for PEP 561 compliance.

### eb-contracts 0.2.2

- Added `all` extras union to `pyproject.toml` for zero-friction `pip install -e ".[all]"`.
- Replaced `print()` warning statements with standard Python `logging.warning`.
- Updated package metadata (author info, Python requirement `>=3.11`).

### eb-features 0.2.6

- Exposed `FeatureConfig`, `FeatureEngineer`, and core feature functions on root `__all__`.
- Added `py.typed` marker and updated Python floor to `>=3.11`.

### eb-adapters 0.2.4

- Removed runtime dependency on `eb-evaluation` to break circular installation cycle.
- Exposed real adapter classes with `fit(X, y)` / `predict(X)` signatures.
- Exact sibling pins (`eb-metrics==0.2.8`, `eb-contracts==0.2.2`).

### eb-examples 0.2.0

- Added `py.typed` marker and `pyarrow` dependency for parquet handling.
- Golden-path scripts import exclusively from public package roots.
- Exact sibling pins for System Release 0.2.9.
