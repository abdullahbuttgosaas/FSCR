# Run 36: assignment rules (data only). Every rule carries its reason; build.py applies them in this order:
#   1. TASK_OVERRIDE (named tasks)            2. Run 29 Common Features rule (ORA_ASK_ area in an ERP offering)
#   3. ORA_ASK_ area in a non-ERP offering -> Common Features (shared setup), unless 1 applies
#   4. FAMILY rule (task-code product prefix, optional name pattern)   5. AREA vote (area_to_row)
#   6. no offering and no family rule -> Unmapped
CF, SEC, GL, AP, AR, CM, FA, EXP, REV, PFM, PUR = ('Common Features', 'Security', 'General Ledger', 'Payables',
    'Receivables', 'Cash Management', 'Fixed Assets', 'Expenses', 'Revenue Management', 'Project Financial Management', 'Purchasing')
GHR, ABS, TL, PAY, BEN, WC, PGM, TRS, REC, LRN = ('Global HR', 'Absence Management', 'Time and Labor', 'Global Payroll', 'Benefits',
    'Workforce Compensation', 'Performance and Goal Management', 'Talent Review and Succession', 'Recruiting', 'Learning')
PRC, SSM, INV, OM, MFG, CST, SP, MNT, TMS, GTM, PH, PD, QM = ('Procurement', 'Sourcing and Supplier Management',
    'Inventory Management', 'Order Management', 'Manufacturing', 'Cost Management', 'Supply Planning', 'Maintenance',
    'Logistics - Transportation Management', 'Logistics - Global Trade Management', 'PLM - Product Hub',
    'PLM - Product Development', 'PLM - Quality Management')
UNM = 'Unmapped'
ROWS = [('ERP', r) for r in (CF, SEC, GL, AP, AR, CM, FA, EXP, REV, PFM, PUR)] + \
       [('HCM', r) for r in (GHR, ABS, TL, PAY, BEN, WC, PGM, TRS, REC, LRN)] + \
       [('SCM', r) for r in (PRC, SSM, INV, OM, MFG, CST, SP, MNT, TMS, GTM, PH, PD, QM)]
ORDER = [r for _, r in ROWS] + [UNM]

# ---- 1. named task overrides (code -> (row, reason))
_INVORG = 'inventory organization setup: configures Inventory Management (Run 34 lesson), not shared ERP setup'
_FAC = 'facility (plant/warehouse) calendar used by inventory and manufacturing organizations'
TASK_OVERRIDE = {
    'INV_MANAGE_INVENTORY_ORGANIZATIONS': (INV, _INVORG),
    'ORA_FUN_MANAGE_INVENTORY_ORGANIZATION_DATA_ACCESS_FOR_USERS': (INV, _INVORG),
    'PO_MANAGE_INVENTORY_ORG_LOCATIONS': (INV, _INVORG),
    'RCS_MANAGE_FACILITY_SCHEDULES': (INV, _FAC), 'RCS_MANAGE_FACILITY_SCHEDULE_EXCEPTIONS': (INV, _FAC),
    'RCS_MANAGE_FACILITY_SHIFTS': (INV, _FAC), 'RCS_MANAGE_FACILITY_WORKDAY_PATTERNS': (INV, _FAC),
    'ORA_RCS_SEARCH_FACILITY_SCHEDULES': (INV, _FAC),
    'EGP_MANAGE_ITEM_ORGANIZATIONS': (PH, 'item organizations hold item master data for Product Hub'),
    'POZ_MANAGE_SUPPLIER_USER_ROLES': (SSM, 'supplier portal user roles: supplier setup'),
    'POZ_MANAGE_SUPPLIER_USER_ROLE_USAGES': (SSM, 'supplier portal user roles: supplier setup'),
    'PER_MANAGE_PERSON_TYPES': (GHR, 'person types are HCM core person setup'),
    'ORA_MANAGE_ATOM_FEEDS': (GHR, 'HCM Atom feeds publish HCM person/employment events'),
    'ORA_FFS_RUN_RESOURCE_TYPE_PREPARATION_PROCESS': (UNM, 'Field Service (CX); no tracker row'),
    'ORA_MANAGE_SALES_AND_SERVICE_ACCESS': (UNM, 'CX Sales and Service access; no tracker row'),
    'ZPM_IMPORT_PARTNER_USERS': (UNM, 'CX Partner Relationship Management users; no tracker row'),
    'ORA_MANAGE_APPROVAL_GROUPS': (CF, 'BPM approval groups are shared by every module'),
    'INV_MANAGE_TASK_CONFIGURATIONS': (CF, 'BPM task configuration for SCM approvals: an application extension (catalog area Application Extensions)'),
    'ORA_MANAGE_PROFILE_ITEM_CATALOG': (GHR, 'HCM profile content catalogs (talent profiles), not product catalogs'),
    'ORA_MANAGE_DIGITAL_ASSISTANT': (CF, 'digital assistant is a cross-application extension'),
    'ORA_MANAGE_COST_ACCOUNTING_PROFILE_OPTIONS': (CST, 'cost accounting profile options'),
    'ORA_MANAGE_RECEIPT_ACCOUNTING_PROFILE_OPTIONS': (CST, 'receipt accounting is part of Cost Management'),
    'ORA_MANAGE_ITEM_SPECIFIC_UOM_CONVERSIONS': (INV, 'units of measure conversions are inventory master data'),
    'ORA_MANAGE_UNIT_OF_MEASURE_CLASSES': (INV, 'units of measure classes are inventory master data'),
    'ORA_MANAGE_SUPPLIER_BANK_ACCOUNT_DESCRIPTIVE_FLEXFIELDS': (SSM, 'supplier bank account fields are supplier setup'),
    'HRW_ESTABLISH_ENTERPRISE_STRUCTURES': (CF, 'enterprise structures are shared setup'),
}

