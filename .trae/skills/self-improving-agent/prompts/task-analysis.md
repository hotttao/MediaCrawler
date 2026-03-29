# Task Analysis Prompt

Use this prompt to systematically analyze tasks before and during execution.

## When to Use

- At the start of complex projects
- When facing ambiguous requirements
- During architectural planning
- When debugging issues

## Analysis Framework

### 1. Task Decomposition

Break down the main task:
- What are the primary components?
- What are the dependencies between components?
- What can be done in parallel?
- What must be done sequentially?

### 2. Risk Identification

Assess potential problems:
- What could go wrong?
- What edge cases need handling?
- What external dependencies exist?
- What assumptions are we making?

### 3. Resource Requirements

Determine what's needed:
- What knowledge or skills are required?
- What tools or libraries are needed?
- What access or permissions are necessary?
- What time constraints exist?

### 4. Success Criteria

Define clear outcomes:
- What does success look like?
- How will we measure progress?
- What are the acceptance criteria?
- What are the quality standards?

## Questions to Explore

1. **Scope**: What exactly needs to be done? What's out of scope?
2. **Context**: What background information is relevant?
3. **Constraints**: What limitations must we work within?
4. **Stakeholders**: Who has interest in the outcome?
5. **Priorities**: What's most important - speed, quality, cost?

## Output Format

```markdown
## Task Analysis

### Objectives
- [Primary goal]
- [Secondary goals]

### Components
1. [Component A]
2. [Component B]
3. [Component C]

### Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [High/Med/Low] | [Strategy] |

### Resources
- [Resource 1]
- [Resource 2]

### Milestones
- [ ] Milestone 1
- [ ] Milestone 2
```

## Tips

1. Don't rush the analysis phase - better planning saves time later
2. Involve stakeholders early if requirements are unclear
3. Document assumptions explicitly
4. Break complex tasks into smaller, manageable pieces
5. Review and update analysis as you learn more