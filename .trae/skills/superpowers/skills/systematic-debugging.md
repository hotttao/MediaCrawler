---
name: "systematic-debugging"
description: "Systematic debugging techniques to identify, isolate, and fix issues methodically. Invoke when user reports a bug or unexpected behavior."
---

# Systematic Debugging Skill

A structured approach to debugging that ensures thorough analysis and effective solutions.

## When to Use

- User reports a bug or error
- Unexpected behavior occurs
- Production issue needs investigation
- Debugging complex or recurring problems

## Debugging Framework

### 1. Reproduce

First, ensure you can reproduce the issue:

- **Isolate**: Find minimal conditions to reproduce
- **Document**: Record exact steps and environment
- **Confirm**: Verify the issue consistently appears

### 2. Understand

Deep dive into the problem:

- **What**: What is the observed behavior?
- **Expected**: What should happen?
- **Gap**: Where is the difference?
- **Scope**: How widespread is the issue?

### 3. Hypothesize

Form a theory:

- **Likely Causes**: What's most probable?
- **Evidence**: What data supports this?
- **Test**: How can we verify?

### 4. Investigate

Gather evidence:

- **Logs**: Check application/logs
- **Debug**: Add debug statements
- **Trace**: Follow the execution flow
- **Compare**: Look at working vs broken states

### 5. Fix

Implement the solution:

- **Minimal**: Make the smallest necessary change
- **Test**: Verify fix works
- **Verify**: Ensure no new issues

### 6. Prevent

Stop it from happening again:

- **Add Tests**: Cover this case
- **Improve Logging**: Better diagnostics
- **Document**: Update docs
- **Alert**: Add monitoring

## Debugging Techniques

### Binary Search
- Divide the problem space in half
- Test which half contains the issue
- Repeat until isolated

### Rubber Duck Debugging
- Explain the problem line by line
- The act of explaining reveals assumptions
- Often leads to the solution

### Version Control
- Check when issue was introduced
- Compare working and broken versions
- Identify the exact change that caused it

### Logging Strategy
- Add context to existing logs
- Trace execution path
- Capture variable states

## Documentation Template

```markdown
# Debug Report

## Issue Summary
[Description of the problem]

## Reproduction
1. Steps to reproduce
2. Expected behavior
3. Actual behavior

## Analysis
- Root cause hypothesis
- Evidence collected
- Tests performed

## Solution
- What was changed
- Why it fixes the issue

## Prevention
- [ ] Added test: [Test description]
- [ ] Updated docs: [Location]
- [ ] Added monitoring: [Metric]
```

## Best Practices

1. **Start Simple**: Check obvious causes first
2. **Isolate**: One variable at a time
3. **Document**: Keep track of what you've tried
4. **Verify Fix**: Ensure problem is truly resolved
5. **Look Beyond**: Check related systems
6. **Learn**: Document lessons for future