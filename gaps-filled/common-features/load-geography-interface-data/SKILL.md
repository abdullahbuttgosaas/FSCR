---
skill_id: "gosaas.gap-fills.common-features.load-geography-interface-data"
name: "Load Geography Interface Data: load a geography file with the Import Management object GeographyInterface (crm importActivities + erpintegrations upload) (GoSaaS gap fill, written, unsafe to test)"
description: "Loads geography rows (country structure levels and names) into the geography interface with a file import activity: the file is uploaded to the content repository (erpintegrations uploadFileToUCM, account crm$/geography$/import$) and an importActivities record with object GeographyInterface reads it. Not completed: master geography is shared and has no delete; three tries on 2026-11-26 read no row because the uploaded file's content name could not be found by REST. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 24, 2026-11-26/27. Route seen live (object, columns, upload, activity create); no row loaded. NOT official FSCR."
layer: "pillar"
pillar: "CX"
offering: "Common Features"
task_code: "HZ_LOAD_GEOGRAPHY_INTERFACE_DATA"
task_name: "Load Geography Interface Data"
dataloader_import_mode: "REST (file upload + Import Management)"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "gosaas.gap-fills.common-features.run-geography-loader (next step after the interface load)"
side_effects:
  - "Step 4 (not completed) adds geographies to the master geography. Every address entry, address validation and tax jurisdiction of the environment sees them. No delete."
---

# Load Geography Interface Data (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: task export refused (flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-26). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run to the end.
> **Status: written, unsafe to test.** Same reason as Run Geography Loader (batch 21): a geography, even a prefix one, shows in every user's address lists and cannot be deleted.

## What it is and when to use
Oracle docs ("How do I import Non-Oracle Licensed geography data?"): geography data from your own source is loaded through Import Management into the geography interface (`HZ_IMP_GEOGRAPHIES_T`) and then into the master geography. Use it at go-live for countries whose geography Oracle does not deliver.

## What was seen live (2026-11-26)
1. Import Management object code **`GeographyInterface`** (from `importExportObjectMetadata`, VERIFIED). File columns: `RecordTypeCode`, `PrimaryGeographyName`, `CountryCode`, `LevelNumber`, `SourceId`, `ParentSourceId`, `LanguageCode` (country row `RecordTypeCode 0`, child rows `1`).
2. Upload: REST `erpintegrations` `uploadFileToUCM` with `DocumentAccount` `crm$/geography$/import$` returns a numeric `DocumentId` (VERIFIED).
3. Activity: REST `crm importActivities` create with `ObjectCode GeographyInterface`, `ImportMode CREATE_RECORD`, `Activate YES` and one `DataFiles` row is accepted (VERIFIED).
4. **The file reference is the open point.** `DataFiles` takes `InputFileContentId` = the content repository **content name** (like `UCMFA0xxxxxxx`), not the numeric `DocumentId`:
   - inline `InputFileContent` (base64): refused, "Invalid attribute" (try 1);
   - `UCMFA0` + DocumentId: activity ran on another document, `COMPLETE_WITH_ERRORS`, `ReadFromFile` empty (try 2);
   - the numeric DocumentId: `ERROR`, `ReadFromFile` empty (try 3);
   - `erpintegrations` finder `DocumentIdsByFilePrefixRF` gives no content name back.
   No row was read in any try, so no geography was created.

## Why it is unsafe to test here
1. Master geography is shared reference data: everyone's address entry and validation uses it.
2. No delete: a wrong row stays.
What would make it safe: an environment the customer owns, their country file, their written approval.

## Placeholders
```text
FSCR = the FSCR root folder (read only)
W    = <GAPS>/common-features/scripts/rest_call.py
RUN  = a NEW empty work folder OUTSIDE FSCR and outside any git repo
C    = /crmRestApi/resources/11.13.18.05
F    = /fscmRestApi/resources/11.13.18.05
```

## Step 1. Build the file (VERIFIED columns)
```text
RecordTypeCode,PrimaryGeographyName,CountryCode,LevelNumber,SourceId,ParentSourceId,LanguageCode
0,<Country name>,<CC>,1,1,,US
1,<Level-2 name>,<CC>,2,11,1,US
```

## Step 2. Upload (VERIFIED)
POST `<F>/erpintegrations` body `{"OperationName":"uploadFileToUCM","DocumentContent":"<base64>","DocumentAccount":"crm$/geography$/import$","ContentType":"csv","FileName":"<name>.csv"}`. Keep `DocumentId`.

## Step 3. Get the content name (GUESS, open point)
Upload the same file once through Tools > Import Management > Import Queue > Create Import Activity on the page and read the file's content id there, or read the content name from the content repository (Content Server search by `DocumentId`). Without it, Step 4 reads nothing.

## Step 4. Create and run the activity (create VERIFIED, run GUESS)
POST `<C>/importActivities` body `{"Name":"<name>","ObjectCode":"GeographyInterface","ImportMode":"CREATE_RECORD","Activate":"YES","DataFiles":[{"FileName":"<name>.csv","InputFileContentId":"<content name>"}]}`. Read `<C>/importActivities/<id>/child/DataFiles` until `Status` is final; `LoadedSuccessfully` must equal the row count.

## Step 5. Load into the master geography
Run Geography Loader (skill run-geography-loader).

## Worked example (2026-11-26, no row loaded)
| Try | File reference | Result |
|---|---|---|
| 1 | inline `InputFileContent` | HTTP 400 Invalid attribute, nothing created |
| 2 | `UCMFA04544821` | COMPLETE_WITH_ERRORS, read another document, 0 rows read |
| 3 | `4544821` | ERROR, 0 rows read |
