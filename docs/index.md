# Electric Barometer

**Electric Barometer** is a decision-governance and evaluation framework for cost-aware forecasting, asymmetric risk, and operational readiness.

It provides a structured ecosystem of metrics, contracts, evaluation tools, and optimization policies designed to support production-grade decision systems—particularly where over- and under-prediction carry materially different consequences.

## What Electric Barometer is

Electric Barometer is:

- A **framework**, not a single model
- **Cost-aware by design**, explicitly encoding asymmetric risk
- Focused on **decision impact**, not just forecast accuracy
- Built to support **production workflows**, governance, and iteration

The ecosystem is modular and composable, with clear separation between metrics, evaluation, optimization, and integration layers.

## Core concepts

At a high level, Electric Barometer centers on:

- **Cost-weighted evaluation**  
  Metrics that reflect real operational asymmetry rather than symmetric error

- **Readiness and plausibility**  
  Signals that capture whether forecasts are operationally actionable

- **Decision calibration**  
  Policies and tuning layers that translate forecasts into decisions

- **Governance and transparency**  
  Explicit contracts, diagnostics, and auditability across the lifecycle

## Package ecosystem

Electric Barometer is composed of multiple focused packages, each with a narrow responsibility:

- **Metrics** — cost-weighted and readiness-aware evaluation primitives  
- **Contracts** — canonical data structures and shared semantics  
- **Evaluation** — diagnostics, validation, and model selection  
- **Optimization** — policies, tuning, and search utilities  
- **Features** — feature engineering utilities  
- **Adapters** — integration layers for external frameworks  
- **Integration** — tooling and conventions for composing the system

Each package exposes a minimal API surface and is documented individually under the Packages section.

## How to use these docs

- Use **Packages** to explore API references for each component
- Use **Concepts** to understand the underlying ideas and design choices
- Use **Guides** to see how components fit together in practice

This documentation site serves as the **authoritative reference** for the Electric Barometer ecosystem.

---

If you want, next we can:
- refine the **Concepts** section hierarchy
- wire the **Packages** nav cleanly now that all leaf repos are synced
- or draft a short “Why Electric Barometer?” page for positioning
