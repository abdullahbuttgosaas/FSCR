# Customers: fields for an Excel upload sheet

Read-only report, 2026-10-23. Sources: `Customers/CLAUDE.md`, `Customers/browser_flow.py`
(`FIELDS`, `ORDER`, `PERSON_NAME_FIELDS`, `SPEC`, `SAMPLES`, `parse_requirements`,
`run_request`) and `--spec`. No Oracle screen was opened and nothing was created.

**Two ways in, two different field sets.** This matters for the sheet:
- **Request file** (`customers.json` / command line): all **36** organization fields (35 for a
  person, plus 5 person name fields) and purposes. Unknown keys are refused.
- **Page** (`--run`): only the **25** fields in `--spec`. Any other key (notes, URL, tax,
  EDI, …) is refused as unknown before Oracle is touched.

If the sheet feeds the page, limit it to the "Page" column below. If it feeds the request
file, every row below can be used.

Dropdown source codes:
- **P** = proven by a created and verified customer.
- **S** = only seen in Oracle's list on the screen.
- **A** = the full live list via `python "Customers/browser_flow.py" --options FIELD --all`
  (about 60 s, one visit to the form, nothing saved).
- **NC** = not covered (no live-list option in the script).

## 1. Fields the script fills, in screen order

The order is the script's fill order (`ORDER`), which follows the screen top to bottom.
There is one exception: Country is filled before the address lines because it redraws
them. Sections are as recorded in CLAUDE.md. Where CLAUDE.md names a section only for the
first field of a group, the following fields are assumed to be in the same section
(marked *).

### Organization Information (organization) / Person Information (person)

| Sheet key | Oracle label | Required | Type | Default if empty | Page | Dropdown values (source) |
|---|---|---|---|---|---|---|
| `customer_type` | Customer Type | yes (pre-filled) | dropdown | Organization | yes | Organization, Person (P, A) |
| `name` | Name | **required when** customer_type = Organization; shown only then | text | – | yes | – |
| `duns_number` | D-U-N-S Number | optional; shown when Organization | text | empty | yes | – |
| `taxpayer_id` | Taxpayer Identification Number | optional | text | empty | yes | – |

Person fields: see section 4.

### Account Information

