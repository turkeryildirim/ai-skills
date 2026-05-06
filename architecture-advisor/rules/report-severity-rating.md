---
title: Issue Severity Rating
impact: HIGH
impactDescription: "Consistent severity ratings enable teams to prioritize correctly"
tags: report, severity, rating, prioritization
---

## Issue Severity Rating

**Impact: HIGH (Consistent severity ratings enable teams to prioritize correctly)**

Without consistent severity criteria, every issue becomes equally important — which means nothing gets prioritized. Use the four-level severity scale below for every finding in the report.

## Severity Levels

### CRITICAL — Fix Before Next Release
An issue that is causing active harm, exposes security vulnerabilities, blocks scalability, or makes the codebase fundamentally untestable. These are not theoretical risks.

```
Examples:
- SQL injection or raw user input in database queries
- Business logic only accessible via HTTP (cannot run in CLI, queue, test)
- Circular dependencies that cause import errors in production
- Hardcoded API keys or credentials in source files
- All code in one file (impossible to maintain)
```

### HIGH — Fix in Current Sprint
An issue that significantly increases maintenance burden, causes test coverage gaps, or violates the primary conventions of the language/framework. Not immediately dangerous but will compound over time.

```
Examples:
- Controllers/ViewControllers over 200 lines with mixed concerns
- No service layer (all logic in route handlers)
- Concrete class dependencies where interfaces should be used
- State management mismatch (global store used for local state)
- Missing error handling strategy (each handler catches differently)
```

### MEDIUM — Schedule in Backlog
An issue that reduces code quality or creates friction but does not block development. Should be addressed but is not urgent.

```
Examples:
- Inconsistent naming conventions across the codebase
- Missing type annotations in a TypeScript project using `any` occasionally
- One god-object utility file that should be split
- No source maps configured for production builds
- Minor props drilling (2-3 levels)
```

### LOW — Nice to Have
An issue that is purely cosmetic, stylistic, or represents a minor deviation from best practices. Useful for completeness but should not consume sprint capacity.

```
Examples:
- Missing `autoload-dev` section in composer.json
- JSDoc comments absent on public utility functions
- Folder names inconsistent (some plural, some singular)
- Minor unused imports in 2-3 files
```

## Incorrect Usage

```markdown
❌ Using CRITICAL for everything

[CRITICAL] Missing JSDoc on helper function
[CRITICAL] Folder is named "util" instead of "utils"
[CRITICAL] Color variables not using CSS custom properties

// Result: developers ignore the report entirely —
// if everything is critical, nothing is critical
```

## Correct Usage

```markdown
✅ Calibrated severity

[CRITICAL] API key hardcoded in src/config/stripe.ts:12
[HIGH] No input validation on POST /orders endpoint
[MEDIUM] Inconsistent error response format (some return {error}, some return {message})
[LOW] README doesn't document local setup steps
```

## Why

- **Triage**: Teams have limited time — severity guides where to spend it
- **Trust**: Inflated severity ratings cause report fatigue and loss of credibility
- **Backlog**: Severity maps to sprint priority — CRITICAL = this sprint, HIGH = next sprint, MEDIUM = backlog, LOW = someday