# ---- 4. family rules: prefix (ORA_ stripped) -> row or list of (name regex, row) checked in order, last item default.
F = 'task-code product family'
FAMILY = {
    # ERP
    'GL': GL, 'FUN': GL, 'XLA': GL, 'ATTRIBUTE': GL, 'XCC': GL, 'FV': GL, 'FIN': GL, 'JV': GL,
    'XLE': CF, 'ZX': CF, 'JE': CF,
    'AP': AP, 'AR': AR, 'IEX': AR, 'ARB': AR, 'HZ': AR, 'JL': AR,
    'IBY': [(r'Funds Capture|Credit Card|Internal Payees', AR), (None, AP)],
    'CE': CM, 'FA': FA, 'FLA': FA, 'EXM': EXP, 'VRM': REV,
    'PJF': PFM, 'PJC': PFM, 'PJB': PFM, 'PJO': PFM, 'PJS': PFM, 'PJT': PFM, 'PJR': PFM, 'PJE': PFM, 'GMS': PFM,
    'POZ': SSM, 'PON': SSM, 'POQ': SSM, 'POR': PRC, 'CMK': PRC,
    'FND': CF, 'ATK': CF, 'FTA': CF, 'VISUAL': CF, 'MCT': CF,
    'ASE': SEC, 'ASXS': SEC, 'GTG': SEC,
    # HCM
    'PER': GHR, 'HRX': GHR, 'HRC': GHR, 'HMO': GHR, 'HCM': GHR, 'HRT': GHR, 'DOCUMENT': GHR,
    'PAY': PAY, 'SUPPLEMENTAL': PAY, 'COSTING': PAY, 'HRY': PAY,
    'BEN': BEN, 'BENEFIT': BEN, 'CMP': WC, 'CMS': WC, 'COMPENSATION': WC, 'ANC': ABS,
    'HWM': TL, 'HXT': TL, 'HTS': TL, 'IRC': REC, 'HRA': PGM, 'HRG': PGM, 'HRR': TRS, 'HRM': TRS,
    # SCM
    'INV': INV, 'INVENTORY': INV, 'LOT': INV, 'PICKING': INV, 'PICK': INV, 'UNITS': INV, 'CONSUMPTION': INV,
    'MATERIAL': INV, 'INTERORGANIZATION': INV, 'INTERSUBINVENTORY': INV, 'LABEL': INV, 'ACCOUNT': INV,
    'ADVANCED': INV, 'RCV': INV, 'RECEIVING': INV, 'WSH': INV, 'SHIPPING': INV, 'SHIP': INV, 'RELEASE': INV, 'ITEM': INV,
    'TRANSPORTATION': TMS,
    'RCS': [(r'Plant|Manufactur', MFG), (r'Expenditure Type|Project', CST), (r'Contract Manufacturing|Intercompany and Contract', MFG), (None, INV)],
    'CST': CST, 'CML': CST, 'FOS': CST, 'PROFIT': CST,
    'DOO': OM, 'FOM': OM, 'QP': OM, 'RESERVATION': OM, 'CJM': OM,
    'WIS': MFG, 'WIE': MFG, 'WIP': MFG, 'REDWOOD': MFG,
    'MNT': MNT, 'CSE': MNT, 'ASSET': MNT, 'MAINTENANCE': MNT,
    'MSC': SP, 'DOS': SP, 'VCS': SP,
    'EGP': [(r'Structure', PD), (r'Create Supplier in Procurement', SSM), (None, PH)],
    'EGO': [(r'Change|Structure|Component', PD), (None, PH)],
    'EGI': PH, 'PD': PH,
    'ACA': PD, 'ACD': PD, 'ACE': PD, 'ACN': PD,
    'ENQ': QM, 'PLM': QM,
    'JMF': GTM, 'INTRASTAT': GTM,
    # no tracker row
    'SUS': UNM, 'RCL': UNM, 'HNS': UNM, 'RATE': UNM, 'UER': UNM, 'EWM': UNM, 'CZ': UNM,
    'PSC': UNM, 'PSCR': UNM, 'OPAL': UNM, 'SVC': UNM, 'CSO': UNM, 'MKT': UNM, 'MKL': UNM, 'MOO': UNM, 'MOT': UNM,
    'MOW': UNM, 'ZCH': UNM, 'ZCQ': UNM, 'ZBS': UNM, 'ZSF': UNM, 'ZPM': UNM, 'ZCM': UNM, 'ZCC': UNM, 'ZOE': UNM,
    'ZEM': UNM, 'ZMM': UNM, 'LOY': UNM, 'OSS': UNM, 'CN': UNM, 'FFS': UNM, 'QSC': UNM, 'CPQ': UNM, 'FOD': UNM,
    'FMK': UNM, 'HEA': UNM, 'HEQ': UNM, 'HER': UNM, 'HES': UNM, 'HEY': UNM, 'HED': UNM,
}
FAMILY_REASON = {
    GL: 'General Ledger product family (GL, intercompany FUN, subledger accounting XLA, budgetary control XCC, federal FV, joint venture FIN/JV)',
    CF: 'shared setup family (legal entities XLE, tax ZX/JE, application extensions FND/ATK)',
    AR: 'customer-side family (AR, collections IEX, bill management ARB, trading community HZ customer model, Brazil collections JL)',
    AP: 'Payables / disbursement family', CM: 'Cash Management (CE bank) family', FA: 'Assets / lease accounting family',
    EXP: 'Expenses (EXM) family', REV: 'Revenue Management (VRM) family', PFM: 'Projects (PJ*) and Grants (GMS) family',
    SSM: 'supplier, sourcing and qualification family (POZ, PON, POQ)', PRC: 'requisitioning (POR) and B2B messaging (CMK) family',
    SEC: 'security console / advanced controls family (ASE, ASXS, GTG)', GHR: 'HCM core person and HR family (PER, HRX, HRC, HRT)',
    PAY: 'payroll family (PAY)', BEN: 'benefits family (BEN)', WC: 'compensation family (CMP, CMS)', ABS: 'absence family (ANC)',
    TL: 'time and labor / scheduling family (HWM, HXT, HTS)', REC: 'recruiting family (IRC)', PGM: 'performance and goals family (HRA, HRG)',
    TRS: 'talent review and succession family (HRR, HRM)', INV: 'inventory, receiving, shipping and facility family (INV, RCV, WSH, RCS)',
    TMS: 'transportation schedules', CST: 'costing family (CST, CML landed cost, FOS financial orchestration)',
    OM: 'order and pricing family (DOO, FOM, QP, CJM)', MFG: 'manufacturing family (WIS, WIE, REDWOOD, RCS plant)',
    MNT: 'maintenance family (MNT, CSE)', SP: 'planning and supply orchestration family (MSC, DOS, VCS)',
    PH: 'item master / product hub family (EGP, EGO items, EGI)', PD: 'product development family (ACA, EGO change orders and structures)',
    QM: 'quality family (ENQ, PLM workflows)', GTM: 'trade reporting family (JMF Intrastat)',
    UNM: 'family with no tracker row (CX, Public Sector, Student, Service Logistics, Sustainability, EHS)',
}

