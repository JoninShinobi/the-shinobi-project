# Shinobi C2 - Master Project Management Plan

## Overview
Centralized management system for portfolio company operations. Commission/royalty model across all projects.

**Work Window:** 17:45 - 22:00 (evenings only)
**Budget:** £0 (leverage free tiers + skills)
**Model:** Commission/royalty on all projects (contracts required)

---

## Phase 1: Daily Workflow Protocol

### Evening Session Structure (17:45 - 22:00)

| Time | Block | Activity |
|------|-------|----------|
| 17:45 | Startup | Check Shinobi C2 dashboard, review today's priorities |
| 18:00 | Fire Tasks | Work on highest priority items (max 2 hours) |
| 20:00 | Marketing | Content scheduling, social engagement (30 min) |
| 20:30 | Admin | Emails, invoices, client comms (30 min) |
| 21:00 | Build | Deep work on current sprint project (45 min) |
| 21:45 | Shutdown | Log time, update tasks, set tomorrow's priorities |

### Daily Check-in Checklist
- [ ] Review all project statuses
- [ ] Check overdue tasks
- [ ] Review any new leads/inquiries
- [ ] Check revenue dashboards (Stripe/KDP)
- [ ] Update priority scores
- [ ] Log all time entries

---

## Phase 2: Project Lifecycle Framework

### 6 Phases

```
SETUP → BUILD → LAUNCH → GROW → MAINTAIN → ARCHIVE
```

| Phase | Focus | Exit Criteria |
|-------|-------|---------------|
| **Setup** | Planning, contracts, infrastructure | Contract signed, repo created, scope defined |
| **Build** | Development, content creation | MVP complete, testing passed |
| **Launch** | Go-live, initial marketing push | Live in production, launch announcements done |
| **Grow** | Marketing, user acquisition, iteration | Stable revenue or metrics growth |
| **Maintain** | Support, updates, optimization | Minimal intervention needed |
| **Archive** | Sunset, documentation, handoff | All assets documented, client notified |

### Phase Transitions
- [ ] Create Directus flow to track phase changes
- [ ] Set up notifications for phase completion
- [ ] Document exit criteria for each project

---

## Phase 3: Priority Matrix (RICE-Lite)

### Scoring Formula
```
Priority Score = (R × 3) + (I × 2) + (C × 2) + (E × 1)
                 ────────────────────────────────────
                              8
```

### Factors (Score 1-5 each)

| Factor | Weight | Description |
|--------|--------|-------------|
| **R** Revenue Potential | 3x | Immediate income opportunity |
| **I** Immediate Deadline | 2x | Time-sensitive obligations |
| **C** Client Health | 2x | Relationship risk/opportunity |
| **E** Effort Efficiency | 1x | Quick wins vs. heavy lifts |

### Priority Categories

| Category | Score Range | Action |
|----------|-------------|--------|
| 🔥 **Fire** | 4.0+ | Work on today |
| 🌊 **Flow** | 3.0-3.9 | This week |
| 🍳 **Simmer** | 2.0-2.9 | This month |
| ❄️ **Cold** | < 2.0 | Backlog / review |

### Implementation Tasks
- [ ] Add `priority_score` field to projects collection
- [ ] Add `priority_category` field to projects collection
- [ ] Create auto-calculation flow
- [ ] Build dashboard view sorted by priority

---

## Phase 4: Marketing Playbook (Zero Budget)

### Tools (Free Tiers)
- [ ] **Buffer** - Social scheduling (3 channels free)
- [ ] **Mailchimp** - Email marketing (500 contacts free)
- [ ] **Canva** - Graphics (free tier)
- [ ] **ChatGPT/Claude** - Content generation
- [ ] **Google Business Profile** - Local SEO

### Content Calendar
| Day | Focus | Channels |
|-----|-------|----------|
| Monday | Portfolio showcase | LinkedIn, Instagram |
| Tuesday | Tips/Education | Twitter, LinkedIn |
| Wednesday | Behind-the-scenes | Instagram Stories |
| Thursday | Client success | LinkedIn |
| Friday | Weekend engagement | All channels |

