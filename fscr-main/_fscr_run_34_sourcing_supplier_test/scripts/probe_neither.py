"""Run 34: read-only REST probes (GET, limit 1) for the two 'neither' tasks. Prints status codes only."""
import api
for api_name, res in [("hcmRestApi", "userCategories"), ("hcmRestApi", "securityUserCategories"), ("fscmRestApi", "userCategories"),
                      ("fscmRestApi", "messages"), ("fscmRestApi", "setupMessages"), ("fscmRestApi", "applicationMessages"), ("fscmRestApi", "fndMessages"),
                      ("fscmRestApi", "supplierQualificationMessages"), ("fscmRestApi", "supplierQualificationQuestions"), ("fscmRestApi", "supplierQualificationAreas")]:
    st, t = api.call("GET", res, {"limit": "1", "onlyData": "true"}, api=api_name)
    print(f"GET /{api_name}/resources/11.13.18.05/{res}?limit=1 -> {st}")
