"""Training entry point for EnergyInvest.

Runs load -> label -> grouped holdout -> train -> evaluate -> save artifacts.
"""

import json
import joblib
from config import DATA_PATH, MODEL_PATH, METRICS_PATH, PREDICTIONS_PATH, FEATURES, TARGET_COL
from src.modeling import load_source, build_resolved_dataset, group_holdout, build_pipeline, evaluate, score_unresolved

def main():
    source=load_source(); resolved=build_resolved_dataset(source)
    train,test=group_holdout(resolved)
    model=build_pipeline(train[TARGET_COL]); model.fit(train[FEATURES],train[TARGET_COL])
    metrics,preds=evaluate(model,test)
    metrics["data"].update({
        "n_source":int(len(source)),"n_resolved":int(len(resolved)),
        "n_train":int(len(train)),"n_test":int(len(test)),
        "train_high_risk_base_rate":float(train[TARGET_COL].mean())
    })
    MODEL_PATH.parent.mkdir(parents=True,exist_ok=True); joblib.dump(model,MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    preds.to_csv(PREDICTIONS_PATH,index=False)
    unresolved=score_unresolved(model,source)
    unresolved.to_csv(METRICS_PATH.parent/"unresolved_scored.csv",index=False)
    print(json.dumps(metrics,indent=2))

if __name__=="__main__": main()
