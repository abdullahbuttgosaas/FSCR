"""Receivables payment terms: Oracle's file layout read from the pod at run time, the import file built from it,
Oracle's log read, and the field-by-field read-back. No Oracle calls here (run.py makes them); everything is a
plain function of the files Oracle gave, so it is tested offline (page/matrix/test_matrix.py).

The one thing fixed in code is the four entity names (ENTITIES). The entity order, the member names, every CSV
header line, the field types and the metadata come from the pod's own template on every run; the import file is
the template's members in the template's own order, the metadata copied byte for byte (CLAUDE.md > File layout).
"""
import csv
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, InvalidOperation

TASK = "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS"
METADATA = "ASM_SETUP_CSV_METADATA.xml"
ENTITIES = {"header": "AR_PAYMENT_TERM", "line": "AR_PAYMENT_TERM_LINE",
            "translation": "AR_PAYMENT_TERM_TRANSLATION", "discount": "AR_PAYMENT_TERM_DISCOUNT"}
AUDIT = ("LastUpdateDate", "LastUpdatedBy", "CreationDate", "CreatedBy", "LastUpdateLogin")
LAYOUT_TEXT = ("Oracle's file layout for Receivables payment terms isn't what this module knows. "
               "Nothing was created.")


class LayoutError(Exception):
    """The pod's files are not the layout this module knows: a plain stop, nothing is built (never a guess)."""

    def __init__(self, why):
        super().__init__(f"{LAYOUT_TEXT} ({why})")
        self.why = why


# ---------------------------------------------------------------- the layout

class Layout:
    """What the pod's template says: members in zip order, the metadata bytes, and per entity its member, header
    line (as written), header columns, field types, node path and position in the metadata."""

    def __init__(self):
        self.members, self.raw, self.metadata, self.entities = [], {}, b"", {}
        self.task = self.status = self.env = self.release = self.process_type = None
        self.newline, self.quote_all = "\n", True

    def entity(self, role):
        return self.entities[ENTITIES[role]]

    def order(self):
        """The entity names in the order the pod's metadata lists them."""
        return sorted(self.entities, key=lambda n: self.entities[n]["position"])


def _text(row, tag):
    el = row.find(tag)
    return (el.text or "").strip() if el is not None else ""


