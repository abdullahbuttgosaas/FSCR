---
skill_id: "gosaas.gap-fills.common-features.manage-applications-core-messages"
name: "Manage Applications Core Messages: load new messages from a pipe-delimited file with the scheduled process Upload Comma-Separated Values File for Import Process (GoSaaS gap fill, failed: job path unknown)"
description: "Creates new application messages (Message Dictionary) from a pipe-delimited MESSAGES file uploaded to the content repository and loaded by the scheduled process Upload Comma-Separated Values File for Import Process (file type MESSAGES). Not run: the process's job package and definition name are not published and could not be read by REST. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 23, 2026-11-26. File format from Oracle docs; not run live. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_APPLCORE_MESSAGES"
task_name: "Manage Applications Core Messages"
dataloader_import_mode: "ESS (file upload + scheduled process)"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "the job package and job definition name of the scheduled process Upload Comma-Separated Values File for Import Process (read once on the Scheduled Processes page; not published)"
  - "the numeric ApplicationId of the application that owns the message (read live, Step 1)"
side_effects:
  - "Step 4 (not run) creates or updates messages. A row whose MessageName and ApplicationId already exist UPDATES that message: only send new names with your prefix."
---

# Manage Applications Core Messages (GoSaaS gap fill, status: failed, next step known)

> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live or read in Oracle's docs on 2026-11-26 · **GUESS** = not run live.

## What it is and when to use
Application messages (Message Dictionary: error, warning and information texts) are made on the Manage Messages page. The task's FSM CSV export is refused (task flag `CSVExportImportSupportedFlag N`, VERIFIED) and the REST resource `messages` is read only (describe: get; a POST is refused "create not enabled", VERIFIED 2026-11-25).
Oracle's docs give a file route (VERIFIED by reading, 2026-11-26): the scheduled process **Upload Comma-Separated Values File for Import Process** loads setup data "for artifacts such as flexfields, messages, lookups" from a flat file in the content repository, with parameters **Flat File Name**, **Account** and **File Type** (`MESSAGES` for messages, `MESSAGE_TOKENS` for their tokens). Source pages: "Upload Comma-Separated Values File for Import Process" and "File Format for Importing Messages" (Oracle Help Center, Implementing Applications / Common Features).

## Why the status is failed (proven cause, 2026-11-26)
To run the process without the page you need its job package and definition name. They are not in Oracle's published docs (3 doc searches), the REST resource `valueSets` that the docs point to has no upload action (describe: only get, create, update, delete, upsert, VERIFIED), and the scheduler REST API returns empty job fields for requests (VERIFIED). Nothing was loaded.
**Next step:** a person opens Scheduled Processes > Schedule New Process > "Upload Comma-Separated Values File for Import Process" once and notes the job's package and definition (shown in the process details), or reads My Oracle Support note 2174930.1; then run Steps 3 to 5 with a prefix message.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\ and the filled-in core\auth\fusionEnv.properties). Read only.
W      = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's REST client unchanged; never prints the server)
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
MSG    = new message name = PREFIX + short name, upper case, at most 30 characters
APPID  = numeric ApplicationId of the owning application (Step 1)
ACCOUNT= the content repository account the process reads from (GUESS: setup/applicationsCoreSetup; read the Account list of values on the process page)
PKG, DEF = the process's job package and job definition name (see Next step)
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. Never print tokens, the server address or user names.

## Step 1. Read the application id and check the name is free (read only, VERIFIED resource)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/messages --query "q=MessageName='<MSG>'" --query onlyData=true --no-open-browser --output "<RUN>/pre.json" > pre.log 2>&1
python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/messages --query "q=ApplicationShortName='FND'" --query limit=1 --query onlyData=true --no-open-browser --output "<RUN>/app.json" > app.log 2>&1
```
`pre.json` must have 0 items. Take `ApplicationId` from `app.json` (GUESS: the field names of the `messages` resource; check with `/messages/describe`).

## Step 2. Build the file (format VERIFIED from Oracle's docs)
Pipe `|` delimited, UTF-8 **without** BOM, header line first. Required columns: MessageName (max 30), ApplicationId, ModuleType, ModuleKey, MessageType (`ERROR`, `WARNING`, `INFORMATION` or `STRING`), ShortText (max 240). Oracle's sample uses ModuleType `APPLICATION` and ModuleKey = the application short name (`FND`).
```text
MessageName|ApplicationId|ModuleType|ModuleKey|MessageNumber|MessageType|ShortText|LoggingEnabled|MessageSeverity|MessageCategory|MessageUserDetails|MessageAdminDetails|MessageCause|MessageUserAction|MessageAdminAction|TranslationNotes
<MSG>|<APPID>|APPLICATION|FND||INFORMATION|Test message <MSG>, not used by any program|N||||||||
```
Save as `<RUN>/<MSG>.txt`. A tokens file (`MESSAGE_TOKENS`: MessageName|ApplicationId|TokenName|DataType|Description) is only needed for messages with tokens.

## Step 3. Upload the file to the content repository (GUESS)
REST `erpintegrations` operation `uploadFileToUcm` (Financials REST guide, "ERP Integrations"): body with `OperationName` `uploadFileToUcm`, `DocumentContent` (base64 of the file), `DocumentAccount` `<ACCOUNT>`, `ContentType` `txt`, `FileName` `<MSG>.txt`. Keep the returned `DocumentId`.

## Step 4. Run the process ONCE (GUESS)
REST `erpintegrations` operation `submitESSJobRequest`: `JobPackageName` `<PKG>`, `JobDefName` `<DEF>`, `ESSParameters` = `<MSG>.txt,<ACCOUNT>,MESSAGES` (order of Flat File Name, Account, File Type: GUESS). Keep the request id; check it with `erpintegrations?finder=ESSJobStatusRF;requestId=<id>` until it succeeds. Never submit twice: check Step 5 first after a dropped connection.

## Step 5. Read back (VERIFIED resource)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/messages --query "q=MessageName='<MSG>'" --query onlyData=true --no-open-browser --output "<RUN>/rb.json" > rb.log 2>&1
```
Expect 1 item with your text.

## Rules and limits
1. Only new message names with your prefix; a known name updates the existing message.
2. Never change a seeded message.
3. The read-back resource `messages` is read only; there is no delete by REST.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused (task flag N) |
| REST `messages` | read only (describe get; POST refused 2026-11-25) |
| `valueSets` describe | no upload action |
| Process job name | not published; scheduler REST shows empty job fields: **failed**, next step above |
