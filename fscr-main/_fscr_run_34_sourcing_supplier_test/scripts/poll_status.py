import api, json, sys, time
ids=[int(x) for x in sys.argv[1:]]
for rnd in range(40):
    out={}
    for rid in ids:
        st,t=api.call("GET","/hcmRestApi/resources/11.13.18.05/dataLoaderDataSets",{"q":f"DataSetRequestId={rid}","onlyData":"true"})
        it=json.loads(t)["items"] if st==200 else []
        out[rid]=(it[0]["DataSetStatus"] if it else "none")
    print(time.strftime("%H:%M:%S"),out,flush=True)
    if all(v not in ("ORA_IN_PROGRESS","none") for v in out.values()): break
    time.sleep(20)
