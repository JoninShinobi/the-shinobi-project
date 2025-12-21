#!/usr/bin/env python3
"""
Security Scanner Agent
Autonomous agent that scans website projects for:
- Outdated packages (requirements.txt, package.json)
- Security vulnerabilities (pip-audit, npm audit)
- Framework version mismatches

Updates website_systems collection in Directus with findings.
Designed to run on a schedule via cron or systemd timer.
"""

import os
import json
import subprocess
import tempfile
import shutil
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path
import httpx

from base_agent import BaseAgent, AgentResult


# Configuration
DIRECTUS_URL = os.getenv("DIRECTUS_URL", "http://localhost:8055")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_ADMIN_TOKEN", "")
GITHUB_ORG = os.getenv("GITHUB_ORG", "JoninShinobi")

# Projects to scan (repo name -> requirements file path)
PYTHON_PROJECTS = {
    "hortus-cognitor": "requirements.txt",
    "sound-box-app": "backend/requirements.txt",
    "kerry-gallagher-art": "requirements.txt",
    "community-harvest": "requirements.txt",
    "am-music-store": "requirements.txt",
}

NODE_PROJECTS = {
    "poetry-comp": "server/package.json",
}


@dataclass
class VulnerabilityReport:
    """Report of vulnerabilities found in a project"""
    project_name: str
    framework: str
    framework_version: str
    vulnerabilities: list = field(default_factory=list)
    outdated_packages: list = field(default_factory=list)
    upgrade_priority: str = "none"  # none, low, medium, high, critical
    scan_date: str = ""
    error: Optional[str] = None


