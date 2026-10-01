# EnergyInvest — Real GIPT Version

## Product Overview

**Persona**  
David, a senior energy investment analyst reviewing a weekly pipeline of prospective power projects.

**Problem**  
Manual first-pass screening does not scale across the Global Integrated Power Tracker (GIPT), which contains more than 183,000 facility records.

**Input**  
Structured project records from the **Global Integrated Power Tracker, September 2026 release**.

**Output**  
For each project:
- model risk score;
- `High Risk`, `Low Risk`, or `Needs Manual Review`;
- optional human-readable explanation.

**Product boundary**  
EnergyInvest is a first-pass prioritisation tool. It does **not** make investment or capital-allocation decisions.

## What Changes Compared with Today?

Without EnergyInvest, an analyst manually opens every candidate project. With the current holdout performance, the model flags **25.17%** of projects for analyst attention while capturing **91.58%** of historically high-risk cases.

For a 50-project pipeline, this corresponds to roughly **13 projects requiring attention instead of all 50**, or a **74.83% reduction in first-pass screening workload**.

## Architecture

![EnergyInvest architecture](docs/architecture.png)

```text
GIPT project records
        |
        v
Data cleaning + label construction
        |
        v
Feature pipeline
        |
        v
XGBoost classifier
        |
        v
Risk score
   |         |         |
 <0.40    0.40-0.60   >0.60
   |         |         |
Low Risk   Manual     High Risk
            Review
              |
              v
       Analyst due diligence

Optional: model evidence -> LLM explanation
```

## Metrics Targeted vs Reached

| Metric | Target / purpose | Reached |
|---|---|---:|
| High-risk recall | >=80%; avoid missing risky projects | **91.58%** |
| Flag rate | materially below 100%; measure remaining analyst workload | **25.17%** |
| Workload reduction | meaningful reduction in first-pass screening | **74.83%** |
| Confirmed-cancelled recall | validate on observed cancellations | **91.46%** |
| Cancelled-inferred recall | test sensitivity to GEM heuristic labels | **91.25%** |
| Precision among flagged | expose false-positive burden | **35.83%** |
| Abstention rate | expose uncertainty rather than force a label | **11.03%** |

## Key Design Reasoning

### Why XGBoost, not an LLM?
The core task is structured supervised classification with historical labels. XGBoost is cheaper, reproducible and easier to evaluate than prompting a foundation model for each project. An LLM is optional and restricted to explanation generation.

### Why grouped holdout?
The supplied GIPT workbook is a current snapshot rather than a historical panel. A row-level random split could place different units from the same facility in both train and test. The holdout is therefore grouped by `GEM location ID`.

### Why not use `Start year` for a time split?
Its meaning differs across resolved and prospective records and may be actual, planned or missing. Treating it as a universal observation timestamp would create a misleading time-based evaluation.

### Why exclude `retired`?
Retirement is a post-operation lifecycle state rather than a development-stage success/failure outcome. `operating` is therefore used as the low-risk comparison group.

## Real GIPT Fields Used
- `Capacity (MW)`
- `Type`
- `Country/area`
- `Subregion`
- `Region`
- `Technology`
- `Associated storage`
- `Fuel (combustion only)`
- `CHP`
- `CCS`
- `Captive Industry Type`
- `Location accuracy`

Outcome-revealing fields, names, IDs and Wiki URLs are not model features.

## Run the Project

```bash
pip install -r requirements.txt
python -m src.train
streamlit run app.py
```

The processed modelling table is already included at `data/processed/gipt_modeling.csv`.

To reproduce extraction from the original GIPT workbook:

```bash
python -m src.extract_gipt "/path/to/Global Integrated Power September 2026.xlsx"
```

## Repository Guide

```text
EnergyInvest_GIPT_Final/
├── README.md
├── requirements.txt
├── app.py
├── config.py
├── docs/
│   ├── architecture.png
│   ├── final_report.md
│   └── video_script.md
├── data/
│   ├── README_DATA.md
│   └── processed/gipt_modeling.csv
├── evals/
│   ├── README_EVALS.md
│   ├── metrics.json
│   └── holdout_predictions.csv
├── src/
│   ├── extract_gipt.py
│   ├── modeling.py
│   ├── train.py
│   ├── predict.py
│   └── explain.py
├── models/
│   └── energyinvest_gipt_model.joblib
└── outputs/
```

## Responsible Use
EnergyInvest uses no personal data. It is a first-pass decision-support prototype only; final due diligence and investment decisions remain with the analyst.
