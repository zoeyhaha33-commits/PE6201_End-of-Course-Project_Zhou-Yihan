"""Core modelling/evaluation for EnergyInvest.

Loads GIPT data, constructs labels, performs grouped holdout splitting,
builds the preprocessing + XGBoost pipeline, applies abstention logic,
computes ML/business metrics, and scores unresolved projects.
"""

import json
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import recall_score, precision_score, f1_score, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from xgboost import XGBClassifier

from config import (
    DATA_PATH, MODEL_PATH, METRICS_PATH, PREDICTIONS_PATH, FEATURES,
    NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET_COL, STATUS_COL, GROUP_COL, ID_COL,
    HIGH_RISK_STATUSES, LOW_RISK_STATUSES, UNRESOLVED_STATUSES,
    ABSTAIN_LOW, ABSTAIN_HIGH, HIGH_RISK_THRESHOLD, TEST_SIZE, RANDOM_STATE
)

def load_source():
    df=pd.read_csv(DATA_PATH, low_memory=False)
    df["Capacity (MW)"]=pd.to_numeric(df["Capacity (MW)"], errors="coerce")
    for c in CATEGORICAL_FEATURES + [STATUS_COL, GROUP_COL, ID_COL]:
        df[c]=df[c].fillna("").astype(str)
    return df

def build_resolved_dataset(df):
    resolved=df[df[STATUS_COL].isin(HIGH_RISK_STATUSES | LOW_RISK_STATUSES)].copy()
    resolved[TARGET_COL]=resolved[STATUS_COL].isin(HIGH_RISK_STATUSES).astype(int)
    # Group fallback only if location ID is missing. This prevents blank IDs becoming one giant group.
    missing=resolved[GROUP_COL].eq("")
    resolved.loc[missing, GROUP_COL]="unit:"+resolved.loc[missing,ID_COL].astype(str)
    return resolved

def group_holdout(df):
    splitter=GroupShuffleSplit(n_splits=1,test_size=TEST_SIZE,random_state=RANDOM_STATE)
    train_idx,test_idx=next(splitter.split(df,df[TARGET_COL],groups=df[GROUP_COL]))
    return df.iloc[train_idx].copy(),df.iloc[test_idx].copy()

def build_pipeline(y):
    pos=max(int((y==1).sum()),1); neg=max(int((y==0).sum()),1)
    num=Pipeline([("imputer",SimpleImputer(strategy="median"))])
    cat=Pipeline([
        ("imputer",SimpleImputer(strategy="most_frequent")),
        ("onehot",OneHotEncoder(handle_unknown="ignore",min_frequency=5))
    ])
    prep=ColumnTransformer([("num",num,NUMERIC_FEATURES),("cat",cat,CATEGORICAL_FEATURES)])
    clf=XGBClassifier(
        n_estimators=300,max_depth=5,learning_rate=0.06,subsample=0.9,colsample_bytree=0.9,
        objective="binary:logistic",eval_metric="logloss",scale_pos_weight=neg/pos,
        random_state=RANDOM_STATE,n_jobs=4
    )
    return Pipeline([("preprocess",prep),("model",clf)])

def triage(scores):
    s=np.asarray(scores)
    return np.where((s>=ABSTAIN_LOW)&(s<=ABSTAIN_HIGH),"Needs Manual Review",
                    np.where(s>HIGH_RISK_THRESHOLD,"High Risk","Low Risk"))

def analyst_flag(labels):
    return np.isin(np.asarray(labels),["High Risk","Needs Manual Review"]).astype(int)

def subgroup_recall(frame,status):
    sub=frame[frame[STATUS_COL].eq(status)]
    if len(sub)==0:return None
    return float(sub["analyst_flag"].mean())

def evaluate(model,test):
    scores=model.predict_proba(test[FEATURES])[:,1]
    labels=triage(scores); flagged=analyst_flag(labels); y=test[TARGET_COL].to_numpy()
    out=test[[ID_COL,GROUP_COL,STATUS_COL,TARGET_COL]].copy()
    out["risk_score"]=scores; out["triage"]=labels; out["analyst_flag"]=flagged
    flag_rate=float(flagged.mean())
    metrics={
      "data": {"n_holdout":int(len(test)),"high_risk_base_rate":float(y.mean())},
      "model": {
        "recall_high_risk":float(recall_score(y,flagged,zero_division=0)),
        "precision_flagged":float(precision_score(y,flagged,zero_division=0)),
        "f1_flagged":float(f1_score(y,flagged,zero_division=0)),
        "flag_rate":flag_rate,"workload_reduction":float(1-flag_rate),
        "abstention_rate":float((labels=="Needs Manual Review").mean()),
        "recall_cancelled":subgroup_recall(out,"cancelled"),
        "recall_cancelled_inferred_4y":subgroup_recall(out,"cancelled - inferred 4 y"),
        "recall_shelved":subgroup_recall(out,"shelved"),
        "recall_shelved_inferred_2y":subgroup_recall(out,"shelved - inferred 2 y"),
        "confusion_matrix":confusion_matrix(y,flagged).tolist()
      },
      "baselines": {
        "always_low":{"recall":0.0,"flag_rate":0.0,"workload_reduction":1.0},
        "always_high":{"recall":1.0,"flag_rate":1.0,"workload_reduction":0.0}
      }
    }
    return metrics,out

def score_unresolved(model,source):
    u=source[source[STATUS_COL].isin(UNRESOLVED_STATUSES)].copy()
    scores=model.predict_proba(u[FEATURES])[:,1]
    u["risk_score"]=scores; u["triage"]=triage(scores)
    return u
