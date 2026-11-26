# Batch 03 result: Supply Planning

Filled by IR · 25/11/2026 · live test of Collect Planning Data, approved by IR in chat (one small net-change run of
units of measure)

## Time log

| Step | Start | Finish |
|---|---|---|
| Read-only: past runs, Oracle REST doc, collection-mode lookup | 00:04 | 00:06 |
| POST (one try) and read back | 00:06 | 00:07 |
| Template resource check, skill and card updates | 00:07 | 00:09 |

## Tasks

| Task | Status | Working min | Waiting min | Records | Job ids |
|---|---|---:|---:|---|---|
| ORA_MSC_COLLECT_PLANNING_DATA | written (live POST refused; not started) | 6 | 2 | none | none (no ESSCollectionJobId returned) |

## Findings

- **`TemplateName` is required.** A POST with `SourceSystem` GPR, `CollectionType` 2 and `EntityList` UOM_CODES came back
  without an error code. Its `Message` was "You must enter a value for the TemplateName attribute.", and it returned no
  job id. A GET showed no new run (VERIFIED).
- **No REST resource lists templates.** Templates are saved on the Collect Planning Data page. A predefined template
  would collect many entities, more than the approved run, so I sent no second POST.
- **The client exits 0 even when Oracle refuses.** Only an `ESSCollectionJobId` in the response proves that a collection
  started. The skill now says so.
- No processes left running; no data changed.

## Route 1: scheduled process (after IR said a template is not needed on the page)

Route 1, the scheduled process (chosen by IR, 25/11/2026): not submitted. Oracle documents `submitESSJobRequest` only
for the flat-file load (job `CSVController`), not for the Fusion-source Collection Job Set. A past request's job name
and parameters could not be read (ESS request endpoint 404; the `ESSJobStatusRF` finder returns none). Guessing
positional parameters on the shared environment could start a full collection, so nothing was sent. The skill now has
an "Other routes checked" section.

## What is left

Collect Planning Data still needs a collection template that holds only the entity to collect. A person saves it on
the Collect Planning Data page (or approves a predefined template). Then send one POST with `TemplateName` and run the
fresh test.
