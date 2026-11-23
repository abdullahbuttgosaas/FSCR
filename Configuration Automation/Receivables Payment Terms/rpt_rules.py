"""Receivables payment terms: every rule that needs no Oracle, for one request of the sheet (or the page's --run).
Plain words with the fix; all problems at once (value problems first, then the business choices, FSCR
ora_input_validation.md:59). The rules and defaults are the spec's sections 1-2 (CLAUDE.md > Input rules).

A problem: {"key": request key or "installments", "row": installment number or None, "text", "fix",
            "field", "value", "suggestions"} - "key"/"text"/"fix" for the preview, "field"/"value"/"suggestions"
            (and "rows"/"row"/"where" for an installment value) for the page's pause-and-ask panel.
"""
from datetime import date

NAME_MAX = 15                  # Oracle's limit for a Receivables payment term name (FSCR PKG:108)
DESC_MAX = 240
MAX_DISCOUNTS = 3
ORDINAL = ("First", "Second", "Third")
PREFIX = ("discount", "discount2", "discount3")
TAX_FREIGHT = {"include in the first installment": "INCLUDE", "allocate across all installments": "ALLOCATE"}
# Only these two until Oracle's own labels for F and T are read on its screen (FSCR contradicts itself on them;
# CLAUDE.md > Open items). The codes agree in every FSCR file.
DISCOUNT_BASIS = {"invoice amount": "I", "lines only": "L"}
DATE_BASIS = {"application date": "APPLICATION_DATE", "receipt date": "RECEIPT_DATE", "deposit date": "DEPOSIT_DATE"}
LABEL = {"INCLUDE": "Include in the first installment", "ALLOCATE": "Allocate across all installments",
         "I": "Invoice amount", "L": "Lines only", "APPLICATION_DATE": "Application date",
         "RECEIPT_DATE": "Receipt date", "DEPOSIT_DATE": "Deposit date"}
HEADER_KEYS = ("name", "set_code", "description", "from_date", "to_date", "base_amount", "print_lead_days",
               "tax_freight", "discount_basis", "discount_date_basis", "cutoff_day", "credit_check", "prepayment",
               "installments")
LINE_KEYS = ("sequence", "relative_amount", "days", "fixed_date", "day_of_month", "months_ahead") + tuple(
    f"{p}_{k}" for p in PREFIX for k in ("percent", "days", "fixed_date", "day_of_month", "months_ahead"))


class Term:
    """One checked term, values as Oracle's file wants them (codes, numbers, ISO dates)."""

    def __init__(self):
        self.name = self.set_code = self.description = None
        self.from_date = self.to_date = None
        self.base_amount = 100
        self.print_lead_days = None
        self.first_installment = self.discount_basis = None
        self.date_basis = "APPLICATION_DATE"
        self.cutoff_day = None
        self.credit_check = self.prepayment = "N"
        self.lines = []               # [{"seq", "amount", "days"|"date"|"dom"+"months", "discounts": [...]}]
        self.filled = {}              # request key -> what the automation fills in (shown on the preview)


class Problems:
    def __init__(self):
        self.items = []

    def bad(self, key, text, fix=None, value=None, suggestions=None, row=None, field=None):
        p = {"key": key, "row": row, "text": text, "fix": fix or "Change it in the sheet and upload it again.",
             "field": field or key, "value": value, "suggestions": [str(s) for s in suggestions or []][:12]}
        if row is not None:
            p.update(rows="installments", where=f"Installment {row}")
        self.items.append(p)


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def number(v, pb, key, label, lo=None, hi=None, whole=False, above=None, row=None, field=None):
    """A number or None (blank or wrong; a wrong one is a problem)."""
    if blank(v):
        return None
    where = f"Installment {row}: " if row else ""
    try:
        if isinstance(v, bool):
            raise ValueError
        n = float(str(v).replace(",", ""))
        if n != n or n in (float("inf"), float("-inf")):
            raise ValueError
    except ValueError:
        pb.bad(key, f"{where}{label} must be a number; it says '{v}'.", "Write a number, for example 30.", v,
               row=row, field=field)
        return None
    if whole and not n.is_integer():
        pb.bad(key, f"{where}{label} must be a whole number; it says '{v}'.", "Write a whole number.", v,
               row=row, field=field)
        return None
    if (lo is not None and n < lo) or (hi is not None and n > hi) or (above is not None and n <= above):
        rng = (f"between {lo} and {hi}" if hi is not None and lo is not None else
               f"above {above}" if above is not None else f"{lo} or more")
        pb.bad(key, f"{where}{label} must be {rng}; it says '{v}'.", f"Write a number {rng}.", v, row=row, field=field)
        return None
    return int(n) if n.is_integer() else n


