# How the tracker row is written

**You do NOT edit the FSCR Module Test Tracker.** It is view only, and Abdullah updates it.
Your module run produces `tracker_row.md` with the final values in exactly the format below, ready to paste.
Then you upload your module's evidence folder to Drive and send Abdullah the folder link. That link becomes the
**Evidence link** for your row.

## File format

`tracker_row.md` has one `## <column name>` heading per tracker column, in the tracker's order, with the value
on the lines under it. Start from `python scripts/tracker_row.py template ...` and finish with
`python scripts/tracker_row.py check tracker_row.md`. The check must say **PASS**.

General rules:
- **Bullets**: columns with several points use one line per point, each starting with `• ` (bullet and a space).
  Short plain sentences. No sub-bullets.
- **Dates**: `dd/mm/yyyy`, for example `17/11/2026`.
- **Missing**: `N/total`, for example `26/41`.
- **Status**: `Completed`, or `Blocked` if you could not finish (say why in Key findings).
- **No owners or people's names** in the gap column, and nowhere else except where the guide says so.
- No tokens, passwords, sign-in names, e-mail addresses or environment addresses anywhere.

## Column by column

| # | Column | What to write | Example |
|---:|---|---|---|
| 1 | Pillar | `ERP`, `HCM` or `SCM`, from `coverage.csv` | `SCM` |
| 2 | Module | the tracker row name, from `coverage.csv` | `Procurement` |
| 3 | FSCR coverage | `Full`, `Partial`, `None` or `Unknown`: the proposed coverage in `coverage.csv` (change it only with a reason in RESULT.md) | `Partial` |
| 4 | Fit rating | `High` (usable as is), `Medium` (usable with GoSaaS adaptation), `Low` (GoSaaS must build its own skills) or `None` (not covered) | `Medium` |
| 5 | Contact Person/Owner | exactly `(no change)`. Abdullah keeps what is there | `(no change)` |
| 6 | Plan accuracy (1–5) | one number 1–5. The reason goes in RESULT.md | `3` |
| 7 | Total Tasks | the module's task count from `coverage.csv` | `41` |
| 8 | Missing | `N/total` = tasks with no skill or guide / Total Tasks, from `coverage.csv` | `26/41` |
| 9 | Gaps filled | exactly `(leave empty)`. Gap fills are not part of this test | `(leave empty)` |
| 10 | Runbook quality (1–5) | one number 1–5 | `3` |
| 11 | Execution & validation (1–5) | one number 1–5 | `3` |
| 12 | Status | `Completed` (or `Blocked`) | `Completed` |
| 13 | Target Completion Date | exactly `(no change)`. Abdullah sets it | `(no change)` |
| 14 | FSCR skills / workflows used | bullets, plain names of what FSCR did | `• Planning (task order)` |
| 15 | Test scenario | bullets: Scope, Planning, Test, Done, Not done | `• Test: 6 sample tasks on the test environment` |
| 16 | Fusion env / release | environment label and release, no address | `Test environment, 11.13.26.10.0` |
| 17 | Tester | your initials only (2–3 capital letters). Abdullah writes your name | `AB` |
| 18 | Last tested | the date you finished, `dd/mm/yyyy` | `17/11/2026` |
| 19 | Key findings | 3–4 bullets, each a full plain sentence with a number where you have one | `• 3 of the 4 tasks that can be loaded went in and read back correct.` |
| 20 | GoSaaS gap / build needed | bullets of what GoSaaS must build. **No owners, names or "assigned to"** | `• Add prerequisites to the Run Book, plus a repair step after a timeout.` |
| 21 | Evidence link | exactly `(Drive folder link, added by Abdullah)` | |

Use these plain names in column 14 (only the ones you actually used):
`Planning (task order)`, `Data loading (import and export)`, `Safety checks before loading (Task Hook)`,
`Run Book creation`, `Setup guides`, `REST API`.

## Example (shortened)

```
## Missing
26/41

## Status
Completed

## Last tested
17/11/2026

## GoSaaS gap / build needed
• Add a Procurement dependency list from Oracle's pages.
• Build screen recipes for Approval Groups and Corporate Cards.
```

Full examples: `examples/*/tracker_row.md`.

## After the run

1. `python scripts/build_evidence.py ...` must end with PASS.
2. Upload the whole `evidence/<Module>/` folder to Drive (a folder in your own Drive is fine; share it with Abdullah
   as Viewer).
3. Send Abdullah the folder link. He pastes your `tracker_row.md` into the tracker and uses the link as the Evidence link.
