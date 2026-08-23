# Changelog

All notable changes to the Electric Barometer ecosystem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Leaf package changelogs are the source of truth. This macro changelog is
synthesized by ``scripts/sync_changelogs.py`` and must not drift from the
leaf entries for a given release date.

## [Unreleased]

### Changed

- Removed conversational docs index outro; fixed RELEASING.md format note.
- Raised the Python floor to `>=3.11` to match leaf packages.

### Fixed

- Resolved ruff formatting/import-sort issues and Pyright import resolution for smoke tests.
- Declared runtime dependencies on `eb-contracts` and `eb-optimization`.

## [System Release 0.2.9] - 2026-08-22

### eb-metrics

#### Added

- Added zero-allocation scalar fast paths for unweighted cwsl, nsl, ud, and hr_at_tau.
- Added 67 property-based stress tests verifying scale invariance, monotonicity, and exact zero limits.
- Exported py.typed marker for PEP 561 compliance.

### eb-evaluation

#### Breaking Changes

- Removed default cost parameters (`cu=2.0`, `co=1.0`) in `evaluate_groups_df` to enforce explicit operational costs ("no hidden heuristics").

#### Performance

- Vectorized group processing, reducing panel evaluation from ~373 ms to <1 ms on multi-million row panels.

#### Added

- Exposed `compare_forecasts` and `__version__` on root `__all__`.

### eb-contracts

#### Added

- Added `all` extras union to `pyproject.toml` for zero-friction `pip install -e ".[all]"`.

#### Fixed

- Replaced `print()` warning statements with standard Python `logging.warning`.
- Updated package metadata (author info, Python requirement `>=3.11`).

### eb-optimization

#### Added

- Exposed `CostRatioPolicy`, `TauPolicy`, `DQCPolicy`, and key helpers on root `__all__`.
- Added `py.typed` marker and updated Python floor to `>=3.11`.

### eb-features

#### Added

- Exposed `FeatureConfig`, `FeatureEngineer`, and core feature functions on root `__all__`.
- Added `py.typed` marker and updated Python floor to `>=3.11`.

### eb-adapters

#### Breaking Changes

- Removed runtime dependency on `eb-evaluation` to break circular installation cycle.

#### Added

- Exposed real adapter classes (`ArimaAdapter`, `SarimaxAdapter`, `XGBoostRegressorAdapter`) with `fit(X, y)` / `predict(X)` signatures.
- Added `test` and `all` extras to `pyproject.toml`.

### eb-examples

#### Added

- Added `py.typed` marker and `pyarrow` dependency for parquet handling.

#### Fixed

- Aligned golden path pipeline script to include explicit FRS evaluation with required `cwsl_max`.
- Updated all metric scripts to import exclusively from public package roots.
