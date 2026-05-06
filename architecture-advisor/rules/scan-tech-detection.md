---
title: Technology Stack Detection
impact: CRITICAL
impactDescription: "Routing to the wrong language persona produces irrelevant findings"
tags: scanning, tech-detection, stack-identification, framework
---

## Technology Stack Detection

**Impact: CRITICAL (Routing to the wrong language persona produces irrelevant findings)**

Applying React architectural rules to a Node.js backend, or Laravel rules to a WordPress project, produces a report full of false positives and missed real issues. Always derive the stack from files — never guess from folder names or file extensions alone.

## Incorrect

```
// ❌ Guessing from file extensions only

// Analyst sees .php files → assumes "Laravel project"
// Reality: it's a WordPress plugin with raw SQL everywhere
// Result: report flags "missing Eloquent" — irrelevant

// ❌ Guessing from folder names
// Analyst sees "controllers/" → assumes MVC backend
// Reality: it's a NestJS project; "controllers" is the NestJS convention
// but the "services/" folder is empty — all logic is in controllers
```

## Correct

```
// ✅ Read the primary dependency file first

// PHP projects → read composer.json
{
  "require": {
    "laravel/framework": "^11.0",   // → Laravel 11
    "php": "^8.3"                   // → PHP 8.3+
  }
}
// → Stack: PHP 8.3 / Laravel 11 → load arch-php-pro

// ─────────────────────────────────────────────

// JavaScript projects → read package.json
{
  "dependencies": {
    "react": "^18.2.0",             // → React present
    "next": "^14.0.0"               // → Next.js → load arch-react-pro
  }
}

{
  "dependencies": {
    "express": "^4.18.0"            // → No UI framework → Node.js backend
  }
}
// → Stack: Node.js / Express → load arch-node-pro

{
  "dependencies": {
    "vite": "^5.0.0"                // + no react/vue →
  }
  // + no major framework deps      // Vanilla JS/TS → load arch-javascript-pro
}

// ─────────────────────────────────────────────

// Swift/iOS projects
// Package.swift present → SPM project
// .xcworkspace + Podfile → CocoaPods
// ContentView.swift → SwiftUI
// AppDelegate.swift (no ContentView) → UIKit
// → load arch-swift-pro
```

## Detection Matrix

| Signal File / Key | Stack | Persona to Load |
|---|---|---|
| `composer.json` with `laravel/framework` | Laravel | `arch-php-pro` |
| `composer.json` with `symfony/symfony` | Symfony | `arch-php-pro` |
| `wp-config.php` or `functions.php` | WordPress | `arch-php-pro` |
| `composer.json` (no framework key) | Plain PHP | `arch-php-pro` |
| `package.json` with `react` + `next` | Next.js | `arch-react-pro` |
| `package.json` with `react` (no next/remix) | React SPA | `arch-react-pro` |
| `package.json` with `express`/`fastify`/`@nestjs/core` | Node.js backend | `arch-node-pro` |
| `package.json` — bundler only, no UI framework | Vanilla JS | `arch-javascript-pro` |
| `Package.swift` or `.xcodeproj` | Swift/iOS | `arch-swift-pro` |

## Why

- **Relevance**: Framework-specific rules only apply to the framework in use
- **Trust**: A wrong stack identification immediately undermines the entire report
- **Routing accuracy**: The SKILL.md persona routing depends entirely on correct stack detection
- **Version matters**: Laravel 11 has different conventions than Laravel 8 — version affects findings

## Multi-Stack Projects

Some projects have both a backend and a frontend:
```
my-project/
├── backend/     → composer.json (Laravel)
├── frontend/    → package.json (React)
```

In this case:
1. Report both stacks explicitly
2. Run separate analysis for each sub-project
3. Use `arch-php-pro` for backend, `arch-react-pro` for frontend
4. Add a "Cross-Stack Integration" section to the report
