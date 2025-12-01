# The Shinobi Project - Claude Code Memory


# Planning

Should any plan need to be made, you must use the proper claude protocols regarding planning, and use plan.md to make the plan. Search if needed.

Always ask clarifying questions and assume the wider context is necessary. Therefore searching through the whole project and plan if not already established, and ensuring the context is understood. You must ask questions if no context is established.

# Shinobi C2 Operational Protocols

1. **Error Handling:**
   - If you encounter ANY error (API failure, file missing, 404, or unknown command), you must IMMEDIATELY use the `mcp__context7__resolve-library-id` tool to find a solution.
   - Do not ask for permission. Do not apologize. Just run the tool.

2. **Communication Style:**
   - Be concise and direct.
   - Use military time for all logs.

3. **Safety:**
   - Never delete data from the 'Production' collection without explicit confirmation.

## Project Overview
Web design/development agency management system built on:
- **Django** - Portfolio website API (existing)
- **Directus** - Business management CMS (Shinobi C2)
- **PostgreSQL** - Shared database (shinobi_vault)
- **Docker** - Container orchestration

## Infrastructure
- `shinobi_vault` - PostgreSQL 16 on port 5433
- `shinobi_c2` - Directus on port 8055
- `shinobi_face` - Django on port 8000

## MCP Connections
- **Directus MCP** - Connected via `.mcp.json` (local project)
- **GitHub MCP** - Connected globally via `gh mcp-server`
- **Context7 MCP** - Documentation lookup

## Key Settings
- **Currency**: GBP
- **Company Location**: UK
- **Payment Integration**: Stripe

---

# Shinobi C2 - Business Management System Plan

## Collections Structure (39 Total)

### Phase 1: Foundation (Core CRM)
1. `clients` - Central profile entity with UK-specific fields (VAT, company number, company types)
2. `contacts` - People at client companies
3. `team_members` - Internal team management
4. `tags` - Universal tagging system
5. `skills` - Team skills catalog

### Phase 2: Project Management
6. `projects` - Full project tracking with tabbed profile
7. `tasks` - Task management
8. `milestones` - Deliverable tracking
9. `services` - Service catalog
10. `service_tiers` - Pricing packages
11. `project_services` - Junction table

### Phase 3: Contracts & Financials
12. `contracts` - Agreement management
13. `invoices` - Billing
14. `payments` - Payment tracking
15. `revenue_tracking` - Commission/rev-share
16. `expenses` - Cost tracking
17. `retainer_tracking` - Retainer management

### Phase 4: Communications
18. `emails` - Email tracking (Google Workspace integration)
19. `communication_log` - All contact types
20. `email_templates` - Templates

### Phase 5: Time & Resources
21. `time_entries` - Time tracking
22. `resource_allocations` - Team allocation
23. `calendar_events` - Scheduling

### Phase 6: Documents & Issues
24. `documents` - File management
25. `document_templates` - Templates
26. `errors` - Issue tracking
27. `support_tickets` - Support management
28. `sla_agreements` - SLA tracking

### Phase 7: Sales Pipeline
29. `leads` - Lead management
30. `proposals` - Proposal tracking

### Phase 8: Advanced
31. `shareholders` - Ownership tracking
32. `credentials_vault` - Secure credentials
33. `access_log` - Credential access audit
34. `knowledge_base` - Documentation
35. `reviews_feedback` - Client feedback
36. `maintenance_schedule` - Maintenance planning

### Phase 9: Integrations
37. `google_workspace_config` - Google setup
38. `integrations` - Third-party connections
39. `audit_log` - System audit trail

---

## Client Profile Tabs (Guidewire-style)
1. Overview - Status, company info, health score
2. Contacts - People at company
3. Projects - Active and historical
4. Contracts - All agreements
5. Communications - Emails, calls, meetings
6. Documents - Files, contracts, deliverables
7. Financials - Invoices, payments, revenue
8. Issues - Errors, support tickets
9. Notes - Extended notes

## Project Profile Tabs
1. Overview - Status, timeline, health, team
2. Tasks - Task board
3. Milestones - Key deliverables
4. Services - Applied services
5. Time Tracking - Hours logged
6. Communications - Project emails
7. Documents - Project files
8. Issues - Bugs, problems
9. Financials - Budget, payments

---

## Technical Notes
- All collections use UUID primary keys
- Currency default: GBP
- Timestamps on all collections
- Stripe integration via `stripe_*` fields
- Google Workspace integration hooks
- **Collapsible field groups** for profile organisation (Company Info, Address, Social, Financials, Notes, etc.)

## UI Approach
- Use Directus **collapsible field groups** instead of tabs
- Groups provide similar UX to tabbed profiles (expand/collapse sections)
- Apply to: clients, contacts, team_members, projects, contracts

---

## Full Plan Reference
See `/Users/aarondudfield/.claude/plans/jolly-tinkering-beaver.md` for complete field-level schema details.

---

## Access Control & Roles

### Roles Setup (Completed)
✅ **4 Roles Created:**
1. **Administrator** - Full system access (built-in)
2. **Manager** - Full business operations (no system settings/credentials)
3. **Team Member** - Limited to assigned work and own time tracking
4. **Read Only** - View-only access to business data

### Role Implementation
- Roles created via SQL: `setup_roles.sql`
- Execute via: `./setup_roles.sh`
- Directus v11+ uses Roles + Policies model
- Each role linked to corresponding policy in `directus_access`

### Permission Configuration
⚠️ **Manual Setup Required:**
- Permissions must be configured in Directus UI
- Navigate to: Settings > Access Control > Policies
- Configure collection-level CRUD permissions
- Apply filters for Team Member role (assigned projects/tasks)

### Documentation Files
- `ROLES_SUMMARY.md` - Role definitions and setup status
- `PERMISSIONS_GUIDE.md` - Comprehensive permission configuration guide
- `PERMISSION_FILTERS.md` - Copy-paste JSON filters for policies

### Security Notes
- `credentials_vault` - Admin only
- `audit_log` - Admin only
- `google_workspace_config` - Admin only
- `integrations` - Admin and Manager only
- All financial data restricted from Team Member and Read Only roles
