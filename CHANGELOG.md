# Changelog

All notable changes to the Electric Barometer ecosystem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Leaf package changelogs are the source of truth. This macro changelog is
synthesized by ``scripts/sync_changelogs.py`` and must not drift from the
leaf entries for a given release date.

## [Unreleased]

## [System Release 0.2.10] - 2026-08-24

### eb-metrics

#### Performance

- Public NSL, UD, HR@τ, and CWSL wrappers share internal validated-array kernels so callers can reuse a single `_validated_nonneg_pair` result.
- `_to_1d_array` returns a 1D C-contiguous `float64` ndarray as a view (no `asarray` copy) and still rejects empty and non-finite values.
- `_validate_shapes` reuses C-contiguous `float64` arrays; `rmse` derives from a single validated MSE; `mase` reuses the validated `y_true` array.

#### Fixed

- Classical regression metrics (`rmse`, `mape`, `wmape`, `mase`, and the shared `_validate_shapes` helper) reject non-1D, empty, and non-finite inputs with explicit `ValueError`s, matching service-kernel domain checks. Valid finite 1D series are unchanged.

### eb-evaluation

#### Performance

- `compute_error_anatomy` aggregates FAS slice stats with `np.bincount` / `np.add.at` and segmented quantiles instead of Python lambdas in `groupby.agg`.
- `build_signals_from_series` validates each `(y, yhat)` pair once and reuses the arrays in NSL / HR / UD / CWSL.
- `apply_ral` broadcasts `uint8` nonneg/snap codes internally and writes the existing string audit columns on export.
- `ReadinessAdjustmentLayer._best_uplift` validates `(y, yhat)` once and scores the uplift grid with `_cwsl_from_validated`.
- `evaluate_governance_panel_df` slices pre-grouped 1D forecast arrays into `run_governance_gate` instead of copying a per-stream DataFrame of `y` / `yhat`.
- `evaluate_hierarchy_df` / `evaluate_panel_df` reduce grouped levels through `evaluate_groups_df` and map onto the existing hierarchy schema.
- `evaluate_panel_with_entity_R` joins `cu = R * co` onto the panel and delegates per-entity metrics to `evaluate_groups_df`.

#### Fixed

- `slice_keys` default interval column is `INTERVAL_INDEX`.
- Pinned sibling packages to System Release 0.2.10 (`eb-metrics==0.2.9`, `eb-adapters==0.2.5`).
- Mixed FAS tokens within one stream fail-close that stream (`mixed_fas_fail_closed`) instead of aborting the panel.
- `evaluate_governance_panel_df` excludes `is_observable is not True` and `is_structural_zero is True` intervals from DQC/FPC/RAL scoring and coverage when those columns are present.

### eb-contracts

#### Performance

- `validate_panel_demand_v1` and `validate_panel_fpc_result_v1` use vectorized `isin` domain checks and skip numeric/datetime recasts plus Series re-wraps when dtypes are already canonical.

#### Fixed

- Demand-panel unit fixtures use warehouse source column names (`FORECAST_ENTITY_KEY`, `BUSINESS_DATE`, `INTERVAL_INDEX`).
- Source distributions exclude the local `.pre-commit-home` cache so Hatchling does not ship hook environments to PyPI.

### eb-optimization

#### Performance

- Vectorize linear cost-balance grids in `estimate_R_cost_balance`, `estimate_entity_R_from_balance`, and RAL `_find_best_uplift`.
- `snap_to_grid` calls evaluation `_snap_to_grid_array` on ndarray inputs instead of round-tripping through Python lists.

#### Fixed

- Pinned sibling packages to System Release 0.2.10 (`eb-metrics==0.2.9`, `eb-evaluation==0.2.10`).

### eb-features

#### Performance

- `FeatureEngineer.transform` sorts once and mutates a single working frame; lag, rolling, and calendar helpers no longer copy at each stage.
- `add_rolling_features` computes each window with one `GroupBy.rolling.agg` over the requested stats.
- `add_lag_features` reuses a single `groupby(entity)[target]` for all lag offsets.

#### Fixed

- Standalone lag, rolling, and calendar helpers stable-sort by entity and timestamp (when present) so `groupby.shift` / `groupby.rolling` follow chronological order.

### eb-adapters

#### Performance

