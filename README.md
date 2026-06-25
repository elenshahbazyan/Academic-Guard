# Student Dropout Risk Prediction - Multi-Agent System

A multi-agent decision-support system that identifies at-risk students and generates actionable intervention plans by combining statistical machine learning, rule-based domain expertise, and LLM-driven reasoning.

## Overview

Predicting student dropout is not a problem that a single model can fully own. A classifier can surface *who* is at risk, but it cannot explain institutional policy (e.g. "zero approved units is an automatic critical case" or "a scholarship holder with elevated risk must be flagged to the scholarship office"), and it cannot turn a probability into a concrete, prioritized action plan for an advisor.

This project addresses that gap with three cooperating agents, each responsible for a distinct layer of reasoning, coordinated through a shared **blackboard architecture**:

| Agent | Reasoning Paradigm | Responsibility |
|---|---|---|
| **Agent 1 — ML Risk Scorer** | Statistical pattern recognition | Learns dropout patterns from historical data and produces a calibrated risk score |
| **Agent 2 — Expert System** | Symbolic, rule-based reasoning | Encodes institutional policy and domain knowledge as explicit, auditable rules |
| **Agent 3 — LLM Planner** | Natural-language synthesis | Reconciles Agents 1 & 2 into a structured, human-readable intervention plan |

Each agent writes its findings to a shared `blackboard` dictionary that is progressively enriched as it passes through the pipeline, and the orchestrator persists the final result as a structured report per student.

## Why a Multi-Agent Design?

A single black-box model would have two weaknesses this architecture is built to avoid:

- **Loss of institutional knowledge.** Some risk signals (unpaid tuition + zero approved units, a scholarship holder trending toward failure) are policy-defined, not statistically discovered. The expert system encodes these as first-class, explainable rules rather than hoping the ML model learns them implicitly.
- **No accountability trail.** A raw probability score gives an advisor nothing to act on. By forcing the ML score through a rule engine and then an LLM planner, every final verdict is backed by a traceable reasoning chain — which rules fired, why, and what action they recommend.

The system also has a built-in **conflict-detection mechanism**: if the expert system's risk category and the ML model's verdict disagree by two or more severity levels, this is flagged as an override. This is intentional — it surfaces exactly the cases where statistical pattern and domain policy disagree, which are precisely the cases most deserving of human review rather than automated resolution.

## Agent Details

### Agent 1 — ML Risk Scorer (`agents/agent1_ml.py`)
A `RandomForestClassifier` trained on academic, demographic, and financial features (200 trees, stratified train/test split, standardized features). Chosen for being CPU-friendly, robust to mixed feature scales, and — critically — interpretable via feature importances. Each prediction returns not just a 0–100 risk score, but the top contributing features for that specific student, giving downstream agents and advisors a window into *why* the model raised a flag.

### Agent 2 — Expert System (`agents/agent2_expert.py`)
A forward-chaining rule engine encoding 14 domain rules across three categories:
- **Academic performance** — unit approval rates, grade thresholds, disengagement signals (e.g. zero evaluations taken)
- **Financial standing** — overdue tuition, debtor status
- **Combined risk** — rules that reason jointly over ML output and structured data (e.g. a scholarship holder with a high ML score, a mature student trending downward)

Rules fire independently and aggregate into a severity category (LOW → CRITICAL), producing a fully traceable reasoning chain and a deduplicated list of recommended actions. This is also where the ML/expert conflict check lives, producing an explicit override flag and justification when the two agents disagree.

### Agent 3 — LLM Intervention Planner (`agents/agent3_llm.py`)
A locally-run LLM (via Ollama) takes the structured outputs of both prior agents — including any flagged conflict — and synthesizes them into a single coherent decision: a final risk category, a one-line case summary, a ranked list of concrete interventions with timing, an encouraging message addressed to the student, and an escalation flag. Running the model locally keeps the system free of per-request API costs and external dependencies. A deterministic, rule-derived fallback path ensures the pipeline always produces a usable report even if the LLM is unavailable — the system degrades gracefully rather than failing.

## Orchestration (`orchestrator.py`)

The `Orchestrator` drives the three agents in sequence, threading a shared blackboard dictionary through each step so every agent's output is visible to the next. It detects and surfaces agent disagreement, prints a consolidated final report, and persists the full reasoning trail — ML score, fired rules, conflict status, and the generated intervention plan — as a timestamped JSON artifact per student, giving every decision a permanent, auditable record.

## Design Highlights

- **Explainability by construction** — every risk verdict traces back to feature importances, fired rules, or both; nothing is a black box.
- **Human-in-the-loop by design** — the ML/expert conflict check exists specifically to route disagreement toward human judgment rather than silently picking a winner.
- **Resilience** — the LLM stage has a fully deterministic fallback, so the absence of an external service degrades the system rather than breaking it.
- **Auditability** — every analysis produces a persisted, structured report capturing the full multi-agent reasoning trail, not just a final number.

## Tech Stack

- **Python** — core implementation
- **scikit-learn** — Random Forest classifier, feature scaling, evaluation metrics
- **pandas / joblib** — data handling and model persistence
- **Ollama (gemma2:2b)** — local LLM inference for intervention planning

    ├── model.joblib         # Persisted trained model + scaler
    └── report_*.json        # Per-student analysis reports
```
