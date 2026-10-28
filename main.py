"""
Generate an invoice PDF and send it to Telegram.

  uv run main.py                          auto date (1st of this month) + auto bill no
  uv run main.py --date 2026-11-15        invoice dated 15 Nov 2026, auto bill no
  uv run main.py --bill-no 20261101-007   auto date, your own bill no
  uv run main.py --no-send                preview only: no Telegram, counter NOT used up

Anything you don't pass is generated automatically.
"""
import argparse
import os
import re
import sys
from datetime import date

from invoicer.invoice_data import ROOT, build_invoice, default_invoice_date, load_config
from invoicer.pdf import render_pdf
from invoicer.state import load_state, next_bill_no, save_state
from invoicer.telegram import send_document


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--date", help="invoice date, YYYY-MM-DD (default: 1st of the current month)")
    ap.add_argument("--bill-no", help="bill number to use (default: auto-generated date + counter)")
    ap.add_argument("--no-send", action="store_true", help="make the PDF only")
    args = ap.parse_args()
    # Empty strings (e.g. a blank GitHub form field) count as "not passed".
    args.date = (args.date or "").strip() or None
    args.bill_no = (args.bill_no or "").strip() or None
    return args


def main() -> int:
    args = parse_args()
    cfg = load_config()

    if args.date:
        try:
            invoice_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"Invalid --date '{args.date}'. Use YYYY-MM-DD, e.g. 2026-11-01.", file=sys.stderr)
            return 2
    else:
        invoice_date = default_invoice_date(cfg)

    state = load_state()
    if args.bill_no:
        bill_no, new_state = args.bill_no, state       # manual: counter untouched
    else:
        bill_no, new_state = next_bill_no(cfg, state, invoice_date)

    inv = build_invoice(cfg, bill_no, invoice_date)

    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    safe_no = re.sub(r"[^\w.-]+", "_", inv.bill_no)
    pdf_path = out_dir / f"Invoice_{safe_no}.pdf"
    render_pdf(inv, str(pdf_path))
    print(f"Created {pdf_path}  (bill no {inv.bill_no}, dated {invoice_date:%d %b %Y}"
          f"{', manual number' if args.bill_no else ''})")

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
    if new_state is not state:
        save_state(new_state)
        print(f"Bill counter saved: {new_state['counter']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
