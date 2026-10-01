"""Streamlit demo interface for EnergyInvest.

Allows analysts to upload project records, score them with the trained model,
and inspect triage outputs and aggregate flag rate.
"""

import streamlit as st
import pandas as pd
import joblib
from config import MODEL_PATH, FEATURES
from src.modeling import triage
from src.explain import explain_locally

st.set_page_config(page_title="EnergyInvest — GIPT",layout="wide")
st.title("EnergyInvest — GIPT September 2026")
st.caption("First-pass screening of unresolved power projects")
st.info("Decision-support prototype only. It does not allocate capital or replace analyst due diligence.")
file=st.file_uploader("Upload a CSV with the required GIPT feature columns",type=["csv"])
if file:
    df=pd.read_csv(file,low_memory=False); df["Capacity (MW)"]=pd.to_numeric(df["Capacity (MW)"],errors="coerce")
    missing=[c for c in FEATURES if c not in df.columns]
    if missing: st.error(f"Missing columns: {missing}")
    else:
        model=joblib.load(MODEL_PATH); scores=model.predict_proba(df[FEATURES])[:,1]; labels=triage(scores)
        df["risk_score"]=scores; df["triage"]=labels; df["explanation"]=[explain_locally(s,l) for s,l in zip(scores,labels)]
        flag=df["triage"].isin(["High Risk","Needs Manual Review"])
        c1,c2,c3=st.columns(3); c1.metric("Projects",len(df)); c2.metric("Flag rate",f"{flag.mean():.1%}"); c3.metric("Manual review",f"{(df['triage']=='Needs Manual Review').mean():.1%}")
        st.dataframe(df,use_container_width=True)
