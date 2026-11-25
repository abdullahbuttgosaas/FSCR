# CHANGELOG: search-legal-reporting-units (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 05, AB with Claude)
- Read-only export: Read-only export XLE_SEARCH_LEGAL_REPORTING_UNITS: same 8-file legal entity package (67 units in XLE_ETB_PROFILE). REST legalReportingUnitsLOV gives MainLegalReportingUnitFlag.
- Live (AB): REST legalReportingUnitsLOV LIKE search found the units; view of XLE_ETB_PROFILE + unit registration: MainEstablishmentFlag=Y, US, registration United States Income Tax. READ-BACK PASS.
- Fresh test: PASS on N24Vision America (main unit, identifier, US, registration number and jurisdiction), export about 84 s, no help.
- Tester notes not applied (suggestions): say success = ZIP written and that 'StatusCode: (unknown)' is normal; one ZIP per folder; drop the cross-reference in Sign-in; viewer prints to screen and file; time about 1.5 min.

## Test records created
- none created (view/search task); looked up existing units: live 28Vision America, fresh test N24Vision America
