task_code: ORA_MSC_COLLECT_PLANNING_DATA
task_name: Collect Planning Data
module: Supply Planning
status: written
filled_by: IR
date: 25/11/2026
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 6
fresh_claude_pass: not run (no collection could be started, so there was nothing for a fresh tester to repeat)
route: REST dataCollections (POST starts a collection; GET and describe checked read-only); no FSM CSV (catalog CSV flag N, FSCR export refuses it)
depends_on: MSC_MANAGE_PLANNING_SOURCE_SYSTEMS (organizations enabled for collections); approval of the planning data owner
test_records: none (nothing loaded)
notes: unsafe to test on a shared environment: a dataCollections POST writes into the shared planning data repository; runs carry no name, so no test prefix. Batch 03 (25/11/2026, approved by IR for one net-change UOM_CODES run): POST {SourceSystem GPR, CollectionType 2, EntityList UOM_CODES} was refused with Message 'You must enter a value for the TemplateName attribute.' (no ESSCollectionJobId; GET showed no new run). Templates are kept on the Collect Planning Data page, and no REST resource lists them; a predefined template collects many entities, beyond the approval. Scheduled-process route (erpintegrations) not submitted: Oracle documents no job name or parameters for the Fusion-source Collection Job Set, and a past request's parameters cannot be read (ESS endpoint 404). Next step: save a template on the Collect Planning Data page that holds only UOM_CODES, or get approval for a predefined template, then POST once with TemplateName and run the fresh test.
