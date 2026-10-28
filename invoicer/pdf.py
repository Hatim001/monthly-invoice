"""Draws the invoice as a one-page A4 PDF that mirrors the Excel layout."""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .invoice_data import Invoice
from .words import amount_in_words

B, R = "Helvetica-Bold", "Helvetica"


def _inr(n: int) -> str:
    """Indian digit grouping: 1234567 -> 12,34,567"""
    s = str(abs(int(n)))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups + [tail])
    return ("-" if n < 0 else "") + s


def _fit(c, text, font, size, max_w):
    while c.stringWidth(text, font, size) > max_w and size > 6:
        size -= 0.5
    return size


def render_pdf(inv: Invoice, path: str) -> None:
    W, H = A4
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle(f"Invoice {inv.bill_no}")
    c.setAuthor(inv.issuer_name)

    L, Rt = 40, W - 40            # outer box left / right
    SPLIT = 375                   # start of amount table (label column)
    VAL = 455                     # start of amount value column
    pad = 8
    y = H - 50                    # current top edge

    def hline(y_, x1=L, x2=Rt, w=1.4):
        c.setLineWidth(w); c.line(x1, y_, x2, y_)

    top = y
    # ---- Title -------------------------------------------------------
    h = 52
    hline(y)
    size = _fit(c, inv.issuer_name, B, 26, Rt - L - 2 * pad)
    c.setFont(B, size)
    c.drawCentredString((L + Rt) / 2, y - h / 2 - size * 0.35, inv.issuer_name)
    y -= h
    hline(y)

    # ---- Client + bill no / date ------------------------------------
    c.setFont(B, 14)
    c.drawString(L + pad, y - 22, inv.client_name)
    c.setFont(B, 13); c.drawString(SPLIT, y - 20, "Bill No.")
    c.setFont(R, 13); c.drawRightString(Rt - pad, y - 20, str(inv.bill_no))
    y -= 32

    c.setFont(R, 11)
    c.drawString(L + pad, y - 16, inv.client_address_lines[0])
    c.setFont(B, 13); c.drawString(SPLIT, y - 16, "Date")
    c.setFont(R, 13)
    c.drawRightString(Rt - pad, y - 16, f"{inv.bill_date.day} {inv.bill_date.strftime('%B %Y')}")
    y -= 26
    for line in inv.client_address_lines[1:]:
        c.setFont(R, 11); c.drawString(L + pad, y - 16, line); y -= 26
    c.setFont(R, 11); c.drawString(L + pad, y - 16, f"A/c No. {inv.account_no}"); y -= 26

    # ---- Description --------------------------------------------------
    c.setFont(B, 11.5)
    for line in inv.description_lines:
        c.drawString(L + pad, y - 16, line); y -= 24
    c.drawString(L + pad, y - 16, f"Month of {inv.month_label}"); y -= 24
    hline(y, w=0.8)
    c.drawString(L + pad, y - 18, inv.agreement_line); y -= 28
    hline(y, w=0.8)

    # ---- Amount table -------------------------------------------------
    rows = [
        ("BASIC", _inr(inv.basic)),
        (f"CGST  {inv.cgst_percent}%", _inr(inv.cgst)),
        (f"SGST  {inv.sgst_percent}%", _inr(inv.sgst)),
        ("TOTAL", _inr(inv.total)),
    ]
    rh = 26
    tbl_top = y
    c.setLineWidth(0.8)
    for i, (lab, val) in enumerate(rows):
        ry = tbl_top - i * rh
        last = i == len(rows) - 1
        c.setFont(B if last else R, 13)
        c.drawString(SPLIT + 6, ry - rh + 8, lab)
        c.drawRightString(Rt - pad, ry - rh + 8, val)
        c.line(SPLIT, ry - rh, Rt, ry - rh)
    c.line(SPLIT, tbl_top, SPLIT, tbl_top - 4 * rh)
    c.setFont(R, 13)
    c.drawString(L + pad, tbl_top - 1.5 * rh - 4, f"HSN {inv.hsn_code}")
    y = tbl_top - 4 * rh

    # ---- In words -----------------------------------------------------
    c.setFont(B, 12)
    c.drawString(L + pad, y - 19, f"In Words- {amount_in_words(inv.total)}")
    y -= 28
    hline(y, w=0.8)

    # ---- Signature area ----------------------------------------------
    y -= 85
    c.setFont(B, 13)
    c.drawRightString(Rt - pad, y + 12, inv.issuer_name)
    hline(y)

    # outer vertical borders
    c.setLineWidth(1.4)
    c.line(L, top, L, y); c.line(Rt, top, Rt, y)

    c.showPage()
    c.save()