class SecurityScannerAgent(BaseAgent):
    """
    Autonomous security scanner for website projects.
    Scans GitHub repos, checks for vulnerabilities, updates Directus.
    """

    def __init__(self):
        super().__init__(
            name="security_scanner",
            description="Scans projects for security vulnerabilities and outdated packages"
        )
        self.temp_dir = None

    @property
    def system_prompt(self) -> str:
        return """You are the Shinobi Security Scanner Agent. Your responsibilities:
1. Analyze vulnerability scan results
2. Prioritize findings by severity
3. Suggest upgrade paths for outdated packages
4. Update the website_systems collection in Directus with findings

When updating Directus, use the mcp__directus__items tool with action 'update'.
Focus on actionable security improvements.
"""

    def build_task_prompt(self, context: dict) -> str:
        return f"""
## Security Scan Results

Project: {context.get('project_name')}
Framework: {context.get('framework')} {context.get('framework_version')}

### Vulnerabilities Found
{json.dumps(context.get('vulnerabilities', []), indent=2)}

### Outdated Packages
{json.dumps(context.get('outdated_packages', []), indent=2)}

### Current Priority: {context.get('upgrade_priority')}

Please:
1. Analyze these findings
2. Update the website_systems record for this project in Directus
3. If critical vulnerabilities exist, note them in the vulnerability_details field
"""

    def directus_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make authenticated request to Directus API"""
        headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
        url = f"{DIRECTUS_URL}{endpoint}"

        with httpx.Client() as client:
            if method == "GET":
                response = client.get(url, headers=headers)
            elif method == "POST":
                response = client.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = client.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

    def get_website_systems(self) -> list:
        """Fetch all website_systems records from Directus"""
        try:
            result = self.directus_request(
                "GET",
                "/items/website_systems?fields=*"
            )
            return result.get("data", [])
        except Exception as e:
            self.log(f"Failed to fetch website_systems: {e}")
            return []

    def update_website_system(self, system_id: str, data: dict):
        """Update a website_systems record in Directus"""
        try:
            self.directus_request(
                "PATCH",
                f"/items/website_systems/{system_id}",
                data
            )
            self.log(f"Updated website_systems/{system_id}")
        except Exception as e:
            self.log(f"Failed to update website_systems/{system_id}: {e}")

    def clone_repo(self, repo_name: str) -> Optional[Path]:
        """Clone a GitHub repo to temp directory"""
        try:
            repo_path = Path(self.temp_dir) / repo_name

            result = subprocess.run(
                ["gh", "repo", "clone", f"{GITHUB_ORG}/{repo_name}", str(repo_path), "--", "--depth", "1"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self.log(f"Failed to clone {repo_name}: {result.stderr}")
                return None

            return repo_path

        except Exception as e:
            self.log(f"Error cloning {repo_name}: {e}")
            return None

    def scan_python_project(self, repo_path: Path, requirements_file: str) -> VulnerabilityReport:
        """Scan a Python project for vulnerabilities"""
        project_name = repo_path.name
        report = VulnerabilityReport(
            project_name=project_name,
            framework="Django",
            framework_version="unknown",
            scan_date=datetime.now(timezone.utc).isoformat()
        )

        requirements_path = repo_path / requirements_file
        if not requirements_path.exists():
            report.error = f"Requirements file not found: {requirements_file}"
            return report

        # Read requirements to get framework version
        try:
            content = requirements_path.read_text()
            for line in content.split("\n"):
                if line.lower().startswith("django=="):
                    report.framework_version = line.split("==")[1].strip()
                    break
        except Exception as e:
            self.log(f"Error reading requirements: {e}")

        # Run pip-audit
        try:
            # Create a virtual environment and install requirements
            venv_path = repo_path / ".venv"
            subprocess.run(
                ["python3", "-m", "venv", str(venv_path)],
                capture_output=True,
                timeout=30
            )

            pip_path = venv_path / "bin" / "pip"

            # Install pip-audit
            subprocess.run(
                [str(pip_path), "install", "pip-audit", "-q"],
                capture_output=True,
                timeout=60
            )

            # Run pip-audit on requirements file
            pip_audit_path = venv_path / "bin" / "pip-audit"
            result = subprocess.run(
                [str(pip_audit_path), "-r", str(requirements_path), "--format", "json"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    for vuln in audit_data:
                        report.vulnerabilities.append({
                            "package": vuln.get("name"),
                            "version": vuln.get("version"),
                            "vulnerability_id": vuln.get("id"),
                            "fix_versions": vuln.get("fix_versions", []),
                            "description": vuln.get("description", "")[:200]
                        })
                except json.JSONDecodeError:
                    pass

        except subprocess.TimeoutExpired:
            report.error = "pip-audit timed out"
        except Exception as e:
            report.error = f"pip-audit error: {str(e)}"

        # Check for outdated packages using pip
        try:
            result = subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_path), "-q", "--dry-run", "--upgrade"],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Parse upgrade suggestions from pip output
            for line in result.stdout.split("\n"):
                if "Would install" in line:
                    packages = line.replace("Would install", "").strip().split()
                    for pkg in packages:
                        if "-" in pkg:
                            name, version = pkg.rsplit("-", 1)
                            report.outdated_packages.append({
                                "package": name,
                                "latest_version": version
                            })

        except Exception as e:
            self.log(f"Error checking outdated packages: {e}")

        # Calculate priority
        report.upgrade_priority = self._calculate_priority(report)

        return report

    def scan_node_project(self, repo_path: Path, package_json_path: str) -> VulnerabilityReport:
        """Scan a Node.js project for vulnerabilities"""
        project_name = repo_path.name
        report = VulnerabilityReport(
            project_name=project_name,
            framework="Next.js",
            framework_version="unknown",
            scan_date=datetime.now(timezone.utc).isoformat()
        )

        package_path = repo_path / package_json_path
        if not package_path.exists():
            report.error = f"Package.json not found: {package_json_path}"
            return report

        # Read package.json
        try:
            package_data = json.loads(package_path.read_text())
            deps = package_data.get("dependencies", {})

            # Get framework version
            if "next" in deps:
                report.framework = "Next.js"
                report.framework_version = deps["next"].replace("^", "").replace("~", "")
            elif "express" in deps:
                report.framework = "Express"
                report.framework_version = deps["express"].replace("^", "").replace("~", "")

        except Exception as e:
            self.log(f"Error reading package.json: {e}")

        # Run npm audit
        try:
            package_dir = package_path.parent

            # Install dependencies first
            subprocess.run(
                ["npm", "install", "--package-lock-only"],
                cwd=str(package_dir),
                capture_output=True,
                timeout=120
            )

            # Run npm audit
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=str(package_dir),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})

                    for pkg_name, vuln_info in vulnerabilities.items():
                        report.vulnerabilities.append({
                            "package": pkg_name,
                            "severity": vuln_info.get("severity"),
                            "via": [v if isinstance(v, str) else v.get("title", "") for v in vuln_info.get("via", [])],
                            "fix_available": vuln_info.get("fixAvailable", False)
                        })

                except json.JSONDecodeError:
                    pass

        except subprocess.TimeoutExpired:
            report.error = "npm audit timed out"
        except Exception as e:
            report.error = f"npm audit error: {str(e)}"

        # Check for outdated packages
        try:
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                cwd=str(package_path.parent),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                try:
                    outdated = json.loads(result.stdout)
                    for pkg_name, info in outdated.items():
                        report.outdated_packages.append({
                            "package": pkg_name,
                            "current": info.get("current"),
                            "wanted": info.get("wanted"),
                            "latest": info.get("latest")
                        })
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            self.log(f"Error checking outdated packages: {e}")

        report.upgrade_priority = self._calculate_priority(report)

        return report

    def _calculate_priority(self, report: VulnerabilityReport) -> str:
        """Calculate upgrade priority based on vulnerabilities"""
        if not report.vulnerabilities and not report.outdated_packages:
            return "none"

        # Check for critical/high severity
        for vuln in report.vulnerabilities:
            severity = vuln.get("severity", "").lower()
            if severity in ["critical", "high"]:
                return "critical" if severity == "critical" else "high"

        # Check for many vulnerabilities
        if len(report.vulnerabilities) >= 5:
            return "high"
        elif len(report.vulnerabilities) >= 2:
            return "medium"
        elif report.vulnerabilities:
            return "low"

        # Check outdated packages
        if len(report.outdated_packages) >= 10:
            return "medium"
        elif report.outdated_packages:
            return "low"

        return "none"

    def run_full_scan(self) -> list[VulnerabilityReport]:
        """Run a full security scan on all projects"""
        reports = []
        self.temp_dir = tempfile.mkdtemp(prefix="shinobi_scan_")
        self.log(f"Starting full security scan in {self.temp_dir}")

        try:
            # Scan Python projects
            for repo_name, req_file in PYTHON_PROJECTS.items():
                self.log(f"Scanning Python project: {repo_name}")
                repo_path = self.clone_repo(repo_name)
                if repo_path:
                    report = self.scan_python_project(repo_path, req_file)
                    reports.append(report)
                    self.log(f"  - {len(report.vulnerabilities)} vulnerabilities, "
                            f"{len(report.outdated_packages)} outdated packages, "
                            f"priority: {report.upgrade_priority}")

            # Scan Node projects
            for repo_name, pkg_file in NODE_PROJECTS.items():
                self.log(f"Scanning Node project: {repo_name}")
                repo_path = self.clone_repo(repo_name)
                if repo_path:
                    report = self.scan_node_project(repo_path, pkg_file)
                    reports.append(report)
                    self.log(f"  - {len(report.vulnerabilities)} vulnerabilities, "
                            f"{len(report.outdated_packages)} outdated packages, "
                            f"priority: {report.upgrade_priority}")

        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.log(f"Cleaned up {self.temp_dir}")

        return reports

    def update_directus_from_reports(self, reports: list[VulnerabilityReport]):
        """Update website_systems collection with scan results"""
        systems = self.get_website_systems()

        # Map project names to system IDs
        name_to_id = {}
        for system in systems:
            name = system.get("project_name", "").lower().replace(" ", "-")
            name_to_id[name] = system.get("id")

        for report in reports:
            # Find matching system record
            system_id = None
            for key, sid in name_to_id.items():
                if report.project_name.lower() in key or key in report.project_name.lower():
                    system_id = sid
                    break

            if not system_id:
                self.log(f"No matching website_systems record for {report.project_name}")
                continue

            # Prepare update data
            update_data = {
                "last_scan_date": report.scan_date,
                "vulnerabilities_found": len(report.vulnerabilities),
                "upgrade_priority": report.upgrade_priority,
                "framework_version": report.framework_version,
            }

            # Add vulnerability details if any
            if report.vulnerabilities:
                update_data["vulnerability_details"] = json.dumps(report.vulnerabilities[:10])  # Limit to 10

            # Update key_packages with outdated info
            if report.outdated_packages:
                packages = []
                for pkg in report.outdated_packages[:15]:  # Limit to 15
                    packages.append({
                        "name": pkg.get("package"),
                        "version": pkg.get("current") or pkg.get("version", "unknown"),
                        "latest": pkg.get("latest") or pkg.get("latest_version"),
                        "needs_update": True
                    })
                update_data["key_packages"] = packages

            if report.error:
                update_data["notes"] = f"Scan error: {report.error}"

            self.update_website_system(system_id, update_data)

    async def execute(self, task_id: str = "scheduled_scan", context: dict = None) -> AgentResult:
        """Execute a full security scan"""
        self.log("Starting scheduled security scan")

        try:
            # Run the scan
            reports = self.run_full_scan()

            # Update Directus
            self.update_directus_from_reports(reports)

            # Summarize results
            total_vulns = sum(len(r.vulnerabilities) for r in reports)
            critical_count = sum(
                1 for r in reports
                if r.upgrade_priority in ["critical", "high"]
            )

            summary = {
                "projects_scanned": len(reports),
                "total_vulnerabilities": total_vulns,
                "critical_or_high_priority": critical_count,
                "reports": [
                    {
                        "project": r.project_name,
                        "vulnerabilities": len(r.vulnerabilities),
                        "priority": r.upgrade_priority
                    }
                    for r in reports
                ]
            }

            self.log(f"Scan complete: {len(reports)} projects, {total_vulns} vulnerabilities, "
                    f"{critical_count} critical/high priority")

            return AgentResult(
                success=True,
                agent_name=self.name,
                task_id=task_id,
                action_taken="security_scan",
                result_data=summary
            )

        except Exception as e:
            self.log(f"Scan failed: {e}")
            return AgentResult(
                success=False,
                agent_name=self.name,
                task_id=task_id,
                action_taken="security_scan",
                error=str(e)
            )


def main():
    """CLI entry point for running the security scanner"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Shinobi Security Scanner Agent")
    parser.add_argument("--project", help="Scan a specific project only")
    parser.add_argument("--dry-run", action="store_true", help="Scan but don't update Directus")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    agent = SecurityScannerAgent()

    if args.project:
        # Single project scan
        agent.log(f"Scanning single project: {args.project}")
        agent.temp_dir = tempfile.mkdtemp(prefix="shinobi_scan_")

        try:
            repo_path = agent.clone_repo(args.project)
            if repo_path:
                if args.project in PYTHON_PROJECTS:
                    report = agent.scan_python_project(repo_path, PYTHON_PROJECTS[args.project])
                elif args.project in NODE_PROJECTS:
                    report = agent.scan_node_project(repo_path, NODE_PROJECTS[args.project])
                else:
                    print(f"Unknown project: {args.project}")
                    return

                if args.json:
                    print(json.dumps({
                        "project": report.project_name,
                        "framework": report.framework,
                        "version": report.framework_version,
                        "vulnerabilities": report.vulnerabilities,
                        "outdated_packages": report.outdated_packages,
                        "priority": report.upgrade_priority
                    }, indent=2))
                else:
                    print(f"\nProject: {report.project_name}")
                    print(f"Framework: {report.framework} {report.framework_version}")
                    print(f"Vulnerabilities: {len(report.vulnerabilities)}")
                    print(f"Outdated packages: {len(report.outdated_packages)}")
                    print(f"Priority: {report.upgrade_priority}")

                if not args.dry_run:
                    agent.update_directus_from_reports([report])

        finally:
            if agent.temp_dir and os.path.exists(agent.temp_dir):
                shutil.rmtree(agent.temp_dir)
    else:
        # Full scan
        result = asyncio.run(agent.execute())

        if args.json:
            print(json.dumps(result.result_data, indent=2))
        else:
            if result.success:
                print(f"\nScan complete!")
                print(f"Projects scanned: {result.result_data['projects_scanned']}")
                print(f"Total vulnerabilities: {result.result_data['total_vulnerabilities']}")
                print(f"Critical/High priority: {result.result_data['critical_or_high_priority']}")
            else:
                print(f"Scan failed: {result.error}")


if __name__ == "__main__":
    main()