def read_layout(zip_bytes, need_completed=True):
    """The Layout of a template (or data) export. Raises LayoutError when the task, status, an entity, a member or a
    header doesn't fit; extra headers are allowed only as parent links (<ENTITY>.<Field>)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise LayoutError("the file Oracle gave is not a zip")
    lay = Layout()
    lay.members = z.namelist()
    lay.raw = {n: z.read(n) for n in lay.members}
    if METADATA not in lay.raw:
        raise LayoutError(f"no {METADATA}")
    lay.metadata = lay.raw[METADATA]
    try:
        root = ET.fromstring(lay.metadata)
    except ET.ParseError as e:
        raise LayoutError(f"{METADATA} can't be read: {e}")
    proc = root.find("MigrationProcessCSVMetadataVORow")
    if proc is None:
        raise LayoutError(f"{METADATA} has no process row")
    lay.task, lay.status = _text(proc, "ObjectShortName"), _text(proc, "ProcessStatus")
    lay.env, lay.release, lay.process_type = _text(proc, "ProcessEnv"), _text(proc, "ProcessRelease"), \
        _text(proc, "ProcessType")
    if lay.task != TASK:
        raise LayoutError(f"the file is for task {lay.task or '(none)'}, not {TASK}")
    if need_completed and lay.status != "COMPLETED":
        raise LayoutError(f"Oracle's process ended {lay.status or '(no status)'}")
    rows = proc.findall("MigrationProcessBusinessObjectCSVMetadata1/MigrationProcessBusinessObjectCSVMetadataVORow")
    for pos, row in enumerate(rows):
        name = _text(row, "BusinessObjectShortName")
        attrs = [a for a in _text(row, "XmlAttributeList").split(",") if a]
        types = [t for t in _text(row, "XmlAttributeTypeList").split(",") if t]
        if len(attrs) != len(types):
            raise LayoutError(f"{name}: {len(attrs)} fields but {len(types)} field types")
        lay.entities[name] = {"name": name, "position": pos, "attrs": attrs, "types": dict(zip(attrs, types)),
                              "node_path": _text(row, "XmlNodePath"), "node_sequence": _text(row, "NodeSequence")}
    missing = [e for e in ENTITIES.values() if e not in lay.entities]
    if missing:
        raise LayoutError(f"the file has no {', '.join(missing)}")
    for name, ent in lay.entities.items():
        member = f"{name}.csv"
        if member not in lay.raw:
            raise LayoutError(f"no {member} in the file")
        data = lay.raw[member]
        text = data.decode("utf-8-sig")
        first = text.split("\n", 1)[0]
        if first.endswith("\r"):
            lay.newline = "\r\n"
        header = next(csv.reader(io.StringIO(first)), [])
        if not header:
            raise LayoutError(f"{member} has no header line")
        extra = [h for h in header if h not in ent["attrs"]]
        bad = [h for h in extra if not re.fullmatch(r"[A-Z_]+\.\w+", h)]
        if bad:
            raise LayoutError(f"{member} has columns Oracle's metadata doesn't name: {', '.join(bad)}")
        absent = [a for a in ent["attrs"] if a not in header]
        if absent:
            raise LayoutError(f"{member} lacks the columns {', '.join(absent)}")
        lay.quote_all = first.startswith('"')
        end = data.find(b"\n")
        ent.update(member=member, header=header, head_bytes=data[:end + 1] if end >= 0 else data + b"\n")
    return lay


def same_layout(a, b):
    """Differences between two layouts (template versus data export): entity order, headers, types."""
    out = []
    if a.order() != b.order():
        out.append(f"entity order {a.order()} versus {b.order()}")
    for n in ENTITIES.values():
        if a.entities[n]["header"] != b.entities[n]["header"]:
            out.append(f"{n} columns differ")
        if a.entities[n]["types"] != b.entities[n]["types"]:
            out.append(f"{n} field types differ")
    return out


# ---------------------------------------------------------------- rows of one term

def iso(d):
    """A date as Oracle's import takes it: YYYY-MM-DD (an export's 2026/10/28 is turned round, never sent as is)."""
    if d in (None, ""):
        return ""
    if isinstance(d, date):
        return d.isoformat()
    s = str(d).strip().split(" ")[0].replace("/", "-")
    return date.fromisoformat(s).isoformat()


def term_rows(term, language):
    """{entity: [row dicts]} for one checked term (run.py's Term), keyed by the pod's column names."""
    k = {"AR_PAYMENT_TERM.Name": term.name, "AR_PAYMENT_TERM.SetCode": term.set_code}
    head = {"Name": term.name, "SetCode": term.set_code, "Description": term.description,
            "StartDateActive": iso(term.from_date), "EndDateActive": iso(term.to_date),
            "BaseAmount": num(term.base_amount), "PrintingLeadDays": num(term.print_lead_days),
            "FirstInstallmentCode": term.first_installment, "CalcDiscountOnLinesFlag": term.discount_basis,
            "DiscountBasisDateType": term.date_basis, "DueCutoffDay": num(term.cutoff_day),
            "CreditCheckFlag": term.credit_check, "PrepaymentFlag": term.prepayment,
            "InUse": "N", "PartialDiscountFlag": "N", "CycleName": ""}
    lines, discounts = [], []
    for ln in term.lines:
        lines.append(dict(k, SequenceNum=str(ln["seq"]), RelativeAmount=num(ln["amount"]),
                          DueDays=num(ln.get("days")), DueDate=iso(ln.get("date")),
                          DueDayOfMonth=num(ln.get("dom")), DueMonthsForward=num(ln.get("months")),
                          SetCode=term.set_code))
        for d in ln["discounts"]:
            discounts.append(dict(k, **{"AR_PAYMENT_TERM_LINE.SequenceNum": str(ln["seq"])},
                                  SequenceNum=str(ln["seq"]), DiscountPercent=num(d["percent"]),
                                  DiscountDays=num(d.get("days")), DiscountDate=iso(d.get("date")),
                                  DiscountDayOfMonth=num(d.get("dom")), DiscountMonthsForward=num(d.get("months")),
                                  SetCode=term.set_code))
    tr = dict(k, Description=term.description, Name=term.name, Language=language, SourceLang=language)
    return {ENTITIES["header"]: [head], ENTITIES["line"]: lines, ENTITIES["translation"]: [tr],
            ENTITIES["discount"]: discounts}


def num(v):
    """A number as text without a trailing .0 ("" when empty)."""
    if v in (None, ""):
        return ""
    d = Decimal(str(v))
    return str(d.quantize(Decimal(1))) if d == d.to_integral_value() else format(d.normalize(), "f")


def build_zip(lay, rows):
    """The import file: every member of the template in the template's own order; the metadata byte for byte;
    each entity's CSV = its header line as Oracle wrote it plus our rows (columns by the header, a column we don't
    fill empty, audit columns always empty, date columns ISO). rows: {entity: [dict]}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for member in lay.members:
            ent = next((e for e in lay.entities.values() if e.get("member") == member), None)
            if ent is None:                      # the metadata (and anything else the pod adds): unchanged
                zo.writestr(member, lay.raw[member])
                continue
            out = io.StringIO()
            w = csv.writer(out, quoting=csv.QUOTE_ALL if lay.quote_all else csv.QUOTE_MINIMAL,
                           lineterminator=lay.newline)
            for r in rows.get(ent["name"], []):
                unknown = [c for c, v in r.items() if v not in (None, "") and c not in ent["header"]]
                if unknown:
                    raise LayoutError(f"{ent['member']} has no column {', '.join(unknown)}")
                vals = []
                for c in ent["header"]:
                    v = "" if c in AUDIT else str(r.get(c) if r.get(c) is not None else "")
                    if v and ent["types"].get(c) == "date":
                        v = iso(v)
                    vals.append(v)
                w.writerow(vals)
            zo.writestr(member, ent["head_bytes"] + out.getvalue().encode("utf-8"))
    return buf.getvalue()


