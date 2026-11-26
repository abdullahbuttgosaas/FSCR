# Screen-only verification: Common Features (AB)

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (dedicated verification run, after the ninth sitting). This file replaces the earlier screen-only audit.

**Method (read only on Oracle; nothing created, changed or deleted):** every one of the 43 tasks then marked screen-only was checked again. 1) CSV: a read-only export of its FSM package (task flag `CSVExportImportSupportedFlag`; for a package, its files and columns). 2) REST: Oracle's REST docs endpoint lists (Common Features read in full; Financials read in large part; Sales in part) and page searches, then direct GETs and `describe` of every candidate resource (never a POST). A 404 on a guessed name is not used alone as proof. 3) Related routes that create the same object for another task.

**Result:** 29 confirmed screen-only with proof on the task's own `STATUS.md`; 13 set back to open; 1 set to failed (Application Tax Options: its CSV can create a row). Three `route only` tasks stay screen-only (Intercompany Exceptions and Task Configurations: the package holds a different object; Help Content: the package holds topics, but 10 create imports were refused and the help REST is read only).

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 20:16 | 20:17 | 1 | List of 43, proof places |
| 20:17 | 20:22 | 5 | 43 read-only exports (4 at a time) |
| 20:18 | 20:23 | 5 | Oracle REST docs endpoint lists and searches (3 helpers, web only) |
| 20:22 | 20:25 | 3 | GET and describe of candidate resources; Import Management object list (timed out) |
| 20:25 | 20:30 | 5 | Decisions, cards, screen-only.csv, tracker, this file |