def day(v, pb, key, label, row=None, field=None):
    if blank(v):
        return None
    where = f"Installment {row}: " if row else ""
    try:
        return date.fromisoformat(str(v).strip())
    except ValueError:
        pb.bad(key, f"{where}{label} must be a date written as YYYY-MM-DD; it says '{v}'.",
               "Write it like 2026-11-01.", v, row=row, field=field)
        return None


def yes_no(v, pb, key, label):
    if blank(v):
        return "N"
    if isinstance(v, bool):
        return "Y" if v else "N"
    t = str(v).strip().lower()
    if t in ("yes", "y", "true"):
        return "Y"
    if t in ("no", "n", "false"):
        return "N"
    pb.bad(key, f"{label} must be Yes or No; it says '{v}'.", "Write Yes or No.", v, ["Yes", "No"])
    return None


def pick(v, table, pb, key, label, why_not=None):
    if blank(v):
        return None
    code = table.get(str(v).strip().lower())
    if code is None:
        pb.bad(key, why_not.format(v=v) if why_not else f"{label} '{v}' isn't one of: "
               + ", ".join(LABEL[c] for c in table.values()) + ".",
               "Pick one of: " + ", ".join(LABEL[c] for c in table.values()) + ".", v,
               [LABEL[c] for c in table.values()])
    return code