# ---------------------------------------------------------------- an export's rows

def read_rows(zip_bytes):
    """{entity: [row dicts]} of a data export (its own layout)."""
    lay = read_layout(zip_bytes)
    out = {}
    for name, ent in lay.entities.items():
        rows = list(csv.reader(io.StringIO(lay.raw[ent["member"]].decode("utf-8-sig"))))
        out[name] = [dict(zip(rows[0], r)) for r in rows[1:] if any(r)]
    return lay, out


def key_of(row):
    """(Name, SetCode) of a header row or a child row."""
    return (row.get("Name") if "AR_PAYMENT_TERM.Name" not in row else row["AR_PAYMENT_TERM.Name"],
            row.get("SetCode") if "AR_PAYMENT_TERM.SetCode" not in row else row["AR_PAYMENT_TERM.SetCode"])


def terms_in(rows):
    """{(Name, SetCode): header row} of an export."""
    return {key_of(r): r for r in rows.get(ENTITIES["header"], [])}


def languages(rows):
    """The base languages Oracle's terms use (translation rows whose Language is their SourceLang)."""
    return sorted({r.get("Language") for r in rows.get(ENTITIES["translation"], [])
                   if r.get("Language") and r.get("Language") == r.get("SourceLang")})


# ---------------------------------------------------------------- read-back

def same(a, b, kind):
    """Two values equal as Oracle means them: dates as dates (2026/10/28 = 2026-10-28), numbers as numbers."""
    a, b = (a or "").strip(), (b or "").strip()
    if a == b:
        return True
    if not a or not b:
        return False
    if kind in ("date", "dateTime"):
        try:
            return iso(a) == iso(b)
        except ValueError:
            return False
    if kind in ("decimal", "long", "integer", "number"):
        try:
            return Decimal(a) == Decimal(b)
        except InvalidOperation:
            return False
    return False


def compare_row(sent, got, types, where):
    out = []
    for c, v in sent.items():
        if c in AUDIT:
            continue
        if not same(v, got.get(c, ""), types.get(c, "string")):
            out.append(f"{where} {c}: Oracle has '{got.get(c, '')}', sent '{v}'")
    return out