### Content Rules
- AI content must look organic (no obvious AI markers)
- Always customize for platform tone
- Mix: 70% value, 20% personality, 10% promotional
- Batch create on weekends when possible

### Marketing Tasks
- [ ] Set up Buffer account
- [ ] Connect social profiles
- [ ] Create content templates in Canva
- [ ] Set up Mailchimp account
- [ ] Build email capture strategy
- [ ] Create Google Business Profile

---

## Phase 5: Directus Schema Updates

### New Fields for `projects` Collection
- [ ] `lifecycle_phase` - Select dropdown (setup/build/launch/grow/maintain/archive)
- [ ] `priority_score` - Decimal (auto-calculated)
- [ ] `priority_category` - Select (fire/flow/simmer/cold)
- [ ] `revenue_model` - Select (fixed_fee/hourly/retainer/commission/royalty/equity)
- [ ] `commission_percentage` - Decimal
- [ ] `next_milestone_date` - Date
- [ ] `last_worked_on` - Timestamp
- [ ] `days_since_contact` - Integer (calculated)

### New Collections
- [ ] `daily_priorities` (singleton) - Today's focus items
- [ ] `marketing_calendar` - Content planning
- [ ] `weekly_reviews` - Sprint retrospectives

### Field Group Organization
- [ ] Create "Priority & Lifecycle" group
- [ ] Create "Revenue Model" group
- [ ] Create "Activity Tracking" group

---

## Phase 6: Automation Flows (10 Total)

### Scheduled Flows

| # | Flow Name | Trigger | Action |
|---|-----------|---------|--------|
| 1 | Daily Priority Calculator | 17:30 daily | Recalculate all project scores |
| 2 | Client Contact Reminder | 09:00 daily | Flag clients with no contact > 7 days |
| 3 | Overdue Task Alert | 17:00 daily | Notification for overdue tasks |
| 4 | Invoice Overdue Reminder | 09:00 daily | Flag invoices > 14 days overdue |
| 5 | Lead Follow-up Nudge | 17:00 daily | Remind about leads > 48 hours |
| 6 | Time Entry Reminder | 21:45 daily | Prompt if no time logged today |
| 7 | Weekly Revenue Report | Sun 20:00 | Summarize week's revenue |
| 8 | Project Milestone Due | 09:00 daily | Alert milestones due in 3 days |

### Event-Triggered Flows

| # | Flow Name | Trigger | Action |
|---|-----------|---------|--------|
| 9 | New Lead Notification | Lead created | Send notification |
| 10 | Auto-Update Last Worked | Task/time entry saved | Update project timestamp |

### Flow Implementation Tasks
- [ ] Create Flow 1: Daily Priority Calculator
- [ ] Create Flow 2: Client Contact Reminder
- [ ] Create Flow 3: Overdue Task Alert
- [ ] Create Flow 4: Invoice Overdue Reminder
- [ ] Create Flow 5: Lead Follow-up Nudge
- [ ] Create Flow 6: Time Entry Reminder
- [ ] Create Flow 7: Weekly Revenue Report
- [ ] Create Flow 8: Project Milestone Due
- [ ] Create Flow 9: New Lead Notification
- [ ] Create Flow 10: Auto-Update Last Worked

---

## Phase 7: Integration Plan

### Stripe Integration (Revenue Tracking)
- [ ] Create Stripe account (if not exists)
- [ ] Set up products for each service tier
- [ ] Configure webhook for payment notifications
- [ ] Build revenue dashboard in Directus

### Amazon KDP Integration (Book Revenue)
- [ ] Set up KDP reports API access
- [ ] Create revenue tracking for book projects
- [ ] Build royalty reporting dashboard

### Buffer Integration (Social Scheduling)
- [ ] Connect Buffer API
- [ ] Create content queue workflow
- [ ] Set up analytics tracking

