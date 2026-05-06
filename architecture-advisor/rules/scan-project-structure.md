---
title: Systematic Project Structure Scan
impact: CRITICAL
impactDescription: "Prevents false findings caused by incomplete project understanding"
tags: scanning, methodology, project-structure, onboarding
---

## Systematic Project Structure Scan

**Impact: CRITICAL (Prevents false findings caused by incomplete project understanding)**

An architectural analysis is only as good as the data collected during the initial scan. Jumping to conclusions after reading two files leads to missed issues, inaccurate tech stack detection, and shallow reports that damage credibility. Always complete a full structural scan before forming any opinion.

## Incorrect

```
// ❌ Analyst reads one controller file and starts reporting

// After reading: src/UserController.php
Report: "This is a Laravel project using MVC.
Issue: UserController is too large."

// Problems:
// - Stack detection is a guess (no composer.json read)
// - Skipped: services/, jobs/, events/, tests/ directories
// - No idea if the large controller is an outlier or the norm
// - Missed: Docker, CI config, environment setup
// - Cannot assess test coverage without reading the test directory
```

## Correct

```
// ✅ Step 1: List root directory
ls -la (or equivalent directory read)
→ Reveals: src/, tests/, docker/, .github/, docs/, Makefile, composer.json

// ✅ Step 2: Read all configuration files
Read: composer.json OR package.json OR Package.swift OR Podfile
→ Reveals: framework, language version, key dependencies

Read: .env.example OR config/*.php OR .env.sample
→ Reveals: external services, database engine, queue driver

Read: docker-compose.yml OR Dockerfile (if present)
→ Reveals: runtime environment, service dependencies

Read: CI config (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
→ Reveals: test commands, deployment pipeline, linting setup

// ✅ Step 3: Map application directory structure
List: src/ OR app/ OR Sources/
→ Note: folder names and their roles (controllers/, services/, models/, etc.)

// ✅ Step 4: Sample code files (3-5 per layer)
Read: 2 entry-point files (routes, main bootstrap)
Read: 2 business logic files (services, use cases, interactors)
Read: 1 data access file (repository, model, DAO)
Read: 1 test file (to gauge testing approach)

// ✅ Step 5: Note what is ABSENT
Missing tests/ directory → low test coverage
Missing config/ validation → raw env access
Missing interfaces/ or protocols/ → tight coupling likely
```

## Why

- **Completeness**: Real architectural issues often live in directories you didn't expect
- **Context**: A large controller is CRITICAL if all controllers are small; LOW if they're all large and it's a known constraint
- **Credibility**: Stakeholders dismiss reports that miss obvious facts visible from the root listing
- **Tech detection accuracy**: Framework version, ORM choice, queue driver — all visible only from config files

## Scan Checklist

```
[ ] Root directory listed
[ ] Primary dependency file read (composer.json / package.json / Package.swift)
[ ] Environment config file read (.env.example / config/)
[ ] Infrastructure config read (docker-compose.yml / Dockerfile)
[ ] CI/CD config read (if present)
[ ] Application directory structure mapped
[ ] Minimum 5 source files sampled across layers
[ ] Test directory structure examined
[ ] Noted: what is MISSING (no tests/, no interfaces/, no docs/)
```