def reconcile(lay, sent, before, after):
    """Every sent term against a fresh export. sent: {(Name, SetCode): {entity: [rows]}}; before / after: an
    export's rows. Returns ({key: {"saved", "diffs", "notes"}}, [names of other terms that changed])."""
    H, L, T, D = (ENTITIES[r] for r in ("header", "line", "translation", "discount"))
    types = {n: e["types"] for n, e in lay.entities.items()}
    res = {}
    for key, rows in sent.items():
        heads = [r for r in after.get(H, []) if key_of(r) == key]
        if not heads:
            res[key] = {"saved": False, "diffs": [], "notes": []}
            continue
        diffs, notes = [], []
        if len(heads) > 1:
            diffs.append(f"Oracle shows {len(heads)} terms named {key[0]} in set {key[1]}")
        diffs += compare_row(rows[H][0], heads[0], types[H], "the term's")
        got_lines = {r.get("SequenceNum"): r for r in after.get(L, []) if key_of(r) == key}
        for ln in rows[L]:
            g = got_lines.pop(ln["SequenceNum"], None)
            if g is None:
                diffs.append(f"installment {ln['SequenceNum']} isn't in Oracle")
            else:
                diffs += compare_row(ln, g, types[L], f"installment {ln['SequenceNum']}")
        diffs += [f"Oracle has an installment {s} that wasn't sent" for s in got_lines]
        got_tr = {r.get("Language"): r for r in after.get(T, []) if key_of(r) == key}
        for tr in rows[T]:
            g = got_tr.pop(tr["Language"], None)
            if g is None:
                diffs.append(f"the name in language {tr['Language']} isn't in Oracle")
            else:
                diffs += compare_row(tr, g, types[T], f"the name in language {tr['Language']}")
        notes += [f"Oracle added the name in language {lang} itself" for lang in got_tr]
        dkey = lambda r: (r.get("AR_PAYMENT_TERM_LINE.SequenceNum"), num(r.get("DiscountPercent") or "0"))
        got_d = {dkey(r): r for r in after.get(D, []) if key_of(r) == key}
        for d in rows[D]:
            g = got_d.pop(dkey(d), None)
            if g is None:
                diffs.append(f"the {d['DiscountPercent']}% discount on installment {d['SequenceNum']} isn't in Oracle")
            else:
                diffs += compare_row(d, g, types[D], f"the {d['DiscountPercent']}% discount")
        diffs += [f"Oracle has a {k[1]}% discount on installment {k[0]} that wasn't sent" for k in got_d]
        res[key] = {"saved": True, "diffs": diffs, "notes": notes}
    changed = []
    for name in (H, L, T, D):
        def rest(rows):
            return sorted(tuple(sorted(r.items())) for r in rows.get(name, []) if key_of(r) not in sent)
        if rest(before) != rest(after):
            b = {key_of(r) for r in before.get(name, [])} | {key_of(r) for r in after.get(name, [])}
            for k in sorted(x for x in b if x not in sent):
                if sorted(tuple(sorted(r.items())) for r in before.get(name, []) if key_of(r) == k) != \
                        sorted(tuple(sorted(r.items())) for r in after.get(name, []) if key_of(r) == k):
                    changed.append(f"{k[0]} ({k[1]})")
    return res, sorted(set(changed))


# ---------------------------------------------------------------- Oracle's log

# Oracle's attribute names -> (request key, sheet label, child row or not)
ATTRS = {"Name": ("name", "Name", False), "SetCode": ("set_code", "Set Code", False),
         "Description": ("description", "Item Description", False),
         "StartDateActive": ("from_date", "From Date", False), "EndDateActive": ("to_date", "To Date", False),
         "BaseAmount": ("base_amount", "Base Amount", False),
         "PrintingLeadDays": ("print_lead_days", "Print Lead Days", False),
         "FirstInstallmentCode": ("tax_freight", "Tax and Freight", False),
         "CalcDiscountOnLinesFlag": ("discount_basis", "Discount Basis", False),
         "DiscountBasisDateType": ("discount_date_basis", "Discount Date Basis", False),
         "DueCutoffDay": ("cutoff_day", "Cutoff Day", False),
         "RelativeAmount": ("relative_amount", "Relative Amount", True), "DueDays": ("days", "Days", True),
         "DueDate": ("fixed_date", "Fixed Date", True), "DueDayOfMonth": ("day_of_month", "Day of Month", True),
         "DueMonthsForward": ("months_ahead", "Months Ahead", True),
         "DiscountPercent": ("discount_percent", "First Discount (%)", True),
         "DiscountDays": ("discount_days", "First Discount Days", True)}
