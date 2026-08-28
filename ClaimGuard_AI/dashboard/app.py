import json
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/business_data.json"
SCEN=ROOT/"data/scenarios.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
d=load(DATA); scenarios=load(SCEN); cm={c["id"]:c for c in d["customers"]}

failed=sum(x["amount"] for x in d["transactions"] if x["status"]=="failed")
abandoned=sum(x["amount"] for x in d["orders"] if x["status"]=="abandoned")
unpaid=sum(x["amount"] for x in d["invoices"] if x["status"]=="unpaid")
refunds=sum(x["amount"] for x in d["refunds"] if x["reason"]=="duplicate")
expected_failed=sum(x["amount"]*cm.get(x["customer_id"],{}).get("recovery_probability",.5) for x in d["transactions"] if x["status"]=="failed")
expected_abandoned=sum(x["amount"]*cm.get(x["customer_id"],{}).get("recovery_probability",.5) for x in d["orders"] if x["status"]=="abandoned" and x["amount"]>=500)
expected_unpaid=sum(x["amount"]*cm.get(x["customer_id"],{}).get("recovery_probability",.5) for x in d["invoices"] if x["status"]=="unpaid" and x["days_overdue"]>=7)
expected=expected_failed+expected_abandoned+expected_unpaid+refunds

st.set_page_config(page_title="ClaimGuard AI",page_icon="💰",layout="wide")
st.title("💰 ClaimGuard AI")
st.caption("Find lost revenue. Explain why. Recover it safely.")
st.metric("Estimated recoverable revenue",f"${expected:,.0f}")
a,b,c,e=st.columns(4)
a.metric("Failed payments",f"${failed:,.0f}")
b.metric("Abandoned orders",f"${abandoned:,.0f}")
c.metric("Unpaid invoices",f"${unpaid:,.0f}")
e.metric("Duplicate-refund signals",f"${refunds:,.0f}")
st.divider()
key=st.selectbox("Demo scenario",list(scenarios),format_func=lambda x:scenarios[x]["title"])
st.info(scenarios[key]["prompt"])
t1,t2,t3,t4=st.tabs(["Payments","Orders","Invoices","Refunds"])
with t1: st.dataframe(pd.DataFrame(d["transactions"]),use_container_width=True,hide_index=True)
with t2: st.dataframe(pd.DataFrame(d["orders"]),use_container_width=True,hide_index=True)
with t3: st.dataframe(pd.DataFrame(d["invoices"]),use_container_width=True,hide_index=True)
with t4: st.dataframe(pd.DataFrame(d["refunds"]),use_container_width=True,hide_index=True)
st.subheader("Action history")
if d["action_history"]: st.dataframe(pd.DataFrame(d["action_history"]),use_container_width=True,hide_index=True)
else: st.success("No recovery actions executed yet. Use human approval in the agent.")
st.caption("Synthetic demo data only.")
