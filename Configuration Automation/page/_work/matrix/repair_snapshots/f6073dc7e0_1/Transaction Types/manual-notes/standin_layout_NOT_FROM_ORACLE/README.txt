STAND-IN, not from Oracle.

Built 2026-11-02 from FSCR e2e-adapter.json (manage-transaction-types, package.entities: members, header lines,
types, node paths, node sequences; release 11.13.26.10.0) for offline tests only, until the read-only check saves the
pod's real template in ../pod_layout_etia_test/. The module never reads this folder.

SUPERSEDED 2026-11-02: the read-only check saved ETIA-TEST's real template in ../pod_layout_etia_test/; the
offline stub uses that. Its headers, node paths and NodeSequence are the same as this stand-in's; only the metadata
file differs. Kept only for comparison.
