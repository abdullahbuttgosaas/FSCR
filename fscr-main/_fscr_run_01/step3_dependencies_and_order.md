# Step 3 — Dependencies and creation order

Source column: **FSCR** = stated in an FSCR file (path given); **Own** = my reasoning / Oracle knowledge; **User** = listed in the task brief.

## Dependencies

| # | Dependency | Source | Check planned |
|---|---|---|---|
| 1 | Reference data set ENTERPRISE must exist for BU default set, payment-term set, price-list access set, customer address set ("Enterprise Set") | FSCR (`organization-structures/ora-resource/ora_dependency_readiness.md` seq 1; payment-terms `ora_dependency_readiness.md` seq 2) | GET `setIdSets` |
| 2 | BU: exact-name duplicate lookup before create | FSCR (`manage-business-unit.md` gate 2) | GET business units by name |
| 3 | BU location "Lahore Warehouse" and managers "Smith, Aron", "Yaqub, Younas" must exist | Own | GET locations / workers |
| 4 | Price list needs its BU to exist and be usable by Pricing (may lag) | User (brief); FSCR has nothing on this | GET BU after create; read BU LOV used by pricing if available; retry later |
| 5 | Price list: pricing charge definition "Sale Price", currencies USD/EUR, line type, calculation method must exist | Own | GET `pricingChargeDefinitions`, currencies |
| 6 | Price list access set needs the price list (same FBDI batch, `SOURCE_PRICE_LIST_ID` link) | FSCR (`import-price-lists/SKILL.md` fallback rule 3) | in package |
| 7 | Payment term: current task template + data export; set resolved; split term needs print lead days and tax/freight choice | FSCR (payment-terms `ora_dependency_readiness.md` seq 1, 2, 6) | FSM exports; decisions logged |
| 8 | Lookup codes need their lookup type; one bad code can drop the whole type in an FSM import | User; FSCR lookups skill says read the resource first | REST: create type, read back, then codes one by one |
| 9 | Order types go into existing lookup type ORA_DOO_ORDER_TYPES ("Type of Sales Order"); only add codes, never edit the type | User + FSCR (`manage-order-lookups/SKILL.md` user-extensible list) | GET type first |
| 10 | Disabled records (FREIGHT, SO_WARRANTY_SWAP) must read back `EnabledFlag = N` | User | read-back |
| 11 | Customer class lookup values "Public sector companies", "Federal class" must exist (CUSTOMER CLASS lookup) | Own | GET lookup |
| 12 | Address set CUSTOMER_RDS must exist and be usable for customer account sites | User | GET `setIdSets` |
| 13 | Customer: party → location → party site → account → account site (in set) → site use (address purpose) | Own (TCA model); FSCR customers skill orders "Input and parent consistency" → "Existing-target matching" → "Configured references" | create in order |
| 14 | US geography validation (city/state/postal) may reject addresses | Own; FSCR lists "geography" under configured_references | read errors |
| 15 | Account DFF / site DFF for extra attributes (Key Account, EDI, etc.) — only if such DFF segments exist in the pod | Own; FSCR customers skill: "DFF contexts/segments" conditional | describe resources |
| 16 | Token valid (1 h lifetime, no refresh) and Run Book active | FSCR (router Run Book gate; auth skill) | before each live step |

## Creation order used

1. **Business Units** (first, because a new BU may take time to become usable for pricing).
2. **Lookup types**, then their **lookup codes** (REST, one by one), then **order types** (codes in ORA_DOO_ORDER_TYPES). Independent of BU — done while BU import runs.
3. **Payment terms** (FSM; independent).
4. **Price lists + access sets** (after BU verified).
5. **Organization customers** with addresses, then **person customers**.
6. **Address purposes** (after their customer sites exist).

## Naming (hard rule 2)
Prefix `FSCRT_` on names and codes; meanings, descriptions, site names also prefixed when they are names (decision D6). Length limits checked against live metadata; shortened values are logged in `mapping.csv`.
