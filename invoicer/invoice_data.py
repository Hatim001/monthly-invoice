"""Works out this month's invoice details from config.json + today's date."""
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    with open(ROOT / "config.json", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class Invoice:
    issuer_name: str
    client_name: str
    client_address_lines: list
    account_no: str
    description_lines: list
    agreement_line: str
    hsn_code: str
    bill_no: str
    bill_date: date
    month_label: str          # e.g. "November-2026"
    basic: int
    cgst: int
    sgst: int
    cgst_percent: int
    sgst_percent: int

    @property
    def total(self) -> int:
        return self.basic + self.cgst + self.sgst


def default_invoice_date(cfg: dict) -> date:
    """Automatic invoice date: the 1st of the current month."""
    tz = ZoneInfo(cfg.get("timezone", "Asia/Kolkata"))
    return datetime.now(tz).date().replace(day=1)


def build_invoice(cfg: dict, bill_no: str, bill_date: date) -> Invoice:

    # Which month the charges are "for"
    if cfg.get("billing_month", "current") == "previous":
        y, m = (bill_date.year, bill_date.month - 1) if bill_date.month > 1 else (bill_date.year - 1, 12)
        for_month = date(y, m, 1)
    else:
        for_month = bill_date
    month_label = for_month.strftime("%B-%Y")

    basic = int(cfg["basic_amount"])
    if cfg.get("gst_applicable"):
        cgst = round(basic * cfg["cgst_percent"] / 100)
        sgst = round(basic * cfg["sgst_percent"] / 100)
    else:
        cgst = sgst = 0

    return Invoice(
        issuer_name=cfg["issuer_name"],
        client_name=cfg["client_name"],
        client_address_lines=cfg["client_address_lines"],
        account_no=cfg["account_no"],
        description_lines=cfg["description_lines"],
        agreement_line=cfg["agreement_line"],
        hsn_code=cfg["hsn_code"],
        bill_no=bill_no,
        bill_date=bill_date,
        month_label=month_label,
        basic=basic, cgst=cgst, sgst=sgst,
        cgst_percent=cfg["cgst_percent"], sgst_percent=cfg["sgst_percent"],
    )
