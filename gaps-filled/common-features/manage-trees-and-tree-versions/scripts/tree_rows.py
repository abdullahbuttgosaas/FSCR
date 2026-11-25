"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 07 (2026-11-25).

Builds an FSM setup-task CSV package with ONE new tree, its data source parameters, one DRAFT version and
(optionally) nodes, for the tasks "Manage Trees and Tree Versions" and "Manage Account Hierarchies".
Every id the rows need is read LIVE by read-only REST (through rest_read.py and FSCR's REST client):
  - fndTreeNodes   (finder TSCodeAndTCodeRowFinder) on an existing TEMPLATE tree of the same structure
                   -> the structure's data source ids (DataSourceId of its nodes)
  - fndTreeDataSourceParams (finder TreeDataSourceParamsRowFinder) per data source
                   -> ParameterId + ParameterValue tuples of the template tree
The template's tuples are copied; a value equal to --template-value-set is replaced by --value-set.
New GUIDs are generated for TreeVersionId and TreeNodeId. Then build_fsm_package.py writes the package
(it refuses keys that already exist in the export, so nothing existing is updated).

Usage (run WITHOUT -I: it starts rest_read.py, which needs FSCR's sign-in code):
  python -B tree_rows.py --fscr <FSCR> --export-dir <RUN>/export_before/unz --out-dir <RUN>/payload \
      --zip-name tree_new.zip --prefix GAPFILL_XX_ --structure GL_ACCT_FLEX \
      --template-tree "<existing tree code>" [--template-value-set "<its value set code>"] \
      --tree <NEW_TREE_CODE> --value-set <VALUE SET for the new tree> --start-date 2026/01/01 \
      [--root VALUE] [--child VALUE:PARENT_VALUE ...]
  --root/--child need a template tree WITH nodes: the root's data source is taken from the template's
  depth-0 nodes, a child's from the template's deeper leaf nodes (ChildCount 0).
Prints the data source ids it found and the builder's result. Prints no token, server or user name.
"""
import argparse, json, subprocess, sys, tempfile, uuid
from pathlib import Path

HERE = Path(__file__).resolve()
HELP = HERE.parents[2] / "manage-docseq-categories" / "scripts"


def rest(fscr, resource, finder, fields):
    out = Path(tempfile.mkdtemp(prefix="gapfill_tr_")) / "r.json"
    cmd = [sys.executable, "-B", str(HELP / "rest_read.py"), "--fscr", fscr, "--resource", resource,
           "--finder", finder, "--fields", fields, "--limit", "500", "--out", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not out.exists():
        sys.exit("STOP: REST read failed (" + resource + "): " + (p.stdout.strip().splitlines() or ["?"])[-1])
    d = json.load(open(out, encoding="utf-8"))
    out.unlink(); out.parent.rmdir()
    if d.get("hasMore"):
        sys.exit("STOP: REST result cut off (hasMore); use a smaller template tree")
    return d["items"]


def gid():
    return uuid.uuid4().hex.upper()


def main():
    ap = argparse.ArgumentParser()
    for k in ("fscr", "export-dir", "out-dir", "zip-name", "prefix", "structure", "template-tree",
              "tree", "value-set", "start-date"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--template-value-set", help="default: the one Pk2StartValue of the template's nodes")
    ap.add_argument("--tree-name")
    ap.add_argument("--version-name")
    ap.add_argument("--end-date", default="4712/12/31")
    ap.add_argument("--root", action="append", default=[])
    ap.add_argument("--child", action="append", default=[], help="VALUE:PARENT_VALUE")
    a = ap.parse_args()

    nodes = rest(a.fscr, "fndTreeNodes",
                 f"TSCodeAndTCodeRowFinder;TreeCode={a.template_tree},TreeStructureCode={a.structure}",
                 "TreeCode,DataSourceId,Depth,ChildCount,Pk2StartValue")
    nodes = [n for n in nodes if n.get("TreeCode") == a.template_tree]
    if not nodes:
        sys.exit("STOP: the template tree has no nodes (or does not exist): pick a template tree with nodes")
    dss = sorted({n["DataSourceId"] for n in nodes})
    root_ds = sorted({n["DataSourceId"] for n in nodes if str(n.get("Depth")) == "0"})
    leaf_ds = sorted({n["DataSourceId"] for n in nodes if str(n.get("Depth")) != "0" and str(n.get("ChildCount")) == "0"})
    if not a.template_value_set:
        vs = sorted({n.get("Pk2StartValue") or "" for n in nodes})
        if len(vs) != 1 or not vs[0]:
            sys.exit(f"STOP: give --template-value-set (template nodes show {vs})")
        a.template_value_set = vs[0]
    print("template value set:", a.template_value_set)
    print("data sources of the template:", ", ".join(dss))
    print("root data source:", root_ds, "| leaf data source:", leaf_ds)

    params = []
    for ds in dss:
        for p in rest(a.fscr, "fndTreeDataSourceParams",
                      f"TreeDataSourceParamsRowFinder;DataSourceId={ds},TreeCode={a.template_tree},TreeStructureCode={a.structure}",
                      "DataSourceId,ParameterId,ParameterValue"):
            v = p.get("ParameterValue") or ""
            if v == a.template_value_set:
                v = a.value_set
            params.append((p["DataSourceId"], p["ParameterId"], v))
    if not any(v == a.value_set for _, _, v in params):
        sys.exit("STOP: no template parameter holds --template-value-set; check the template's value set code")
    print(f"parameters: {len(params)} (value set parameter(s) replaced by {a.value_set})")

    S, T = a.structure, a.tree
    X = "ORA_FND_APP_TREE_VERSION"
    vid = gid()
    rows = [f"FND_APP_TREE.csv|TreeStructureCode={S}|TreeCode={T}|TreeName={a.tree_name or T}|SetId=0|Description=Test tree, draft, not used"]
    for ds, pid, v in params:
        rows.append(f"ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv|FND_APP_TREE.TreeStructureCode={S}|FND_APP_TREE.TreeCode={T}|DataSourceId={ds}|ParameterId={pid}|ParameterValue={v}")
    n_nodes = len(a.root) + len(a.child)
    rows.append(f"ORA_FND_APP_TREE_VERSION.csv|TreeStructureCode={S}|TreeCode={T}|TreeVersionId={vid}|ChangedSinceValidation=Y"
                f"|Description=Test version|EffectiveStartDate={a.start_date}|EffectiveEndDate={a.end_date}|LevelCount=0"
                f"|NodeCount={n_nodes}|Status=DRAFT|TreeVersionName={a.version_name or T + '_V1'}")
    ids = {}
    if n_nodes and (len(root_ds) != 1 or len(leaf_ds) != 1):
        sys.exit("STOP: nodes need exactly one root and one leaf data source in the template")
    kids = {}
    for c in a.child:
        kids.setdefault(c.split(":", 1)[1], []).append(c.split(":", 1)[0])
    for i, r in enumerate(a.root, 1):
        ids[r] = gid()
        rows.append(f"ORA_FND_APP_TREE_VERSION_NODE.csv|{X}.TreeStructureCode={S}|{X}.TreeCode={T}|{X}.TreeVersionId={vid}"
                    f"|TreeNodeId={ids[r]}|DataSourceId={root_ds[0]}|Pk1StartValue={r}|Pk2StartValue={a.value_set}"
                    f"|Depth=0|ChildCount={len(kids.get(r, []))}|SortOrder={i}")
    for par, cs in kids.items():
        if par not in ids:
            sys.exit(f"STOP: parent {par} of a --child is not a --root")
        for i, c in enumerate(cs, 1):
            rows.append(f"ORA_FND_APP_TREE_VERSION_NODE.csv|{X}.TreeStructureCode={S}|{X}.TreeCode={T}|{X}.TreeVersionId={vid}"
                        f"|TreeNodeId={gid()}|ParentTreeNodeId={ids[par]}|DataSourceId={leaf_ds[0]}|Pk1StartValue={c}"
                        f"|Pk2StartValue={a.value_set}|Depth=1|ChildCount=0|ParentDataSourceId={root_ds[0]}"
                        f"|ParentPk1Value={par}|ParentPk2Value={a.value_set}|SortOrder={i}")

    cmd = [sys.executable, "-I", str(HELP / "build_fsm_package.py"), "--export-dir", a.export_dir, "--out-dir", a.out_dir,
           "--zip-name", a.zip_name, "--prefix", a.prefix,
           "--key", "FND_APP_TREE.csv=TreeStructureCode,TreeCode",
           "--key", "ORA_FND_APP_TREE_VERSION.csv=TreeStructureCode,TreeCode,TreeVersionName",
           "--key", "ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv=FND_APP_TREE.TreeStructureCode,FND_APP_TREE.TreeCode,ParameterId",
           "--key", f"ORA_FND_APP_TREE_VERSION_NODE.csv={X}.TreeVersionId,TreeNodeId",
           "--prefix-col", "FND_APP_TREE.csv=TreeCode"]
    for r in rows:
        cmd += ["--row", r]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(p.stdout.strip())
    if p.returncode:
        print(p.stderr.strip())
        return p.returncode
    print(f"TREE_VERSION_ID={vid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
