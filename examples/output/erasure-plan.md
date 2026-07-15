# Erasure plan DSR-2026-0042

- Status: **review_required**
- Subject reference: `sha256:10c6201edf7da63b`
- DataHub snapshot: `datahub-ecommerce-demo-2026-07-15`
- Generated: `2026-07-15T10:47:02.670479+00:00`

## Coverage

- 7 assets discovered across 6 lineage edges
- 19 PII-bearing fields mapped
- 6 assets have actionable handling rules
- 1 asset is protected by review gates
- Owner coverage: 100.0%

## Planned actions

| # | Asset | Action | Fields | Owner | Gate |
|---:|---|---|---|---|---|
| 1 | ecommerce.customers | delete | customer_id, email, full_name, phone | Privacy Engineering | Approval required |
| 2 | support.tickets | anonymize | customer_id, message_body, requester_email | Support Data | Approval required |
| 3 | analytics.customer_360 | anonymize | customer_id, email_hash, segment | Analytics Platform | Approval required |
| 4 | Customer Retention Overview | refresh | customer_id | Growth Analytics | Approval required |
| 5 | finance.invoices | retain | billing_address, billing_name, customer_id | Finance Data | Blocked |
| 6 | marketing.customer_export | delete | audience_id, customer_id, email | Marketing Engineering | Approval required |
| 7 | ml.customer_churn_features | review | customer_id, support_sentiment | ML Platform | Approval required |

## Review gates

- Resolve or confirm the legal-hold gate for finance.invoices; ForgetOps will not mutate this asset.

## DataHub evidence loop

- Read tools: search, list_schema_fields, get_entities, get_lineage
- Planned write-back: add_tags, add_structured_properties, update_description, save_document

> This plan is a dry run. It records organization-defined policy metadata and does not constitute legal advice.
