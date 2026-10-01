# DATA EXPLAINER

## Source
Global Energy Monitor, **Global Integrated Power Tracker (GIPT), September 2026 release**.

## Source table used
`Power facilities`

## Source size
183,404 rows in the supplied September 2026 workbook.

## Label construction
High-risk historical labels:
- `cancelled`
- `cancelled - inferred 4 y`
- `shelved`
- `shelved - inferred 2 y`

Low-risk historical label:
- `operating`

Unresolved records scored after training:
- `announced`
- `pre-construction`
- `construction`

`retired` is excluded because retirement occurs after operation and is not directly comparable with development-stage success/failure.

## Feature selection
Included:
- Capacity (MW)
- Type
- Country/area
- Subregion
- Region
- Technology
- Associated storage
- Fuel (combustion only)
- CHP
- CCS
- Captive Industry Type
- Location accuracy

Excluded from prediction:
- Status
- project names
- GEM IDs
- Wiki URLs
- Start year
- other outcome-revealing fields

## Leakage reasoning
`Status` is the label. Names, IDs and URLs can act as hidden identifiers. `Start year` is excluded because the workbook is a current snapshot and the field can represent actual, planned or missing dates across different project states.

## Important label limitation
`cancelled - inferred 4 y` and `shelved - inferred 2 y` partly encode GEM's own inactivity heuristics. Evaluation therefore reports confirmed and inferred subgroup recall separately.

## Reproducibility
The repository includes the processed modelling table at `data/processed/gipt_modeling.csv`.

The extraction script `src/extract_gipt.py` can rebuild the processed table from the original workbook.
