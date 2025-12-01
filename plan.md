# Shinobi C2 Security Hardening Plan

## Overview
Implement comprehensive security measures for the Shinobi C2 business management system to protect sensitive client and business data.

---

## Phase 1: Infrastructure Hardening

### 1.1 Access Control - Cloudflare Tunnel + Access
- [ ] Set up Cloudflare Tunnel (cloudflared) on GCP instance
- [ ] Configure Cloudflare Access application for Directus
- [ ] Add authentication policy (Google login + OTP)
- [ ] Configure Access audit logging
- [ ] No public ports exposed - all traffic via Cloudflare

### 1.2 Docker/Environment Security
- [ ] Replace default passwords in `docker-compose.yml`
- [ ] Use environment variables from `.env` file (not committed to git)
- [ ] Add `.env` to `.gitignore`
- [ ] Configure PostgreSQL SSL connections
- [ ] Set up proper network isolation between containers
- [ ] Disable unnecessary ports exposure (Directus only accessible via Cloudflare Tunnel)
- [ ] Add health checks and restart policies

### 1.3 Database Security
- [ ] Enable PostgreSQL encryption at rest
- [ ] Configure connection pooling with PgBouncer
- [ ] Set up database user with minimal required permissions
- [ ] Enable query logging for audit trail
- [ ] Configure automatic backups with encryption

---

## Phase 2: Directus Security Configuration

### 2.1 Authentication & Access
- [ ] Enable 2FA requirement for all users
- [ ] Configure session timeout (e.g., 30 mins idle)
- [ ] Set up password complexity requirements
- [ ] Implement IP allowlisting (if applicable)
- [ ] Configure rate limiting for login attempts
- [ ] Set secure cookie flags (httpOnly, secure, sameSite)

### 2.2 Role-Based Access Control (RBAC)
- [ ] Create role: `Admin` - Full access
- [ ] Create role: `Manager` - Client/project management, no system settings
- [ ] Create role: `Team Member` - Own projects/tasks, limited client view
- [ ] Create role: `Read Only` - Reporting access only
- [ ] Configure field-level permissions (hide sensitive fields per role)
- [ ] Set up collection-level permissions per role

### 2.3 API Security
- [ ] Configure CORS properly (restrict origins)
- [ ] Set up API rate limiting
- [ ] Disable GraphQL introspection in production
- [ ] Configure proper cache headers

---

## Phase 3: Data Protection

### 3.1 Sensitive Field Encryption
Collections with sensitive data requiring encryption:

**`credentials_vault`** (HIGH PRIORITY)
- [ ] `username` - Encrypt
- [ ] `password` - Encrypt (or remove - use external vault)
- [ ] `api_key` - Encrypt
- [ ] `secret_key` - Encrypt
- [ ] `access_token` - Encrypt
- [ ] `notes` - Encrypt

**`clients`**
- [ ] `vat_number` - Encrypt
- [ ] `company_number` - Encrypt
- [ ] `internal_notes` - Encrypt

**`contacts`**
- [ ] `phone` - Consider encryption
- [ ] `email` - Consider encryption (but needed for queries)

**`invoices` / `payments`**
- [ ] `stripe_payment_intent_id` - Encrypt
- [ ] Bank details fields - Encrypt

### 3.2 Credentials Vault Strategy
**Recommendation**: Don't store actual passwords in Directus.
- [ ] Integrate with external secrets manager (1Password, Bitwarden, HashiCorp Vault)
- [ ] Store only references/metadata in `credentials_vault`
- [ ] Add field: `external_vault_id` (reference to external system)
- [ ] Add field: `vault_provider` (dropdown: 1password, bitwarden, manual)
- [ ] Remove or deprecate direct password storage

### 3.3 Backup & Recovery
- [ ] Daily encrypted backups to separate location
- [ ] Weekly backup verification/test restore
- [ ] 30-day backup retention
- [ ] Backup encryption key stored separately from backups

---

## Phase 4: Audit & Monitoring

### 4.1 Audit Logging
- [ ] Enable Directus activity logging (already exists)
- [ ] Configure `audit_log` collection for custom events
- [ ] Log all credential access via `access_log` collection
- [ ] Log failed authentication attempts
- [ ] Log permission-denied events
- [ ] Set up log retention policy (90 days?)

### 4.2 Monitoring & Alerts
- [ ] Set up uptime monitoring
- [ ] Alert on multiple failed login attempts
- [ ] Alert on credential vault access
- [ ] Alert on bulk data exports
- [ ] Weekly security summary report

---

## Phase 5: Operational Security

### 5.1 Access Management
- [ ] Document all user accounts and their purposes
- [ ] Quarterly access reviews
- [ ] Immediate deprovisioning process for departures
- [ ] No shared accounts policy
- [ ] Service account audit

### 5.2 Development Practices
- [ ] Never commit secrets to git
- [ ] Separate dev/staging/production environments
- [ ] Production data never in dev (use anonymised copies)
- [ ] Security review before production deployment

---

## Implementation Priority

### Immediate (Before Production)
1. Environment variables & secrets management
2. Strong unique passwords
3. Directus roles & permissions
4. Credentials vault strategy (external integration)
5. Basic audit logging

### Short-term (First Month)
1. 2FA enforcement
2. Encrypted backups
3. Field-level encryption for sensitive data
4. Rate limiting

### Medium-term (First Quarter)
1. Full monitoring & alerting
2. IP allowlisting
3. Penetration testing
4. Incident response plan

---

## Questions to Clarify

1. **Hosting**: Where will this run in production? (VPS, cloud provider, self-hosted?)
2. **Users**: How many users will access the system? What roles?
3. **External access**: Will this be accessible from internet or VPN-only?
4. **Compliance**: Any specific requirements (GDPR, ISO 27001)?
5. **Budget**: For external tools (secrets manager, monitoring, etc.)
6. **Credentials**: Do you want to integrate with 1Password/Bitwarden, or just not store passwords at all?