# Oracle's Receivables messages (FSCR ora_error_handling.md, CodeSearch 2026-08-12) -> (request key, plain reason)
MESSAGES = {
    "AR_SU_UNIQUE_PAY_TERMS": ("name", "Oracle already has a payment term with this name in this set"),
    "AR_SU_INVALID_PRINT_LEAD_DAYS": ("print_lead_days", "Print Lead Days isn't valid: a term with 2 or more "
                                                         "installments needs a whole number above 0"),
    "AR_SU_TOT_RELAMOUNT_EQ_BASE_AM": ("base_amount", "the installments don't add up to the Base Amount"),
    "AR_SU_TERM_ENTER_LINE": (None, "Oracle needs at least one installment"),
    "AR_SU_COMPLETE_DISCOUNT_INFO": (None, "a discount is incomplete"),
    "AR_SU_BASE_AMT_POSITIVE": ("base_amount", "Base Amount must be above 0"),
    "AR_API_INVALID_LOOKUP": (None, "a chosen value isn't one of Oracle's"),
    "AR_SU_DISCOUNT_PERCENT_RANGE": ("discount_percent", "a discount must be between 0 and 100 percent"),
    "FND_CMN_REC_COMB_VALS_EXST": (None, "the same discount is given twice on one installment"),
    "AR_SU_TERM_FULLY_ALLOCATED": (None, "the installments already add up to the whole amount"),
    "FND_CMN_TO_ERLY_EQ_FRM_DATE": ("to_date", "To Date must be after the From Date"),
    "AR_CONS_BILL_CLEAR_INSTALL": (None, "a billing-cycle term can't have several installments"),
}


def unpack(data):
    if data[:2] == b"PK":
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            return [z.read(n).decode("utf-8", "replace") for n in z.namelist()]
        except zipfile.BadZipFile:
            return []
    return [data.decode("utf-8", "replace")]


def log_failures(texts, names):
    """The failed rows in Oracle's process log: [{"term": a sent name the block quotes or None, "reasons", "field",
    "child", "raw"}]. How the Receivables log names a failed row is not proven yet, so a block is tied to a term only
    when it quotes that term's exact name; the read-back decides which terms were saved (CLAUDE.md > Gotchas)."""
    out = []
    for text in texts:
        flat = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", " ").replace("\\/", "/")
        for blk in flat.split("Row Identifier: ")[1:]:
            head, _, body = blk.partition("Message Text:")
            if "Status: Error" not in head:
                continue
            raw = " ".join(body.split("Total Objects", 1)[0].split())
            reasons, field, child = [], None, False
            for code, (key, plain) in MESSAGES.items():
                if code in raw:
                    reasons.append(f"{plain} ({code})")
                    field = field or key
                    child = child or key in ("discount_percent",)
            for attr in re.findall(r"LOV_(\w+) with given set of values leads to no matching row", raw):
                key, label, kid = ATTRS.get(attr, (None, attr, False))
                field, child = field or key, child or kid
                reasons.append(f"Oracle has no matching value for {label}")
            for attr in re.findall(r"JBO-27040: Value .*? for field (\w+) exceeds the maximum length allowed", raw):
                key, label, kid = ATTRS.get(attr, (None, attr, False))
                field, child = field or key, child or kid
                reasons.append(f"{label} is longer than Oracle allows")
            for attr in re.findall(r"JBO-27014: Attribute (\w+) in \w+ is required", raw):
                if not reasons:
                    key, label, kid = ATTRS.get(attr, (None, attr, False))
                    field, child = field or key, child or kid
                    reasons.append(f"Oracle says {label} is required")
            if re.search(r"JBO-250(09|27)", raw) and not reasons:
                reasons.append("Oracle couldn't read a date (JBO-25009 / JBO-25027)")
            for code, msg in re.findall(r"(JBO-\d+|FND-\d+|AR-\d+): (.*?)(?=JBO-\d+|FND-\d+|AR-\d+|$)", raw):
                if code in ("JBO-25026", "JBO-25072", "JBO-27024", "JBO-27014", "JBO-27040", "JBO-25009", "JBO-25027"):
                    continue
                reasons.append(f"{msg.strip(' .')} ({code})")
            if not reasons:
                reasons = [raw[:300] or "Oracle gave no reason"]
            term = next((n for n in sorted(names, key=len, reverse=True) if n and n in head + raw), None)
            out.append({"term": term, "reasons": list(dict.fromkeys(reasons)), "field": field, "child": child,
                        "raw": raw[:1500]})
    return out
