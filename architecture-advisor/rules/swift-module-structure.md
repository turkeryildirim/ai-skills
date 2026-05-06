---
title: Swift Module and Package Structure Analysis
impact: HIGH
impactDescription: "Missing modularization in large Swift projects causes slow build times and tight coupling"
tags: swift, spm, modules, targets, package-structure, build-time
---

## Swift Module and Package Structure Analysis

**Impact: HIGH (Missing modularization in large Swift projects causes slow build times and tight coupling)**

Swift Package Manager (SPM) enables true modular architecture: separate targets for features, shared utilities, and network layers. When a codebase larger than 10,000 lines of Swift lives in a single target with no modular boundaries, build times grow linearly, coupling is invisible (no compile-time enforcement), and features cannot be developed independently.

## Incorrect

```swift
// ❌ Single monolithic target — everything in one Xcode target

MyApp (target)
├── Models/
│   ├── User.swift
│   ├── Order.swift
│   └── Product.swift
├── Services/
│   ├── UserService.swift
│   ├── OrderService.swift
│   └── AnalyticsService.swift   // ❌ Analytics coupled to main target
├── Features/
│   ├── Login/
│   ├── Orders/
│   └── Profile/
└── Utilities/
    └── Extensions.swift

// All 15,000 lines compile together on every change
// Analytics code can freely import Order models (accidental coupling)
// No way to develop Login feature in isolation
```

```swift
// ❌ Circular SPM target dependencies

// Package.swift
targets: [
    .target(name: "UserFeature", dependencies: ["OrderFeature"]),
    .target(name: "OrderFeature", dependencies: ["UserFeature"]), // ❌ Circular
]
// This fails to compile
```

## Correct

```swift
// ✅ SPM multi-target modular structure

// Package.swift
let package = Package(
    name: "MyApp",
    targets: [
        // ✅ Core/shared layer — no dependencies on feature targets
        .target(name: "SharedModels", dependencies: []),
        .target(name: "NetworkKit", dependencies: ["SharedModels"]),
        .target(name: "Analytics", dependencies: ["SharedModels"]),

        // ✅ Feature targets — depend only on Core, not on each other
        .target(
            name: "LoginFeature",
            dependencies: ["SharedModels", "NetworkKit"]
        ),
        .target(
            name: "OrderFeature",
            dependencies: ["SharedModels", "NetworkKit", "Analytics"]
        ),
        .target(
            name: "ProfileFeature",
            dependencies: ["SharedModels", "NetworkKit"]
        ),

        // ✅ App target composes features
        .target(
            name: "MyApp",
            dependencies: ["LoginFeature", "OrderFeature", "ProfileFeature"]
        ),

        // ✅ Test targets per module
        .testTarget(name: "LoginFeatureTests", dependencies: ["LoginFeature"]),
        .testTarget(name: "OrderFeatureTests", dependencies: ["OrderFeature"]),
    ]
)
```

## Dependency Graph Rules

```
✅ Valid dependency directions:
App → Feature → Core
Feature → Shared Utilities
Feature → NetworkKit
Core/Shared → (nothing from App or Feature)

❌ Invalid directions:
Core → Feature          (Core should not know about Features)
Feature A → Feature B   (Features should be independent)
Utility → Feature       (Utilities should be generic)
```

## Module Structure Assessment

```
Project size thresholds for modularization:
< 5,000 LOC  → Single target acceptable
5,000-10,000 → Consider: Core + App split
> 10,000 LOC → Modularization REQUIRED
> 50,000 LOC → Full feature module per domain area

Indicators of missing modularization (in a >10k LOC project):
❌ Single .xcodeproj target with all source files
❌ No Package.swift (still on CocoaPods with no SPM modules)
❌ Analytics/tracking code imported directly in feature files
❌ UI utilities importing business models
❌ Build time > 90 seconds for incremental builds (usually signals missing modularization)
```

## CocoaPods vs SPM Signal

```
CocoaPods (Podfile present, no Package.swift):
→ External dependencies only via CocoaPods — acceptable
→ No internal modularization unless using local podspecs

Package.swift present:
→ Check: is it used for internal modules or only wrapping external packages?
→ Multi-target = good; single target = missed opportunity

Both present (migration state):
→ Note as MEDIUM issue: mixed dependency management creates confusion
→ Recommend completing SPM migration
```

## Why

- **Build time**: Xcode only recompiles changed targets; a change in `Analytics` doesn't rebuild `OrderFeature` if they're separate targets
- **Coupling enforcement**: Swift cannot import a type from another target unless explicitly declared as a dependency — accidental coupling becomes a compile error
- **Team parallelism**: Teams can work on `OrderFeature` and `LoginFeature` in separate packages simultaneously
