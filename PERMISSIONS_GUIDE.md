# Shinobi C2 - Roles & Permissions Setup Guide

## Overview

Directus v11+ uses a **Roles + Policies** system for access control:
- **Roles** are assigned to users
- **Policies** contain the actual permissions (CRUD rules for collections)
- Multiple policies can be attached to a role
- Permissions are aggregated from all policies assigned to a user or their role

## Setup Instructions

### Step 1: Run SQL to Create Roles

Execute the SQL script to create the role and policy structure:

```bash
docker exec shinobi_vault psql -U shinobi -d shinobi_db -f /path/to/setup_roles.sql
```

Or copy the SQL into the container first:

```bash
docker cp setup_roles.sql shinobi_vault:/tmp/setup_roles.sql
docker exec shinobi_vault psql -U shinobi -d shinobi_db -f /tmp/setup_roles.sql
```

### Step 2: Configure Permissions in Directus UI

After creating roles and policies via SQL, configure permissions in the Directus admin interface:

1. Navigate to **Settings > Access Control > Policies**
2. Select each policy and configure permissions per collection

---

## Role Definitions

### 1. Administrator (Built-in)
**UUID:** `c81a8e99-02a5-40e0-af02-d3127b5f5591`
**Policy:** Administrator (admin_access: true)

**Permissions:**
- Full system access
- All collections: Create, Read, Update, Delete
- Access to system settings
- Access to credentials_vault
- Access to audit_log

---

### 2. Manager
**UUID:** `10000000-0000-0000-0000-000000000001`
**Policy:** Manager Policy
**Icon:** supervised_user_circle

**Purpose:** Business operations management without system-level access

**Permissions by Collection:**

#### ✅ Full Access (CRUD)
- `clients` - All fields
- `contacts` - All fields
- `projects` - All fields
- `contracts` - All fields
- `invoices` - All fields
- `payments` - All fields
- `proposals` - All fields
- `leads` - All fields
- `tasks` - All fields
- `milestones` - All fields
- `time_entries` - All fields
- `resource_allocations` - All fields
- `services` - All fields
- `service_tiers` - All fields
- `project_services` - Junction table
- `expenses` - All fields
- `revenue_tracking` - All fields
- `retainer_tracking` - All fields
- `documents` - All fields
- `document_templates` - All fields
- `emails` - All fields
- `email_templates` - All fields
- `communication_log` - All fields
- `calendar_events` - All fields
- `calendar_events_attendees` - Junction table
- `errors` - All fields
- `support_tickets` - All fields
- `sla_agreements` - All fields
- `reviews_feedback` - All fields
- `maintenance_schedule` - All fields
- `knowledge_base` - All fields
- `shareholders` - All fields
- `tags` - All fields
- `skills` - All fields
- `team_members` - Read only (can view team)
- `team_members_skills` - Read only

#### ❌ No Access
- `credentials_vault` - Restricted
- `audit_log` - Restricted
- `google_workspace_config` - Restricted
- `integrations` - Restricted
- System collections (`directus_*`)

---

### 3. Team Member
**UUID:** `10000000-0000-0000-0000-000000000002`
**Policy:** Team Member Policy
**Icon:** person

**Purpose:** Individual contributor with limited access to assigned work

**Permissions by Collection:**

#### ✅ Read Only (Limited Fields)
**`clients`** - Read access to:
- `id`, `name`, `company_type`, `status`, `website`, `logo`
- FILTER: Only clients associated with projects they're assigned to

**`contacts`** - Read access to:
- `id`, `first_name`, `last_name`, `email`, `phone`, `position`, `client`
- FILTER: Only contacts for clients they can access

**`projects`** - Read access to:
- All fields
- FILTER: `$CURRENT_USER` in `team_members` or is `project_manager`

**`team_members`** - Read only:
- `id`, `first_name`, `last_name`, `email`, `avatar`, `position`, `skills`

#### ✅ Create, Read, Update (Own Records)
**`tasks`** - Full CRUD:
- FILTER READ: `assigned_to._eq.$CURRENT_USER` OR `created_by._eq.$CURRENT_USER`
- FILTER UPDATE: `assigned_to._eq.$CURRENT_USER` OR `created_by._eq.$CURRENT_USER`
- CREATE: Can create tasks assigned to themselves

