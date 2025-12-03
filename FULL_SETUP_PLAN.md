# Shinobi C2 - Full Setup Plan

## Current State

### Leads (2)
- **AM Music** (Aaron Maloney) - New lead
- **Fluffy Cow Events** (Marlon) - New lead

### Active Clients (8)
| Client | Contact | Project |
|--------|---------|---------|
| Kerry Gallagher Art | Kerry Gallagher | Website Design |
| Hortus Cognitor | Hannah Watkins | Website & Branding |
| Jamaican Tea | Harold Howell | E-commerce Website |
| Book Publishing | Andy Richardson | Publishing Platform |
| Community Harvest Whetstone | TBD | Website & Marketing |
| The Laurel - 7 Acre Project | TBD | 7 Acre Project |
| LMS Project | Adam Lincoln | LMS Development |
| The Shinobi Project | In-House | SoundBox, HaikuTea, Type.Delete, WhatIsReal |

---

## Phase 1: Data Completion (Manual - You)

### 1.1 Complete Client Profiles
For each client, fill in:
- [ ] Company email, phone, address
- [ ] Website URL
- [ ] Industry, business stage
- [ ] Logo upload
- [ ] Brand colours
- [ ] VAT/Company number (if applicable)

### 1.2 Complete Contact Details
For each contact:
- [ ] Correct email addresses
- [ ] Phone numbers
- [ ] Job titles
- [ ] Preferred contact method/time

### 1.3 Add Missing Contacts
- [ ] Community Harvest Whetstone - Who's the contact?
- [ ] The Laurel - Who's the contact?

### 1.4 Refine Project Details
For each project:
- [ ] Accurate descriptions
- [ ] Start dates
- [ ] Estimated end dates
- [ ] Budget amounts
- [ ] Project type refinement

---

## Phase 2: Integrations Setup

### 2.1 Google Workspace Integration
**Time: ~30 mins**

1. Go to Google Cloud Console
2. Create project "Shinobi C2"
3. Enable APIs:
   - Gmail API
   - Google Calendar API
   - Google Drive API
4. Create OAuth 2.0 credentials
5. Add credentials to `google_workspace_config` in Directus
6. Test connection

**Result:** Email sync, calendar sync, Drive integration

### 2.2 Stripe Integration
**Time: ~15 mins**

1. Get Stripe API keys (test + live)
2. Add to `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_xxx
   STRIPE_SECRET_KEY=sk_xxx
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   ```
3. Configure webhook endpoint
4. Test with invoice creation

**Result:** Payment processing, automatic payment recording

### 2.3 1Password Integration (Credentials Reference)
**Time: ~10 mins**

1. For each client with credentials:
   - Create entries in 1Password
   - Copy item IDs
   - Add to `credentials_vault` with vault_provider=1password

**Result:** Secure credential references, no passwords in Directus

---

## Phase 3: Automations (Flows)

### 3.1 Core Flows to Build

| Flow | Trigger | Action |
|------|---------|--------|
| New Lead Notification | Lead created | Email/Slack notification |
| Lead Converted | Lead status → won | Create client + project |
| Invoice Overdue | Daily schedule | Check dates, send reminder |
| Email Sync | Every 5 mins | Pull Gmail, match to clients |
| Calendar Sync | Every 15 mins | Pull events, link to clients |
| New Support Ticket | Webhook | Notify + assign |
| Project Complete | Status → completed | Request review, archive |

### 3.2 Client Website Webhooks

For each client website with contact forms:
- Create webhook endpoint
- Configure form to POST to Directus
- Auto-create lead/support ticket

---

## Phase 4: Deploy to Production

### 4.1 GCP Setup
**Time: ~1 hour**

1. Create GCP project
2. Spin up Compute Engine VM (e2-medium)
3. Install Docker
4. Clone repo
5. Create production `.env` with strong passwords
6. Run `docker-compose up -d`

### 4.2 Cloudflare Tunnel + Access
**Time: ~30 mins**

1. Install cloudflared on VM
2. Create tunnel in Cloudflare dashboard
3. Point tunnel to localhost:8055
4. Create Access application
5. Add Google auth policy
6. Enable OTP
7. Test access

### 4.3 Domain Setup
- Point `c2.theshinobiproject.com` (or similar) to Cloudflare

### 4.4 Backups
- Configure daily PostgreSQL backups
- Encrypt and store in GCS bucket
- Test restore procedure

---

## Phase 5: Role Permissions (~80 mins in Directus UI)

Configure in Settings > Access Control > Policies:

### Manager Policy
Full CRUD on: clients, contacts, projects, tasks, invoices, payments, time_entries, etc.
No access: credentials_vault, audit_log, system settings

### Team Member Policy
Filtered access: Only assigned projects/tasks
Own records: Time entries, tasks
Limited client view: No financial fields

### Read Only Policy
Read-only on business collections
No financial data

---

## Phase 6: Dashboards & Reports

### 6.1 Create Insights Panels
- Pipeline value (leads)
- Revenue this month
- Overdue invoices
- Projects by status
- Time logged this week

### 6.2 Custom Views
- "My Tasks" filtered list
- "Overdue Items" across collections
- "Recent Communications" timeline

---

## Immediate Next Steps

1. **You:** Complete client profile data (emails, phones, addresses)
2. **You:** Set up Google Cloud project + OAuth credentials
3. **Me:** Build core automation Flows once Google is connected
4. **Together:** Deploy to GCP when ready

---

## Questions to Answer

1. What projects are active vs completed for each client?
2. Do you want time tracking on all projects?
3. Which clients need credentials stored?
4. What email templates do you need? (Invoice, follow-up, etc.)
5. Any specific automations you want prioritised?
