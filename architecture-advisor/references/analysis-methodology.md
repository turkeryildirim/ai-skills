---
name: analysis-methodology
description: Step-by-step methodology for conducting architecture analysis across any language or stack. Universal process that applies before language-specific rules.
type: reference
---

# Architecture Analysis Methodology

Universal process for conducting a thorough, repeatable architectural analysis. Apply this before any language-specific rules.

## Phase 1: Project Discovery (Always First)

### 1.1 Root Directory Scan
```
Read: top-level directory listing
Note:
  - Total file/directory count (size signal)
  - Presence of: tests/, docs/, .github/, docker/, infra/
  - Absence of: tests/ (no tests), docs/ (no documentation)
```

### 1.2 Configuration Files (Read All That Exist)
| File | What It Tells You |
|------|-------------------|
| `package.json` | Node/JS stack, framework, scripts, version |
| `composer.json` | PHP stack, framework, version |
| `Package.swift` | Swift SPM structure, external dependencies |
| `Podfile` | iOS external dependencies, CocoaPods |
| `.env.example` | External services, database engine, queue |
| `docker-compose.yml` | Runtime services, ports, environment |
| `Dockerfile` | Base image, build steps, exposed ports |
| `.github/workflows/*.yml` | CI commands (test, lint, build, deploy) |
| `.gitlab-ci.yml` | Same as above |
| `Makefile` | Common project commands |

### 1.3 Application Directory Map
Read the primary source directory (`src/`, `app/`, `Sources/`) and map:
```
What directories exist → What roles they likely play
What's missing → What patterns are absent
```

### 1.4 Code Sampling
Read at minimum:
- 2 entry-point/bootstrap files
- 2 business logic files (services, use cases, view models)
- 1 data access file (repository, model, DAO)
- 1 route/controller/view-controller file
- 1 test file (to gauge testing approach and coverage)

---

## Phase 2: Stack Detection

Run the tech detection process from `rules/scan-tech-detection.md`:
1. Read primary dependency file
2. Identify: language, framework, key libraries
3. Load matching language persona from `agents/`

---

## Phase 3: Analysis

Apply language-specific rules in priority order:

| Priority | What to Analyze |
|----------|----------------|
| 1 | **Layer structure** — is there clear separation between layers? |
| 2 | **Coupling** — are dependencies pointing the right direction? |
| 3 | **Framework idiom adherence** — is the framework used as intended? |
| 4 | **Security posture** — are inputs validated, secrets safe, auth enforced? |
| 5 | **Testability signals** — are there tests? Can code be tested without full bootstrap? |
| 6 | **Performance risks** — blocking operations, N+1 queries, missing caching |
| 7 | **Build and tooling** — is the build correctly configured? |

### Evidence Collection Format

For each finding, collect:
```
What: [description of the issue or strength]
Where: [file path + line number if specific]
Evidence: [direct quote or description from the code]
Impact: [why this matters in practical terms]
```

---

## Phase 4: Report Composition

Use `references/report-template.md` as the output template.

### Calibration Before Writing
Before writing findings:
1. **Count CRITICALs** — are there really that many? Re-evaluate if >5 (inflation risk)
2. **Count Strengths** — must be at least 3 real strengths (balance)
3. **Sort issues** — CRITICAL → HIGH → MEDIUM → LOW
4. **Deduplicate** — don't list the same root cause as 3 separate issues

### Finding vs Opinion Test
Every finding must pass:
- [ ] Can I point to a specific file or pattern in the codebase?
- [ ] Is the recommendation specific and actionable?
- [ ] Would a developer know exactly what to do next from reading this?

If any answer is "no" — rephrase or remove the finding.

---

## Common Analysis Mistakes to Avoid

| Mistake | Correction |
|---------|------------|
| Flagging something as CRITICAL based on guessing | Read the actual file first |
| Reporting "no tests" without checking the test directory | Always check `tests/`, `spec/`, `__tests__/` |
| Recommending a pattern without knowing the team's framework | Tailor recommendations to detected framework |
| Listing only issues — no strengths | Balance is required for credibility |
| Vague recommendations ("improve the code") | Specific recommendations ("move business logic from OrderController to OrderService") |
| Applying React rules to a Vue project | Stack detection before analysis |

---

## Multi-Stack Projects

For projects with separate backend + frontend:
1. Analyze each sub-project independently
2. Use matching persona for each
3. Add a "Cross-Stack Integration" section covering:
   - API contract consistency (does frontend match backend response shape?)
   - Authentication handoff (JWT, session, OAuth2 flow)
   - Shared type definitions (if any)
   - Deployment coupling (same CI/CD? separate?)
