"""
Generate this month's invoice PDF and send it to Telegram.

  uv run main.py                     build the PDF and send it
  uv run main.py --no-send           preview only: no Telegram, counter NOT used up
  uv run main.py --date 2026-11-01   pretend today is that date (for testing)
"""
import argparse
import os
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

from invoicer.invoice_data import ROOT, build_invoice, load_config
from invoicer.pdf import render_pdf
from invoicer.state import load_state, next_bill_no, save_state
from invoicer.telegram import send_document


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-send", action="store_true")
    ap.add_argument("--date", help="YYYY-MM-DD override for today")
    args = ap.parse_args()

    cfg = load_config()
    tz = ZoneInfo(cfg.get("timezone", "Asia/Kolkata"))
    today = date.fromisoformat(args.date) if args.date else datetime.now(tz).date()
    bill_date = today.replace(day=1)

    state = load_state()
    bill_no, new_state = next_bill_no(cfg, state, bill_date)
    inv = build_invoice(cfg, bill_no, today)

    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    pdf_path = out_dir / f"Invoice_{inv.bill_no}.pdf"
    render_pdf(inv, str(pdf_path))
    print(f"Created {pdf_path}")

    if args.no_send:
        print("Preview only: state.json left unchanged.")
        return 0

    token, chat_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are not set.", file=sys.stderr)
        return 1
    caption = f"Invoice {inv.bill_no} – {inv.month_label} – ₹{inv.total:,}"
    send_document(token, chat_id, str(pdf_path), caption)
    print("Sent to Telegram.")

    # Only after a successful send, so a failed run never uses up a number.
    save_state(new_state)
    print(f"Bill counter saved: {new_state['counter']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
