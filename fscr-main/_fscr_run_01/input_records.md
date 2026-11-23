THE RECORDS (this is the whole input; there is no workbook to find)
First save this section unchanged as _fscr_run_01\input_records.md. Then work from it.

[1] Business Units (Name | Active | Location | Manager | Default Set)
- Quillon Ridge Outfitters West F01 | Yes | (none) | Smith, Aron | ENTERPRISE
- Brindle Harbor Marine Supply F01 | Yes | Lahore Warehouse | Yaqub, Younas | ENTERPRISE

[2] Price Lists (header only: no items, charges or tiers)
- Name: Quillon Ridge Wholesale Tents USD F01 | Description: Wholesale tent and shelter prices for retail dealers | Type: Segment price list | Currency: USD | Business Unit: Quillon Ridge Outfitters West F01 | Start: 2026-11-03 | End: none | Pricing Charge Definition: Sale Price | Line Type: Buy | Calculation Method: Price
- Name: Brindle Harbor Dock Equipment EUR F01 | Description: Dock and mooring equipment prices for European marinas | Type: Segment price list | Currency: EUR | Business Unit: Brindle Harbor Marine Supply F01 | Start: 2026-11-03 | End: 2027-10-31 | Pricing Charge Definition: Sale Price | Line Type: (default) | Calculation Method: (default)
Price List Access Sets: both price lists get set ENTERPRISE.

[3] Payment Terms
- 2 Percent 10 Net 30 Marine F01 | From 2026-11-03 | To 2028-12-31 | Description: 2 percent off if paid in 10 days, otherwise due in 30 | one line: 100% due in 30 days, first discount 2% if paid within 10 days | Set: ENTERPRISE
- Deposit 25 Balance 75 Alpine F01 | From: today | To: none | Description: 25 percent deposit at 15 days, balance at 60 days | two lines: 25% due in 15 days; 75% due in 60 days | Set: ENTERPRISE

[4] Lookup Types (all User type, Module "Order Management")
- OUTDOOR_ACTIVITY_F01 | Meaning: Outdoor activity F01 | Description: Activities a product is sold for | REST Access Secured: default
- CARRIER_SERVICE_TIER_F01 | Meaning: Carrier service tier F01 | Description: Shipping service levels offered to dealers | REST Access Secured: Authenticated
Lookup Codes (Type | Code | Seq | Enabled | Meaning | Description | Tag):
- OUTDOOR_ACTIVITY_F01 | HIKING | 1 | Yes | Hiking
- OUTDOOR_ACTIVITY_F01 | PADDLING | 2 | Yes | Paddling | Kayak and canoe gear | water
- CARRIER_SERVICE_TIER_F01 | STANDARD | (auto) | Yes | Standard ground
- CARRIER_SERVICE_TIER_F01 | FREIGHT | (auto) | No | Pallet freight

[5] Order Types (lookup type "Type of Sales Order", Manage Order Lookups)
- Code SO_TRAIL_DEALER_F01 | Enabled Yes | Meaning: Trail Dealer Replenishment F01 | Description: Stock refills for trail dealers
- Code SO_WARRANTY_SWAP_F01 | Enabled No | Meaning: Warranty Swap Order F01 | Description: Replacement under warranty

