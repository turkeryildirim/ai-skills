---
title: JavaScript Module System Analysis
impact: HIGH
impactDescription: "Mixed or broken module systems cause build failures and circular dependency bugs"
tags: javascript, esm, commonjs, modules, circular-dependencies, imports
---

## JavaScript Module System Analysis

**Impact: HIGH (Mixed or broken module systems cause build failures and circular dependency bugs)**

Modern JavaScript has two module systems: ESM (`import`/`export`) and CommonJS (`require`/`module.exports`). Mixing them in a single project without explicit configuration causes runtime errors, broken tree-shaking, and bundler warnings. Circular dependencies — where A imports B and B imports A — cause subtle initialization bugs that are hard to trace.

## Incorrect

```javascript
// ❌ Mixing ESM and CommonJS in the same project

// src/utils/format.js — uses ESM
export const formatDate = (date) => date.toISOString();

// src/utils/logger.js — uses CommonJS
const formatDate = require('./format');  // ❌ Cannot require an ESM module
module.exports = { log: (msg) => console.log(formatDate(msg)) };

// src/index.js — mixes both
import { formatDate } from './utils/format.js';
const logger = require('./utils/logger');  // ❌ require in an ESM file
```

```javascript
// ❌ Circular dependency

// src/services/userService.js
import { getOrder } from './orderService.js'; // depends on orderService

// src/services/orderService.js
import { getUser } from './userService.js'; // depends on userService

// Result: one of these modules gets an undefined export at initialization time
// The bug only appears at runtime, not at build time in many configurations
```

```javascript
// ❌ Global namespace pollution
// All modules write to window.* for cross-module communication

// moduleA.js
window.sharedState = { count: 0 };

// moduleB.js
window.sharedState.count++; // Implicit dependency, invisible to bundler
```

## Correct

```javascript
// ✅ Consistent ESM throughout
// package.json
{ "type": "module" }  // All .js files treated as ESM

// src/utils/format.js
export const formatDate = (date) => date.toISOString();
export const formatCurrency = (cents) => `$${(cents / 100).toFixed(2)}`;

// src/utils/logger.js
import { formatDate } from './format.js'; // ✅ ESM import
export const log = (msg) => console.log(formatDate(msg));

// src/index.js
import { log } from './utils/logger.js';  // ✅ Consistent ESM
```

```javascript
// ✅ Breaking circular dependencies with a shared module
// Instead of A→B→A, extract the shared logic:

// src/shared/types.js — shared types/constants, no imports from A or B
export const OrderStatus = { PENDING: 'pending', COMPLETE: 'complete' };

// src/services/userService.js
import { OrderStatus } from '../shared/types.js'; // ✅ No circular dep

// src/services/orderService.js
import { OrderStatus } from '../shared/types.js'; // ✅ Same shared module
```

## What to Look For During Analysis

```javascript
// Check for module system in package.json
{ "type": "module" }       // → project uses ESM
// absent "type" field     // → defaults to CJS

// Check entry file imports
// ESM:
import x from './y.js';
export const z = ...;

// CJS:
const x = require('./y');
module.exports = { z: ... };

// Circular dependency detection
// Look for patterns where files in the same layer import each other:
// services/A imports services/B and services/B imports services/A
```

## Module System Detection Signals

| Signal | Conclusion |
|---|---|
| `"type": "module"` in package.json | Project uses ESM |
| No `"type"` field, `.js` files use `require()` | Project uses CJS |
| `.mjs` files present | ESM, regardless of package.json |
| `.cjs` files present | CJS, regardless of package.json |
| `require()` in a `"type": "module"` project | CRITICAL mixing issue |
| `import` in a CJS project without Babel/TS | Will fail at runtime |

## Why

- **Build reliability**: Bundlers (Vite, Webpack, Rollup) handle pure ESM or pure CJS cleanly; mixed projects produce warnings and sometimes broken output
- **Tree-shaking**: Only ESM enables dead code elimination — CJS bundles always include entire modules
- **Circular deps**: These cause `undefined` export bugs that are infamously hard to debug because they appear intermittently
