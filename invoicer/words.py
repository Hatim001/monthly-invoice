"""Amount in words, Indian numbering system (thousand / lakh / crore)."""

_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
         "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
         "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
         "Eighty", "Ninety"]


def _below_100(n: int) -> str:
    if n < 20:
        return _ONES[n]
    return (_TENS[n // 10] + (" " + _ONES[n % 10] if n % 10 else "")).strip()


def _below_1000(n: int) -> str:
    parts = []
    if n >= 100:
        parts.append(_ONES[n // 100] + " Hundred")
        n %= 100
    if n:
        parts.append(_below_100(n))
    return " ".join(parts)


def amount_in_words(n: int) -> str:
    """68040 -> 'Sixty Eight Thousand Forty Only'"""
    n = int(round(n))
    if n == 0:
        return "Zero Only"
    parts = []
    for value, name in ((10_000_000, "Crore"), (100_000, "Lakh"), (1_000, "Thousand")):
        if n >= value:
            parts.append(_below_100(n // value) + " " + name)
            n %= value
    if n:
        parts.append(_below_1000(n))
    return " ".join(parts) + " Only"
