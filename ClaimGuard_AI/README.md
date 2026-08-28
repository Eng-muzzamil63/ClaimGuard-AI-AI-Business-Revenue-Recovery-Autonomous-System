# ClaimGuard AI

## Find lost revenue. Explain why. Recover it safely.

ClaimGuard AI is a Windows-friendly hackathon project that investigates revenue leakage across failed payments, abandoned high-value orders, unpaid invoices, and refund anomalies. It calculates recoverable revenue, prioritizes opportunities, and exposes human-approved recovery actions through MCP.

**Flow:** business question → evidence → investigation → revenue impact → recovery recommendation → human approval → action → verification.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python mcp/server.py
```

In a second terminal:

```powershell
.venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```

MCP endpoint:

`http://127.0.0.1:8001/mcp`

## TrueForge

Connect the MCP endpoint above to TrueForge. Configure human approval for the three action tools. The project does not require a local sandbox for its core workflow; sandbox execution is optional for generated calculations.

## First agent prompt

> Find all potentially recoverable revenue from the last 30 days. Investigate failed payments, abandoned high-value orders, unpaid invoices, and refund anomalies. Rank opportunities by recoverable value and confidence. Do not execute any recovery action without my approval.

All data is synthetic.

## Portfolio positioning

> Built ClaimGuard AI, an autonomous revenue-leakage investigation agent that correlates payment, order, invoice, customer, and refund data, quantifies recoverable revenue, prioritizes recovery opportunities, and requires human approval before executing financial actions.