**`time_entries`** - Full CRUD:
- FILTER READ: `team_member._eq.$CURRENT_USER`
- FILTER UPDATE: `team_member._eq.$CURRENT_USER`
- FILTER DELETE: `team_member._eq.$CURRENT_USER`
- CREATE: Can only create entries for themselves

#### ✅ Read Only
- `milestones` - Read only (for assigned projects)
- `services` - Read only (service catalog)
- `service_tiers` - Read only
- `documents` - Read only (for accessible projects)
- `calendar_events` - Read only (team calendar)
- `errors` - Read only (project issues)
- `support_tickets` - Read only (for assigned projects)
- `knowledge_base` - Read only

#### ❌ No Access
- `contracts`, `invoices`, `payments`, `expenses`
- `revenue_tracking`, `retainer_tracking`, `shareholders`
- `proposals`, `leads`
- `credentials_vault`, `audit_log`
- `integrations`, `google_workspace_config`
- System collections (`directus_*`)

---

### 4. Read Only
**UUID:** `10000000-0000-0000-0000-000000000003`
**Policy:** Read Only Policy
**Icon:** visibility

**Purpose:** View-only access for reporting and auditing

**Permissions by Collection:**

#### ✅ Read Only (All Fields)
- `clients` - Read all fields
- `contacts` - Read all fields
- `projects` - Read all fields
- `contracts` - Read all fields (no financial details)
- `tasks` - Read all fields
- `milestones` - Read all fields
- `time_entries` - Read all fields
- `services` - Read all fields
- `service_tiers` - Read all fields
- `documents` - Read all fields
- `emails` - Read all fields
- `communication_log` - Read all fields
- `calendar_events` - Read all fields
- `errors` - Read all fields
- `support_tickets` - Read all fields
- `sla_agreements` - Read all fields
- `maintenance_schedule` - Read all fields
- `knowledge_base` - Read all fields
- `team_members` - Read all fields
- `tags` - Read all fields
- `skills` - Read all fields

#### ❌ No Access
- `invoices`, `payments`, `expenses` - Financial data restricted
- `revenue_tracking`, `retainer_tracking`
- `shareholders`
- `proposals`, `leads`
- `credentials_vault`, `audit_log`
- `integrations`, `google_workspace_config`
- System collections (`directus_*`)

---

## Permission Configuration in Directus UI

### How to Set Permissions

1. **Navigate to Policies:**
   - Settings > Access Control > Policies

2. **Select a Policy:**
   - Click on the policy name (e.g., "Manager Policy")

3. **Add Collection Permissions:**
   - Click "+ Add Collection"
   - Select collection from dropdown
   - Configure CRUD permissions:
     - ✅ **Create** - Can create new items
     - ✅ **Read** - Can view items
     - ✅ **Update** - Can edit items
     - ✅ **Delete** - Can remove items

4. **Set Access Level:**
   - **All Access** - No restrictions
   - **Use Custom** - Apply filters and field restrictions

5. **Configure Filters (for Custom Access):**
   - Click "Use Custom"
   - Add filter rules (see Filter Examples below)

6. **Configure Field Access:**
   - Under "Field Permissions"
   - Select which fields are readable/writable

---

## Filter Examples

### Team Member - View Only Assigned Projects
```json
{
  "_or": [
    {
      "team_members": {
        "team_members_id": {
          "_eq": "$CURRENT_USER"
        }
      }
    },
    {
      "project_manager": {
        "_eq": "$CURRENT_USER"
      }
    }
  ]
}
```

### Team Member - Edit Only Own Tasks
```json
{
  "assigned_to": {
    "_eq": "$CURRENT_USER"
  }
}
```

### Team Member - Edit Only Own Time Entries
```json
{
  "team_member": {
    "_eq": "$CURRENT_USER"
  }
}
```

### Manager - Access All Except Restricted Collections
**No filter needed** - Use "All Access" and simply exclude restricted collections

---

## Directus Dynamic Variables

Use these in filter rules:

- `$CURRENT_USER` - Current user's ID
- `$CURRENT_ROLE` - Current user's role ID
- `$NOW` - Current timestamp
- `$NOW(-7 days)` - Date manipulation

