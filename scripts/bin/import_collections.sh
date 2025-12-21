#!/bin/bash
# Import contract collections into Directus

DIRECTUS_URL="http://localhost:8055"
TOKEN="i6DpdwdfQbWQ5_uQElOYuuZFWyOdK1uk"

echo "Creating contract_templates collection..."
curl -s -X POST "$DIRECTUS_URL/collections" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "contract_templates",
    "schema": {},
    "meta": {
      "icon": "description",
      "note": "Master templates for legal documents with merge fields",
      "display_template": "{{name}} (v{{version}})",
      "singleton": false,
      "sort_field": "sort"
    },
    "fields": [
      {"field": "id", "type": "uuid", "meta": {"special": ["uuid"], "interface": "input", "readonly": true, "hidden": true}, "schema": {"is_primary_key": true}},
      {"field": "name", "type": "string", "meta": {"interface": "input", "required": true, "width": "half", "note": "Human-readable template name"}, "schema": {"max_length": 255}},
      {"field": "slug", "type": "string", "meta": {"interface": "input", "required": true, "width": "half", "note": "URL-friendly identifier"}, "schema": {"max_length": 100, "is_unique": true}},
      {"field": "document_type", "type": "string", "meta": {"interface": "select-dropdown", "required": true, "width": "half", "options": {"choices": [{"text": "Client Services Agreement", "value": "client_services"}, {"text": "Website Development Agreement", "value": "web_development"}, {"text": "Maintenance Agreement", "value": "maintenance"}, {"text": "Non-Disclosure Agreement", "value": "nda"}, {"text": "Terms of Service", "value": "tos"}, {"text": "Privacy Policy", "value": "privacy_policy"}, {"text": "Data Processing Agreement", "value": "dpa"}, {"text": "Cookie Policy", "value": "cookie_policy"}]}}},
      {"field": "version", "type": "string", "meta": {"interface": "input", "required": true, "width": "half", "note": "Semantic version"}, "schema": {"max_length": 20, "default_value": "1.0.0"}},
      {"field": "status", "type": "string", "meta": {"interface": "select-dropdown", "required": true, "width": "half", "options": {"choices": [{"text": "Draft", "value": "draft"}, {"text": "Active", "value": "active"}, {"text": "Archived", "value": "archived"}]}}, "schema": {"default_value": "draft"}},
      {"field": "requires_signature", "type": "boolean", "meta": {"interface": "boolean", "width": "half", "note": "Whether this document requires a digital signature"}, "schema": {"default_value": true}},
      {"field": "effective_date", "type": "timestamp", "meta": {"interface": "datetime", "width": "half", "note": "When this version becomes active"}},
      {"field": "content_html", "type": "text", "meta": {"interface": "input-code", "required": true, "note": "Full HTML content with merge fields", "options": {"language": "html"}}},
      {"field": "merge_fields", "type": "json", "meta": {"interface": "input-code", "note": "JSON array of available merge fields", "options": {"language": "json"}}, "schema": {"default_value": "[]"}},
      {"field": "sort", "type": "integer", "meta": {"interface": "input", "hidden": true}},
      {"field": "date_created", "type": "timestamp", "meta": {"special": ["date-created"], "interface": "datetime", "readonly": true, "width": "half"}},
      {"field": "date_updated", "type": "timestamp", "meta": {"special": ["date-updated"], "interface": "datetime", "readonly": true, "width": "half"}}
    ]
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'data' in d else d)"

echo ""
echo "Creating contract_signatures collection..."
curl -s -X POST "$DIRECTUS_URL/collections" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "contract_signatures",
    "schema": {},
    "meta": {
      "icon": "draw",
      "note": "Digital signature records with legal audit trail",
      "display_template": "{{signatory_name}} - {{consented_at}}",
      "singleton": false
    },
    "fields": [
      {"field": "id", "type": "uuid", "meta": {"special": ["uuid"], "interface": "input", "readonly": true, "hidden": true}, "schema": {"is_primary_key": true}},
      {"field": "contract_id", "type": "uuid", "meta": {"interface": "select-dropdown-m2o", "required": true, "width": "half", "note": "Parent contract"}},
      {"field": "signatory_name", "type": "string", "meta": {"interface": "input", "required": true, "width": "half", "note": "Full legal name"}, "schema": {"max_length": 255}},
      {"field": "signatory_email", "type": "string", "meta": {"interface": "input", "required": true, "width": "half", "note": "Email address"}, "schema": {"max_length": 255}},
      {"field": "signatory_role", "type": "string", "meta": {"interface": "select-dropdown", "required": true, "width": "half", "options": {"choices": [{"text": "Director", "value": "director"}, {"text": "Owner", "value": "owner"}, {"text": "Manager", "value": "manager"}, {"text": "Authorised Representative", "value": "authorised_rep"}, {"text": "Other", "value": "other"}]}}},
      {"field": "signature_type", "type": "string", "meta": {"interface": "select-dropdown", "required": true, "width": "half", "options": {"choices": [{"text": "Typed Name", "value": "typed"}, {"text": "Drawn Signature", "value": "drawn"}, {"text": "Checkbox Consent", "value": "checkbox"}]}}},
      {"field": "signature_data", "type": "text", "meta": {"interface": "input-code", "note": "Base64 image or typed name"}},
      {"field": "signature_hash", "type": "string", "meta": {"interface": "input", "readonly": true, "note": "SHA-256 hash"}, "schema": {"max_length": 64}},
      {"field": "consent_text", "type": "text", "meta": {"interface": "input-multiline", "note": "The consent statement shown"}},
      {"field": "consented_at", "type": "timestamp", "meta": {"interface": "datetime", "required": true, "width": "half", "note": "Timestamp of consent"}},
      {"field": "ip_address", "type": "string", "meta": {"interface": "input", "readonly": true, "width": "half"}, "schema": {"max_length": 45}},
      {"field": "user_agent", "type": "text", "meta": {"interface": "input", "readonly": true}},
      {"field": "geolocation", "type": "json", "meta": {"interface": "input-code", "note": "Optional location data", "options": {"language": "json"}}}
    ]
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'data' in d else d)"

