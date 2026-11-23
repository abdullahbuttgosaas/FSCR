"""Transaction sources: every rule that needs no Oracle, for one request of the sheet (or the page's --run).
Plain words with the fix; all problems at once. The rules are the spec's sections 1-2 (FSCR manage-transaction-sources:
ora_input_validation.md, ora_defaulting_rules.md, ora_design_enforcement.md; CLAUDE.md > Input rules).

A request: {"name", "set_code", "description", "source_type", "from_date", "status", "auto_numbering",
            "last_number", "invalid_lines", "grouping_rule", "grouping_rule_pending"}.
"grouping_rule_pending" is set by the page when the grouping rule is a row of the same upload (registry depends_on).

A problem: {"key", "row": None, "text", "fix", "field", "value", "suggestions"}.
"""
from datetime import date

RESERVED = "ORA_"              # Oracle's own sources (FSCR ora_design_enforcement.md)
TYPES = {"manual": "INV", "inv": "INV", "imported": "FOREIGN", "foreign": "FOREIGN"}
STATUS = {"active": "A", "a": "A", "inactive": "I", "i": "I"}
INVALID_LINES = {"create invoice": "Create", "create": "Create", "reject invoice": "Reject", "reject": "Reject"}
LABEL = {"INV": "Manual", "FOREIGN": "Imported", "A": "Active", "I": "Inactive", "Create": "Create Invoice",
         "Reject": "Reject Invoice", "Y": "Yes", "N": "No"}
KEYS = ("name", "set_code", "description", "source_type", "from_date", "status", "auto_numbering", "last_number",
        "invalid_lines", "grouping_rule", "grouping_rule_pending")


class Source:
    """One checked source, values as Oracle's file wants them."""

    def __init__(self):
        self.name = self.set_code = self.description = None
        self.source_type, self.status, self.numbering, self.invalid_lines = "INV", "A", "Y", "Reject"
        self.from_date = self.last_number = None
        self.grouping_rule, self.rule_pending = None, False
        self.filled = {}              # request key -> what the automation fills in (shown on the preview)


class Problems:
    def __init__(self):
        self.items = []

    def bad(self, key, text, fix=None, value=None, suggestions=None):
        self.items.append({"key": key, "row": None, "text": text, "fix": fix or "Change it in the sheet and upload it "
                           "again.", "field": key, "value": value, "suggestions": [str(s) for s in suggestions or []][:12]})


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def pick(v, table, pb, key, label, default, filled):
    """A fixed choice: the code, the default when empty (shown as filled in), None when wrong."""
    if blank(v):
        filled[key] = LABEL[default]
        return default
    code = table.get(str(v).strip().lower())
    if code is None:
        choices = sorted({LABEL[c] for c in table.values()})
        shown = "the drop-down's two choices" if key == "source_type" else ", ".join(choices)   # page's plain words
        pb.bad(key, f"{label} '{v}' isn't one of {shown}.", f"Pick one of {shown}.", v, choices)
    return code


