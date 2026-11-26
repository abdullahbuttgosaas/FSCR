"""Add ONE disabled test approval rule to a Procurement approval task by REST (GoSaaS gap fill).

Reads every id live (task, participant, condition attribute), checks the rule name is
not used on that participant, POSTs once, then reads the participant's rules again and
proves: exactly 1 rule added (yours), 0 removed, 0 changed.

The rule is safe by design: EnabledFlag false, one condition "<amount attribute> greater
than <threshold>" (default 999999999999), one action Automatic / Rejected, priority LOW.
It is a PENDING rule change: it is never deployed by this script (no deployRulesToBPM,
no discardPendingRuleChanges).

Runs FSCR's REST client through rest_call.py (Oracle's real error text, no server
address). Prints no token, server address or user name.

Usage:
  python -I approval_rule.py --fscr <FSCR> --rest-call <rest_call.py> --run <RUN>
      --task "Requisition Approvals" --participant "Header Hierarchy"
      --attribute-key requisitionTotal --dimension-key ReqHeaderDimension
      --rule GAPFILL_XX_RQ1 --prefix GAPFILL_XX_ [--threshold 999999999999]
      [--dry-run | --readback-only]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

API = "/fscmRestApi/resources/11.13.18.05"


def rest(a, name, endpoint, *extra):
    out = Path(a.run) / f"{name}.json"
    cmd = [sys.executable, "-B", a.rest_call, a.fscr, endpoint, *extra,
           "--no-open-browser", "--output", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (Path(a.run) / f"{name}.log").write_text(p.stdout + p.stderr, encoding="utf-8")
    if p.returncode != 0:
        msg = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith("HTTP") or "error" in l.lower()]
        raise SystemExit(f"STOP: REST call '{name}' failed: {' | '.join(msg)[-600:] or 'see ' + name + '.log'}")
    return json.loads(out.read_text(encoding="utf-8"))


def get_items(a, name, endpoint, q):
    d = rest(a, name, endpoint, "--query", f"q={q}", "--query", "onlyData=true", "--query", "limit=500")
    if d.get("hasMore"):
        raise SystemExit(f"STOP: more than 500 rows in {name}; narrow the filter")
    return d.get("items", [])


def rules_of(a, name, pid):
    return get_items(a, name, f"{API}/approvalRules", f"ParticipantId={pid}")


def main() -> int:
    ap = argparse.ArgumentParser()
    for k in ("--fscr", "--rest-call", "--run", "--task", "--participant", "--attribute-key",
              "--dimension-key", "--rule", "--prefix"):
        ap.add_argument(k, required=True)
    ap.add_argument("--threshold", type=float, default=999999999999)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--readback-only", action="store_true")
    a = ap.parse_args()
    Path(a.run).mkdir(parents=True, exist_ok=True)

    if not a.rule.startswith(a.prefix) or len(a.rule) > 80:
        raise SystemExit("STOP: the rule name must start with the prefix")

    tasks = [x for x in rest(a, "task", f"{API}/approvalTasks", "--query", "onlyData=true",
                             "--query", "limit=200")["items"] if x["Task"] == a.task]
    if len(tasks) != 1:
        raise SystemExit(f"STOP: approval task '{a.task}' found {len(tasks)} times (names: approvalTasks GET)")
    t = tasks[0]
    tid = t["TaskId"]
    print(f"task: {t['Task']} (TaskKey {t['TaskKey']}), IsRulesUpgradedFlag={t['IsRulesUpgradedFlag']}, "
          f"HasPendingRuleChangesFlag={t['HasPendingRuleChangesFlag']}")

    parts = rest(a, "participants", f"{API}/approvalTasks/{tid}/child/participants",
                 "--query", "onlyData=true", "--query", "limit=200")["items"]
    pm = [p for p in parts if p["Participant"] == a.participant]
    if len(pm) != 1:
        raise SystemExit(f"STOP: participant '{a.participant}' found {len(pm)} times; names: "
                         + "; ".join(f"{p['Participant']} [{p['Stage']}]" for p in parts))
    pid = pm[0]["ParticipantId"]
    print(f"participant: {a.participant} [{pm[0]['Stage']}]")

    attrs = [x for x in get_items(a, "attribute", f"{API}/approvalAttributesLOV",
                                  f"TaskId={tid};DisplayDataTypeCode='NUMBER'")
             if x["AttributeKey"] == a.attribute_key]
    am = [x for x in attrs if x["DimensionKey"] == a.dimension_key]
    if len(am) != 1:
        raise SystemExit(f"STOP: attribute {a.attribute_key}/{a.dimension_key} found {len(am)} times; "
                         f"dimensions with that key: {[x['DimensionKey'] for x in attrs]}")
    at = am[0]
    if at["DisplayDataTypeCode"] != "NUMBER" or at["AttributeTypeCode"] != "RULE_ONLY":
        raise SystemExit(f"STOP: attribute must be NUMBER / RULE_ONLY, is {at['DisplayDataTypeCode']} / {at['AttributeTypeCode']}")
    print(f"condition attribute: {at['Attribute']} ({a.attribute_key}, {a.dimension_key})")

    before = rules_of(a, "rules_before" if not a.readback_only else "rules_now", pid)
    names = [r["Rule"] for r in before]
    print(f"rules on this participant now: {len(before)}")

    if a.readback_only:
        mine = [r for r in before if r["Rule"] == a.rule]
        print(f"READBACK: {a.rule} found {len(mine)} time(s)"
              + (f", EnabledFlag={mine[0]['EnabledFlag']}" if mine else ""))
        return 0 if len(mine) == 1 else 1

    if a.rule in names:
        raise SystemExit(f"STOP: rule {a.rule} already exists on this participant; never create it twice")

    body = {
        "TaskId": tid, "ParticipantId": pid, "Rule": a.rule,
        "Description": "Gap-fill test rule. Disabled. Never enable or deploy.",
        "EnabledFlag": False, "RuleAlwaysAppliesFlag": False, "PriorityCode": "LOW",
        "conditions": [{"ConditionNumber": 1, "ConditionAttributeId": at["AttributeId"],
                        "OperatorCode": "MORE_THAN", "ComparisonTypeCode": "VALUE",
                        "ComparisonValueNumber": a.threshold}],
        "actions": [{"ActionTypeCode": "AUTOMATIC", "AutomaticOutcomeCode": "REJECTED"}],
    }
    bf = Path(a.run) / "rule_body.json"
    bf.write_text(json.dumps(body, indent=1), encoding="utf-8")
    print(f"body written: {bf.name} (disabled, condition > {a.threshold:.0f}, action Automatic/Rejected)")
    if a.dry_run:
        print("DRY RUN: nothing sent")
        return 0

    made = rest(a, "post", f"{API}/approvalRules", "--method", "POST", "--body-file", str(bf.resolve()))
    print(f"POST OK: RuleId {made.get('RuleId')}, Rule {made.get('Rule')}, EnabledFlag {made.get('EnabledFlag')}")

    after = rest(a, "rules_after", f"{API}/approvalRules", "--query", f"q=ParticipantId={pid}",
                 "--query", "onlyData=true", "--query", "limit=500", "--query", "expand=conditions,actions")["items"]
    key = lambda r: (r["Rule"], r["EnabledFlag"], r["LastUpdateDate"], r["PriorityCode"])
    b = {r["RuleId"]: key(r) for r in before}
    c = {r["RuleId"]: key(r) for r in after}
    added = [c[k][0] for k in c if k not in b]
    removed = [b[k][0] for k in b if k not in c]
    changed = [b[k][0] for k in b if k in c and b[k] != c[k]]
    mine = [r for r in after if r["Rule"] == a.rule]
    for r in mine:
        for x in r.get("conditions", []):
            print(f"  condition: {x.get('ConditionText')}")
        for x in r.get("actions", []):
            print(f"  action: {x.get('ActionTypeCode')} / {x.get('AutomaticOutcomeCode')}")
    t2 = rest(a, "task_after", f"{API}/approvalTasks/{tid}", "--query", "onlyData=true")
    print(f"rules before {len(before)}, after {len(after)}; added {added}; removed {removed}; changed {changed}")
    print(f"task HasPendingRuleChangesFlag now {t2['HasPendingRuleChangesFlag']} (pending, NOT deployed)")
    ok = added == [a.rule] and not removed and not changed and len(mine) == 1 and mine[0]["EnabledFlag"] is False
    print("RESULT: PASS" if ok else "RESULT: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
