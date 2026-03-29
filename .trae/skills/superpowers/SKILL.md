---
name: "superpowers"
description: "Superpowers - A collection of AI coding agent skills including brainstorming, code review, debugging, TDD, and more. Invoke when working on complex development tasks or when you need structured development workflows."
---

# Superpowers

**A collection of AI coding agent skills for professional development workflows.**

<p align="center">
  <a href="https://github.com/obra/superpowers">
    <img src="https://img.shields.io/badge/GitHub-Open%20Source-green?style=flat-square&logo=github" alt="GitHub">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
  </a>
</p>

A curated collection of AI agent skills that enhance development workflows. These skills provide structured approaches to common development tasks, from planning to completion.

## When to Use

**Invoke this skill when:**
- Starting a new development task or project
- Need structured approaches to coding tasks
- Requesting code review or feedback
- Working on debugging complex issues
- Following test-driven development
- Planning and executing multi-step tasks

## Available Skills

### Development Workflow Skills

| Skill | Purpose |
|-------|---------|
| **brainstorming** | Generate and explore ideas with structured brainstorming techniques |
| **writing-plans** | Create detailed, actionable development plans |
| **executing-plans** | Execute plans systematically with progress tracking |
| **verification-before-completion** | Verify all requirements are met before completing tasks |

### Code Quality Skills

| Skill | Purpose |
|-------|---------|
| **receiving-code-review** | Process and act on code review feedback effectively |
| **requesting-code-review** | Prepare code for review and facilitate the process |
| **test-driven-development** | Apply TDD methodology for robust code development |
| **systematic-debugging** | Debug issues systematically with proven techniques |

### Advanced Workflows

| Skill | Purpose |
|-------|---------|
| **subagent-driven-development** | Coordinate multiple sub-agents for parallel execution |
| **dispatching-parallel-agents** | Manage concurrent agent tasks efficiently |
| **finishing-a-development-branch** | Complete and merge development branches properly |
| **using-git-worktrees** | Work on multiple branches simultaneously |

### Meta Skills

| Skill | Purpose |
|-------|---------|
| **writing-skills** | Create new skills for the agent framework |
| **using-superpowers** | Overview and navigation of all available skills |

## Quick Start

### Basic Usage

```
User: Help me implement a new feature
→ Use writing-plans to create a structured plan
→ Use brainstorming for initial ideas
→ Execute plan with executing-plans skill
→ Verify with verification-before-completion
```

### Code Review Workflow

```
1. Request review with requesting-code-review
2. Receive feedback
3. Process with receiving-code-review
4. Apply changes systematically
```

### Debugging Workflow

```
1. Use systematic-debugging to analyze the issue
2. Apply fix
3. Verify with verification-before-completion
```

## Core Philosophy

1. **Structured Approach**: Every task follows a clear, repeatable process
2. **Verification**: Never assume - always verify before completion
3. **Continuous Improvement**: Learn from each interaction and refine approach
4. **Collaboration**: Effective communication and feedback loops
5. **Parallel Execution**: When possible, run tasks concurrently for efficiency

## Skill Interactions

Skills are designed to work together:

```
writing-plans → executing-plans → verification-before-completion
                                    ↓
                                  ↑_____↓ (feedback loop)

code-review: receiving-code-review ↔ requesting-code-review

testing: test-driven-development → verification-before-completion

debugging: systematic-debugging → verification-before-completion
```

## Development Branch Workflow

```
1. Create branch with using-git-worktrees
2. Implement with writing-plans + executing-plans
3. Test with test-driven-development
4. Review with requesting-code-review
5. Address feedback with receiving-code-review
6. Finish branch with finishing-a-development-branch
```

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Professional development workflows for AI agents.*