### Google Workspace (Already Configured)
- [ ] Verify Gmail sync working
- [ ] Set up calendar integration
- [ ] Configure Drive document links

---

## Phase 8: Weekly & Monthly Rhythms

### Weekly Review (Sunday 20:00)
- [ ] Review all project progress
- [ ] Update priority scores
- [ ] Plan next week's focus
- [ ] Check revenue metrics
- [ ] Celebrate wins

### Monthly Review (1st of Month)
- [ ] Full financial review
- [ ] Project portfolio health check
- [ ] Marketing metrics analysis
- [ ] Goal setting for month
- [ ] Contract/agreement review

---

## Phase 9: Success Metrics

### Key Performance Indicators

| Metric | Target | Tracking |
|--------|--------|----------|
| Revenue (Monthly) | £500+ within 6 months | Stripe + KDP |
| Projects in "Grow" phase | 3+ | Directus |
| Lead conversion rate | 30%+ | Directus |
| Average project health | 7+/10 | Calculated |
| Marketing posts/week | 5+ | Buffer |
| Client contact frequency | < 7 days | Directus |

### Dashboard Views to Create
- [ ] Revenue Overview
- [ ] Project Priority Board
- [ ] Lead Pipeline
- [ ] Time Utilization
- [ ] Marketing Calendar

---

## Phase 10: Implementation Roadmap

### Week 1: Foundation
- [ ] Add new fields to projects collection
- [ ] Create new collections (daily_priorities, marketing_calendar, weekly_reviews)
- [ ] Set up priority scoring system
- [ ] Update all existing projects with lifecycle phase

### Week 2: Automation
- [ ] Build Flows 1-5 (priority calculator, reminders)
- [ ] Test scheduled triggers
- [ ] Configure notification channels

### Week 3: Marketing Infrastructure
- [ ] Set up Buffer + Mailchimp
- [ ] Create content templates
- [ ] Build marketing calendar
- [ ] Schedule first week of content

### Week 4: Integrations
- [ ] Configure Stripe integration
- [ ] Set up KDP tracking
- [ ] Build revenue dashboards
- [ ] Test payment webhooks

### Week 5: Polish & Launch
- [ ] Build remaining Flows 6-10
- [ ] Create dashboard views
- [ ] Document all workflows
- [ ] Go live with daily protocol

---

## Current Project Inventory

### Priority Review Needed

| Project | Client | Phase | Priority | Action Needed |
|---------|--------|-------|----------|---------------|
| When Sparrows Fall | Poetry Book | Build | 🔥 High | Complete design, KDP setup |
| Hortus Cognitor | Own | Build | 🔥 High | UI refinements |
| SoundBox | Own | Launch | 🌊 Flow | Production deployment |
| Kerry Gallagher | KG | Build | 🌊 Flow | Mobile responsive |
| Community Harvest | Client | Launch | 🌊 Flow | WhiteNoise deployed |
| HaikuTea | Own | Setup | 🍳 Simmer | Needs planning |
| TheLaurel | Own | Setup | 🍳 Simmer | Legal/planning |
| WhatIsReal | Own | Setup | ❄️ Cold | Needs review |

---

## Quick Reference

### Contract Requirements
All commission/royalty agreements MUST be signed before work begins:
- Commission percentage clearly stated
- Payment terms defined
- IP ownership specified
- Termination clauses included

### Revenue Models
- **Fixed Fee**: One-time payment for defined scope
- **Hourly**: Billed per hour worked
- **Retainer**: Monthly recurring for ongoing support
- **Commission**: Percentage of revenue generated
- **Royalty**: Ongoing percentage of sales
- **Equity**: Ownership stake in project/company

---

## Notes

- Days off are essential - don't burn out
- Focus on building the SYSTEM, not just the projects
- Let clients do the selling when possible
- Commission model = aligned incentives
- Document everything in Shinobi C2

---

*Last Updated: 2024-12-03*
*Generated by Shinobi C2*
