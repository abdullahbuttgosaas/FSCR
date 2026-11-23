"""Transaction types (header only): every rule that needs no Oracle, for one request of the sheet (or the page's --run).
Plain words with the fix; all problems at once. The rules are the spec's sections 1-2 (FSCR manage-transaction-types:
ora_input_validation.md, ora_defaulting_rules.md, ora_reference_lookups.md, ora_design_enforcement.md; CLAUDE.md > Input
rules). FSCR: "Require explicit create values ... do not invent defaults", so nothing required is ever filled in here.

A request: {"name", "set_code", "description", "trx_class", "status", "from_date", "to_date", "open_receivable",
            "post_to_gl", "allow_freight", "tax_calculation", "natural_application", "allow_overapplication",
            "creation_sign", "transaction_status", "printing_option", "payment_term", "payment_term_set",
            "payment_term_pending"}.
"payment_term_pending" is set by the page when the payment term is a row of the same upload (registry depends_on).

A problem: {"key", "row": None, "text", "fix", "field", "value", "suggestions"}.
"""
from datetime import date

NAME_MAX, DESCRIPTION_MAX = 20, 80          # FSCR E2E fieldConstraints (SRC-E2E-MTT-FIELD-LENGTH-20260909)
# Oracle's class codes (FSCR valueContracts). v1 offers Invoice and Debit Memo only (spec section 1).
CLASSES = {"invoice": "INV", "inv": "INV", "debit memo": "DM", "dm": "DM"}
NOT_OFFERED = {"credit memo": "CM", "cm": "CM", "adjustment": "ADJ", "adj": "ADJ", "bills receivable": "BR",
               "br": "BR", "chargeback": "CB", "cb": "CB", "deposit": "DEP", "dep": "DEP", "guarantee": "GUAR",
               "guar": "GUAR"}
STATUS = {"active": "A", "a": "A", "inactive": "I", "i": "I"}
SIGN = {"positive sign": "P", "p": "P"}                 # the only verified CreationSign (FSCR)
TRX_STATUS = {"open": "OP", "op": "OP"}                 # the only verified DefaultStatus (FSCR)
PRINTING = {"print": "PRI", "pri": "PRI", "do not print": "NOT", "not": "NOT"}
LABEL = {"INV": "Invoice", "DM": "Debit Memo", "A": "Active", "I": "Inactive", "P": "Positive Sign", "OP": "Open",
         "PRI": "Print", "NOT": "Do Not Print", "Y": "Yes", "N": "No"}
# request key -> (Oracle column, sheet label); the seven required Yes/No flags
FLAGS = {"open_receivable": ("AccountingAffectFlag", "Open Receivable"), "post_to_gl": ("PostToGl", "Post to GL"),
         "allow_freight": ("AllowFreightFlag", "Allow Freight"),
         "tax_calculation": ("TaxCalculationFlag", "Tax Calculation"),
         "natural_application": ("NaturalApplicationOnlyFlag", "Natural Application Only"),
         "allow_overapplication": ("AllowOverapplicationFlag", "Allow Overapplication")}
KEYS = ("name", "set_code", "description", "trx_class", "status", "from_date", "to_date", *FLAGS, "creation_sign",
        "transaction_status", "printing_option", "payment_term", "payment_term_set", "payment_term_pending")


class TrxType:
    """One checked transaction type, values as Oracle's file wants them."""

    def __init__(self):
        self.name = self.set_code = self.description = self.trx_class = self.status = None
        self.from_date = self.to_date = None
        self.flags = {}               # Oracle column -> Y / N
        self.sign = self.trx_status = self.printing = None
        self.term = self.term_set = None
        self.term_pending = False


class Problems:
    def __init__(self):
        self.items = []

    def bad(self, key, text, fix=None, value=None, suggestions=None):
        self.items.append({"key": key, "row": None, "text": text, "fix": fix or "Change it in the sheet and upload it "
                           "again.", "field": key, "value": value, "suggestions": [str(s) for s in suggestions or []][:12]})


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def choice(v, table, pb, key, label, shown, never=None):
    """A required fixed choice: its code, or None with a problem (missing is asked, never defaulted)."""
    if blank(v):
        pb.bad(key, f"{label} is missing. It is never filled in for you.", f"Pick {shown}.", None,
               sorted({LABEL[c] for c in table.values()}))
        return None
    code = table.get(" ".join(str(v).split()).lower())
    if code is None:
        if never and " ".join(str(v).split()).lower() in never:
            pb.bad(key, f"{label} '{v}' isn't offered yet: {never.get('_why')}", f"Pick {shown}.", v,
                   sorted({LABEL[c] for c in table.values()}))
        else:
            pb.bad(key, f"{label} '{v}' isn't one of {shown}.", f"Pick {shown}.", v,
                   sorted({LABEL[c] for c in table.values()}))
    return code


def a_date(v, pb, key, label, required):
    if blank(v):
        if required:
            pb.bad(key, f"{label} is missing. It is never filled in for you.",
                   f"Fill in the date, for example 2026-11-01.")
        return None
    try:
        return date.fromisoformat(str(v).strip().split(" ")[0].split("T")[0])
    except ValueError:
        pb.bad(key, f"{label} must be a date written as YYYY-MM-DD; it says '{v}'.", "Write it like 2026-11-01.", v)
        return None


