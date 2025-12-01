-- Shinobi C2 Role Setup SQL
-- Directus v11+ uses Roles + Policies for permissions
-- This script creates the role structure. Permissions must be configured via Directus UI afterward.

-- ============================================================================
-- ROLES
-- ============================================================================

-- 1. Admin Role (already exists, but including for reference)
-- UUID: c81a8e99-02a5-40e0-af02-d3127b5f5591
-- Has full access via Administrator policy

-- 2. Manager Role
INSERT INTO directus_roles (id, name, icon, description)
VALUES (
    '10000000-0000-0000-0000-000000000001',
    'Manager',
    'supervised_user_circle',
    'Can manage clients, projects, contracts, invoices. Cannot access system settings, credentials_vault, or audit_log.'
)
ON CONFLICT (id) DO NOTHING;

-- 3. Team Member Role
INSERT INTO directus_roles (id, name, icon, description)
VALUES (
    '10000000-0000-0000-0000-000000000002',
    'Team Member',
    'person',
    'Can view clients (limited fields), manage own tasks/time entries, view assigned projects.'
)
ON CONFLICT (id) DO NOTHING;

-- 4. Read Only Role
INSERT INTO directus_roles (id, name, icon, description)
VALUES (
    '10000000-0000-0000-0000-000000000003',
    'Read Only',
    'visibility',
    'Can view clients, projects, reports but cannot edit anything.'
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- POLICIES
-- ============================================================================

-- Manager Policy
INSERT INTO directus_policies (id, name, icon, description, admin_access, app_access, enforce_tfa)
VALUES (
    '20000000-0000-0000-0000-000000000001',
    'Manager Policy',
    'policy',
    'Full access to business operations. No system settings or credentials access.',
    false,
    true,
    false
)
ON CONFLICT (id) DO NOTHING;

-- Team Member Policy
INSERT INTO directus_policies (id, name, icon, description, admin_access, app_access, enforce_tfa)
VALUES (
    '20000000-0000-0000-0000-000000000002',
    'Team Member Policy',
    'policy',
    'Limited access to assigned work and own time tracking.',
    false,
    true,
    false
)
ON CONFLICT (id) DO NOTHING;

-- Read Only Policy
INSERT INTO directus_policies (id, name, icon, description, admin_access, app_access, enforce_tfa)
VALUES (
    '20000000-0000-0000-0000-000000000003',
    'Read Only Policy',
    'policy',
    'Read-only access to business data. No write permissions.',
    false,
    true,
    false
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- ROLE-POLICY ASSOCIATIONS (directus_access)
-- ============================================================================

-- Link Manager Role to Manager Policy
INSERT INTO directus_access (id, role, policy, sort)
VALUES (
    '30000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    1
)
ON CONFLICT (id) DO NOTHING;

-- Link Team Member Role to Team Member Policy
INSERT INTO directus_access (id, role, policy, sort)
VALUES (
    '30000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000002',
    '20000000-0000-0000-0000-000000000002',
    1
)
ON CONFLICT (id) DO NOTHING;

-- Link Read Only Role to Read Only Policy
INSERT INTO directus_access (id, role, policy, sort)
VALUES (
    '30000000-0000-0000-0000-000000000003',
    '10000000-0000-0000-0000-000000000003',
    '20000000-0000-0000-0000-000000000003',
    1
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- View all roles
SELECT id, name, description, icon FROM directus_roles ORDER BY name;

-- View all policies
SELECT id, name, description, admin_access, app_access FROM directus_policies ORDER BY name;

-- View role-policy associations
SELECT
    r.name as role_name,
    p.name as policy_name,
    da.sort
FROM directus_access da
JOIN directus_roles r ON da.role = r.id
JOIN directus_policies p ON da.policy = p.id
ORDER BY r.name, da.sort;
