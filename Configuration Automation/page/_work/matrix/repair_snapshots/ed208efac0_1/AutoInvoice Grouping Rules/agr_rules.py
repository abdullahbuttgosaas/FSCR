"""AutoInvoice grouping rules: every rule that needs no Oracle, for one request of the sheet (or the page's --run).
Plain words with the fix; all problems at once. The rules are the spec's sections 1-2 (FSCR
manage-autoinvoice-grouping-rules: ora_input_validation.md, ora_defaulting_rules.md; CLAUDE.md > Input rules).

A request: {"name", "description", "from_date", "to_date", "classes": [{"transaction_class", "characteristic"}]}.
One class row = one transaction class, or one characteristic under it; rows with the same class make one class.

A problem: {"key": request key or "classes", "row": class row number or None, "text", "fix", "field", "value",
            "suggestions"} - "key"/"text"/"fix" for the preview, "field"/"value"/"suggestions" (and "rows"/"row"/
            "where" for a class row value) for the page's pause-and-ask panel.
"""
from datetime import date

NAME_MAX = 40                  # Oracle's limit for a grouping rule name (FSCR ora_input_validation.md:23)
DESC_MAX = 80                  # FSCR ora_input_validation.md:24
RESERVED = "ORA_"              # Oracle's own rules (FSCR SKILL:183)
CLASSES = {"invoice": "I", "debit memo": "D", "credit memo": "C", "i": "I", "d": "D", "c": "C"}
LABEL = {"I": "Invoice", "D": "Debit Memo", "C": "Credit Memo"}
HEADER_KEYS = ("name", "description", "from_date", "to_date", "classes")
ROW_KEYS = ("transaction_class", "characteristic")


class Rule:
    """One checked rule, values as Oracle's file wants them."""

    def __init__(self):
        self.name = self.description = None
        self.from_date = self.to_date = None
        self.classes = {}             # class code -> [characteristic names], in sheet order
        self.filled = {}              # request key -> what the automation fills in (shown on the preview)
        self.notes = {}               # request key -> yellow note


class Problems:
    def __init__(self):
        self.items = []

    def bad(self, key, text, fix=None, value=None, suggestions=None, row=None, field=None):
        p = {"key": key, "row": row, "text": text, "fix": fix or "Change it in the sheet and upload it again.",
             "field": field or key, "value": value, "suggestions": [str(s) for s in suggestions or []][:12]}
        if row is not None:
            p.update(rows="classes", where=f"Class row {row}")
        self.items.append(p)


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def day(v, pb, key, label):
    if blank(v):
        return None
    try:
        return date.fromisoformat(str(v).strip())
    except ValueError:
        pb.bad(key, f"{label} must be a date written as YYYY-MM-DD; it says '{v}'.", "Write it like 2026-11-01.", v)
        return None


