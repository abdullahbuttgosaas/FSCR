# Price list - manual steps proven in Postman (by the user, 2026-10)

Base: `/fscmRestApi/resources/11.13.18.05`, Basic auth.

1. Create: `POST priceLists`
   `{"PriceListName": "...", "BusinessUnit": "ABD", "CurrencyCode": "USD", "StartDate": "<ISO with offset>"}`
   Defaults returned: Type SEGMENT, LineType ORA_BUY, CalculationMethod PRICE, Status IN_PROGRESS.
2. Access set: `POST priceLists/{PriceListId}/child/accessSets`
   `{"AccessSetCode": "001 CUSTOMER SITE"}`
   Without an access set the UI refuses approval ("access list required").
3. Approve: `PATCH priceLists/{PriceListId}` `{"StatusCode": "APPROVED"}`
   No lines/items needed. No approve action exists in describe.
4. Verify: `GET priceLists?q=PriceListName='<name>'&expand=accessSets`
   -> StatusCode APPROVED and the access set present.

Results: ZZ_POC_PRICELIST1 and ZZ_POC_PRICELIST2 (business unit ABD, USD, approved).
