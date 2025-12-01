# Shinobi C2 - Permission Filter Quick Reference

Copy-paste these filters directly into Directus when configuring policies.

---

## Team Member Policy Filters

### Projects Collection - Read Permission
**Filter:** User must be assigned to project or be the project manager

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

---

### Clients Collection - Read Permission
**Filter:** User can only see clients for projects they're assigned to

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

---

### Contacts Collection - Read Permission
**Filter:** User can only see contacts for accessible clients

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

---

### Tasks Collection - Read Permission
**Filter:** User can only see tasks assigned to them or created by them

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

---

### Tasks Collection - Update Permission
**Filter:** User can only edit tasks assigned to them

```json
{
  "assigned_to": {
    "_eq": "$CURRENT_USER"
  }
}
```

---

### Tasks Collection - Create Permission
**Filter:** User can only create tasks assigned to themselves

```json
{
  "assigned_to": {
    "_eq": "$CURRENT_USER"
  }
}
```

---

### Time Entries Collection - Read Permission
**Filter:** User can only see their own time entries

```json
{
  "team_member": {
    "_eq": "$CURRENT_USER"
  }
}
```

---

### Time Entries Collection - Update/Delete Permission
**Filter:** User can only modify their own time entries

```json
{
  "team_member": {
    "_eq": "$CURRENT_USER"
  }
}
```

---

### Time Entries Collection - Create Permission
**Filter:** User can only create entries for themselves

```json
{
  "team_member": {
    "_eq": "$CURRENT_USER"
  }
}
```

---

### Documents Collection - Read Permission
**Filter:** User can only see documents for accessible projects

```json
{
  "project": {
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
```

---

### Milestones Collection - Read Permission
**Filter:** User can only see milestones for accessible projects

```json
{
  "project": {
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
```

---

### Errors Collection - Read Permission
**Filter:** User can only see errors for accessible projects

```json
{
  "project": {
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
```

---

### Support Tickets Collection - Read Permission
**Filter:** User can only see tickets for accessible projects

```json
{
  "project": {
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
```

---

## Manager Policy Filters

### Credentials Vault - NO ACCESS
**Action:** Do NOT add this collection to Manager Policy

### Audit Log - NO ACCESS
**Action:** Do NOT add this collection to Manager Policy

### Google Workspace Config - NO ACCESS
**Action:** Do NOT add this collection to Manager Policy

### Integrations - NO ACCESS
**Action:** Do NOT add this collection to Manager Policy

### All Other Collections - FULL ACCESS
**Filter:** Leave empty `{}` for full access

---

## Read Only Policy Filters

### All Collections - READ ONLY
**Filter:** Leave empty `{}` for read access to all items

**Field Restrictions:**

For `invoices`, `payments`, `expenses` collections:
- Set permission to "No Access" (completely deny)

For `contracts` collection:
- Allow Read but restrict financial fields:
  - Hide: `contract_value`, `payment_terms`, `stripe_subscription_id`

---

## Common Filter Patterns

### Current User's Items
```json
{
  "user": {
    "_eq": "$CURRENT_USER"
  }
}
```

### Current User's Role
```json
{
  "role": {
    "_eq": "$CURRENT_ROLE"
  }
}
```

### Recent Items (Last 30 Days)
```json
{
  "date_created": {
    "_gte": "$NOW(-30 days)"
  }
}
```

### Published Only
```json
{
  "status": {
    "_eq": "published"
  }
}
```

### Multiple Conditions (AND)
```json
{
  "_and": [
    {
      "status": {
        "_eq": "published"
      }
    },
    {
      "date_created": {
        "_gte": "$NOW(-30 days)"
      }
    }
  ]
}
```

### Multiple Conditions (OR)
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

---

## Field Restrictions

### Team Member - Clients Collection
**Read Field Restrictions:**

Allow these fields only:
- `id`
- `name`
- `company_type`
- `status`
- `website`
- `logo`
- `industry`
- `description`

Deny these fields:
- `stripe_customer_id`
- `stripe_subscription_id`
- `total_value`
- `annual_value`
- `payment_terms`

---

### Read Only - Contracts Collection
**Read Field Restrictions:**

Deny these fields:
- `contract_value`
- `payment_terms`
- `stripe_subscription_id`

---

## How to Apply Filters in Directus

1. **Navigate to Policy:**
   - Settings > Access Control > Policies
   - Click on policy name

2. **Add Collection Permission:**
   - Click "+ Add Collection"
   - Select collection

3. **Set Permission Level:**
   - For each CRUD action (Create, Read, Update, Delete)
   - Choose "All Access" or "Use Custom"

4. **Apply Filter:**
   - If "Use Custom" selected
   - In "Item Permissions" field
   - Paste JSON filter from above

5. **Set Field Restrictions:**
   - Expand "Field Permissions"
   - Select/deselect specific fields
   - Or use "All" / "None"

6. **Save**

---

## Testing Filters

### Test via API
```bash
# Login as test user
curl -X POST http://localhost:8055/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Use returned token
curl http://localhost:8055/items/projects \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test via Directus UI
1. Create test user with role
2. Log out as admin
3. Log in as test user
4. Navigate to collections
5. Verify filtered results

---

## Dynamic Variable Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `$CURRENT_USER` | Current user's UUID | `"owner": {"_eq": "$CURRENT_USER"}` |
| `$CURRENT_ROLE` | Current user's role UUID | `"role": {"_eq": "$CURRENT_ROLE"}` |
| `$NOW` | Current timestamp | `"date": {"_lte": "$NOW"}` |
| `$NOW(-7 days)` | 7 days ago | `"date": {"_gte": "$NOW(-7 days)"}` |
| `$NOW(+1 year)` | 1 year from now | `"expires": {"_lte": "$NOW(+1 year)"}` |

---

## Troubleshooting

### Filter Not Working
- Check JSON syntax (use a JSON validator)
- Verify field names match database exactly
- Test filter in Collection interface first
- Check nested relationship paths

### User Sees Nothing
- Verify filter allows at least some items
- Check user has role assigned
- Verify policy has `app_access: true`
- Check role is linked to policy

### User Sees Too Much
- Review filter logic (AND vs OR)
- Check for empty filters `{}`
- Verify field restrictions are set

---

## Quick Copy Commands

### Export Policy Permissions (for backup)
```bash
docker exec shinobi_vault psql -U shinobi -d shinobi_db -c \
  "SELECT collection, action, permissions FROM directus_permissions WHERE policy = 'POLICY_UUID';" \
  > policy_backup.txt
```

### Check What User Can Access
```bash
docker exec shinobi_vault psql -U shinobi -d shinobi_db -c \
  "SELECT p.collection, p.action, p.permissions
   FROM directus_permissions p
   JOIN directus_access da ON p.policy = da.policy
   JOIN directus_users u ON u.role = da.role
   WHERE u.email = 'user@example.com';"
```
