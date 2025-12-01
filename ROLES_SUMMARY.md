# Shinobi C2 - Roles Setup Summary

## ✅ Completed Setup

The following roles and policies have been created in your Directus instance:

---

## Roles Created

| Role | UUID | Icon | Description |
|------|------|------|-------------|
| **Administrator** | `c81a8e99-02a5-40e0-af02-d3127b5f5591` | verified | Built-in admin role (existing) |
| **Manager** | `10000000-0000-0000-0000-000000000001` | supervised_user_circle | Can manage clients, projects, contracts, invoices |
| **Team Member** | `10000000-0000-0000-0000-000000000002` | person | Can view clients, manage own tasks/time entries |
| **Read Only** | `10000000-0000-0000-0000-000000000003` | visibility | Can view clients, projects, reports (no edits) |

---

## Policies Created

| Policy | UUID | Admin Access | App Access | Description |
|--------|------|--------------|------------|-------------|
| **Administrator** | `ba448bfe-9d48-4b5c-8093-65147758291e` | ✅ Yes | ✅ Yes | Full system access (existing) |
| **Manager Policy** | `20000000-0000-0000-0000-000000000001` | ❌ No | ✅ Yes | Full business operations access |
| **Team Member Policy** | `20000000-0000-0000-0000-000000000002` | ❌ No | ✅ Yes | Limited access to assigned work |
| **Read Only Policy** | `20000000-0000-0000-0000-000000000003` | ❌ No | ✅ Yes | Read-only business data access |

---

## Role-Policy Associations

| Role | Policy | Status |
|------|--------|--------|
| Administrator | Administrator | ✅ Active |
| Manager | Manager Policy | ✅ Active |
| Team Member | Team Member Policy | ✅ Active |
| Read Only | Read Only Policy | ✅ Active |

---

## What's Been Done

1. ✅ **Created 3 new roles** (Manager, Team Member, Read Only)
2. ✅ **Created 3 new policies** (one for each new role)
3. ✅ **Linked roles to policies** via `directus_access` table
4. ✅ **Set app access** for all new roles
5. ✅ **Disabled admin access** for all non-admin roles

---

## What's NOT Done Yet (Manual Configuration Required)

The roles and policies exist but have **NO COLLECTION PERMISSIONS** configured yet. You must configure these in the Directus UI.

### ⚠️ Important: Next Steps Required

1. **Log into Directus** at http://localhost:8055
2. **Navigate to:** Settings > Access Control > Policies
3. **For each policy, configure collection permissions:**

#### Manager Policy Collections (Full CRUD)
- clients
- contacts
- projects
- contracts
- invoices
- payments
- proposals
- leads
- tasks
- milestones
- time_entries
- resource_allocations
- services, service_tiers, project_services
- expenses, revenue_tracking, retainer_tracking
- documents, document_templates
- emails, email_templates, communication_log
- calendar_events, calendar_events_attendees
- errors, support_tickets, sla_agreements
- reviews_feedback, maintenance_schedule
- knowledge_base, shareholders
- tags, skills
- team_members (Read Only)

#### Manager Policy - DENIED Collections
- ❌ credentials_vault
- ❌ audit_log
- ❌ google_workspace_config
- ❌ integrations
- ❌ All `directus_*` system collections

---

#### Team Member Policy Collections

**Read with Filters:**
- clients (filter by assigned projects)
- contacts (filter by accessible clients)
- projects (filter: `$CURRENT_USER` in team_members OR is project_manager)
- team_members (read only, no filter)

**Full CRUD with Filters:**
- tasks (filter: `assigned_to._eq.$CURRENT_USER`)
- time_entries (filter: `team_member._eq.$CURRENT_USER`)

**Read Only (no filters):**
- milestones, services, service_tiers
- documents, calendar_events
- errors, support_tickets
- knowledge_base

#### Team Member Policy - DENIED Collections
- ❌ contracts, invoices, payments, expenses
- ❌ revenue_tracking, retainer_tracking, shareholders
- ❌ proposals, leads
- ❌ credentials_vault, audit_log
- ❌ integrations, google_workspace_config
- ❌ All `directus_*` system collections

---

#### Read Only Policy Collections

**Read Only (All Fields):**
- clients, contacts, projects
- contracts (no financial fields)
- tasks, milestones, time_entries
- services, service_tiers
- documents, emails, communication_log
- calendar_events
- errors, support_tickets, sla_agreements
- maintenance_schedule, knowledge_base
- team_members, tags, skills

#### Read Only Policy - DENIED Collections
- ❌ invoices, payments, expenses
- ❌ revenue_tracking, retainer_tracking, shareholders
- ❌ proposals, leads
- ❌ credentials_vault, audit_log
- ❌ integrations, google_workspace_config
- ❌ All `directus_*` system collections

---

## Quick Access URLs

- **Directus Admin:** http://localhost:8055
- **Access Control:** http://localhost:8055/admin/settings/access-control/policies
- **Users Management:** http://localhost:8055/admin/users

---

## Testing Checklist

Create test users for each role and verify:

### Manager Role Test
- [ ] Can create/edit clients
- [ ] Can create/edit projects
- [ ] Can create/edit invoices
- [ ] Cannot access Settings
- [ ] Cannot view credentials_vault
- [ ] Cannot view audit_log

### Team Member Role Test
- [ ] Can only see assigned projects
- [ ] Can create own time entries
- [ ] Can edit own tasks
- [ ] Cannot see all clients
- [ ] Cannot create invoices
- [ ] Cannot access Settings

### Read Only Role Test
- [ ] Can view clients and projects
- [ ] Cannot edit anything
- [ ] Cannot create new items
- [ ] Cannot delete items
- [ ] Can view reports (when built)

---

## Database Commands

### View All Roles
```sql
SELECT id, name, description, icon
FROM directus_roles
ORDER BY name;
```

### View All Policies
```sql
SELECT id, name, admin_access, app_access
FROM directus_policies
ORDER BY name;
```

### View Role-Policy Links
```sql
SELECT
    r.name as role,
    p.name as policy,
    p.admin_access,
    p.app_access
FROM directus_access da
JOIN directus_roles r ON da.role = r.id
JOIN directus_policies p ON da.policy = p.id
ORDER BY r.name;
```

---

## Files Created

1. **`setup_roles.sql`** - SQL script to create roles, policies, and associations
2. **`setup_roles.sh`** - Bash script to execute the SQL in Docker
3. **`PERMISSIONS_GUIDE.md`** - Comprehensive guide for configuring permissions
4. **`ROLES_SUMMARY.md`** - This file

---

## Support

If roles aren't appearing in Directus:
1. Refresh browser cache (Cmd+Shift+R)
2. Check database: `docker exec shinobi_vault psql -U shinobi -d shinobi_db -c "SELECT * FROM directus_roles;"`
3. Check Directus logs: `docker logs shinobi_c2`

If permissions aren't working:
1. Verify policy is linked to role in `directus_access`
2. Check policy has `app_access: true`
3. Ensure user is assigned to correct role
4. Review filter syntax in policy permissions

---

## References

- **Full Permission Config Guide:** `PERMISSIONS_GUIDE.md`
- **Directus Access Control Docs:** https://docs.directus.io/guides/access-control.html
- **Filter Rules Syntax:** https://docs.directus.io/guides/filter-rules.html