echo ""
echo "Creating contract_audit_log collection..."
curl -s -X POST "$DIRECTUS_URL/collections" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "contract_audit_log",
    "schema": {},
    "meta": {
      "icon": "history",
      "note": "Complete audit trail for contract actions",
      "display_template": "{{action}} - {{date_created}}",
      "singleton": false
    },
    "fields": [
      {"field": "id", "type": "uuid", "meta": {"special": ["uuid"], "interface": "input", "readonly": true, "hidden": true}, "schema": {"is_primary_key": true}},
      {"field": "contract_id", "type": "uuid", "meta": {"interface": "select-dropdown-m2o", "required": true, "width": "half", "note": "Related contract"}},
      {"field": "action", "type": "string", "meta": {"interface": "select-dropdown", "required": true, "width": "half", "options": {"choices": [{"text": "Created", "value": "created"}, {"text": "Sent", "value": "sent"}, {"text": "Viewed", "value": "viewed"}, {"text": "Signed", "value": "signed"}, {"text": "Expired", "value": "expired"}, {"text": "Revoked", "value": "revoked"}]}}},
      {"field": "actor_type", "type": "string", "meta": {"interface": "select-dropdown", "width": "half", "options": {"choices": [{"text": "System", "value": "system"}, {"text": "Admin", "value": "admin"}, {"text": "Client", "value": "client"}]}}},
      {"field": "actor_id", "type": "string", "meta": {"interface": "input", "width": "half"}, "schema": {"max_length": 255}},
      {"field": "actor_email", "type": "string", "meta": {"interface": "input", "width": "half"}, "schema": {"max_length": 255}},
      {"field": "ip_address", "type": "string", "meta": {"interface": "input", "readonly": true, "width": "half"}, "schema": {"max_length": 45}},
      {"field": "user_agent", "type": "text", "meta": {"interface": "input", "readonly": true}},
      {"field": "metadata", "type": "json", "meta": {"interface": "input-code", "note": "Additional action data", "options": {"language": "json"}}},
      {"field": "date_created", "type": "timestamp", "meta": {"special": ["date-created"], "interface": "datetime", "readonly": true, "width": "half"}}
    ]
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'data' in d else d)"

echo ""
echo "Creating policy_acceptances collection..."
curl -s -X POST "$DIRECTUS_URL/collections" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "policy_acceptances",
    "schema": {},
    "meta": {
      "icon": "check_circle",
      "note": "Tracks ToS, Privacy Policy, Cookie acceptances",
      "display_template": "{{policy_type}} v{{policy_version}} - {{accepted_at}}",
      "singleton": false
    },
    "fields": [
      {"field": "id", "type": "uuid", "meta": {"special": ["uuid"], "interface": "input", "readonly": true, "hidden": true}, "schema": {"is_primary_key": true}},
      {"field": "client_id", "type": "uuid", "meta": {"interface": "select-dropdown-m2o", "width": "half", "note": "Linked client"}},
      {"field": "contact_id", "type": "uuid", "meta": {"interface": "select-dropdown-m2o", "width": "half", "note": "Person who accepted"}},
      {"field": "policy_type", "type": "string", "meta": {"interface": "select-dropdown", "required": true, "width": "half", "options": {"choices": [{"text": "Terms of Service", "value": "tos"}, {"text": "Privacy Policy", "value": "privacy_policy"}, {"text": "Cookie Policy", "value": "cookie_policy"}]}}},
      {"field": "policy_version", "type": "string", "meta": {"interface": "input", "required": true, "width": "half", "note": "Version accepted"}, "schema": {"max_length": 20}},
      {"field": "acceptor_email", "type": "string", "meta": {"interface": "input", "required": true, "width": "half"}, "schema": {"max_length": 255}},
      {"field": "accepted_at", "type": "timestamp", "meta": {"interface": "datetime", "required": true, "width": "half"}},
      {"field": "ip_address", "type": "string", "meta": {"interface": "input", "readonly": true, "width": "half"}, "schema": {"max_length": 45}},
      {"field": "user_agent", "type": "text", "meta": {"interface": "input", "readonly": true}}
    ]
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'data' in d else d)"

echo ""
echo "Done!"
