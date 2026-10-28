"""
Remembers the running bill counter in state.json.

  counter : last number handed out (only ever goes up, never resets)
  issued  : {"2026-11": "20261101-001", ...}  one bill number per month

Because each month is recorded, re-running the job in the same month
(a manual test, a retry after an error) re-uses that month's bill number
instead of burning a new one.
"""
import json
from datetime import date

from .invoice_data import ROOT

STATE_FILE = ROOT / "state.json"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"counter": 0, "issued": {}}
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def next_bill_no(cfg: dict, state: dict, bill_date: date) -> tuple[str, dict]:
    """Return (bill_no, new_state). Does NOT write anything to disk."""
    key = f"{bill_date:%Y-%m}"
    if key in state["issued"]:
        return state["issued"][key], state

    counter = max(state["counter"] + 1, cfg.get("counter_start", 1))
    bill_no = cfg["bill_no_format"].format(date=bill_date, counter=counter)
    new_state = {
        "counter": counter,
        "issued": {**state["issued"], key: bill_no},
    }
    return bill_no, new_state
