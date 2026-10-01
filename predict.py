"""Batch prediction utility for EnergyInvest.

Loads the trained pipeline and scores a user-supplied CSV using the
required GIPT-derived feature columns.
"""

import argparse
import joblib
import pandas as pd
from config import MODEL_PATH, FEATURES
from src.modeling import triage

def main():
    p=argparse.ArgumentParser(); p.add_argument("csv"); p.add_argument("--out",default="outputs/predictions.csv")
    a=p.parse_args(); df=pd.read_csv(a.csv,low_memory=False); df["Capacity (MW)"]=pd.to_numeric(df["Capacity (MW)"],errors="coerce")
    model=joblib.load(MODEL_PATH); scores=model.predict_proba(df[FEATURES])[:,1]
    df["risk_score"]=scores; df["triage"]=triage(scores); df.to_csv(a.out,index=False); print(df[["risk_score","triage"]].head())
if __name__=="__main__": main()
