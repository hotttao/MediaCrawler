---
name: "skill-vetter"
description: "Security-first skill vetting tool. Scans and reviews skill code before installation to detect red flags, permission risks, and suspicious patterns. Invoke before installing any new skill from external sources."
---

# Skill Vetter

**A security audit tool for AI agents.**

<p align="center">
  <img src="https://img.shields.io/badge/Downloads-167k-blue?style=flat-square" alt="Downloads">
  <img src="https://img.shields.io/badge/Stars-710-green?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/badge/License-MIT--0-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Security-Audit-red?style=flat-square" alt="Security">
</p>

A zero-risk, instruction-only vetting tool that performs "deep health checks" on any new skill before installation. It scans skill code for malicious patterns, unauthorized permissions, and suspicious network behaviors.

## When to Use

**Invoke this skill IMMEDIATELY when:**

- Installing any new skill from ClawHub, GitHub, or other sources
- User asks to install or add a skill
- Before enabling community-contributed skills
- When security review is requested

**This skill should be used BEFORE any skill installation to ensure safety.**

## Core Features

### 1. Source Tracing

Verify the skill's origin and author credibility:

- Check GitHub stars and activity
- Review author reputation
- Validate repository authenticity

### 2. Code Review (14 Red Flag Checks)

Scans for common malicious patterns:

| Category        | Check                                        |
| --------------- | -------------------------------------------- |
| **Credentials** | Detects API key theft, hardcoded secrets     |
| **Network**     | Suspicious external calls, data exfiltration |
| **File System** | Unauthorized file access, path traversal     |
| **Execution**   | Code execution, shell commands               |
| **Persistence** | Background daemons, auto-start mechanisms    |
| **Obfuscation** | Base64 encoded strings, eval usage           |

### 3. Permission Minimization

Ensures the skill requests only necessary permissions:

- Minimal scope access
- No credential requirements
- No persistent system presence

### 4. Security Rating

Provides assessment classification:

- ✅ **Benign** - Safe to install
- ⚠️ **Medium Risk** - Review recommended
- 🚨 **High Risk** - Do not install

## Quick Vetting Commands

Use these commands to inspect GitHub-hosted skills:

```bash
# Check repo stars and activity
curl -s https://api.github.com/repos/{owner}/{repo} | jq '.stargazers_count, .updated_at'

# List all files in repository
curl -s https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1 | jq '.tree[].path'

# View SKILL.md content
curl -s https://raw.githubusercontent.com/{owner}/{repo}/main/SKILL.md

# Check for suspicious patterns in code
grep -E "(eval|base64|exec|curl|wget|chmod)" {files}
```

## Vetting Checklist

### Pre-Installation Review

1. **Source Verification**
   - [ ] Is the repository from a trusted author?
   - [ ] Has the repo been recently updated?
   - [ ] Are there security advisories?

2. **Permission Analysis**
   - [ ] Does the skill request credentials?
   - [ ] Are permission requests minimal and justified?
   - [ ] Does it request persistent system access?

3. **Code Security Scan**
   - [ ] No eval() or dynamic code execution
   - [ ] No base64 encoded obfuscated strings
   - [ ] No unauthorized network calls
   - [ ] No file system operations beyond scope

4. **Install Mechanism**
   - [ ] No binary downloads
   - [ ] No extracted archives from untrusted sources
   - [ ] No environment variable requirements

### Post-Vetting Decision

| Rating                | Action                              |
| --------------------- | ----------------------------------- |
| **Benign (Low Risk)** | Safe to install                     |
| **Medium Risk**       | Review code manually, then decide   |
| **High Risk**         | Do not install, report to community |

## Security Best Practices

1. **Always vet first**: Never install a skill without running security checks
2. **Trust indicators**: Check stars, downloads, author reputation
3. **Manual review**: For high-risk skills, perform human code review
4. **Controlled environment**: Run vetting commands without sensitive credentials in shell
5. **Layered security**: Security has layers - review code before running

## Important Warnings

⚠️ **Vetting requires network access**: The agent will read candidate skill files and may perform GitHub API calls. Ensure you want these permissions.

⚠️ **Not foolproof**: The checklist detects obvious red flags but cannot guarantee detection of cleverly obfuscated or time-delayed malicious code.

⚠️ **For high-risk skills**: Require manual human approval for skills classified as MEDIUM+ or requesting any credentials.

## Quick Start

```
User: Install this skill from GitHub
→ Use skill-vetter first to scan the skill
→ Perform security checks (14 red flags)
→ Get security rating
→ Decide whether to proceed
```

## License

MIT-0 License - Free to use, modify, and redistribute. No attribution required.

---

_Like a lobster shell, security has layers — review code before you run it._
