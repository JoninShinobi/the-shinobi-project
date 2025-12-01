# Shinobi C2 - Roles Quick Start Checklist

## Step 1: Verify Roles Are Created ✅

The roles have already been created. Verify them:

```bash
docker exec shinobi_vault psql -U shinobi -d shinobi_db -c \
  "SELECT name, description FROM directus_roles ORDER BY name;"
```

**Expected Output:**
- Administrator
- Manager
- Read Only
- Team Member

---

## Step 2: Configure Manager Policy Permissions

1. **Login to Directus:** http://localhost:8055
2. **Navigate to:** Settings > Access Control > Policies
3. **Select:** "Manager Policy"

### Add These Collections (Full CRUD - All Access):

**Core Business:**
- ✅ clients
- ✅ contacts
- ✅ projects
- ✅ tasks
- ✅ milestones

**Financial:**
- ✅ contracts
- ✅ invoices
- ✅ payments
- ✅ expenses
- ✅ revenue_tracking
- ✅ retainer_tracking

**Sales:**
- ✅ leads
- ✅ proposals

**Operations:**
- ✅ services
- ✅ service_tiers
- ✅ project_services
- ✅ time_entries
- ✅ resource_allocations

**Communication:**
- ✅ emails
- ✅ email_templates
- ✅ communication_log
- ✅ calendar_events
- ✅ calendar_events_attendees

**Documents & Support:**
- ✅ documents
- ✅ document_templates
- ✅ errors
- ✅ support_tickets
- ✅ sla_agreements

**Advanced:**
- ✅ reviews_feedback
- ✅ maintenance_schedule
- ✅ knowledge_base
- ✅ shareholders

**Meta:**
- ✅ tags
- ✅ skills

### Add Read-Only Access:
- ✅ team_members (Read permission only)
- ✅ team_members_skills (Read permission only)

### DO NOT Add (Restricted):
- ❌ credentials_vault
- ❌ audit_log
- ❌ google_workspace_config
- ❌ integrations
- ❌ Any `directus_*` system collections

---

## Step 3: Configure Team Member Policy Permissions

1. **Select:** "Team Member Policy"

### Read Only (No Filters):
- ✅ services
- ✅ service_tiers
- ✅ milestones
- ✅ knowledge_base
- ✅ team_members
- ✅ skills

### Read with Filters:

#### Projects (Read Permission)
**Action:** Set to "Use Custom"
**Filter:** (Copy from `PERMISSION_FILTERS.md`)
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

#### Clients (Read Permission)
**Action:** Set to "Use Custom"
**Filter:**
```json
{
  "projects": {
    "_some": {
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
  }
}
```

**Field Restrictions:**
- Allow: `id`, `name`, `company_type`, `status`, `website`, `logo`, `industry`, `description`
- Deny: `stripe_customer_id`, `total_value`, `annual_value`, `payment_terms`

#### Contacts (Read Permission)
**Action:** Set to "Use Custom"
**Filter:**
```json
{
  "client": {
    "projects": {
      "_some": {
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
    }
  }
}
```

### Full CRUD with Filters:

#### Tasks (All Permissions)
**Create/Read/Update/Delete:** Set to "Use Custom"
**Filter for Read:**
```json
{
  "_or": [
    {
      "assigned_to": {
        "_eq": "$CURRENT_USER"
      }
    },
    {
      "created_by": {
        "_eq": "$CURRENT_USER"
      }
    }
  ]
}
```

**Filter for Update/Delete:**
```json
{
  "assigned_to": {
    "_eq": "$CURRENT_USER"
  }
}
```

#### Time Entries (All Permissions)
**Create/Read/Update/Delete:** Set to "Use Custom"
**Filter:**
```json
{
  "team_member": {
    "_eq": "$CURRENT_USER"
  }
}
```

### DO NOT Add:
- ❌ contracts, invoices, payments
- ❌ expenses, revenue_tracking, retainer_tracking
- ❌ proposals, leads
- ❌ shareholders
- ❌ credentials_vault, audit_log
- ❌ google_workspace_config, integrations

---

## Step 4: Configure Read Only Policy Permissions

1. **Select:** "Read Only Policy"

### Read Only Access (All Fields):
- ✅ clients
- ✅ contacts
- ✅ projects
- ✅ tasks
- ✅ milestones
- ✅ time_entries
- ✅ services
- ✅ service_tiers
- ✅ documents
- ✅ emails
- ✅ communication_log
- ✅ calendar_events
- ✅ errors
- ✅ support_tickets
- ✅ sla_agreements
- ✅ maintenance_schedule
- ✅ knowledge_base
- ✅ team_members
- ✅ tags
- ✅ skills

### Read with Field Restrictions:

#### Contracts (Read Permission)
**Field Restrictions:**
- Deny: `contract_value`, `payment_terms`, `stripe_subscription_id`

