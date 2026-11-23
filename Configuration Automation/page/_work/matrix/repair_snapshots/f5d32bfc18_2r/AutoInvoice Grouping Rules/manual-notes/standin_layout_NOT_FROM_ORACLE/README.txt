STAND-IN, not from Oracle.

These files are NOT an export from any Oracle pod. They were built on 2026-11-01 from FSCR's offline contract
(fscr-main/pillars/erp/financials/customer-billing/manage-autoinvoice-grouping-rules/e2e-adapter.json,
package.entities: member names, header lines, field types, node paths, node sequences; evidence release
11.13.26.10.0). ProcessEnv "etia-test" is written so the offline stub's pod check passes; no pod produced it.

Used ONLY by the offline matrix (page/matrix/stub_grouping.py). The module itself never reads this folder: on every
run it reads the layout from the pod's own template (setupTaskCSVTemplateExports), falling back to the data file.

The real layout (entity order, headers, quoting, release) is confirmed only in the live test. After that test,
save the real template's header lines and metadata next to this folder (as Receivables Payment Terms'
pod_layout_etia_test/) and point the stub at them.

SUPERSEDED 2026-11-01: the read-only live check saved ETIA-TEST's real template in ../pod_layout_etia_test/, and the
offline stub now uses that. This folder is kept only for comparison (see the folder's CLAUDE.md > File layout).
