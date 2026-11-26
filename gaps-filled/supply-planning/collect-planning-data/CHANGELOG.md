# CHANGELOG: Collect Planning Data

Task code: ORA_MSC_COLLECT_PLANNING_DATA · filled by IR · 24/11/2026 · route REST (dataCollections) · status written (unsafe to test)

## Test records and ProcessIds

None. Nothing was loaded: a collection writes into the shared planning data repository (see STATUS.md notes).

## Read-only checks (batch 02)

| Check | Result |
|---|---|
| FSCR task-level export (`--data`) | refused: catalog `CSVExportImportSupportedFlag` N; no ZIP written |
| REST GET dataCollections (limit 2, then the skill's own 25-run query) | works; runs keyed by InstanceId + RefreshNumber; latest runs `Completed` / `NORMAL`; `SourceSystem` and `CollectionType` empty on all 25 (flat-file loads) |
| REST describe dataCollections | 29 attributes; collection actions GET and POST (`create`); item actions GET and DELETE; no children |
| `fusion_rest_client.py --help` | JSON body option is `--body-file` (first draft said `--data`; fixed before the skill was finished) |

## History

- Batch 01 (earlier sitting): skipped as unsafe without a skill. Re-opened in batch 02 because the new rule says that
  unsafe tasks still need a full SKILL.md.
- Batch 02: SKILL.md written from the read-only checks above and Oracle's docs (Overview of Data Collections for Supply
  Chain Planning; Manage Planning Source Systems for Data Collections; Considerations for Enabling Organizations for
  Data Collections).

## Live test (batch 03, 25/11/2026, approved by IR: one small net-change run)

| Try | Body | Result |
|---|---|---|
| 1 | SourceSystem GPR, CollectionType 2, EntityList UOM_CODES | refused: Message "You must enter a value for the TemplateName attribute."; no ESSCollectionJobId; GET shows newest run still 11015 (nothing created) |

Not retried: a template is required, and no REST resource lists templates (dataCollectionTemplates, collectionTemplates
and planningCollectionTemplates do not exist). A predefined template would collect many more entities than the approved
units-of-measure run. Read-only checks in the same batch: lookup MSC_DATA_COLLECTION_MODE (1 Targeted, 2 Net change,
3 Automatic selection); 147 past runs, 63 of them Fusion collections with entity codes such as UOM_CODES.

Skill fixes: TemplateName is now required in Placeholders and Build rows; added the "can succeed without starting
anything" check; GPR comes from Oracle's REST doc example (26D) and is still a GUESS.

Route 1, the scheduled process (chosen by IR, 25/11/2026): not submitted. Oracle documents `submitESSJobRequest` only
for the flat-file load (job `CSVController`), not for the Fusion-source Collection Job Set. A past request's job name
and parameters could not be read (ESS request endpoint 404; the `ESSJobStatusRF` finder returns none). Guessing
positional parameters on the shared environment could start a full collection, so nothing was sent. The skill now has
an "Other routes checked" section.

## Tester notes

No fresh test: the task is unsafe to test, and a fresh test without a live load would prove nothing.
