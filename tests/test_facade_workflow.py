"""Facade workflow tests through ``electric_barometer`` public imports."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import electric_barometer as eb


def _build_sample_panel_df() -> pd.DataFrame:
    n = 60
    y_a = np.array([0.1 * (i + 1) for i in range(n)], dtype=float)
    base_a = np.array([v * 0.90 if (i % 2) else v for i, v in enumerate(y_a)], dtype=float)
    ral_a = np.array([v * 1.01 for v in y_a], dtype=float)
    y_b = np.array(([0.0] * 10) + ([4.0] * 20) + ([8.0] * 15) + ([12.0] * 15), dtype=float)
    base_b = np.array(([0.0] * 10) + ([4.0] * 20) + ([4.0] * 15) + ([8.0] * 15), dtype=float)
    ral_b = y_b.copy()
    df_a = pd.DataFrame(
        {
            "site_id": [1] * n,
            "forecast_entity_id": [10] * n,
            "y": y_a,
            "yhat_base": base_a,
            "yhat_ral": ral_a,
        }
    )
    df_b = pd.DataFrame(
        {
            "site_id": [2] * n,
            "forecast_entity_id": [20] * n,
            "y": y_b,
            "yhat_base": base_b,
            "yhat_ral": ral_b,
        }
    )
    return pd.concat([df_a, df_b], ignore_index=True)


def test_facade_omitted_fas_fails_closed() -> None:
    df = _build_sample_panel_df()
    panel, decisions = eb.run_governance_workflow_df(
        df=df,
        keys=["site_id", "forecast_entity_id"],
        actual_col="y",
        base_forecast_col="yhat_base",
        ral_forecast_col="yhat_ral",
        tau=2.0,
    )
    assert (decisions["fas_class"] == "BLOCKED").all()
    assert (decisions["status"] == "red").all()
    assert (decisions["ral_policy"] == "disallow").all()
    np.testing.assert_allclose(
        panel["yhat_ral_governed"].to_numpy(dtype=float),
        panel["yhat_base_governed"].to_numpy(dtype=float),
        rtol=0,
        atol=1e-12,
    )
    assert not panel["ral_apply_ral_applied"].to_numpy(dtype=bool).any()


def test_facade_apply_ral_copies_baseline_when_fas_missing() -> None:
    df = _build_sample_panel_df()
    _panel, decisions = eb.run_governance_workflow_df(
        df=df,
        keys=["site_id", "forecast_entity_id"],
        actual_col="y",
        base_forecast_col="yhat_base",
        ral_forecast_col="yhat_ral",
        tau=2.0,
    )
    applied = eb.apply_ral(
        df=df,
        decisions=decisions,
        key_cols=["site_id", "forecast_entity_id"],
        yhat_base_col="yhat_base",
        yhat_ral_col="yhat_ral",
    )
    np.testing.assert_allclose(
        applied["yhat_ral_governed"].to_numpy(dtype=float),
        applied["yhat_base_governed"].to_numpy(dtype=float),
        rtol=0,
        atol=1e-12,
    )


def test_facade_injected_allow_cannot_bypass_snap() -> None:
    df = _build_sample_panel_df()
    decisions = pd.DataFrame(
        {
            "site_id": [1, 2],
            "forecast_entity_id": [10, 20],
            "ral_policy": ["allow", "allow"],
            "status": ["green", "green"],
            "fas_class": ["ALLOWED", "ALLOWED"],
            "dqc_class": ["continuous_like", "continuous_like"],
            "snap_required": [False, False],
            "snap_unit": [np.nan, np.nan],
        }
    )
    _panel, out_decisions = eb.run_governance_workflow_df(
        df=df,
        keys=["site_id", "forecast_entity_id"],
        actual_col="y",
        base_forecast_col="yhat_base",
        ral_forecast_col="yhat_ral",
        tau=2.0,
        fas_class="ALLOWED",
        decisions_df=decisions,
    )
    row_q = out_decisions[out_decisions["forecast_entity_id"] == 20].iloc[0]
    assert str(row_q["dqc_class"]).lower() in {"quantized", "piecewise_packed"}
    assert bool(row_q["snap_required"]) is True
    snap_unit = float(str(row_q["snap_unit"]))
    assert np.isfinite(snap_unit) and snap_unit > 0.0


def test_facade_injected_allow_cannot_upgrade_gate_caution() -> None:
    df = _build_sample_panel_df()
    df["fas_class"] = "CONDITIONAL"
    decisions = pd.DataFrame(
        {
            "site_id": [1, 2],
            "forecast_entity_id": [10, 20],
            "ral_policy": ["allow", "allow"],
            "status": ["green", "green"],
            "fas_class": ["ALLOWED", "ALLOWED"],
            "dqc_class": ["continuous_like", "continuous_like"],
            "snap_required": [False, False],
            "snap_unit": [np.nan, np.nan],
        }
    )
    _panel, out_decisions = eb.run_governance_workflow_df(
        df=df,
        keys=["site_id", "forecast_entity_id"],
        actual_col="y",
        base_forecast_col="yhat_base",
        ral_forecast_col="yhat_ral",
        tau=2.0,
        fas_class_col="fas_class",
        decisions_df=decisions,
    )
    row = out_decisions[out_decisions["forecast_entity_id"] == 10].iloc[0]
    policy = str(row["ral_policy"]).lower()
    assert policy != "allow"
    assert policy in {"caution_after_snap", "disallow"}
    assert str(row["status"]).lower() in {"yellow", "red"}


def test_facade_enforce_snapping_default_matches_apply_ral_ceil() -> None:
    df = _build_sample_panel_df()
    panel, decisions = eb.run_governance_workflow_df(
        df=df,
        keys=["site_id", "forecast_entity_id"],
        actual_col="y",
        base_forecast_col="yhat_base",
        ral_forecast_col="yhat_ral",
        tau=2.0,
        fas_class="ALLOWED",
        snap_mode="ceil",
    )
    row_q = decisions[decisions["forecast_entity_id"] == 20].iloc[0]
    if not bool(row_q["snap_required"]):
        pytest.skip("quantized stream did not require snap")
    unit = float(row_q["snap_unit"])
    stream = df.loc[df["forecast_entity_id"] == 20]
    y_vals = [float(v) for v in stream["y"].tolist()]
    dqc = eb.classify_dqc(y=y_vals)
    ral_vals = np.asarray(stream["yhat_ral"], dtype=float)
    enforced = eb.enforce_snapping(ral_vals, dqc=dqc, enforce="snap")
    governed = panel.loc[panel["forecast_entity_id"] == 20, "yhat_ral_governed"]
    if bool(panel.loc[panel["forecast_entity_id"] == 20, "ral_apply_ral_applied"].any()):
        np.testing.assert_allclose(governed.to_numpy(dtype=float), enforced, rtol=0, atol=1e-12)
    snapped_base = eb.enforce_snapping(
        np.asarray(stream["yhat_base"], dtype=float),
        dqc=dqc,
        enforce="snap",
    )
    assert unit > 0
    np.testing.assert_allclose(
        np.round(enforced / unit),
        enforced / unit,
        rtol=0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        np.round(snapped_base / unit),
        snapped_base / unit,
        rtol=0,
        atol=1e-12,
    )


def test_facade_enforce_snapping_rejects_ignore() -> None:
    y = [0.1 * i for i in range(1, 40)]
    dqc = eb.classify_dqc(y=y)
    with pytest.raises(ValueError, match="ignore"):
        eb.enforce_snapping(np.array(y, dtype=float), dqc=dqc, enforce="ignore")
