"""Added by GoSaaS, not part of official FSCR. Gap fill, Sourcing, 2026-11-27. Offline: no Oracle call.

Prints the lookup types in the scope of a lookup task's read-only export (from ASM_SETUP_CSV_METADATA.xml,
tags ScopeValueBoAttributeValueCode), one per line. Prints nothing else from the metadata (it also holds the
submitting user name, which is never printed). The word "edit" in the scope is a mode, not a type: skipped.

Usage: python -I scope_lookup_types.py <RUN>/export_before/unz
"""
import re
import sys
from pathlib import Path

x = (Path(sys.argv[1]) / "ASM_SETUP_CSV_METADATA.xml").read_text(encoding="utf-8")
types = sorted({v.strip() for v in re.findall(r"<ScopeValueBoAttributeValueCode>([^<]*)<", x)} - {"edit", ""})
if not types:
    sys.exit("STOP: no lookup type in the export scope")
print("\n".join(types))
