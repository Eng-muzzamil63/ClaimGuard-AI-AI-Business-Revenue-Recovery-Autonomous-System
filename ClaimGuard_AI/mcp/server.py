from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from fastmcp import FastMCP

ROOT=Path(__file__).resolve().parents[1]
DATA_FILE=Path(os.getenv("CLAIMGUARD_DATA_DIR", ROOT/"data"))/"business_data.json"
mcp=FastMCP("ClaimGuard AI")

def load()->dict[str,Any]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))
def save(d):
    DATA_FILE.write_text(json.dumps(d,indent=2),encoding="utf-8")
def cmap(d): return {c["id"]:c for c in d["customers"]}

@mcp.tool
def get_revenue_snapshot():
    """Return high-level revenue leakage signals."""
    d=load()
    failed=sum(x["amount"] for x in d["transactions"] if x["status"]=="failed")
    abandoned=sum(x["amount"] for x in d["orders"] if x["status"]=="abandoned")
    unpaid=sum(x["amount"] for x in d["invoices"] if x["status"]=="unpaid")
    refunds=sum(x["amount"] for x in d["refunds"] if x["reason"]=="duplicate")
    return {"company":d["company"],"failed_payment_value":failed,"abandoned_order_value":abandoned,"unpaid_invoice_value":unpaid,"duplicate_refund_value":refunds,"gross_leakage_signals":failed+abandoned+unpaid+refunds}

@mcp.tool
def query_transactions(status:str|None=None):
    """Return transactions, optionally filtered by status."""
    rows=load()["transactions"]; return [r for r in rows if status is None or r["status"]==status]
@mcp.tool
def query_orders(status:str|None=None):
    """Return orders, optionally filtered by status."""
    rows=load()["orders"]; return [r for r in rows if status is None or r["status"]==status]
@mcp.tool
def query_invoices(status:str|None=None):
    """Return invoices, optionally filtered by status."""
    rows=load()["invoices"]; return [r for r in rows if status is None or r["status"]==status]
@mcp.tool
def query_refunds():
    """Return refunds."""
    return load()["refunds"]
@mcp.tool
def query_customers():
    """Return customer recovery context."""
    return load()["customers"]

@mcp.tool
def find_failed_payments():
    """Find failed payments enriched with recovery context."""
    d=load(); cm=cmap(d); out=[]
    for t in d["transactions"]:
        if t["status"]!="failed": continue
        c=cm.get(t["customer_id"],{})
        p=c.get("recovery_probability",.5)
        out.append({**t,"customer_name":c.get("name"),"lifetime_value":c.get("lifetime_value"),"recovery_probability":p,"expected_recoverable_value":round(t["amount"]*p,2)})
    return sorted(out,key=lambda x:x["expected_recoverable_value"],reverse=True)

@mcp.tool
def find_abandoned_orders(min_amount:float=500):
    """Find abandoned orders above a value threshold."""
    d=load(); cm=cmap(d); out=[]
    for o in d["orders"]:
        if o["status"]!="abandoned" or o["amount"]<min_amount: continue
        c=cm.get(o["customer_id"],{}); p=c.get("recovery_probability",.5)
        out.append({**o,"customer_name":c.get("name"),"lifetime_value":c.get("lifetime_value"),"recovery_probability":p,"expected_recoverable_value":round(o["amount"]*p,2)})
    return sorted(out,key=lambda x:x["expected_recoverable_value"],reverse=True)

@mcp.tool
def find_unpaid_invoices(min_days_overdue:int=7):
    """Find unpaid invoices beyond a minimum overdue period."""
    d=load(); cm=cmap(d); out=[]
    for i in d["invoices"]:
        if i["status"]!="unpaid" or i["days_overdue"]<min_days_overdue: continue
        c=cm.get(i["customer_id"],{}); p=c.get("recovery_probability",.5)
        out.append({**i,"customer_name":c.get("name"),"expected_recoverable_value":round(i["amount"]*p,2)})
    return sorted(out,key=lambda x:x["expected_recoverable_value"],reverse=True)

@mcp.tool
def find_refund_anomalies():
    """Find refunds marked as duplicate; this is an investigation signal, not proof of fraud."""
    return sorted([r for r in load()["refunds"] if r["reason"]=="duplicate"],key=lambda x:x["amount"],reverse=True)

@mcp.tool
def calculate_recovery_opportunity():
    """Estimate recoverable revenue using explainable customer recovery probabilities."""
    a=find_failed_payments(); b=find_abandoned_orders(); c=find_unpaid_invoices(); d=find_refund_anomalies()
    totals={"failed_payments":round(sum(x["expected_recoverable_value"] for x in a),2),"abandoned_orders":round(sum(x["expected_recoverable_value"] for x in b),2),"unpaid_invoices":round(sum(x["expected_recoverable_value"] for x in c),2),"refund_anomalies":round(sum(x["amount"] for x in d),2)}
    totals["total_expected_recovery"]=round(sum(totals.values()),2); return totals

@mcp.tool
def create_recovery_case(case_type:str,reference_id:str,amount:float,rationale:str):
    """Create a synthetic recovery case. Must require human approval in the agent runtime."""
    d=load(); action={"type":"recovery_case","case_type":case_type,"reference_id":reference_id,"amount":amount,"rationale":rationale,"status":"created"}
    d["action_history"].append(action); save(d); return action

@mcp.tool
def queue_payment_recovery(transaction_id:str,message:str):
    """Queue synthetic payment recovery. Must require human approval."""
    d=load(); t=next((x for x in d["transactions"] if x["id"]==transaction_id),None)
    if not t: raise ValueError(f"Unknown transaction: {transaction_id}")
    action={"type":"payment_recovery","transaction_id":transaction_id,"amount":t["amount"],"message":message,"status":"queued"}
    d["action_history"].append(action); save(d); return action

@mcp.tool
def flag_refund_for_review(refund_id:str,reason:str):
    """Flag a synthetic refund for finance review. Must require human approval."""
    d=load(); r=next((x for x in d["refunds"] if x["id"]==refund_id),None)
    if not r: raise ValueError(f"Unknown refund: {refund_id}")
    action={"type":"refund_review","refund_id":refund_id,"amount":r["amount"],"reason":reason,"status":"flagged"}
    d["action_history"].append(action); save(d); return action

@mcp.tool
def get_action_history():
    """Return synthetic recovery actions."""
    return load()["action_history"]

if __name__=="__main__":
    mcp.run(transport="http",host="127.0.0.1",port=8001,path="/mcp")