## Table (43 tasks)
| Task | Level | CSV result | REST result | Decision | Proof location |
|---|---|---|---|---|---|
| Create Data Role for Implementation Users (`FND_CREATE_DATA_ROLE_FOR_IMPLEMENTATION_USERS`) | neither | refused (flag N) | no data role resource (transactionSecurityProfiles is a different object) | **open** | `create-data-role-for-implementation-users/STATUS.md` |
| Guided Journeys (`ORA_RCS_GUIDED_JOURNEY`) | neither | refused (flag N) | hcm journeys GET 200, describe: create, update, delete, duplicateJourney (VERIFIED today); guidedJourneys get only (earlier) | **open** | `guided-journeys/STATUS.md` |
| Load Geography Interface Data (`HZ_LOAD_GEOGRAPHY_INTERFACE_DATA`) | neither | refused (flag N) | crm importActivities: create (VERIFIED describe) for the Import Management object Geography; crm setupAssistants child Geographies: create (VERIFIED describe, loads Oracl | **open** | `load-geography-interface-data/STATUS.md` |
| Manage Applications Core Messages (`FND_MANAGE_APPLCORE_MESSAGES`) | neither | refused (flag N) | fscm messages: describe get only; a test POST was refused (HTTP 400 create not enabled, 2026-11-25, batch 09) | **open** | `manage-applications-core-messages/STATUS.md` |
| Manage Indirect Tax Automation with Thomson Reuters (`ORA_MANAGE_INDIRECT_TAX_AUTOMATION_WITH_THOMSON_REUTERS`) | neither | refused (flag N) | fscm taxPartnerRegistrations: create (VERIFIED describe), TaxPartnerName is free text with no list of values; taxPartnerServices 404 | **open** | `manage-indirect-tax-automation-with-thomson-reut/STATUS.md` |
| Manage Internal Resource Organizations (`HZ_MANAGE_RESOURCE_ORGANIZATIONS`) | neither | refused (flag N) | crm resourceUsers POST with a manager role and a new ResourceOrganizationName CREATED organization GAPFILL_AB_B20_ORG1 (VERIFIED live 2026-11-26, batch 20); setupAssistan | **open** | `manage-internal-resource-organizations/STATUS.md` |
| Manage Messages (`FND_MANAGE_MESSAGES`) | neither | refused (flag N) | fscm messages: describe get only; test POST refused (batch 09); atkPopupItems has POST but is popup messages, a different object | **open** | `manage-messages/STATUS.md` |
| Manage Messages for General Ledger (`ORA_GL_MANAGE_APPLCORE_MESSAGES`) | neither | refused (flag N) | fscm messages: describe get only; test POST refused (batch 09) | **open** | `manage-messages-for-general-ledger/STATUS.md` |
| Manage Resource Teams (`HZ_MANAGE_RESOURCE_TEAMS`) | neither | refused (flag N) | resourceTeams, teams 404; queues child resourceTeams has POST but links an existing team to a queue | **open** | `manage-resource-teams/STATUS.md` |
| Manage Tax Geographies (`ZX_MANAGE_TAX_GEOGRAPHIES`) | neither | refused (flag N) | crm geographies get only; crm setupAssistants child Geographies: create (VERIFIED describe); crm importActivities create (Import Management Geography and geography zone o | **open** | `manage-tax-geographies/STATUS.md` |
| Manage Thomson Reuters Services (`ORA_MANAGE_THOMSON_REUTERS_SERVICES`) | neither | refused (flag N) | fscm taxPartnerRegistrations: create (VERIFIED describe), free-text TaxPartnerName; thomsonReutersServices 404 | **open** | `manage-thomson-reuters-services/STATUS.md` |
| Manage Associated Balancing Segments (`XLE_MANAGE_ASSOCIATED_BALANCING_SEGMENTS`) | route only | flag Y, 7 files: package = legal entity package (7 files) | legalEntitiesLOV describe: get only | **open** | `manage-associated-balancing-segments/STATUS.md` |
| Manage Cross-Validation Rules (`GL_MANAGE_CROSS-VALIDATION_RULES`) | route only | flag Y, 7 files: package = chart of accounts key flexfield package (7 files) | no cross-validation rule resource (chartOfAccountsFilters is a different object) | **open** | `manage-cross-validation-rules/STATUS.md` |
| Manage Application Tax Options (`ZX_MANAGE_APPLICATION_TAX_OPTIONS`) | route only | flag Y, 1 files: package holds this object: ZX_APPLICATION_TAX_OPTIONS.csv (34 columns, 0 rows) | no application tax options resource in the Financials list (partyTaxProfiles, partyFiscalClassifications are other objects); 6 names 404 (earlier) | **failed** | `manage-application-tax-options/STATUS.md` |
| Assign Help Text Administration Duty (`ATK_ASSIGN_FUSION_HELP_TEXT_ADMINISTRATION_DUTY`) | neither | refused (flag N) | hcm /scim/Roles GET 200: GET and PATCH only, PATCH manages the USER members of a role, not duty roles inside a job role; fscm roles 404 | **screen-only** | `assign-help-text-admin-duty/STATUS.md` |
| Create Enterprise Additional Account Attributes for China (`ORA_JA_CN_CREATE_ADDITIONAL_ACC_ATTRIBUTES_FOR_CHINA`) | neither | refused (flag N) | chinaAdditionalAccountAttributes, additionalAccountAttributes 404 | **screen-only** | `manage-china-additional-acc-attributes/STATUS.md` |
| Deploy WebLogic Communication Services (`MCT_DEPLOY_WEBLOGIC_COM_SVC`) | neither | refused (flag N) | crm communicationServices 404; multiChannelAdapterToolbars 200 but holds CTI toolbars | **screen-only** | `deploy-weblogic-comm-services/STATUS.md` |
| Integrate WebLogic Communication Services with Telephony Network (`MCT_INTEG_WEBLOGIC_W_TELEPHONY`) | neither | refused (flag N) | crm telephonyNetworks, telephonyIntegrations 404 | **screen-only** | `integrate-weblogic-telephony/STATUS.md` |
| Manage Approval Groups (`ORA_MANAGE_APPROVAL_GROUPS`) | neither | refused (flag N) | fscm and hcm approvalGroups 404; /bpm/api/4.0/tasks GET 200 but handles workflow tasks, not groups | **screen-only** | `manage-approval-groups/STATUS.md` |
| Manage Avalara E-invoicing (`ORA_MANAGE_AVALARA_E_INVOICING`) | neither | refused (flag N) | taxPartners, eInvoicingPartners 404; taxPartnerRegistrations is for tax calculation partners | **screen-only** | `manage-avalara-e-invoicing/STATUS.md` |
| Manage Backends for Visual Builder Studio (`ORA_VISUAL_BUILDER_BACKENDS`) | neither | refused (flag N) | backends 404; no backend resource in the Common Features list | **screen-only** | `manage-backends-for-visual-builder-studio/STATUS.md` |
| Manage Digital Assistant (`ORA_MANAGE_DIGITAL_ASSISTANT`) | neither | refused (flag N) | fscm digitalAssistants, crm digitalAssistantConfigurations 404 | **screen-only** | `manage-digital-assistant/STATUS.md` |
| Manage Global Search Configurations (`ORA_FND_MANAGE_GLOBAL_SEARCH_CONFIGURATIONS`) | neither | refused (flag N) | globalSearchConfigurations 404; no search resource in the Common Features list | **screen-only** | `manage-global-search-configurations/STATUS.md` |
| Manage ISO Languages (`FND_MANAGE_ISO_LANGUAGES`) | neither | refused (flag N) | languagesLOV GET 200, describe get only (VERIFIED today); languages 404; Common Features list: boss v1 languages is read and query only | **screen-only** | `manage-iso-languages/STATUS.md` |
| Manage Industries (`FND_MANAGE_INDUSTRIES`) | neither | refused (flag N) | industries (fscm, crm), industriesLOV 404; no industry resource in the Common Features list | **screen-only** | `manage-industries/STATUS.md` |
| Manage Languages (`FND_MANAGE_LANGUAGES`) | neither | refused (flag N) | languagesLOV describe get only (VERIFIED today); languages 404; boss v1 languages read and query only | **screen-only** | `manage-languages/STATUS.md` |
| Manage Natural Languages (`FND_MANAGE_NATURAL_LANGUAGES`) | neither | refused (flag N) | naturalLanguagesLOV GET 200, describe get only (VERIFIED today); naturalLanguages 404 | **screen-only** | `manage-natural-languages/STATUS.md` |
| Manage Read-Only Schema Column Masking for Users (`ORA_FND_MANAGE_RO_MASKING`) | neither | refused (flag N) | fscm readOnlySchemaMasking, columnMasks 404; no masking resource in the Common Features list | **screen-only** | `manage-ro-schema-masking/STATUS.md` |
| Manage Simulator Transactions (`ZX_MANAGE_SIMULATOR_TRANSACTIONS`) | neither | refused (flag N) | simulatorTransactions, taxSimulatorTransactions 404; Financials tax resources list has no simulator | **screen-only** | `manage-simulator-transactions/STATUS.md` |
| Manage Suggestion Groups (`ORA_FND_MANAGE_SUGGESTION_GROUPS`) | neither | refused (flag N) | suggestionGroups 404; crm setupAssistants child AdaptiveSearch has create but only switches adaptive search on per sales object, a different object | **screen-only** | `manage-suggestion-groups/STATUS.md` |
| Manage Tablet Application Configuration (`FTA_MANAGE_TABLET_APPLICATION_CONFIGURATION`) | neither | refused (flag N) | fscm tabletApplicationConfigurations, crm mobileApplicationConfigurations 404; no tablet resource in the Common Features list | **screen-only** | `manage-tablet-app-config/STATUS.md` |
| Manage Taxonomy Hierarchy (`FND_MANAGE_TAXONOMY_HIERARCHY`) | neither | refused (flag N) | taxonomyHierarchies 404; Common Features list: boss v1 taxonomyNodes read and query only | **screen-only** | `manage-taxonomy-hierarchy/STATUS.md` |
| Manage Territories (`FND_MANAGE_TERRITORIES`) | neither | refused (flag N) | territoriesLOV GET 200, describe get only (VERIFIED today); territories 404; boss v1 territories read and query only | **screen-only** | `manage-territories/STATUS.md` |
| Manage Time Zones (`FND_MANAGE_TIMEZONES`) | neither | refused (flag N) | timezonesLOV GET 200, describe get only (VERIFIED today); timezones 404; boss v1 timezones read and query only | **screen-only** | `manage-time-zones/STATUS.md` |
| Manage User Identity Synchronization to PaaS Identity Store (`ORA_FND_USER_IDENTITY_SYNCHRONIZATION_REPORT`) | neither | refused (flag N) | fscm userIdentitySynchronizations 404; SCIM Users creates users, a different object | **screen-only** | `user-identity-sync-paas/STATUS.md` |
| Migrate Enterprise Roles and Assignments to PaaS Identity Store (`ORA_FND_MANAGE_ROLES_TO_SYNCHRONIZE`) | neither | refused (flag N) | fscm roleSynchronizations, hcm roles 404; SCIM Roles has no POST | **screen-only** | `migrate-roles-to-paas-identity/STATUS.md` |
| Register URL for the telephony gateway or soft switch for SIP domain (`MCT_MANAGE_TELEPHONY_SIP_DOMAIN`) | neither | refused (flag N) | crm telephonyDomains 404 | **screen-only** | `register-url-for-the-telephony-gateway-or-soft-s/STATUS.md` |
| Set User General Preferences (`FND_SET_USER_GENERAL_PREFERENCES`) | neither | refused (flag N) | userPreferences 404; SCIM Users POST has no language, time zone or date format fields; hcm selfDetails only reads the signed-in user's session | **screen-only** | `set-user-general-preferences/STATUS.md` |
| Set Watchlist Options (`ATK_CUSTOMIZE_WATCHLIST`) | neither | refused (flag N) | watchlistItems 404; no watchlist resource in the Common Features list | **screen-only** | `set-watchlist-options/STATUS.md` |
| View Available Asset Books (`FUN_VIEW_AVAILABLE_ASSET_BOOKS`) | neither | refused (flag N) | fixedAssetBooksLOV GET 200, describe get only (VERIFIED today); setIdAssignmentsAssetBook has POST but assigns a set to a book, it does not create books | **screen-only** | `view-available-asset-books/STATUS.md` |
| Manage Help Content (`ORA_ATK_MANAGE_HELP_CONTENT`) | route only | flag Y, 3 files: package holds the help topic files (ATK_KR_TOPIC 5 rows, ORA_ATK_KR_TITLE 10, ORA_ATK_KR_GRAPHICS 0), BUT a ne | atkhelpcentertopics GET 200, describe: get only (VERIFIED today); 6 other help names 404 (earlier) | **screen-only** | `manage-help-content/STATUS.md` |
| Manage Intercompany Exceptions (`XLE_MANAGE_INTERCOMPANY_EXCEPTIONS`) | route only | flag Y, 7 files: package = legal entity package (7 files: entity, establishment, registrations, address) | Financials endpoint list read: intercompanyAgreements and intercompanyTransactionSourceDocuments are transactions, intercompany*LOV read only; intercompanyExceptions 404  | **screen-only** | `manage-intercompany-exceptions/STATUS.md` |
| Manage Task Configurations for Supply Chain Management (`INV_MANAGE_TASK_CONFIGURATIONS`) | route only | flag Y, 2 files: package = 2 standard lookup files, 0 rows | taskConfigurations 404 (earlier); /bpm/api/4.0/tasks GET 200 but it is runtime worklist tasks, a different object | **screen-only** | `manage-task-configurations-for-supply-chain-mana/STATUS.md` |

## Skill check (every task open, failed or written; no new task started)
| Status | Task | Skill on its card |
|---|---|---|
| open | Manage Cross-Validation Rules | NO (no skill yet) |
| skipped-unsafe | Manage Common CRM Business Unit Profile Options | yes: `manage-crm-bu-profile-options/SKILL.md` |
| skipped-unsafe | Map Reports to Work Areas | yes: `map-reports-to-work-areas/SKILL.md` |
| open | Manage Associated Balancing Segments | NO (no skill yet) |
| open | Publish Account Hierarchies | NO (no skill yet) |
| skipped-unsafe | Manage Archive and Purge Policies | yes: `manage-archive-purge-policies/SKILL.md` |
| open | Establish Enterprise Structures | NO (no skill yet) |
| skipped-unsafe | Manage User-Defined Rules for Project Management | yes: `manage-project-user-defined-rules/SKILL.md` |
| failed | Manage Enterprise Financial Data Export Options for China | yes: `manage-china-financial-data-export-options/SKILL.md` |
| failed | Manage Letter of Intent Limits for Italy | yes: `manage-letter-of-intent-limits-italy/SKILL.md` |
| written-untested | Manage Tax Box Allocation Rules | yes: `manage-tax-box-allocation-rules/SKILL.md` |
| failed | Manage Application Tax Options | yes: `manage-application-tax-options/SKILL.md` |
| open | Create Data Role for Implementation Users | NO (no skill yet) |
| open | Manage Applications Core Messages | NO (no skill yet) |
| open | Manage Messages | NO (no skill yet) |
| skipped-unsafe | Revoke Data Role from Implementation Users | yes: `revoke-data-role-impl-users/SKILL.md` |
| open | Load Geography Interface Data | NO (no skill yet) |
| failed | Manage Partner Organizations | yes: `manage-partner-organizations/SKILL.md` |
| open | Manage Internal Resource Organizations | NO (no skill yet) |
| open | Manage Resource Teams | NO (no skill yet) |
| skipped-unsafe | Run Geography Loader | yes: `run-geography-loader/SKILL.md` |
| open | Manage Messages for General Ledger | NO (no skill yet) |
| open | Manage Indirect Tax Automation with Thomson Reuters | NO (no skill yet) |
| skipped-unsafe | Manage Indirect Tax Automation with Avalara | yes: `manage-avalara-onboarding/SKILL.md` |
| open | Manage Thomson Reuters Services | NO (no skill yet) |
| open | Guided Journeys | NO (no skill yet) |
| skipped-unsafe | Run Jurisdiction and Rates Upload Program | yes: `run-jurisdiction-rates-upload/SKILL.md` |
| open | Manage Tax Geographies | NO (no skill yet) |

Tasks that still need a skill: **15** (all open).

## Counts after this run
| tested | written | failed | screen-only | open | total |
|---:|---:|---:|---:|---:|---:|
| 91 | 9 | 4 | 29 | 15 | 148 |