### DO NOT Add:
- ❌ invoices
- ❌ payments
- ❌ expenses
- ❌ revenue_tracking
- ❌ retainer_tracking
- ❌ shareholders
- ❌ proposals
- ❌ leads
- ❌ credentials_vault
- ❌ audit_log
- ❌ google_workspace_config
- ❌ integrations

---

## Step 5: Create Test Users

1. **Navigate to:** User Directory
2. **Click:** "+ Create User"

### Test User 1 - Manager
- **Email:** manager@test.local
- **Password:** TestManager123!
- **Role:** Manager
- **First Name:** Test
- **Last Name:** Manager

### Test User 2 - Team Member
- **Email:** member@test.local
- **Password:** TestMember123!
- **Role:** Team Member
- **First Name:** Test
- **Last Name:** Member

### Test User 3 - Read Only
- **Email:** readonly@test.local
- **Password:** TestReadOnly123!
- **Role:** Read Only
- **First Name:** Test
- **Last Name:** Viewer

---

## Step 6: Test Permissions

### Test Manager Role:
1. Log out as admin
2. Log in as `manager@test.local`
3. Verify:
   - [ ] Can access Content > Clients
   - [ ] Can create new client
   - [ ] Can access Projects
   - [ ] Can access Invoices
   - [ ] Cannot access Settings
   - [ ] Cannot see credentials_vault

### Test Team Member Role:
1. Log out
2. Log in as `member@test.local`
3. Verify:
   - [ ] Can see limited clients list (empty if not assigned)
   - [ ] Cannot access Invoices
   - [ ] Can create time entries
   - [ ] Can edit own tasks
   - [ ] Cannot access Settings

**Note:** Create a test project and assign this user to verify project visibility

### Test Read Only Role:
1. Log out
2. Log in as `readonly@test.local`
3. Verify:
   - [ ] Can view Clients
   - [ ] Can view Projects
   - [ ] Cannot create anything (no "+" buttons)
   - [ ] Cannot edit items
   - [ ] Cannot delete items
   - [ ] Cannot access financial collections

---

## Step 7: Adjust as Needed

Based on testing, adjust permissions:

1. **Too Restrictive?**
   - Add more collections to policy
   - Adjust filters to be more permissive
   - Add more fields to read permissions

2. **Too Permissive?**
   - Remove collections from policy
   - Add stricter filters
   - Restrict fields in read permissions

---

## Quick Commands

### View All Users and Their Roles
```bash
docker exec shinobi_vault psql -U shinobi -d shinobi_db -c \
  "SELECT u.email, r.name as role FROM directus_users u
   JOIN directus_roles r ON u.role = r.id
   ORDER BY r.name, u.email;"
```

### Check Policy Permissions Count
```bash
docker exec shinobi_vault psql -U shinobi -d shinobi_db -c \
  "SELECT p.name as policy, COUNT(*) as permission_count
   FROM directus_permissions per
   JOIN directus_policies p ON per.policy = p.id
   GROUP BY p.name
   ORDER BY p.name;"
```

### List Collections Without Permissions for a Policy
```bash
docker exec shinobi_vault psql -U shinobi -d shinobi_db -c \
  "SELECT collection FROM directus_collections
   WHERE collection NOT IN
     (SELECT collection FROM directus_permissions
      WHERE policy = 'POLICY_UUID')
   AND collection NOT LIKE 'directus_%'
   ORDER BY collection;"
```

---

## Common Issues

### Issue: User Can't Log In
**Fix:** Verify user has `status: 'active'`

### Issue: User Sees No Collections
**Fix:**
1. Check policy has `app_access: true`
2. Verify role is linked to policy in `directus_access`
3. Check user is assigned to role

### Issue: Filters Not Working
**Fix:**
1. Verify JSON syntax
2. Test filter in Collection view first
3. Check field names match database

### Issue: User Sees Everything
**Fix:**
1. Review policy permissions
2. Check for empty filters `{}`
3. Verify correct policy is assigned

---

## Time Estimate

- **Step 2 (Manager):** 15 minutes
- **Step 3 (Team Member):** 30 minutes (filters)
- **Step 4 (Read Only):** 10 minutes
- **Step 5 (Test Users):** 5 minutes
- **Step 6 (Testing):** 20 minutes

**Total:** ~80 minutes

---

## Need Help?

- **Permission Filters:** See `PERMISSION_FILTERS.md`
- **Detailed Guide:** See `PERMISSIONS_GUIDE.md`
- **Role Definitions:** See `ROLES_SUMMARY.md`
- **Directus Docs:** https://docs.directus.io/guides/access-control.html

---

## Completion Checklist

- [ ] Manager Policy configured (35+ collections)
- [ ] Team Member Policy configured (with filters)
- [ ] Read Only Policy configured
- [ ] Test users created (3 users)
- [ ] Manager role tested
- [ ] Team Member role tested (with assigned project)
- [ ] Read Only role tested
- [ ] Documentation reviewed
- [ ] Team trained on role system
- [ ] Production users created with correct roles