def check(req):
    """(TrxType or None, problems) for one request."""
    pb, t = Problems(), TrxType()
    if not isinstance(req, dict):
        pb.bad("name", "This row could not be read.")
        return None, pb.items
    for k in sorted(set(req) - set(KEYS)):
        pb.bad(k, f"'{k}' is not a transaction type field.", "Remove it.", req[k])
    n = req.get("name")
    if blank(n):
        pb.bad("name", "Name is missing.", "Fill in the transaction type's Name.")
    elif not isinstance(n, str):
        pb.bad("name", "Name must be text.", value=n)
    elif n != n.strip():
        pb.bad("name", f"Name '{n}' starts or ends with a space. Oracle keeps such a space, so it would be a "
               "different transaction type; remove it.", "Remove the space at the start or end.", n, [n.strip()])
    elif len(n) > NAME_MAX:
        pb.bad("name", f"Name '{n}' has {len(n)} characters; Oracle takes at most {NAME_MAX}. It is never shortened "
               "for you.", f"Write a name of at most {NAME_MAX} characters.", n)
    else:
        t.name = n
    s = req.get("set_code")
    if blank(s):
        pb.bad("set_code", "Set Code is missing. Choose Oracle's reference data set for this transaction type; it is "
               "never filled in for you.", "Pick the set from the drop-down, for example COMMON.")
    else:
        t.set_code = str(s).strip()
    d = req.get("description")
    if not blank(d):
        d = str(d)
        if len(d) > DESCRIPTION_MAX:
            pb.bad("description", f"Item Description has {len(d)} characters; Oracle takes at most {DESCRIPTION_MAX}. "
                   "It is never shortened for you.", f"Write at most {DESCRIPTION_MAX} characters.", d)
        else:
            t.description = d
    t.trx_class = choice(req.get("trx_class"), CLASSES, pb, "trx_class", "Class", "Invoice or Debit Memo",
                         dict(NOT_OFFERED, _why="this version offers Invoice and Debit Memo only (a credit memo needs a "
                              "negative sign, and the other classes need setup that isn't on the sheet)."))
    t.status = choice(req.get("status"), STATUS, pb, "status", "Status", "Active or Inactive")
    t.from_date = a_date(req.get("from_date"), pb, "from_date", "From Date", True)
    t.to_date = a_date(req.get("to_date"), pb, "to_date", "To Date", False)
    if t.from_date and t.to_date and t.to_date < t.from_date:
        pb.bad("to_date", f"To Date {t.to_date} is before From Date {t.from_date}.",
               "Use a To Date on or after the From Date, or leave it empty.", str(req.get("to_date")))
    for key, (col, label) in FLAGS.items():
        v = req.get(key)
        if blank(v):
            pb.bad(key, f"{label} is missing. It is never filled in for you.", "Write Yes or No.", None, ["Yes", "No"])
        elif isinstance(v, bool) or str(v).strip().lower() in ("yes", "y", "true", "no", "n", "false"):
            t.flags[col] = "Y" if (v is True or str(v).strip().lower() in ("yes", "y", "true")) else "N"
        else:
            pb.bad(key, f"{label} must be Yes or No; it says '{v}'.", "Write Yes or No.", v, ["Yes", "No"])
    if t.flags.get("NaturalApplicationOnlyFlag") == "Y" and t.flags.get("AllowOverapplicationFlag") == "Y":
        pb.bad("allow_overapplication", "Natural Application Only and Allow Overapplication can't both be Yes.",
               "Set one of the two to No.", "Yes", ["No"])
    t.sign = choice(req.get("creation_sign"), SIGN, pb, "creation_sign", "Creation Sign", "Positive Sign")
    t.trx_status = choice(req.get("transaction_status"), TRX_STATUS, pb, "transaction_status", "Transaction Status",
                          "Open")
    t.printing = choice(req.get("printing_option"), PRINTING, pb, "printing_option", "Printing Option",
                        "Print or Do Not Print")
    term, tset = req.get("payment_term"), req.get("payment_term_set")
    if not blank(term):
        term = str(term)
        if term != term.strip():
            pb.bad("payment_term", f"Payment Term '{term}' starts or ends with a space.", "Remove the space.", term,
                   [term.strip()])
        elif blank(tset):
            pb.bad("payment_term_set", f"Payment Term Set is missing for payment term {term}. Oracle needs the term's "
                   "reference data set too; it is never filled in for you.",
                   "Fill in the set of that payment term, for example COMMON.")
        else:
            t.term, t.term_set = term, str(tset).strip()
            t.term_pending = bool(req.get("payment_term_pending"))
    elif not blank(tset):
        pb.bad("payment_term_set", "Payment Term Set only applies with a Payment Term.",
               "Fill in the Payment Term, or leave Payment Term Set empty.", tset)
    return (t if not pb.items else None), pb.items


def describe(t):
    """What Oracle will get, in plain words (the preview's summary)."""
    yn = {c: LABEL[v] for c, v in t.flags.items()}
    return (f"Oracle will get: {'an' if t.trx_class == 'INV' else 'a'} {LABEL[t.trx_class]} type in set {t.set_code}, "
            f"{LABEL[t.status]}, from {t.from_date.isoformat()}" + (f" to {t.to_date.isoformat()}" if t.to_date else "")
            + f"; open receivable {yn['AccountingAffectFlag']}, post to GL {yn['PostToGl']}, freight "
            f"{yn['AllowFreightFlag']}, tax calculation {yn['TaxCalculationFlag']}, natural application only "
            f"{yn['NaturalApplicationOnlyFlag']}, overapplication {yn['AllowOverapplicationFlag']}; "
            f"{LABEL[t.sign]}, transaction status {LABEL[t.trx_status]}, {LABEL[t.printing]}"
            + (f"; payment term {t.term} (set {t.term_set})" + (" created first from this sheet" if t.term_pending else "")
               if t.term else "; no payment term")
            + ". Not set: accounts (not offered yet), credit memo and subsequent types, rule set, legal entity, "
              "flexfields.")