# ---- 5. area map: offering default, then per-area override. reason text is written to area_to_row.csv
OFFERING_DEFAULT = {
    'XLE_FINANCIALS_JUR': (GL, 'Financials offering; module area overrides below'),
    'XLE_FIN_CONTROL_JUR': (GL, 'Fusion Accounting Hub configures ledgers and subledger accounting'),
    'PJF_PROJ_MNG': (PFM, 'Project Financial Management offering'),
    'PJT_PROJECT_EXECUTION_MGMT': (PFM, 'Project Execution is part of Projects; tracker has only Project Financial Management'),
    'ORA_GMS_GRANTS_MANAGEMENT': (PFM, 'Grants Management is built on Projects'),
    'ORA_RISK_AND_CONTROLS': (SEC, 'Risk and Security (advanced access controls)'),
    'PO_PROCUREMENT': (PRC, 'Procurement offering (Run 32 tags)'),
    'ORA_MANUFACTURING_AND_SUPPLY_C': (INV, 'Manufacturing and Supply Chain Materials Management; area overrides below'),
    'DOO_ORCHESTRATION': (OM, 'Order Management offering'),
    'PIM_PROD_MNG': (PH, 'Product Management offering = Product Hub; area overrides below'),
    'ORA_MSC_VALUE_CHAIN_PLANNING': (SP, 'Supply Chain Planning offering'),
    'ORA_GLOBAL_HUMAN_RESOURCES': (GHR, 'Global Human Resources offering'), 'ORA_HCM_SECURITY': (SEC, 'HCM Security offering: security profiles and data roles'),
    'CUSTOM_HCM_TOOL': (GHR, 'HCM tools (profiles, questionnaires, approvals) are HCM common'),
    'ORA_IRC_HCM_COMMUNICATE': (GHR, 'HCM Communicate is employee communication'),
    'ORA_WORKFORCE_ABSENCE_MANAGEMENT': (ABS, 'Absence offering'), 'ORA_WORKFORCE_TIME_MANAGEMENT': (TL, 'Time offering'),
    'ORA_WORKFORCE_SCHEDULING_MANAGEMENT': (TL, 'Workforce scheduling sits with Time and Labor'),
    'ORA_GLOBAL_PAYROLL': (PAY, 'Global Payroll offering'), 'ORA_BENEFITS_CONFIG': (BEN, 'Benefits offering'),
    'ORA_COMPENSATION': (WC, 'Compensation offering'), 'ORA_PERFORMANCE_MANAGEMENT': (PGM, 'Performance offering'),
    'ORA_GOAL_MANAGEMENT': (PGM, 'Goal offering'), 'ORA_TALENT_REVIEW_SETUP': (TRS, 'Talent Review offering'),
    'ORA_SUCCESSION_MANAGEMENT': (TRS, 'Succession offering'), 'ORA_RECRUITING': (REC, 'Recruiting offering'),
    'ORA_LEARNING_MANAGEMENT': (LRN, 'Learning offering'),
}
NO_ROW = 'offering has no tracker row (CX, Public Sector or Student Management)'
AREA_OVERRIDE = {
    'ORA_FUN_BANKING_CONFIGURATIONS': (CM, 'bank configurations'), 'ORA_CE_CASH_MGMT_BANK': (CM, 'Cash Management'),
    'ORA_FIN_ARB_BILL_MANAGEMENT': (AR, 'customer bill presentment'), 'FIN_COLLECTIONS_DEPLOYED': (AR, 'collections of customer receivables'),
    'ORA_FIN_CUST_BILL': (AR, 'customer billing'), 'ORA_FIN_CUSTOMER_PAYMENTS': (AR, 'customer receipts'),
    'ORA_EGP_CUSTOMER': (AR, 'customer model; SCM/GL/RCS tasks listed here go by family'),
    'FIN_RECEIVABLES_DEPLOYED': (AR, 'Receivables'), 'ORA_CRM_RESOURCES': (AR, 'resources used as salespersons/collectors in Financials'),
    'FIN_EXPENSES_DEPLOYED': (EXP, 'Expenses'), 'ORA_FIN_REPORT_CENTER': (GL, 'GL financial reporting'),
    'FIN_FIXED_ASSETS_DEPLOYED': (FA, 'Assets'), 'ORA_FLA_LEASE_ACCOUNTING': (FA, 'lease accounting books right-of-use assets'),
    'ORA_FIN_GENERAL_LEDGER': (GL, 'General Ledger'), 'FIN_INTERCOMPANY_DEPLOYED': (GL, 'intercompany posts to GL'),
    'ORA_FIN_JV_JOINT_VENTURE': (GL, 'joint venture cost distribution from GL'), 'ORA_XCC_PUBLICSECTOR': (GL, 'budgetary control in GL'),
    'ORA_FV_US_FEDERAL_FINANCIALS': (GL, 'federal financials extend GL'), 'ORA_FIN_ACCOUNT_TRANSFORM': (GL, 'accounting hub'),
    'FIN_PAYABLES_DEPLOYED': (AP, 'Payables'), 'ORA_FIN_PAYMENTS': (AP, 'disbursements'),
    'ORA_VRM_REVENUE_MANAGEMENT': (REV, 'Revenue Management'), 'ORA_FIN_REV_REC': (REV, 'revenue recognition'),
    'FIN_APPLICABILITY_ZX': (CF, 'Transaction Tax is shared by Payables, Receivables, Procurement and Projects'),
    'ORA_EGP_FA_ITEMS': (PH, 'item master setup'),
    # Procurement (Run 32 tags kept)
    'ORA_PO_PURCHASING_FOUNDATION': (PUR, 'Run 32 tag Purchasing'), 'ORA_PO_PURCHASING_CAT_FA': (PUR, 'Run 32 tag Purchasing'),
    'ORA_EXTERNAL_PURCHASE_PRICES': (PUR, 'Run 32 tag Purchasing'),
    'ORA_PO_PROC_FOUNDATION_FA': (PRC, 'Run 32 tag Procurement'), 'ORA_PO_APPROVAL_MANAGEMENT_FA': (PRC, 'Run 32 tag Procurement'),
    'ORA_PO_PRC_TRX_ACC_RULES_FA': (PRC, 'Run 32 tag Procurement (its XLA tasks go to General Ledger by family)'),
    'PO_SSP_DEPLOYED': (PRC, 'Run 32 tag Procurement'), 'OKC_PROC_CONTRACTS_ENABLED': (PRC, 'Run 32 tag Procurement'),
    'ORA_PO_COMPLIANCE_CHECKLISTS_FA': (PRC, 'Run 32 tag Procurement'),
    'ORA_EGP_SUPPLIERS': (SSM, 'supplier model; the inventory org, GL, legal entity, TCA tasks listed here go by family (Run 34)'),
    'PO_SOURCING_DEPLOYED': (SSM, 'Run 32 tag Sourcing and Supplier Management'),
    'ORA_PO_QUALIFICATION_DEPLOYED': (SSM, 'Run 32 tag Sourcing and Supplier Management'),
    'PO_SUP_PORTAL_DEPLOYED': (SSM, 'Run 32 tag Sourcing and Supplier Management'),
    'ORA_EGP_SUPPLIER_FOR_PIM': (SSM, 'suppliers referenced by product data'),
    'ORA_CJM_SUPPLIER_INCENTIVES': (PRC, 'supplier rebates; Run 32 left it out (borderline)'),
    'ORA_SUS_SUSTAINABILITY': (UNM, 'Sustainability (emissions) has no tracker row'),
    'WSH_ENABLE_RECEIVING': (INV, 'receiving is inventory logistics'), 'CMR_RECEIPT_ACCOUNTING': (CST, 'receipt accounting is Cost Management'),
    # Manufacturing and SCM materials
    'ORA_ADVANCED_INVENTORY_MANAGEMENT': (INV, 'inventory'), 'ORA_WSH_INVENTORY_MGMT': (INV, 'inventory'),
    'ORA_RCS_FACILITIES': (INV, 'inventory organizations and facilities'),
    'ORA_RCS_CARRIERS_TRANSIT_TIMES': (INV, 'carriers and transit times serve shipping in Inventory Management'),
    'WSH_ENABLE_SHIPPING': (INV, 'shipping is inventory logistics'),
    'CST_DEFINE_COST_MANAGEMENT': (CST, 'cost accounting'), 'CST_COST_AND_PROFIT_PLANNING': (CST, 'cost planning'),
    'ORA_CML_LANDED_COST_MGMT': (CST, 'landed cost'), 'ORA_FOS_SUPPLY_CHAIN_FIN_FLOW': (CST, 'transfer pricing and financial flows'),
    'JMF_INTRASTAT': (GTM, 'Intrastat trade reporting'), 'ORA_MNT_MGMT': (MNT, 'maintenance'),
    'ORA_WIS_COMMON_MFG_WORK_SETUP': (MFG, 'manufacturing master data'),
    'ORA_ENQ_PRODUCT_RECALL_MANAGEMENT': (INV, 'recall of on-hand inventory'), 'ORA_RCL': (UNM, 'Service Logistics has no tracker row'),
    'EGO_ADVANCED_PRODUCT_STRUCT': (PD, 'item structures (engineering BOM)'),
    'ORA_VCS_SUPPLY_COLLABORATION': (SP, 'supply collaboration on forecasts'), 'ORA_DOS_SUPPLY_CHAIN_ORCH': (SP, 'supply orchestration'),
    'ORA_EGP_FA_CATALOGS': (PH, 'item catalogs'),
    # Order Management
    'ORA_FOM_CHANNEL_REV_MGMT': (OM, 'channel revenue (customer side)'), 'ORA_DOO_ORDER_FULLFILLMENT': (OM, 'orders'),
    'ORA_FOM_PRICING': (OM, 'pricing'),
    # Product Management
    'ORA_ACD_CONCEPT_DESIGN_MGMT': (PD, 'innovation'), 'ORA_ACA_PROD_DEV': (PD, 'product development'),
    'ORA_ACE_PRODUCT_PORTFOLIO': (PD, 'portfolio'), 'ORA_ACN_PROD_RQMNTS_IDEA': (PD, 'requirements and ideation'),
    'EGO_CHANGE_ORDERS': (PD, 'engineering change orders'), 'ORA_ENQ_QUALITY_ISSUE_ACTION': (QM, 'quality issues'),
    'ORA_EGP_FA_INVENTORY_ORGANIZAT': (INV, 'inventory organizations'), 'ORA_EGP_FA_ITEM_ORGANIZATIONS': (PH, 'item organizations'),
    # contracts
    'OKC_PROJECT_CONTRACTS': (PFM, 'project contracts'),
}
OKC_TIE = PRC   # OKC task in both Procurement Contracts and Project Contracts: Run 32 precedent

