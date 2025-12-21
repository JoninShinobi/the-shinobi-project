# Shinobi Security Scanner Agent

Autonomous security scanning agent that monitors website projects for vulnerabilities and outdated packages.

## Features

- Scans Python projects using `pip-audit` for security vulnerabilities
- Scans Node.js projects using `npm audit` for security vulnerabilities
- Detects outdated packages across all projects
- Updates `website_systems` collection in Directus with findings
- Calculates upgrade priority (none, low, medium, high, critical)
- Can run on a schedule via cron or systemd timer

## Requirements

- Python 3.10+
- GitHub CLI (`gh`) authenticated with repo access
- `pip-audit` (installed automatically during scans)
- `npm` for Node.js project scanning
- Directus with `website_systems` collection

## Environment Variables

```env
DIRECTUS_URL=http://localhost:8055
DIRECTUS_ADMIN_TOKEN=your-admin-token
GITHUB_ORG=JoninShinobi
```

## Usage

### Full Scan (All Projects)

```bash
./scripts/run_security_scan.sh
```

### Single Project Scan

```bash
./scripts/run_security_scan.sh --project sound-box-app
```

### Dry Run (No Directus Updates)

```bash
./scripts/run_security_scan.sh --dry-run
```

### JSON Output

```bash
./scripts/run_security_scan.sh --json
```

## Monitored Projects

### Python (Django)
| Repository | Requirements Path |
|------------|-------------------|
| hortus-cognitor | requirements.txt |
| sound-box-app | backend/requirements.txt |
| kerry-gallagher-art | requirements.txt |
| community-harvest | requirements.txt |
| am-music-store | requirements.txt |

### Node.js
| Repository | Package.json Path |
|------------|-------------------|
| poetry-comp | server/package.json |

## VPS Deployment

### 1. Install Dependencies

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm

# Install GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate GitHub CLI
gh auth login
```

### 2. Deploy Project

```bash
# Clone the project
sudo mkdir -p /opt/shinobi-project
sudo chown $USER:$USER /opt/shinobi-project
git clone https://github.com/JoninShinobi/the-shinobi-project.git /opt/shinobi-project

# Create .env file
cat > /opt/shinobi-project/.env << EOF
DIRECTUS_URL=https://your-directus-instance.com
DIRECTUS_ADMIN_TOKEN=your-admin-token
GITHUB_ORG=JoninShinobi
EOF

chmod 600 /opt/shinobi-project/.env
```

### 3. Setup Systemd Timer

```bash
# Copy service files
sudo cp /opt/shinobi-project/scripts/systemd/shinobi-security-scanner.service /etc/systemd/system/
sudo cp /opt/shinobi-project/scripts/systemd/shinobi-security-scanner.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable shinobi-security-scanner.timer
sudo systemctl start shinobi-security-scanner.timer

# Check timer status
systemctl list-timers | grep shinobi
```

### 4. Alternative: Cron Setup

```bash
# Add to crontab
crontab -e

# Run every Sunday at 02:00
0 2 * * 0 /opt/shinobi-project/scripts/run_security_scan.sh >> /var/log/shinobi-security.log 2>&1
```

## Output

### Console Output

```
==========================================
Shinobi Security Scanner
Started: 2024-12-21 14:30:00
==========================================

[14:30:00] [security_scanner] Starting scheduled security scan
[14:30:00] [security_scanner] Starting full security scan in /tmp/shinobi_scan_xyz
[14:30:05] [security_scanner] Scanning Python project: hortus-cognitor
[14:30:15] [security_scanner]   - 0 vulnerabilities, 3 outdated packages, priority: low
[14:30:15] [security_scanner] Scanning Python project: sound-box-app
...
[14:32:00] [security_scanner] Scan complete: 6 projects, 2 vulnerabilities, 0 critical/high priority

==========================================
Completed: 2024-12-21 14:32:00
==========================================
```

### Directus Updates

The scanner updates `website_systems` collection with:

| Field | Description |
|-------|-------------|
| `last_scan_date` | ISO timestamp of scan |
| `vulnerabilities_found` | Count of vulnerabilities |
| `vulnerability_details` | JSON array of vulnerability info |
| `upgrade_priority` | none, low, medium, high, critical |
| `key_packages` | JSON array of packages with update status |
| `framework_version` | Detected framework version |

## Extending

### Adding New Python Projects

Edit `security_scanner.py`:

```python
PYTHON_PROJECTS = {
    # ... existing projects ...
    "new-project": "requirements.txt",
}
```

### Adding New Node Projects

```python
NODE_PROJECTS = {
    # ... existing projects ...
    "new-node-project": "package.json",
}
```

## Security Considerations

- The scanner runs with minimal permissions (read-only repo access)
- Temporary directories are cleaned up after each scan
- No sensitive data is stored in logs
- Directus token should have limited permissions (only `website_systems` write access)
- Scanner should run on a private VPS, not publicly exposed

## Troubleshooting

### "gh not authenticated"
```bash
gh auth login
```

### "pip-audit not found"
pip-audit is installed into a virtual environment during scanning. Ensure Python venv module is available:
```bash
sudo apt install python3-venv
```

### "npm audit failed"
Ensure npm is installed and updated:
```bash
npm install -g npm@latest
```

### Directus connection errors
Check environment variables and network connectivity:
```bash
curl -H "Authorization: Bearer $DIRECTUS_ADMIN_TOKEN" $DIRECTUS_URL/items/website_systems
```
