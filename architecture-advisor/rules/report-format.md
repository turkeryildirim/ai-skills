---
title: Architecture Report Format
impact: HIGH
impactDescription: "Unstructured reports are ignored; structured reports drive action"
tags: report, format, structure, output
---

## Architecture Report Format

**Impact: HIGH (Unstructured reports are ignored; structured reports drive action)**

An architectural analysis has no value if its findings cannot be acted upon. A flat list of complaints without context, severity, or next steps will be ignored or misunderstood. Every report must follow a consistent structure that stakeholders can scan and act on.

## Incorrect

```markdown
❌ Unstructured report

# Code Review

The code has some issues. The controllers are large and the database queries 
are not optimized. There are no tests. The project structure is a bit messy 
but overall it works. The team should improve the code quality.

Problems:
- Large controllers
- No tests  
- Messy structure

// Issues:
// - No severity ratings
// - No code evidence (where exactly?)
// - No actionable recommendations
// - No strengths (unbalanced)
// - Cannot prioritize what to fix first
```

## Correct

```markdown
✅ Structured architecture report

# Architecture Report: [Project Name]
**Analyzed:** 2025-05-05  
**Stack:** PHP 8.3 / Laravel 11 / MySQL 8  
**Analyst Persona:** arch-php-pro  

---

## Executive Summary

Brief 3-5 sentence overview of the project's architectural health, key strengths, 
and the 1-2 most critical issues that need immediate attention.

---

## Strengths

> Always include at least 3 strengths. A balanced report earns trust.

- **PSR-4 Compliant Namespace Structure** — All namespaces match directory paths. 
  Autoloading works correctly and is easy to follow.
- **Form Request Validation** — All write endpoints use dedicated FormRequest classes. 
  Controllers stay thin.
- **CI Pipeline Present** — GitHub Actions runs tests on every PR.

---

## Issues

> Sort by severity: CRITICAL first, then HIGH, MEDIUM, LOW.

### [CRITICAL] Business Logic in Controllers
**Location:** `app/Http/Controllers/OrderController.php:45-220`  
**Evidence:** `OrderController::store()` is 175 lines, contains payment processing, 
inventory deduction, and email dispatch inline.  
**Impact:** Untestable without HTTP request, duplicated in `app/Console/Commands/ProcessOrder.php`.  
**Recommendation:** Extract to `app/Actions/Order/CreateOrderAction.php`. 
Inject `PaymentService`, `InventoryService` via constructor.  
**Rule:** → `php-framework-patterns`

---

### [HIGH] No Interface for External Services
**Location:** `app/Services/StripePaymentService.php` (used directly in 6 files)  
**Evidence:** Concrete class instantiated via `new StripePaymentService()` or resolved 
without binding.  
**Impact:** Cannot swap payment provider, cannot mock in tests.  
**Recommendation:** Create `app/Contracts/PaymentGateway.php` interface, bind in 
`AppServiceProvider`, inject interface everywhere.  
**Rule:** → `php-coupling-analysis`

---

### [MEDIUM] Raw SQL Mixed with Eloquent
**Location:** `app/Repositories/ReportRepository.php:88`  
**Evidence:** `DB::select('SELECT * FROM orders WHERE ...')` adjacent to Eloquent calls.  
**Impact:** Inconsistent data access patterns, bypasses Eloquent casting.  
**Recommendation:** Rewrite as Eloquent query builder. If performance requires raw SQL, 
isolate in a dedicated `QueryObject`.  
**Rule:** → `php-coupling-analysis`

---

## Prioritized Action List

> Ordered by impact. Use this as a backlog.

1. [CRITICAL] Extract `OrderController::store()` logic to Action class
2. [HIGH] Create `PaymentGateway` interface and bind concrete implementation
3. [HIGH] Add `EventServiceProvider` to remove inline event dispatches from controllers
4. [MEDIUM] Standardize data access to Eloquent (remove raw SQL from repositories)
5. [LOW] Add `composer.json` autoload-dev section for test utilities
```

## Why

- **Severity ratings** enable prioritization — teams fix CRITICAL before LOW
- **Evidence with file locations** makes findings verifiable, not opinions
- **Strengths section** builds trust and shows the report is balanced
- **Rule references** allow readers to understand the reasoning behind each finding
- **Actionable recommendations** give developers a clear next step, not just criticism
- **Prioritized action list** gives the team a ready-made backlog