def check(req, today=None):
    """(Term or None, problems) for one request. today: the date an empty From Date gets (Oracle's today minus one
    day, from run.py); the page always sends the From Date the preview showed."""
    pb, t = Problems(), Term()
    if not isinstance(req, dict):
        pb.bad("name", "This row could not be read.")
        return None, pb.items
    for k in sorted(set(req) - set(HEADER_KEYS)):
        pb.bad(k, f"'{k}' is not a Receivables payment term field.", "Remove it.", req[k])
    # ---- values first
    n = req.get("name")
    if blank(n):
        pb.bad("name", "Name is missing.", "Fill in the term's Name (at most 15 characters).")
    elif not isinstance(n, str):
        pb.bad("name", "Name must be text.", value=n)
    elif n != n.strip():
        pb.bad("name", f"Name '{n}' starts or ends with a space. Oracle keeps such a space, so it would be a "
               "different term; remove it.", "Remove the space at the start or end.", n, [n.strip()])
    elif len(n) > NAME_MAX:
        pb.bad("name", f"Name is longer than 15 characters (Oracle's limit for Receivables payment terms). "
               f"Shorten it.", f"Shorten it to 15 characters or fewer, for example '{n[:NAME_MAX].rstrip()}'.",
               n, [n[:NAME_MAX].rstrip()])
    else:
        t.name = n
    s = req.get("set_code")
    if blank(s):
        pb.bad("set_code", "Set Code is missing. Choose Oracle's reference data set for this term; it is never "
               "filled in for you.", "Pick the set from the drop-down, for example COMMON.")
    else:
        t.set_code = str(s).strip()
    d = req.get("description")
    if not blank(d):
        if len(str(d)) > DESC_MAX:
            pb.bad("description", f"Item Description can be at most {DESC_MAX} characters; it has {len(str(d))}.",
                   f"Shorten it to {DESC_MAX} characters.", d, [str(d)[:DESC_MAX].rstrip()])
        else:
            t.description = str(d)
    t.from_date = day(req.get("from_date"), pb, "from_date", "From Date")
    if blank(req.get("from_date")) and today:
        t.from_date = today
        t.filled["from_date"] = f"{today.isoformat()} (Oracle's today minus one day)"
    t.to_date = day(req.get("to_date"), pb, "to_date", "To Date")
    if t.from_date and t.to_date and t.to_date <= t.from_date:
        pb.bad("to_date", "To Date must be after the From Date.",
               f"Write a date after {t.from_date.isoformat()}, or leave it empty for no end.", req.get("to_date"))
    base = number(req.get("base_amount"), pb, "base_amount", "Base Amount", above=0)
    if blank(req.get("base_amount")):
        t.filled["base_amount"] = "100 (the installments are then percentages)"
    elif base is not None:
        t.base_amount = base
    t.print_lead_days = number(req.get("print_lead_days"), pb, "print_lead_days", "Print Lead Days", lo=0, whole=True)
    t.cutoff_day = number(req.get("cutoff_day"), pb, "cutoff_day", "Cutoff Day", 1, 31, whole=True)
    t.credit_check = yes_no(req.get("credit_check"), pb, "credit_check", "Credit Check")
    t.prepayment = yes_no(req.get("prepayment"), pb, "prepayment", "Prepayment")
    tf = pick(req.get("tax_freight"), TAX_FREIGHT, pb, "tax_freight", "Tax and Freight")
    db = pick(req.get("discount_basis"), DISCOUNT_BASIS, pb, "discount_basis", "Discount Basis",
              "Discount Basis '{v}' can't be used yet: only Invoice amount and Lines only are offered until Oracle's "
              "own words for the other two are confirmed on its screen.")
    ddb = pick(req.get("discount_date_basis"), DATE_BASIS, pb, "discount_date_basis", "Discount Date Basis")
    if ddb:
        t.date_basis = ddb
    elif blank(req.get("discount_date_basis")):
        t.filled["discount_date_basis"] = "Application date"
    # ---- installments
    rows = req.get("installments")
    if not isinstance(rows, list) or not rows:
        pb.bad("installments", "This term has no installments. Add at least one row for it on the Receivables Term "
               "Lines tab.", "Add an installment row with this term's Name, a Relative Amount and its Days.")
        rows = []
    seqs = []
    for i, r in enumerate(rows, 1):
        ln = check_line(r, i, pb, seqs)
        if ln:
            t.lines.append(ln)
    has_disc = any(ln["discounts"] for ln in t.lines) or any(
        isinstance(r, dict) and any(not blank(r.get(f"{p}_percent")) for p in PREFIX) for r in rows)
    base_ok = base is not None or blank(req.get("base_amount"))
    if t.lines and len(t.lines) == len(rows) and base_ok:
        total = sum(float(ln["amount"]) for ln in t.lines)
        if abs(total - float(t.base_amount)) > 1e-9:
            pb.bad("installments", f"The installments add up to {total:g}, but Base Amount is {t.base_amount:g}. "
                   f"They must add up to exactly {t.base_amount:g}.",
                   f"Change the Relative Amounts so they add up to {t.base_amount:g}, or change Base Amount.")
    # ---- business choices (never defaulted)
    split = len(rows) >= 2
    if split:
        if blank(req.get("print_lead_days")):
            pb.bad("print_lead_days", f"This term has {len(rows)} installments, so Print Lead Days is needed (a whole "
                   "number above 0).", "Fill in Print Lead Days, for example 1.", None, ["1"])
        elif t.print_lead_days is not None and t.print_lead_days <= 0:
            pb.bad("print_lead_days", f"This term has {len(rows)} installments, so Print Lead Days must be a whole "
                   f"number above 0; it says '{req.get('print_lead_days')}'.", "Write a whole number above 0.",
                   req.get("print_lead_days"), ["1"])
        if blank(req.get("tax_freight")):
            pb.bad("tax_freight", f"This term has {len(rows)} installments: choose Tax and Freight (first "
                   "installment, or across all installments).", "Pick one from the drop-down.", None,
                   [LABEL["INCLUDE"], LABEL["ALLOCATE"]])
    if tf:
        t.first_installment = tf
    elif blank(req.get("tax_freight")) and not split:
        t.first_installment = "INCLUDE"
        t.filled["tax_freight"] = LABEL["INCLUDE"]
    if has_disc:
        if blank(req.get("discount_basis")):
            pb.bad("discount_basis", "A discount is given, so choose the Discount Basis.",
                   "Pick Invoice amount or Lines only.", None, [LABEL["I"], LABEL["L"]])
    elif blank(req.get("discount_basis")):
        db = "I"
        t.filled["discount_basis"] = LABEL["I"]
    t.discount_basis = db
    if blank(req.get("credit_check")):
        t.filled["credit_check"] = "No"
    if blank(req.get("prepayment")):
        t.filled["prepayment"] = "No"
    return (t if not pb.items else None), pb.items


