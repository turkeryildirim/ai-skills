---
name: report-template
description: Standard architecture analysis report template. Copy and fill in for every analysis output.
type: reference
---

# Architecture Analysis Report Template

Copy this template for every report. Fill in all sections — do not skip Strengths.

---

```markdown
# Architecture Report: [Project Name]

**Analysis Date:** YYYY-MM-DD  
**Stack:** [Language] [Version] / [Framework] [Version] / [Key Libraries]  
**Analyst Persona:** [arch-php-pro | arch-node-pro | arch-react-pro | arch-javascript-pro | arch-swift-pro]  
**Codebase Size:** ~[N] files / ~[N] lines of code (estimate from directory scan)  

---

## Executive Summary

[3-5 sentences. Cover: what the project is, its overall architectural health, the most critical issue, and the primary strength. This section is read by stakeholders who won't read the rest.]

Example:
> This Laravel 11 e-commerce backend follows a mostly idiomatic Laravel structure with proper Eloquent usage and FormRequest validation. The primary architectural concern is business logic concentrated in controllers rather than dedicated Action or Service classes, making key workflows untestable without HTTP. The codebase has good migration discipline and strong validation coverage. Priority action: extract controller logic to Action classes before the next major feature addition.

---

## Strengths

> List at least 3 genuine strengths. Skip this section is not acceptable.

- **[Strength Name]** — [Specific evidence and why it matters]
  Example: **FormRequest Validation** — All 14 write endpoints use dedicated FormRequest classes. Controllers remain thin and validation errors are consistent.

- **[Strength Name]** — [Specific evidence and why it matters]

- **[Strength Name]** — [Specific evidence and why it matters]

---

## Issues

> Sort by severity: CRITICAL first. Each issue must have all 5 fields.

### [CRITICAL] [Issue Title]
**Location:** `path/to/file.ext:line-range`  
**Evidence:** [Direct description of what was found — quote code or describe the pattern]  
**Impact:** [What goes wrong because of this issue — practical consequences]  
**Recommendation:** [Specific, actionable next step — name the file, class, or pattern to create/change]  
**Rule:** → `rule-id` (link to relevant rule in rules/)

---

### [HIGH] [Issue Title]
**Location:** `path/to/file.ext`  
**Evidence:** [...]  
**Impact:** [...]  
**Recommendation:** [...]  
**Rule:** → `rule-id`

---

### [MEDIUM] [Issue Title]
**Location:** `path/to/file.ext`  
**Evidence:** [...]  
**Impact:** [...]  
**Recommendation:** [...]  
**Rule:** → `rule-id`

---

### [LOW] [Issue Title]
**Location:** [...]  
**Evidence:** [...]  
**Impact:** [...]  
**Recommendation:** [...]  

---

## Architecture Overview

[Optional but recommended for complex projects. Include a simple text diagram of the current architecture and the target architecture if a refactor is recommended.]

### Current (As-Is)
```
HTTP Request
    │
    ▼
Controller (500 lines — business logic, DB queries, email sending)
    │
    ▼
Eloquent Model / DB::
```

### Recommended (To-Be)
```
HTTP Request
    │
    ▼
FormRequest (validation)
    │
    ▼
Controller (thin — calls action)
    │
    ▼
Action Class (single operation)
    ├── Service (business rules)
    └── Repository (data access)
```

---

## Language/Stack-Specific Findings

[Add any language-specific sections based on the persona used. Examples below:]

### PHP/Laravel
- **Framework Fit:** [Idiomatic / Partial / Fighting Framework]
- **PSR-4 Compliance:** [Compliant / N violations found]
- **Test Coverage Signals:** [tests/ directory present/absent, PHPUnit configured Y/N]

### React
- **State Management Assessment:** [Current solution vs recommended]
- **Component Quality:** [Average size estimate, props drilling depth]
- **Data Fetching Pattern:** [useEffect+fetch / React Query / SWR / Server Components]

### Node.js
- **Layer Compliance:** [Controller→Service→Repository present Y/N]
- **Error Handling:** [Centralized / Ad-hoc / Missing]
- **Security Middleware:** [Helmet Y/N, CORS Y/N, Rate limit Y/N, Validation Y/N]

### Swift
- **Architectural Pattern:** [MVC / MVVM / VIPER / TCA / None]
- **UIKit/SwiftUI Ratio:** [UIKit only / SwiftUI only / Mixed N%/N%]
- **Modularization:** [Single target / N SPM targets]

---

## Prioritized Action List

> Ready to drop into a sprint backlog. Ordered by impact.

1. [CRITICAL] [Specific action] — [File or component affected]
2. [CRITICAL] [Specific action]
3. [HIGH] [Specific action]
4. [HIGH] [Specific action]
5. [MEDIUM] [Specific action]
6. [LOW] [Specific action]

---

## What to Analyze Next

[Optional. Identify areas that need deeper investigation but were out of scope for this analysis.]

- [ ] Database query performance (requires running EXPLAIN ANALYZE)
- [ ] Security audit (recommend dedicated security-review skill)
- [ ] Test coverage report (requires running test suite with coverage flag)
```