# ---- borderline list (written to sensitivity.csv); kind = area|family|task, key, alternative row, note
SENSITIVITY = [
    ('area', 'ORA_ASK_INITIAL_USER', SEC, 'Run 29 kept Initial Users in Common Features; tracker has a Security row'),
    ('area', 'ORA_ASK_USERS_AND_SECURITY', SEC, 'Run 29 kept Users and Security in Common Features; tracker has a Security row'),
    ('area', 'ORA_ASK_FIN_REPORTING_STRUCT', GL, 'chart of accounts, calendars and ledgers; Run 29 flagged that some teams count them under GL'),
    ('area', 'ORA_ASK_WORKFORCE_STRUCTURE', GHR, 'departments and jobs are HCM objects (Run 29 flag)'),
    ('area', 'ORA_ASK_ORGANIZATION_STRUCTURE', UNM, 'CX resource and partner organizations stay in Common Features; no CX row'),
    ('area', 'FIN_APPLICABILITY_ZX', AP, 'tax could sit with Payables/Receivables; Run 29 did not count it'),
    ('family', 'XLA', CF, 'subledger accounting rules are shared by every subledger; Procurement Transaction Account Rules (Run 32: Procurement) move here'),
    ('family', 'HZ', CF, 'trading community model is shared by customers and suppliers'),
    ('family', 'FUN', CF, 'intercompany FUN tasks; BU tasks already Common Features'),
    ('family', 'FND', UNM, 'FND lookups/profiles listed only in HCM or CX common areas'),
    ('family', 'HRT', TRS, 'talent profiles feed performance, talent review and succession'),
    ('family', 'IRC', GHR, 'HCM Communicate (employee communications) uses IRC codes'),
    ('family', 'CMK', OM, 'B2B collaboration messaging also serves inbound sales orders; Run 32 had them in Sourcing and Supplier Management'),
    ('family', 'CJM', PRC, 'supplier incentives share CJM codes with channel revenue'),
    ('family', 'FOS', INV, 'supply chain financial orchestration could be Inventory or Order Management'),
    ('family', 'DOS', INV, 'supply chain orchestration executes inventory transfers'),
    ('family', 'VCS', SSM, 'supply collaboration is with suppliers'),
    ('family', 'FLA', GL, 'lease accounting'), ('family', 'FV', UNM, 'US Federal Financials'), ('family', 'FIN', UNM, 'Joint Venture Management'),
    ('family', 'GMS', UNM, 'Grants Management is its own product'), ('family', 'PJT', UNM, 'Project Execution Management (not financial)'),
    ('family', 'PJR', UNM, 'Project Resource Management (not financial)'),
    ('family', 'WSH', TMS, 'shipping and carriers could be read as transportation'),
    ('family', 'RCV', PUR, 'receiving could be read as purchasing'), ('family', 'JMF', UNM, 'Intrastat is not Oracle Global Trade Management'),
    ('family', 'EGP', INV, 'items and catalogs; Run 32 counted Purchasing Categories (EGP) under Purchasing'),
    ('family', 'RCL', INV, 'service logistics parts inventory'), ('family', 'SUS', PRC, 'sustainability appears in the Procurement offering'),
    ('family', 'GTG', UNM, 'advanced access controls is a separate product'),
    ('family', 'IBY', AR, 'shared payment setup (formats, payment systems) could be Receivables'),
    ('family', 'HNS', GHR, 'Environment, Health and Safety'),
    ('offering', 'ORA_WORKFORCE_SCHEDULING_MANAGEMENT', UNM, 'workforce scheduling is a separate product'),
    ('area', 'ORA_ENQ_PRODUCT_RECALL_MANAGEMENT', QM, 'recall could be quality'),
    ('area', 'ORA_CJM_SUPPLIER_INCENTIVES', UNM, 'Run 32 left it out of scope'),
    ('task', 'INV_MANAGE_INVENTORY_ORGANIZATIONS', CF, 'Run 29 counted it in Common Features (Organization Structures)'),
    ('task', 'EGP_MANAGE_ITEM_ORGANIZATIONS', INV, 'item organizations are organizations'),
    ('rule', 'OKC tie (Procurement Contracts and Project Contracts)', PFM, 'contract setup shared by procurement and project contracts'),
    ('rule', 'no offering, no family rule', 'any', 'task in no enabled offering; product unclear from code alone'),
]