def check(req):
    """(Source or None, problems) for one request."""
    pb, t = Problems(), Source()
    if not isinstance(req, dict):
        pb.bad("name", "This row could not be read.")
        return None, pb.items
    for k in sorted(set(req) - set(KEYS)):
        pb.bad(k, f"'{k}' is not a transaction source field.", "Remove it.", req[k])
    n = req.get("name")
    if blank(n):
        pb.bad("name", "Name is missing.", "Fill in the source's Name.")
    elif not isinstance(n, str):
        pb.bad("name", "Name must be text.", value=n)
    elif n != n.strip():
        pb.bad("name", f"Name '{n}' starts or ends with a space. Oracle keeps such a space, so it would be a "
               "different source; remove it.", "Remove the space at the start or end.", n, [n.strip()])
    elif n.upper().startswith(RESERVED):
        pb.bad("name", f"Name can't start with {RESERVED}: Oracle keeps those names for its own sources.",
               f"Use a name without {RESERVED} at the start.", n)
    else:
        t.name = n
    s = req.get("set_code")
    if blank(s):
        pb.bad("set_code", "Set Code is missing. Choose Oracle's reference data set for this source; it is never "
               "filled in for you.", "Pick the set from the drop-down, for example COMMON.")
    else:
        t.set_code = str(s).strip()
    d = req.get("description")
    if blank(d):
        pb.bad("description", "Item Description is missing. Oracle needs a description for a new transaction source.",
               "Write what the source is for.")
    else:
        t.description = str(d)
    t.source_type = pick(req.get("source_type"), TYPES, pb, "source_type", "Type", "INV", t.filled)
    if blank(req.get("from_date")):
        pb.bad("from_date", "From Date is missing. A transaction source needs an explicit start date; it is never "
               "filled in for you.", "Fill in the date the source starts, for example 2026-11-01.")
    else:
        try:
            t.from_date = date.fromisoformat(str(req["from_date"]).strip())
        except ValueError:
            pb.bad("from_date", f"From Date must be a date written as YYYY-MM-DD; it says '{req['from_date']}'.",
                   "Write it like 2026-11-01.", req["from_date"])
    t.status = pick(req.get("status"), STATUS, pb, "status", "Status", "A", t.filled)
    t.invalid_lines = pick(req.get("invalid_lines"), INVALID_LINES, pb, "invalid_lines", "Invalid Lines", "Reject",
                           t.filled)
    v = req.get("auto_numbering")
    if blank(v):
        t.numbering, t.filled["auto_numbering"] = "Y", "Yes"
    elif isinstance(v, bool) or str(v).strip().lower() in ("yes", "y", "true", "no", "n", "false"):
        t.numbering = "Y" if (v is True or str(v).strip().lower() in ("yes", "y", "true")) else "N"
    else:
        pb.bad("auto_numbering", f"Automatic Numbering must be Yes or No; it says '{v}'.", "Write Yes or No.", v,
               ["Yes", "No"])
        t.numbering = None
    ln = req.get("last_number")
    if t.numbering == "Y":
        if blank(ln):
            pb.bad("last_number", "Last Number is missing. With automatic numbering Oracle starts the numbering at "
                   "this number; it is never filled in for you.", "Fill in a whole number, 1 or more.", None, ["1"])
        else:
            try:
                f = float(str(ln).replace(",", ""))
                if isinstance(ln, bool) or not f.is_integer() or f < 1:
                    raise ValueError
                t.last_number = int(f)
            except ValueError:
                pb.bad("last_number", f"Last Number must be a whole number, 1 or more; it says '{ln}'.",
                       "Write a whole number, for example 1.", ln, ["1"])
    elif t.numbering == "N" and not blank(ln):
        pb.bad("last_number", "Last Number only applies with automatic numbering.",
               "Leave Last Number empty, or set Automatic Numbering to Yes.", ln)
    g = req.get("grouping_rule")
    if not blank(g):
        g = str(g)
        if t.source_type == "INV":
            pb.bad("grouping_rule", "A grouping rule only applies to an AutoInvoice source; this one is Manual.",
                   "Change Type to the AutoInvoice choice, or leave Grouping Rule empty.", g)
        elif g != g.strip():
            pb.bad("grouping_rule", f"Grouping Rule '{g}' starts or ends with a space.", "Remove the space.", g,
                   [g.strip()])
        else:
            t.grouping_rule, t.rule_pending = g, bool(req.get("grouping_rule_pending"))
    return (t if not pb.items else None), pb.items


def describe(t):
    """What Oracle will get, in plain words (the preview's summary)."""
    return (f"Oracle will get: " + ("an AutoInvoice source" if t.source_type == "FOREIGN" else "a Manual source")
            + f" in set {t.set_code}, {LABEL[t.status]}, from "
            f"{t.from_date.isoformat()}, "
            + (f"automatic numbering starting at {t.last_number}" if t.numbering == "Y" else "no automatic numbering")
            + f", invalid lines: {LABEL[t.invalid_lines]}"
            + (f", grouping rule {t.grouping_rule}" + (" (created first from this sheet)" if t.rule_pending else "")
               if t.grouping_rule else "")
            + ". Also set: no default transaction type, no credit source, no legal entity, no flexfields, AutoInvoice "
              "options left empty (not on the sheet).")