def check_line(r, i, pb, seqs):
    """One installment row: its share, ONE due date, up to three discounts."""
    w = f"Installment {i}: "
    if not isinstance(r, dict):
        pb.bad("installments", f"{w}this row could not be read.", row=i)
        return None
    before = len(pb.items)
    extra = sorted(set(r) - set(LINE_KEYS))
    if any(k.startswith("discount") for k in extra):
        pb.bad("installments", f"{w}at most 3 discounts per installment (Oracle's limit).",
               "Keep the First, Second and Third Discount only.", row=i)
        extra = [k for k in extra if not k.startswith("discount")]
    for k in extra:
        pb.bad("installments", f"{w}'{k}' is not an installment field.", "Remove it.", row=i)
    seq = number(r.get("sequence"), pb, "installments", "Sequence", lo=1, whole=True, row=i, field="sequence")
    seq = seq if seq is not None else (i if blank(r.get("sequence")) else None)
    if seq is not None and seq in seqs:
        pb.bad("installments", f"{w}Sequence {seq} is used twice in this term.", "Give each installment its own "
               "Sequence, or leave Sequence empty (then 1, 2, 3 in row order).", r.get("sequence"), row=i,
               field="sequence")
    seqs.append(seq)
    amount = r.get("relative_amount")
    if blank(amount):
        pb.bad("installments", f"{w}Relative Amount is missing.", "Fill in its share of the Base Amount, for "
               "example 50.", row=i, field="relative_amount")
        amt = None
    else:
        amt = number(amount, pb, "installments", "Relative Amount", above=0, row=i, field="relative_amount")
        if amt is None and len(pb.items) > before and "above 0" in pb.items[-1]["text"]:
            pb.items[-1]["text"] = (f"{w}Relative Amount must be above 0; it says '{amount}'. Relative Amount is a "
                                    "share of the Base Amount, not money, so Receivables has no amount-due line of 0.")
    days = number(r.get("days"), pb, "installments", "Days", lo=0, whole=True, row=i, field="days")
    fixed = day(r.get("fixed_date"), pb, "installments", "Fixed Date", row=i, field="fixed_date")
    dom = number(r.get("day_of_month"), pb, "installments", "Day of Month", 1, 31, whole=True, row=i,
                 field="day_of_month")
    months = number(r.get("months_ahead"), pb, "installments", "Months Ahead", lo=0, whole=True, row=i,
                    field="months_ahead")
    used = [lab for k, lab in (("days", "Days"), ("fixed_date", "Fixed Date"), ("day_of_month", "Day of Month"))
            if not blank(r.get(k))]
    if len(used) != 1:
        pb.bad("installments", f"{w}give one due date: Days, Fixed Date or Day of Month." if not used else
               f"{w}give one due date, not {' and '.join(used)}.", "Keep one of Days, Fixed Date or Day of Month.",
               row=i, field="days")
    if not blank(r.get("day_of_month")) and blank(r.get("months_ahead")):
        pb.bad("installments", f"{w}Day of Month needs Months Ahead (0 = same month).", "Fill in Months Ahead, "
               "for example 0 or 1.", None, ["0", "1"], row=i, field="months_ahead")
    if not blank(r.get("months_ahead")) and blank(r.get("day_of_month")):
        pb.bad("installments", f"{w}Months Ahead only goes with Day of Month.", "Remove Months Ahead, or add a Day "
               "of Month.", r.get("months_ahead"), row=i, field="months_ahead")
    discounts, pcts, gap = [], [], False
    for k, p in enumerate(PREFIX):
        label = f"{ORDINAL[k]} Discount"
        given = [x for x in ("percent", "days", "fixed_date", "day_of_month", "months_ahead") if not blank(r.get(f"{p}_{x}"))]
        if not given:
            gap = True
            continue
        if gap:
            pb.bad("installments", f"{w}fill the {ORDINAL[k - 1]} Discount before the {label}.", "Move it to the "
                   "first empty discount section.", row=i, field=f"{p}_percent")
        pct = number(r.get(f"{p}_percent"), pb, "installments", f"{label} (%)", 0, 100, row=i, field=f"{p}_percent")
        if blank(r.get(f"{p}_percent")):
            pb.bad("installments", f"{w}the {label} has its date but no percent.", "Fill in its percent, or clear "
                   "the whole discount.", row=i, field=f"{p}_percent")
        elif pct is None and len(pb.items) and "between 0 and 100" in pb.items[-1]["text"]:
            pb.items[-1]["text"] = f"{w}a discount must be between 0 and 100 percent."
        if pct is not None:
            if pct in pcts:
                pb.bad("installments", f"{w}{pct:g}% is given twice. Each discount on an installment needs its own "
                       "percent.", "Change one of the two percents, or remove one discount.", r.get(f"{p}_percent"),
                       row=i, field=f"{p}_percent")
            pcts.append(pct)
        dd = number(r.get(f"{p}_days"), pb, "installments", f"{label} Days", lo=0, whole=True, row=i,
                    field=f"{p}_days")
        df = day(r.get(f"{p}_fixed_date"), pb, "installments", f"{label} Fixed Date", row=i, field=f"{p}_fixed_date")
        dm = number(r.get(f"{p}_day_of_month"), pb, "installments", f"{label} Day of Month", 1, 31, whole=True,
                    row=i, field=f"{p}_day_of_month")
        da = number(r.get(f"{p}_months_ahead"), pb, "installments", f"{label} Months Ahead", lo=0, whole=True,
                    row=i, field=f"{p}_months_ahead")
        when = [x for x in ("days", "fixed_date", "day_of_month") if not blank(r.get(f"{p}_{x}"))]
        if len(when) != 1:
            pb.bad("installments", f"{w}the {label} needs one date: Days, Fixed Date or Day of Month." if not when
                   else f"{w}the {label} needs one date, not several.", "Keep one of its Days, Fixed Date or Day "
                   "of Month.", row=i, field=f"{p}_days")
        if not blank(r.get(f"{p}_day_of_month")) and blank(r.get(f"{p}_months_ahead")):
            pb.bad("installments", f"{w}the {label}'s Day of Month needs Months Ahead (0 = same month).",
                   "Fill in its Months Ahead, for example 0.", None, ["0", "1"], row=i, field=f"{p}_months_ahead")
        if not blank(r.get(f"{p}_months_ahead")) and blank(r.get(f"{p}_day_of_month")):
            pb.bad("installments", f"{w}the {label}'s Months Ahead only goes with its Day of Month.",
                   "Remove it, or add the Day of Month.", row=i, field=f"{p}_months_ahead")
        discounts.append({"percent": pct, "days": dd, "date": df, "dom": dm, "months": da})
    if len(discounts) > MAX_DISCOUNTS:
        pb.bad("installments", f"{w}at most 3 discounts per installment (Oracle's limit).", row=i)
    if len(pb.items) > before:
        return None
    return {"seq": seq, "amount": amt, "days": days, "date": fixed, "dom": dom, "months": months,
            "discounts": discounts}


