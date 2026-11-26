---
skill_id: "gosaas.gap-fills.procurement.manage-intake-request-approvals"
name: "Manage Intake Request Approvals: add one disabled approval rule by REST (GoSaaS gap fill)"
description: "Adds ONE new approval rule, DISABLED and never deployed, to a participant of the 'Intake Request Approvals' approval task through Oracle REST approvalRules, then reads the participant's rules back (1 added, 0 removed, 0 changed). Ids are read live. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 06, 2026-11-27. NOT official FSCR."
task_code: "ORA_PO_MANAGE_INTAKE_REQUEST_APPROVALS"
task_name: "Manage Intake Request Approvals"
offering: "Procurement"
dataloader_import_mode: "REST"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
side_effects:
  - "Adds one rule to the task as a PENDING rule change. The task then shows pending changes (HasPendingRuleChangesFlag true) until someone deploys or discards them on the page. The rule is disabled, so a later deployment by anyone changes no routing."
  - "This skill never deploys (deployRulesToBPM), never discards (discardPendingRuleChanges: it would also drop other people's pending changes) and never edits or deletes an existing rule."
---

# Manage Intake Request Approvals (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no CSV route for this task (catalog CSV flag N) and no skill. This skill uses FSCR's REST client in place through the GoSaaS wrapper `rest_call.py` and edits no FSCR file.
> Labels: **VERIFIED** = seen live · **GUESS** = not run live. Status of this skill: Steps 1 and 2 VERIFIED on this task; Step 3 was refused on the test environment because the task's rules are not upgraded from BPM (POR-2011627). The same script's POST and read-back are VERIFIED on Requisition and Purchasing Document Approvals.

> **Unsafe to test on a shared environment (written, not loaded).** On the test environment this task has `IsRulesUpgradedFlag=False`: its rules still live in BPM. Oracle refuses every new rule with `POR-2011627 You can't create approval rules until the rules for the approval task have been upgraded from BPM` (VERIFIED 2026-11-27). The upgrade is a one-time action on the **Manage Intake Request Approvals** page. It switches the task's rule source for **everyone**, and REST has no action to undo it (only `clearApprovalRules`, which deletes the task's rules). Run Step 3 only where the task is already upgraded, or after the owner of the approval setup has upgraded it on purpose.

## What it is and when to use
The task sets the approval rules of the **Intake Request Approvals** approval task. Each rule belongs to one **participant** (a routing step such as "Preapproval Serial 2") and has conditions and actions. Oracle's REST resources (VERIFIED):
- `approvalTasks`: the approval tasks; children `participants` and `approvalRulesDeploymentJobs`; actions `deployRulesToBPM`, `discardPendingRuleChanges`, `clearApprovalRules`.
- `approvalAttributesLOV`: the condition attributes of a task (filter `q=TaskId=<id>`).
- `approvalRules`: the rules, children `conditions` and `actions`. A GET needs `q=ParticipantId=<id>` (else `POR-2011550`).

Use this skill to add a **new** rule for a test, or as the pattern for a real rule. A test rule is disabled, priority LOW, with one condition "<amount> greater than 999999999999" and one action Automatic / Rejected. Even if someone enabled and deployed it, it would only touch documents above that amount.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds procurement\ and common-features\)
S     = <GAPS>/procurement/scripts/approval_rule.py
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); create it first: mkdir -p "<RUN>"
PREFIX= your test prefix, e.g. GAPFILL_XX_ (the script's --prefix: it refuses a RULE that does not start with it)
RULE  = new rule name = PREFIX + short name, e.g. GAPFILL_XX_IR1 (letters, digits, underscores)
PART  = participant name, e.g. Preapproval Serial 2 (Step 1 lists them)
KEY   = condition attribute key of a NUMBER amount, e.g. amount
DIM   = its dimension key, e.g. IntakeRequestLine
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; a valid cached sign-in returns at once). It lasts about one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names.

## Prerequisites
1. The approval task's rules must be **upgraded from BPM** (`IsRulesUpgradedFlag=True`). Step 1 and Step 2 print it. If it is `False`, stop: a new rule is refused with `POR-2011627` (VERIFIED). Do not upgrade it yourself (shared, and REST cannot undo it).
2. Nothing else: participants and condition attributes come with the task (VERIFIED).

