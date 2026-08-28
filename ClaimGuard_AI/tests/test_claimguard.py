import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(): return json.loads((ROOT/"data/business_data.json").read_text(encoding="utf-8"))
def test_domains():
    d=load()
    assert len(d["transactions"])>=5 and len(d["orders"])>=5 and len(d["invoices"])>=3 and len(d["refunds"])>=3 and len(d["customers"])>=5
def test_signals():
    d=load()
    assert any(x["status"]=="failed" for x in d["transactions"])
    assert any(x["status"]=="abandoned" for x in d["orders"])
    assert any(x["status"]=="unpaid" for x in d["invoices"])
    assert any(x["reason"]=="duplicate" for x in d["refunds"])