**Nested References:**
- `$CURRENT_USER.role` - User's role
- `$CURRENT_USER.email` - User's email

---

## Testing Role Permissions

### Create Test Users

1. Navigate to **User Directory**
2. Click "+ Create User"
3. Fill in details and **assign role**
4. Set password
5. Save

### Test User Access

1. Log out as admin
2. Log in as test user
3. Verify:
   - Can only see permitted collections
   - CRUD actions respect permissions
   - Filters work correctly (e.g., only assigned projects visible)

---

## Common Permission Patterns

### Read with Field Restrictions
**Use Case:** Team members can view clients but not financial data

**Setup:**
1. Set Read permission to "Use Custom"
2. In "Item Permissions" set filter to `{}`  (all items)
3. In "Field Permissions" > "Read Field Permissions":
   - Deselect: `stripe_customer_id`, `total_value`, `annual_value`

### Owner-Only Access
**Use Case:** Team members can only edit their own time entries

**Setup:**
1. Create permission: `time_entries`
2. Set Update to "Use Custom"
3. Filter:
```json
{
  "team_member": {
    "_eq": "$CURRENT_USER"
  }
}
```

### Related Access
**Use Case:** View clients only if assigned to one of their projects

**Setup:**
1. Create permission: `clients`
2. Set Read to "Use Custom"
3. Filter:
```json
{
  "projects": {
    "team_members": {
      "team_members_id": {
        "_eq": "$CURRENT_USER"
      }
    }
  }
}
```

---

## Security Considerations

### Credentials Vault Access
- **NEVER** grant access to `credentials_vault` except Admin
- Use Directus built-in encryption for sensitive fields
- Audit access via `audit_log`

### Audit Logging
- Keep `audit_log` restricted to Admin only
- Review regularly for suspicious activity
- Track changes to roles and policies

### Two-Factor Authentication
- Enable `enforce_tfa` in policies for Manager and above
- Set in Policy settings: `enforce_tfa: true`

### IP Restrictions (Optional)
- Set `ip_access` in policies to restrict by IP
- Example: `["192.168.1.0/24", "10.0.0.0/8"]`

---

## Verification Queries

### Check Roles
```sql
SELECT id, name, description, icon
FROM directus_roles
ORDER BY name;
```

### Check Policies
```sql
SELECT id, name, description, admin_access, app_access
FROM directus_policies
ORDER BY name;
```

### Check Role-Policy Links
```sql
SELECT
    r.name as role_name,
    p.name as policy_name,
    p.admin_access,
    p.app_access
FROM directus_access da
JOIN directus_roles r ON da.role = r.id
JOIN directus_policies p ON da.policy = p.id
ORDER BY r.name;
```

### Check User Roles
```sql
SELECT
    u.first_name,
    u.last_name,
    u.email,
    r.name as role_name
FROM directus_users u
LEFT JOIN directus_roles r ON u.role = r.id
ORDER BY r.name, u.last_name;
```

---

## Next Steps

1. ✅ Run `setup_roles.sql` to create roles and policies
2. ⚠️ Configure detailed permissions in Directus UI:
   - Settings > Access Control > Policies
3. ✅ Create test users for each role
4. ✅ Test permissions thoroughly
5. ✅ Document any custom permission rules
6. ✅ Review and adjust based on team feedback

---

## Troubleshooting

### User Can't See Any Collections
- Check user has app_access (policy setting)
- Verify role is assigned to user
- Ensure policy is linked to role in `directus_access`

### Permissions Not Working as Expected
- Check filter syntax (use Directus filter JSON format)
- Test filters in Collection interface first
- Verify dynamic variables like `$CURRENT_USER` resolve correctly

### Can't Edit Own Records
- Check both READ and UPDATE permissions
- Verify filter allows user's own records
- Test by creating item as that user

---

## Resources

- [Directus v11 Access Control](https://docs.directus.io/guides/access-control.html)
- [Filter Rules Syntax](https://docs.directus.io/guides/filter-rules.html)
- [Dynamic Variables](https://docs.directus.io/guides/filter-rules.html#dynamic-variables)