- `to_panel_demand_v1` copies only spec-referenced source columns from the warehouse frame.
- `_coerce_nullable_bool` uses `Series.isin` / boolean masks instead of a Python per-cell map.
- `to_panel_demand_v1` projects source columns without a defensive deep copy; string-coercion of bool encodings runs only on values still unrecognized after `isin()`.
- `impute_zero_when_observable` uses `Series.where` instead of chained `.loc` / `.fillna`.

#### Added

- QSR interval adapter maps `IS_TRAINABLE` to canonical `is_observable` when present. Absent that column, `is_observable` is the Kleene AND of `IS_INTERVAL_OBSERVABLE` and `IS_DATE_OBSERVABLE` when both exist. Warehouse observability columns are retained uncoerced on the panel frame.
- QSR interval adapter treats `IS_STRUCTURAL_ZERO` as optional. Missing or `None` source columns default canonical `is_structural_zero` to `False`.

#### Fixed

- QSR interval adapter source defaults now match the warehouse schema (`FORECAST_ENTITY_KEY`, `BUSINESS_DATE`, `INTERVAL_INDEX`, `INTERVAL_INDEX_START_TIME`, `FORECAST_ENTITY_DEMAND_QUANTITY`, `IS_DATE_OBSERVABLE`). `HALF_HOUR_NUMBER` and `LOCAL_START_TIME` remain accepted aliases.
- `_coerce_nullable_bool` maps unrecognized boolean tokens to `<NA>` instead of raising, so invalid gate strings cannot crash `to_panel_demand_v1`.
- Pinned sibling packages to System Release 0.2.10 (`eb-metrics==0.2.9`, `eb-contracts==0.2.3`).

### eb-examples

#### Fixed

- Golden-path demo dataset and scripts use warehouse source column names (`FORECAST_ENTITY_KEY`, `BUSINESS_DATE`, `INTERVAL_INDEX`, `INTERVAL_INDEX_START_TIME`, `IS_DATE_OBSERVABLE`).
- Pinned sibling packages to System Release 0.2.10, including `electric-barometer==0.2.10`.

## [System Release 0.2.9] - 2026-08-23

### Added

- Public facade re-exports `run_governance_workflow_df`, `evaluate_governance_panel_df`, `apply_ral`, `decide_governance`, DQC/FPC/FAS/RAL taxonomies, and `enforce_snapping` from `electric_barometer`.
- `py.typed` marker for PEP 561 compliance.

### Changed

- Package version is `0.2.9`, matching this system release header.
- Development Status classifier is `5 - Production/Stable`.
- Sibling dependencies are exact pins for System Release 0.2.9, including the 0.2.9 leaf safety recut (`eb-evaluation==0.2.9`, `eb-optimization==0.2.7`).
- README Python badge specifies `>=3.11`; copyright year is 2026.
- Removed conversational docs index outro; fixed RELEASING.md format note.
- `enforce_snapping` on the facade rejects `enforce="ignore"` and defaults to `ceil`.
- Facade workflow tests cover missing FAS fail-close, tighten-only reconciliation, snap consistency, panel coverage boundaries, and unknown FAS batch continuity.

### Fixed

- Resolved ruff formatting/import-sort issues and Pyright import resolution for smoke tests.
- Declared runtime dependencies on `eb-contracts` and `eb-optimization`.

### eb-evaluation 0.2.9

- Mandatory FAS review on panel, workflow, `decide_governance`, and `run_governance_gate`.
- `apply_ral` treats NA/empty `fas_class` as BLOCKED; DQC/gate fail-close on NaN or negative demand.
- Fail-closed governance, snap, injected-decision reconciliation, and finite-coverage gates.
- `apply_ral` / `run_governance_workflow_df` keep snap mode `ceil` unless `infer_policy_from_recommendations=True`.
- `ReadinessAdjustmentLayer.transform` requires an approved decisions table; `apply_mask` cannot authorize writes alone.

### eb-optimization 0.2.7

- `apply_ral_policy` is hard-deprecated; artifact `.transform()` / `adjust_forecast` require an approved governance table.
- Leaf artifact writers refuse `apply_mask` without a valid approved decisions table.
- `snap_to_grid` and `enforce_snapping` default to `ceil`, refuse non-finite cells, and hard-raise on `enforce="ignore"`.
- `compute_dqc` delegates the full series to `eb_evaluation.classify_dqc`.

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
- Golden-path governance and RAL scripts call `electric_barometer.run_governance_workflow_df` and `electric_barometer.apply_ral`.
- FAS review is mandatory; `--no-fas` is removed.
- Exact sibling pins for System Release 0.2.9, including `electric-barometer==0.2.9`.
