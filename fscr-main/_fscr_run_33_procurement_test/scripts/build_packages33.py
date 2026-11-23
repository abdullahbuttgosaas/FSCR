"""Run 33: build FSM CSV packages holding ONLY new FSCRT_ rows. Headers + metadata XML are copied unchanged from the ETIA-TEST export
(export_before/<TASK>/unz). Usage: build_packages33.py <TASK_CODE> [...]   (edit the SPEC dict to change values between attempts)"""
import csv, zipfile, shutil, sys, json
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
BU = "FSCRT_Brindle Harbor Marine Supply F01"
def build(task, files, tag=""):
    src = RUN / "export_before" / task / "unz"; out = RUN / "payload" / (task + tag); out.mkdir(parents=True, exist_ok=True)
    for n in list(out.glob("*")):
        if n.is_file(): n.unlink()
    for name, rows in files.items():
        h = next(csv.reader(open(src / name, encoding="utf-8-sig", newline="")))
        for r in rows: assert set(r) <= set(h), (name, set(r) - set(h))
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(h)
            for r in rows: w.writerow([r.get(c, "") for c in h])
    shutil.copy(src / "ASM_SETUP_CSV_METADATA.xml", out / "ASM_SETUP_CSV_METADATA.xml")
    z = out / f"{task.lower()}_fscrt.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in ["ASM_SETUP_CSV_METADATA.xml", *files]: zf.write(out / n, n)
    print("wrote", z)
    return z
STY = "FSCRT_R33 Style"
SPEC = {
 "PO_MANAGE_DOCUMENT_STYLES": {
  "PO_DOC_STYLE_VALUE.csv": [dict(StyleName=STY, LineTypeAllowed="ALL", PriceBreaksFlag="Y", ProgressPaymentFlag="N", RetainageFlag="N", Status="ACTIVE",
        StyleDescription="FSCR Run 33 test document style", ConsignedItemsFlag="N", OutsideProcessingFlag="N", ConfiguredItemFlag="N", EnableCreditLineTypes="Y")],
  "PO_DOC_STYLE_HEADER.csv": [{"PO_DOC_STYLE_VALUE.StyleName": STY, "DocumentSubtype": s, "DisplayName": f"FSCRT_R33 {s.title()}", "EnabledFlag": "Y"} for s in ("BLANKET", "CONTRACT", "STANDARD")],
  "PO_DOC_STYLE_LINE.csv": [{"PO_DOC_STYLE_VALUE.StyleName": STY, "StyleAttributeName": "PURCHASE_BASES", "StyleAllowedValue": v, "EnabledFlag": "Y"} for v in ("GOODS", "SERVICES")],
  "PO_DOC_STYLE_HEADER_TRANSLATION.csv": [{"PO_DOC_STYLE_VALUE.StyleName": STY, "PO_DOC_STYLE_HEADER.DocumentSubtype": s, "DisplayName": f"FSCRT_R33 {s.title()}", "DocumentSubtype": s, "Language": "US", "SourceLang": "US"} for s in ("BLANKET", "CONTRACT", "STANDARD")]},
 "ORA_PO_MANAGE_PROCUREMENT_DOCUMENT_NUMBERING": {
  "ORA_PO_UNIQUE_IDENTIFIER_CONT_ALL.csv": [dict(ShortCode=BU, EnterpriseId="1", TableName="REQUISITION", DeterminantType="REQUISITIONING_BU", MinimumDigits="5", Prefix="FSCRT_R33|")]},
}
Q = "FSCRT_R33_Q1"; S = "FSCRT_R33_SEC1"
QV = json.load(open(RUN / "scripts/question_values.json")) if (RUN / "scripts/question_values.json").exists() else {}
SPEC["ORA_PO_COMPLIANCE_CHECKLIST_QUESTIONS"] = {
  "ORA_POQ_CHECKLIST_QUESTION.csv": [{**dict(QuestionName=Q, RevisionNumber="1", ActivationDate="2026/11/17", AllowRespCommentFlag="N", LatestRevisionFlag="Y",
        QuestionText="FSCRT_R33 test checklist question", ResponseRequiredFlag="N"), **QV}],
  "ORA_POQ_TRANS_CHECKLIST_QUESTION.csv": [{"ORA_POQ_CHECKLIST_QUESTION.QuestionName": Q, "ORA_POQ_CHECKLIST_QUESTION.RevisionNumber": QV.get("RevisionNumber", "1"), "Language": "US", "QuestionText": "FSCRT_R33 test checklist question", "SourceLang": "US"}]}
SV = json.load(open(RUN / "scripts/section_values.json")) if (RUN / "scripts/section_values.json").exists() else {}
SPEC["ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS"] = {
  "ORA_POQ_CHECKLIST_SECTION.csv": [{**dict(QualAreaName=S, RevisionNumber_QualArea="1", QualAreaDescription="FSCR Run 33 test section", LatestRevisionFlag="Y", ActivationDate="2026/11/17", SectionName=S), **SV}],
  "ORA_POQ_CHECKLIST_SECTION_QUESTIONS.csv": [],
  "ORA_POQ_TRANS_CHECKLIST_SECTION.csv": [{"ORA_POQ_CHECKLIST_SECTION.QualAreaName": S, "ORA_POQ_CHECKLIST_SECTION.RevisionNumber_QualArea": "1", "Language": "US", "SectionName": S, "SourceLang": "US"}]}
if __name__ == "__main__":
    for t in sys.argv[1:]: build(t, SPEC[t])
