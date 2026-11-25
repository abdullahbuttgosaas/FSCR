# CHANGELOG: view-service-clients (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 05, AB with Claude)
- Read-only export: Read-only export FUN_VIEW_SERVICE_CLIENTS: 5 files (FUN_BU_SERVICE_PROVIDERS 276 rows, FUN_BU_USAGE 1105, FUN_BUSINESS_UNIT 186 (has person name columns), LE_<n> 8567) + metadata. REST finBusinessUnitsLOV.
- Live (AB): finBusinessUnitsLOV 1 row; FUN_BU_SERVICE_PROVIDERS: 3 rows for the BU (serves one other BU on 2 function pairs and itself on 1). READ-BACK PASS.
- Fresh test PASS on AKBusiness Unit Corporate: serves itself on 4 pairs (active) and one other BU on 3 pairs (ended, ActiveFlag=N); export 62 s.
- Tester notes not applied (suggestions): time 1 to 2 min; name the BU in the worked example; viewer prints twice with --out; zip file name holds the environment name; function id names.

## Test records created
- none created (view task); looked up existing business units: live GoSaaS Labs PK, fresh test AKBusiness Unit Corporate