[6] Organization Customers (field: value)
Customer A:
Name: Kestrel Basin Trading Cooperative F01 | D-U-N-S: 204118306 | Taxpayer ID: 84-2210764 | Account Description: Buying cooperative for trail shops | Account Type: External | Customer Class: Public sector companies | Account Established: 2026-11-02 | Account Termination: 2028-12-31 | Account Notes: Net 45 account, seasonal volume orders | Shipping Instructions: Deliver to loading bay B, weekdays 7am to 3pm | Customer Agreement: Two year dealer supply agreement | Account Address Set: Enterprise Set | Address From: 2026-11-02 | Address To: 2028-12-31 | Site Name: Kestrel Basin Depot | Mail Stop: Bay B | Country: United States | Address Line 1: 2210 Pearl Street | Line 2: Unit 5 | City: Boulder | State: CO | Postal Code: 80302 | Responsible Mineral Status: Conflict Free | Address: Cooperative depot | URL: https://www.kestrelbasin.example.com | ContactEmail: buying@kestrelbasin.example.com | Authorizer: Rhea Lindqvist | Supplier Site ID: 4201 | Sales Tax Inside City Limits: Yes | Translated Customer Name: Kestrel Basin Trading Co-op | Key Account: Yes | Trading Partner Identifier: 5502101 | EDI Location Code: KBT-EDI-01
Customer B:
Name: Pemberton Cove Boatworks F01 | D-U-N-S: 428351077 | Taxpayer ID: 36-9054187 | Account Description: Boat builder and chandlery | Account Type: External | Customer Class: Public sector companies | Account Established: 2026-11-03 | Account Termination: 2029-06-30 | Account Notes: Rush orders common in spring | Shipping Instructions: Deliver to the slipway office | Customer Agreement: Marine parts framework agreement | Account Address Set: CUSTOMER_RDS | Address From: 2026-11-03 | Address To: 2029-06-30 | Site Name: Pemberton Cove Yard | Mail Stop: Slip 3 | Country: United States | Address Line 1: 1740 Wynkoop Street | Line 2: Suite 110 | City: Denver | State: CO | Postal Code: 80202 | Responsible Mineral Status: Undetermined | Address: Boatyard office | URL: https://www.pembertoncove.example.com | ContactEmail: purchasing@pembertoncove.example.com | Authorizer: Saoirse Vandenberg | Supplier Site ID: 4203 | Sales Tax Inside City Limits: Yes | Translated Customer Name: Pemberton Cove Boatworks LLC | Key Account: Yes | Trading Partner Identifier: 5502103 | EDI Location Code: PCB-EDI-03

[7] Person Customers (field: value)
Person A:
Prefix: Mr. | First Name: Caspian | Middle Name: Reed | Last Name: Thornbury | Suffix: Jr. | Taxpayer ID: 58-4410237 | Account Description: Independent trail guide | Account Type: External | Customer Class: Public sector companies | Account Established: 2026-11-02 | Account Termination: none | Account Notes: Pays by card at pickup | Shipping Instructions: Hold at front desk | Customer Agreement: Individual gear purchase terms | Account Address Set: Enterprise Set | Address From: 2026-11-02 | Address To: none | Site Name: Thornbury Residence | Mail Stop: Unit 1 | Country: United States | Address Line 1: 1250 N State Street | Line 2: Apt 3B | City: Chicago | State: IL | Postal Code: 60601 | Responsible Mineral Status: Conflict Free | Address: Home address | URL: https://www.thornbury.example.com | ContactEmail: caspian@thornbury.example.com | Authorizer: Caspian Thornbury | Supplier Site ID: 4301 | Sales Tax Inside City Limits: Yes | Translated Customer Name: Caspian R Thornbury | Key Account: No | Trading Partner Identifier: 6603101 | EDI Location Code: CT-EDI-01
Person B:
Prefix: Ms. | First Name: Linnea | Middle Name: none | Last Name: Voskuijlen | Suffix: none | Taxpayer ID: 63-7702158 | Account Description: Kayak instructor | Account Type: External | Customer Class: Federal class | Account Established: 2026-11-02 | Account Termination: 2027-12-31 | Account Notes: Orders paddles twice a year | Shipping Instructions: Leave with neighbour if absent | Customer Agreement: Instructor equipment terms | Account Address Set: Enterprise Set | Address From: 2026-11-02 | Address To: 2027-12-31 | Site Name: Voskuijlen Home | Mail Stop: none | Country: United States | Address Line 1: 88 Beacon Street | Line 2: none | City: Boston | State: MA | Postal Code: 02110 | Responsible Mineral Status: N/A | Address: Home address | URL: https://www.voskuijlen.example.com | ContactEmail: linnea@voskuijlen.example.com | Authorizer: Linnea Voskuijlen | Supplier Site ID: 4302 | Sales Tax Inside City Limits: No | Translated Customer Name: Linnea Voskuijlen | Key Account: No | Trading Partner Identifier: 6603102 | EDI Location Code: LV-EDI-02

[8] Address Purposes (Customer | Primary | Purpose | From)
- Kestrel Basin Trading Cooperative F01 | Yes | Bill to | 2026-11-02
- Kestrel Basin Trading Cooperative F01 | Yes | Ship to | 2026-11-02
- Pemberton Cove Boatworks F01 | Yes | Bill to | 2026-11-03
- Pemberton Cove Boatworks F01 | Yes | Ship to | 2026-11-03
- Caspian Thornbury | Yes | Bill to | 2026-11-02
- Linnea Voskuijlen | Yes | Ship to | 2026-11-02
