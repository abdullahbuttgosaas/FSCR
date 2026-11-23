import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
for off in sys.argv[2:]:
    o = d["offerings"][off]
    print("==", off, o["offeringName"], "FAs", o["functionalAreaCount"], "tasks", o["taskCount"])
    for fa in o["functionalAreaOrder"]:
        f = o["functionalAreas"][fa]
        print("  ", fa, "|", f["functionalAreaName"], "|", len(f.get("tasks", [])))