# ---- overrides added after the first run (area vote picked a wrong row, or task had no offering but a clear product)
TASK_OVERRIDE.update({
    'PO_MANAGE_PROCUREMENT_AGENTS': (PRC, 'procurement agents (buyers) are Procurement setup; area vote tied 4 ways'),
    'ORA_EDR_ELECTRONIC_SIGN_PREF': (INV, 'SCM electronic-records preferences; listed with inventory organization setup (Customers, Suppliers, Item Organizations, Facilities)'),
    'ORA_MANAGE_CANDIDATE_DIMENSION_SOURCE_NAMES': (REC, 'candidate data is Recruiting'),
    'ORA_PO_CONFIGURE_ELECTRONIC_SIGNATURE': (PRC, 'no offering; procurement document signatures'),
    'ORA_PO_MANAGE_SPECIAL_HANDLING_TYPES': (PRC, 'no offering; purchasing document special handling'),
    'ORA_CREATE_JOINT_VENTURE_SYSTEM_OPTIONS_IN_SPREADSHEET': (GL, 'no offering; joint venture (same row as Joint Venture Management area)'),
    'ORA_CREATE_INVOICING_PARTNERS_IN_SPREADSHEET': (GL, 'no offering; joint venture invoicing partners'),
    'ORA_MANAGE_HCM_ALERTS': (GHR, 'no offering; HCM alerts'),
    'ORA_MANAGE_HCM_SEARCH_ACL_REGENERATION_EXCLUSION_RULES': (GHR, 'no offering; HCM search'),
    'ORA_MANAGE_INVENTORY_DOCUMENT_OUTPUT_PREFERENCES': (INV, 'no offering; inventory documents'),
    'ORA_MANAGE_MOVEMENT_REQUEST_APPROVAL': (INV, 'no offering; inventory movement requests'),
})
SENSITIVITY.append(('task', 'ORA_EDR_ELECTRONIC_SIGN_PREF', CF, 'e-records preferences are shared by SCM and PLM'))
SENSITIVITY.append(('rule', 'ORA_ASK_ area in a non-ERP offering only', 'family row (e.g. HZ resources -> Receivables, ATK -> Common Features)', 'outside Run 29 scope; sent to Common Features as shared setup'))
