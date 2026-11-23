"""Run 18 quick screen (FSCR files only): skill file, readiness file, and other FSCR files that name the candidate
as a dependency. Read-only, local."""
import json,re,os,glob,sys
C=[("AR_MANAGE_RECEIVABLES_PAYMENT_TERMS","Receivables payment terms",r"payment term"),
   ("AP_MANAGE_PAYMENT_TERMS","Payables payment terms",r"payment term"),
   ("FUN_MANAGE_BUSINESS_UNIT","Business units",r"business unit"),
   ("FND_MANAGE_REFERENCE_DATA_SETS","Reference data sets",r"reference data set|SetCode|set code"),
   ("XLE_MANAGE_LEGAL_ENTITY","Legal entities",r"legal entit"),
   ("GL_MANAGE_PRIMARY_LEDGERS","Primary ledgers",r"\bledger"),
   ("GL_MANAGE_ACCOUNTING_CALENDARS","Accounting calendars",r"accounting calendar"),
   ("INV_MANAGE_UNITS_OF_MEASURE","Units of measure",r"unit of measure|units of measure|\bUOM\b"),
   ("FND_MANAGE_CURRENCIES","Currencies",r"currenc"),
   ("GL_MANAGE_CONVERSION_RATE_TYPES","Conversion rate types",r"conversion rate type"),
   ("ZX_MANAGE_TAX_REGIMES","Tax regimes",r"tax regime"),
   ("WSH_MANAGE_CARRIERS","Carriers",r"\bcarrier"),
   ("AR_MANAGE_RECEIVABLES_CUSTOMER_PROFILE_CLASSES","Customer profile classes",r"profile class")]
cat=json.load(open('knowledge/setup-task-catalog/effective/setupTasksAll.json',encoding='utf-8'))
cat=cat if isinstance(cat,list) else cat.get('items') or cat.get('tasks') or list(cat.values())[0]
flags={t['TaskCode']:(t.get('ExportImportSupportedFlag'),t.get('CSVExportImportSupportedFlag')) for t in cat}
files=[f.replace(os.sep,'/') for f in glob.glob('pillars/**/*.md',recursive=True)+glob.glob('shared/**/*.md',recursive=True)+glob.glob('core/**/*.md',recursive=True)]
txt={f:open(f,encoding='utf-8',errors='replace').read() for f in files}
dep=[f for f in files if f.endswith('ora_dependency_readiness.md')]
out=[]
for code,name,rx in C:
    own=[f for f in files if re.search(r'task_code:\s*"?'+code,txt[f])]
    owndir={os.path.dirname(f) for f in own}
    rd=[f for f in dep if os.path.dirname(os.path.dirname(f)) in owndir or os.path.dirname(f).rsplit('/',1)[0] in owndir]
    users=[f for f in dep if re.search(rx,txt[f],re.I) and f not in rd]
    mods=sorted({'/'.join(f.split('/')[1:3]) for f in users})
    out.append(dict(code=code,name=name,flags=flags.get(code),skill=own[:3],readiness=rd[:2],dependents_n=len(users),dependent_modules=mods,dependents=users))
json.dump(out,open(sys.argv[1],'w'),indent=1)
for o in out: print(o['name'].ljust(26),o['flags'],'skill:',(o['skill'] or ['NONE'])[0][:95],'| dep files:',o['dependents_n'],'modules:',len(o['dependent_modules']))