def describe(t, language, set_name=None):
    """What Oracle will get, in plain words (the preview's summary)."""
    def when(x, word="in"):
        if x.get("days") is not None:
            return f"{word} {x['days']} days"
        if x.get("date"):
            return f"on {x['date'].isoformat()}"
        return f"on day {x['dom']}" + (f", {x['months']} month(s) ahead" if x.get("months") else " of the same month")
    parts = []
    for ln in t.lines:
        ds = "; ".join(f"{d['percent']:g}% discount {when(d, 'within')}" for d in ln["discounts"])
        parts.append(f"{ln['amount']:g} {when(ln)}" + (f" ({ds})" if ds else ""))
    n = len(t.lines)
    return (f"Oracle will get: {n} installment{'s' if n != 1 else ''}: " + "; ".join(parts) +
            f". Base Amount {t.base_amount:g}"
            + (f", Print Lead Days {t.print_lead_days}" if t.print_lead_days is not None else "")
            + f", tax and freight: {LABEL[t.first_installment].lower()}, discount basis: {LABEL[t.discount_basis].lower()}"
            f", discount date basis: {LABEL[t.date_basis].lower()}. Set {t.set_code}"
            + (f" ({set_name})" if set_name and set_name != t.set_code else "")
            + f", name language {language}. From {t.from_date.isoformat() if t.from_date else '(not set)'}"
            + (f" to {t.to_date.isoformat()}" if t.to_date else "")
            + ". Also set: In Use No, Allow Discount on Partial Payments No, no billing cycle (not on the sheet).")