## Step 1. Read the task, its participants and attributes (read only, VERIFIED)
```bash
cd "<RUN>"
python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/approvalTasks --query onlyData=true --query limit=200 --no-open-browser --output tasks.json > tasks.log 2>&1
python -I -c "import json; [print(t['TaskId'],'|',t['Task'],'| upgraded',t['IsRulesUpgradedFlag'],'| pending',t['HasPendingRuleChangesFlag']) for t in json.load(open('tasks.json',encoding='utf-8'))['items']]"
```
Find the line for `Intake Request Approvals` (add `| grep -i "Intake Request Approvals"` to shorten the list) and note its TaskId as `<TID>` (read live; never copy it from another environment). `Task` cannot be used in `q=` (`not queriable`, VERIFIED), so the filter is done in Python.
```bash
python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/approvalTasks/<TID>/child/participants --query onlyData=true --query limit=200 --no-open-browser --output parts.json > parts.log 2>&1
python -I -c "import json; [print(p['Participant'],'|',p['Stage']) for p in json.load(open('parts.json',encoding='utf-8'))['items']]"
python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/approvalAttributesLOV --query "q=TaskId=<TID>;DisplayDataTypeCode='NUMBER'" --query onlyData=true --query limit=500 --no-open-browser --output attrs.json > attrs.log 2>&1
python -I -c "import json; [print(a['AttributeKey'],'|',a['DimensionKey'],'|',a['Attribute']) for a in json.load(open('attrs.json',encoding='utf-8'))['items'] if a['AttributeTypeCode']=='RULE_ONLY']"
```
Pick `<PART>` from the first list and `<KEY>` / `<DIM>` from the second (on the test environment `amount` / `IntakeRequestLine` = "Amount", VERIFIED). `AttributeKey` cannot be used in `q=` either. Join two filters with `;`, never `and`. Check for an expired sign-in with `grep -E "HTTP (401|403)" *.log` (no output = fine); on a hit, sign in again.

## Step 2. Dry run (no change, VERIFIED)
```bash
python -I "<S>" --fscr "<FSCR>" --rest-call "<W>" --run "<RUN>/rule" --task "Intake Request Approvals" --participant "<PART>" --attribute-key <KEY> --dimension-key <DIM> --rule <RULE> --prefix <PREFIX> --dry-run
```
The script reads the task, participant and attribute live, counts the participant's rules, checks that `<RULE>` is not one of them, and writes `<RUN>/rule/rule_body.json`. Success: the last line is `DRY RUN: nothing sent`. A line starting `STOP:` says what is wrong (task or participant name not found, attribute not NUMBER, rule name already used). `IsRulesUpgradedFlag=False` in the first line: stop (Prerequisite 1).

## Step 3. Create ONCE (VERIFIED on Requisition and Purchasing Document Approvals; refused on this task here, see the note at the top)
Run the Step 2 command again without `--dry-run`, with a new `--run` folder (e.g. `"<RUN>/rule2"`) so the dry-run files stay apart. The script POSTs once to `approvalRules`:
```json
{"TaskId": <TID>, "ParticipantId": <read live>, "Rule": "<RULE>", "EnabledFlag": false, "RuleAlwaysAppliesFlag": false, "PriorityCode": "LOW",
 "conditions": [{"ConditionNumber": 1, "ConditionAttributeId": <read live from approvalAttributesLOV>, "OperatorCode": "MORE_THAN", "ComparisonTypeCode": "VALUE", "ComparisonValueNumber": 999999999999}],
 "actions": [{"ActionTypeCode": "AUTOMATIC", "AutomaticOutcomeCode": "REJECTED"}]}
```
Oracle refuses (VERIFIED) `ConditionTypeCode` and `ActionNumber` ("cannot be set") and `ConditionAttributeKey` (send `ConditionAttributeId`). Success: `POST OK: RuleId ..., EnabledFlag False`. A dropped connection or a hang: never POST again; run the read-back below first (the rule may exist).

## Step 4. Read back (VERIFIED)
The create run itself reads the participant's rules again and prints `condition: <attribute> Greater than 999999999999`, `action: AUTOMATIC / REJECTED`, `added ['<RULE>']; removed []; changed []`, `HasPendingRuleChangesFlag now True (pending, NOT deployed)` and `RESULT: PASS`. The proof is the `added [...]` line; the pending flag may already have been True before your run (others' pending changes), which is normal. To read back later:
```bash
python -I "<S>" --fscr "<FSCR>" --rest-call "<W>" --run "<RUN>/rb" --task "Intake Request Approvals" --participant "<PART>" --attribute-key <KEY> --dimension-key <DIM> --rule <RULE> --prefix <PREFIX> --readback-only
```
Success: `READBACK: <RULE> found 1 time(s), EnabledFlag=False`.

## Rules and limits
1. New, disabled rules only. Never enable, deploy (`deployRulesToBPM`) or discard (`discardPendingRuleChanges`): deploy publishes every pending change of the task; discard also throws away other people's pending changes.
2. A REST-created rule is a **pending** change: the task's `HasPendingRuleChangesFlag` is True afterwards (VERIFIED; it went False → True on a task with no pending changes, and stays True if it already was). It shows on the **Manage Intake Request Approvals** page as an undeployed change. A disabled rule routes nothing even if someone else deploys (GUESS: not deployed in the test).
3. REST `approvalRules` has no DELETE (describe lists get, create, upsert, duplicate; VERIFIED). Plan as if the rule stays; it can be removed on the page.
4. Real rules (route to an approval group, a supervisor chain or a user) need action fields such as `RouteUsingCode`, `ApprovalGroup`, `UserTypeCode`: GUESS. Read a working rule with `expand=actions` first.
5. `TaskId`, `ParticipantId` and `ConditionAttributeId` differ per environment: always read them live.

## Worked example (2026-11-27, names only)
| Step | Result |
|---|---|
| Own try (script) | `GAPFILL_AB_B6_IR1` on participant "Preapproval Serial 2": Steps 1-2 OK; POST refused `POR-2011627` (task not upgraded from BPM); nothing created (participant rules 0) |