def check(req):
    """(Rule or None, problems) for one request. No date is ever filled in: FSCR says the start date must be explicit
    (ora_defaulting_rules.md:14), so an empty From Date is a problem, not Oracle's today."""
    pb, t = Problems(), Rule()
    if not isinstance(req, dict):
        pb.bad("name", "This row could not be read.")
        return None, pb.items
    for k in sorted(set(req) - set(HEADER_KEYS)):
        pb.bad(k, f"'{k}' is not an AutoInvoice grouping rule field.", "Remove it.", req[k])
    n = req.get("name")
    if blank(n):
        pb.bad("name", "Name is missing.", f"Fill in the rule's Name (at most {NAME_MAX} characters).")
    elif not isinstance(n, str):
        pb.bad("name", "Name must be text.", value=n)
    elif n != n.strip():
        pb.bad("name", f"Name '{n}' starts or ends with a space. Oracle keeps such a space, so it would be a "
               "different rule; remove it.", "Remove the space at the start or end.", n, [n.strip()])
    elif len(n) > NAME_MAX:
        pb.bad("name", f"Name is longer than {NAME_MAX} characters (Oracle's limit for grouping rules). Shorten it.",
               f"Shorten it to {NAME_MAX} characters or fewer, for example '{n[:NAME_MAX].rstrip()}'.", n,
               [n[:NAME_MAX].rstrip()])
    elif n.upper().startswith(RESERVED):
        pb.bad("name", f"Name can't start with {RESERVED}: Oracle keeps those names for its own rules.",
               f"Use a name without {RESERVED} at the start, for example '{n[len(RESERVED):].lstrip('_ ')}'.", n,
               [n[len(RESERVED):].lstrip("_ ")] if n[len(RESERVED):].strip("_ ") else [])
    else:
        t.name = n
    d = req.get("description")
    if not blank(d):
        if len(str(d)) > DESC_MAX:
            pb.bad("description", f"Item Description can be at most {DESC_MAX} characters; it has {len(str(d))}.",
                   f"Shorten it to {DESC_MAX} characters.", d, [str(d)[:DESC_MAX].rstrip()])
        else:
            t.description = str(d)
    if blank(req.get("from_date")):
        pb.bad("from_date", "From Date is missing. Grouping rules need an explicit start date; it is never filled in "
               "for you.", "Fill in the date the rule starts, for example 2026-11-01.")
    t.from_date = day(req.get("from_date"), pb, "from_date", "From Date")
    t.to_date = day(req.get("to_date"), pb, "to_date", "To Date")
    if t.from_date and t.to_date and t.to_date < t.from_date:
        pb.bad("to_date", "To Date can't be before the From Date.",
               f"Write {t.from_date.isoformat()} or later, or leave it empty for no end.", req.get("to_date"))
    rows = req.get("classes")
    if rows in (None, ""):
        rows = []
    if not isinstance(rows, list):
        pb.bad("classes", "The class rows of this rule could not be read.")
        rows = []
    if not rows:
        t.notes["classes"] = ("This rule has no transaction class rows; Oracle's mandatory grouping attributes "
                              "still apply.")
    seen_plain, seen_char = set(), set()
    for i, r in enumerate(rows, 1):
        w = f"Class row {i}: "
        if not isinstance(r, dict):
            pb.bad("classes", f"{w}this row could not be read.", row=i)
            continue
        for k in sorted(set(r) - set(ROW_KEYS)):
            pb.bad("classes", f"{w}'{k}' is not a class row field.", "Remove it.", row=i)
        c = r.get("transaction_class")
        if blank(c):
            pb.bad("classes", f"{w}Transaction Class is missing.", "Pick Invoice, Debit Memo or Credit Memo.", None,
                   list(LABEL.values()), row=i, field="transaction_class")
            continue
        code = CLASSES.get(str(c).strip().lower())
        if code is None:
            pb.bad("classes", f"{w}'{c}' isn't one of: Invoice, Debit Memo, Credit Memo.",
                   "Pick one of: Invoice, Debit Memo, Credit Memo.", c, list(LABEL.values()), row=i,
                   field="transaction_class")
            continue
        ch = r.get("characteristic")
        if not blank(ch) and not isinstance(ch, str):
            ch = str(ch)
        if blank(ch):
            if code in seen_plain:
                pb.bad("classes", f"{w}{LABEL[code]} is listed twice for this rule.",
                       "Keep one row for it; add a Characteristic to the other or remove it.", c, row=i,
                       field="transaction_class")
            seen_plain.add(code)
            t.classes.setdefault(code, [])
            continue
        if ch != ch.strip():
            pb.bad("classes", f"{w}Characteristic '{ch}' starts or ends with a space.", "Remove the space.", ch,
                   [ch.strip()], row=i, field="characteristic")
            continue
        if (code, ch) in seen_char:
            pb.bad("classes", f"{w}characteristic {ch} is listed twice under {LABEL[code]}.",
                   "Keep one of the two rows.", ch, row=i, field="characteristic")
            continue
        seen_char.add((code, ch))
        t.classes.setdefault(code, []).append(ch)
    return (t if not pb.items else None), pb.items


def describe(t):
    """What Oracle will get, in plain words (the preview's summary)."""
    parts = []
    for code, chars in t.classes.items():
        parts.append(LABEL[code] + (f" grouped also by {', '.join(chars)}" if chars else " (mandatory attributes only)"))
    n = len(t.classes)
    return (f"Oracle will get: {n} transaction class{'es' if n != 1 else ''}" + (": " + "; ".join(parts) if parts else "")
            + f". From {t.from_date.isoformat()}" + (f" to {t.to_date.isoformat()}" if t.to_date else "")
            + ". Also set: no line ordering rule, no flexfields, no consolidated billing flag (not on the sheet).")