| Sheet key | Oracle label | Required | Type | Default if empty | Page | Dropdown values (source) |
|---|---|---|---|---|---|---|
| `account_description` | Account Description | optional | text | empty | yes | – |
| `account_type` | Account Type | optional | dropdown | empty | yes | External, Internal (External: P by ZZ_TEST_4418; Internal: S; full list A) |
| `customer_class` | Customer Class* | optional | dropdown | empty | yes | Federal class, Public sector companies (S, A) |
| `account_established_date` | Account Established Date* | optional | date | Oracle's today | yes | – |
| `account_termination_date` | Account Termination Date* | optional | date | empty | **no** | – |
| `account_notes_other` | Account Notes Other* | optional | long text | empty | **no** | – |
| `shipping_instructions` | Shipping Instrustions* (Oracle's spelling) | optional | long text | empty | **no** | – |
| `customer_agreement` | Customer Agreement* | optional | long text | empty | **no** | – |

### Account Address

| Sheet key | Oracle label | Required | Type | Default if empty | Page | Dropdown values (source) |
|---|---|---|---|---|---|---|
| `account_address_set` | Account Address Set | **required** | dropdown (name or code) | – | yes | P: Enterprise Set (ENTERPRISE), CUSTOMER_RDS, 001 Customer Site (001 CUSTOMER SITE). 36 sets seen on 2026-10-20 (S, listed in CLAUDE.md). Full list A |
| `address_from_date` | From Date | optional (required on screen, but pre-filled) | date | Oracle's today | yes | – |
| `address_to_date` | To Date | optional | date | empty | **no** | – |

### Address

| Sheet key | Oracle label | Required | Type | Default if empty | Page | Dropdown values (source) |
|---|---|---|---|---|---|---|
| `site_name` | Site Name | optional | text | empty | yes | – |
| `mail_stop` | Mail Stop* | optional | text | empty | **no** | – |
| `country` | Country* | optional | dropdown | United States | yes | United States (P). 250 countries (A); Pakistan saved TESTCUSTOMER3 by request file |
| `address_line_1` | Address Line 1* | optional | text | empty | yes | – |
| `address_line_2` | Address Line 2* | optional | text | empty | yes | – |
| `state` | State* | optional | dropdown (Oracle geography) | empty | yes | CA (P). 105 United States states incl. CA and CALIFORNIA (A; United States only) |
| `city` | City* | optional | text, must exist in Oracle's geography | empty | yes | no list; CUPERTINO proven; stored in capitals |
| `postal_code` | Postal Code* | optional | text, must exist in Oracle's geography | empty | yes | no list; 95014 proven, 94105 not in this pod |
| `responsible_mineral_status` | Responsible Mineral Status* | optional | dropdown (typed, then checked) | empty | **no** | Conflict Free, N/A, No Data, Undetermined (S; NC: no --options) |
| `address_note` | Address* (the extra field under the address) | optional | text | empty | **no** | – |
| `url` | URL* | optional | text | empty | **no** | – |
| `contact_email` | ContactEmail* (Oracle's spelling) | optional | text | empty | **no** | – |
| `authorizer` | Authorizer* | optional | text | empty | **no** | – |
| `supplier_site_id` | Supplier Site ID* | **required** | text | – | yes | free text (section 6) |
| `sales_tax_geocode` | Sales Tax Geocode* | optional | text | empty | **no** | – (not on the screen for Pakistan) |
| `sales_tax_inside_city_limits` | Sales Tax Inside City Limits* | optional | yes/no | **yes** (ticked) | **no** | – |

### Account Address Details

| Sheet key | Oracle label | Required | Type | Default if empty | Page | Dropdown values (source) |
|---|---|---|---|---|---|---|
| `customer_category_code` | Customer Category Code | optional | dropdown | empty | **no** | **the list is empty in this pod** (S); NC |
| `site_language` | Site Language* | optional | dropdown | empty | **no** | 37 languages, e.g. American English, Arabic (S; not all recorded); NC |
| `translated_customer_name` | Translated Customer Name* | optional | text | empty | **no** | – |
| `key_account` | Key Account* | optional | yes/no | no (unticked) | yes | – |
| `trading_partner_identifier` | Trading Partner Identifier* | optional | **number only** | empty | **no** | – |
| `edi_location_code` | EDI Location Code* | optional | text | empty | **no** | – |

### Address Purposes (table)

See section 3.

## 2. Fields the script does NOT fill

- **Every field you named is already filled by the script, through the request file:**
  Customer Category Code, Site Language, Responsible Mineral Status, Trading Partner
  Identifier, Key Account, Translated Customer Name, EDI Location Code, Sales Tax Geocode,
  Sales Tax Inside City Limits and Authorizer. Through the **page**, only Key Account is
  available; the others are refused there as unknown keys.
- **Not filled at all:**

| Field | Needs a value from a list? |
|---|---|
| ~~Bill-to Site on a purpose row~~ | now filled (2026-10-23): see section 3 |
| Business Unit (Edit Site page only, not on Create Customer) | yes. Not covered |
| Manager | not recorded. Not covered |
| More than one account or more than one site per customer | – |

- Other screen fields: CLAUDE.md doesn't record any further fields on Create Customer. Any
  field not listed in section 1 is "not covered"; I didn't open the screen to check.
- **Dropdowns with no live list in the script** (not covered): Customer Category Code (and
  its list is empty in this pod), Site Language (37 values seen, not all recorded),
  Responsible Mineral Status (4 values seen).

## 3. Address purposes

- Sheet keys per purpose: `purpose` (required in each row), `from_date`, `to_date`, and since
  2026-10-23 `primary` (yes/no, empty = no) and `bill_to_site` (text). On the screen these
  are the Address Purposes table columns **Purpose**, **From Date**, **To Date**,
  **Primary** (the Set Primary action) and **Bill-to Site**. The Site number column is
  read-only.
  - Primary: at most one per purpose type. Oracle also makes the first purpose of each type
    Primary by itself when saving.
  - Bill-to Site: only on a Ship to row. It must be one of that customer's Bill to
    addresses, written as Oracle lists it, e.g. `1 Main Street,CUPERTINO, CA 95014`.
  - Both fields work on the page and in the request file.
- Allowed values (18; S; full list `--options purposes.purpose --all`): Acknowledgments,
  Bill to, Bills of lading, Correspondence, Credit contact, Credit memos, Deliver to,
  Drawee, Dunning, Installed at, Invoices, Late charges, Legal, Self service user, Ship to,
  Sold to, Statements, Subscription Location. Proven (P): Bill to, Ship to.
- How many: 0 or more. The script sets no limit, but each purpose may appear **only once**
  per customer ("a purpose is listed twice" is refused). So the maximum is 18, all on the
  one site. The most proven in one customer is 2 (Bill to + Ship to).
- Dates:
  - Format `YYYY-MM-DD` or `today`.
  - `today` means **Oracle's today minus one day**, read from the form, never the PC clock.
  - From Date empty: Oracle fills it in (shown on the form). To Date empty: stays empty.
  - **A purpose's dates must lie within the address dates.** A purpose cannot start before
    `address_from_date`, which is Oracle's today when left empty. Oracle refuses the save
    otherwise (HZ-120150, nothing saved). So a purpose from `today` (Oracle's today minus
    one) also needs `address_from_date` on or before that day.
  - Page date rules: an end date must be after Oracle's today and after its start; a start
    later than Oracle's today is allowed ("won't be active until …").
  - On the form, an earlier purpose row may briefly show To Date 12/31/4712; after the save
    it is empty.

## 4. Person customers

- `customer_type` = Person turns the form into **Create Person Customer**. The **Person
  Information** section replaces Name and D-U-N-S Number. Everything else is identical.

| Sheet key | Oracle label | Required | Type | Default if empty | Values |
|---|---|---|---|---|---|
| `prefix` | Prefix | optional | dropdown | empty | Mr., Mrs., Ms. (Ms.: P; all three S; A) |
| `first_name` | First Name | **required for a person** (the only person field with an asterisk) | text | – | – |
| `middle_name` | Middle Name | optional | text | empty | – |
| `last_name` | Last Name | optional (not required) | text | empty | – |
| `suffix` | Suffix | optional | text (free, e.g. Jr.) | empty | – |

- Taxpayer ID and every account, address and purpose field apply to persons too.
- **Not for a person:** `name` and `duns_number`. Both are refused ("D-U-N-S number doesn't
  apply to a person customer."). The reverse also holds: prefix, middle, last name and
  suffix are refused for an organization.
- The customer name Oracle stores is "First Middle Last Suffix" (e.g. "ZZ_TEST_9231 Q
  Tester Jr."). The prefix isn't part of the name. That combined name is what is checked
  for duplicates.
- The page path for persons: the checks were tried, but a person save through the page
  hasn't been tried yet. Person saves are proven through the request file (ZZ_TEST_4055,
  ZZ_TEST_9231).

## 5. Read-only in Oracle: keep out of the sheet

Registry ID, Account Number, Site Number, and the purpose rows' Site number. Oracle
assigns them when the form opens. The script reports the Registry ID in its result.

## 6. Supplier Site ID

- Free text on the screen: no list, no format check seen. It is used exactly as given:
  not empty, no leading or trailing spaces.
- Values accepted in created customers: 12345, 1001, 1002, 2001, 2002, 3001, 3008, 3010
  (e.g. **3010** = ZZ_TEST_4418, **3008** = ZZ_TEST_2336).
- All used values are digits. Letters or symbols have never been tried, so the safe format
  is digits only. No uniqueness check has been seen: the same ID wasn't reused in the tests.
- Oracle marks it required at save ("Supplier Site ID: You must enter a value").

## 7. Things a sheet could get wrong

- **Page vs request file:** the page refuses the 18 extra fields (section 1, Page = no).
- **Type-dependent fields:** Name and D-U-N-S only for Organization; First Name (required)
  and Prefix/Middle/Last/Suffix only for Person. Mixing them is refused.
- **Duplicates:** an existing customer with the same name (case-insensitive) is skipped,
  never changed. The same name twice in one upload is refused. Oracle itself allows
  duplicate names (three "ABC" exist).
- **Geography must already exist in Oracle:** State, City and Postal Code must be places
  Oracle knows, and are checked in that order (each narrows the next). City is stored in
  capitals. "CA" matches both CA and CALIFORNIA; the script picks the exact one. 94105 is
  not in this pod. A missing place can't be created; the run stops with nothing saved.
- **Country:** the page offers only United States, and its State list holds only United
  States states, so another country's state is refused there. Through the request file
  another country works (Pakistan proven): its address fields redraw, and Pakistan has
  no Sales Tax Geocode field. Leave that column empty for non-US addresses.
- **Trading Partner Identifier:** numbers only ("The value must be a number").
- **Yes/no:** must be true/false (page: yes/no). Sales Tax Inside City Limits defaults to
  **yes**, so an empty cell means ticked.
- **Dates:** `YYYY-MM-DD` or `today` only, and Excel date cells must be exported as that
  text. Purpose dates must lie within the address dates (section 3).
- **Dropdown spelling:** a value must match Oracle's list exactly, or case-insensitively
  when that match is unique; nothing is guessed. Account Address Set accepts the name or
  the code. Watch Oracle's own spellings: "Shipping Instrustions", "ContactEmail".
- **Customer Category Code:** its list is empty in this pod, so any value will be refused.
- **Text cells:** no leading or trailing spaces, and no empty strings (leave the cell
  blank instead).
- **One customer = one account + one site.** One upload row can't hold several sites or
  accounts.
