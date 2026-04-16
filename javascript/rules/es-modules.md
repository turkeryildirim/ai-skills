---
title: Use ES Modules for Code Organization and Code Splitting
impact: MEDIUM
impactDescription: CommonJS prevents tree-shaking; monolithic files resist reuse and slow initial load times
tags: es6, modules, import, export, code-splitting
---

# Use ES Modules for Code Organization and Code Splitting

Use ES module `export`/`import` syntax instead of CommonJS `require`. Split code into focused modules and use dynamic `import()` for on-demand loading.

## Bad Example

```javascript
// CommonJS — no tree-shaking, synchronous loading
const _ = require("lodash");
const { validateEmail } = require("./utils");

module.exports = function processUser(user) {
  // entire lodash loaded even if only one function used
  return _.pick(user, ["name", "email"]);
};

// Everything in one file — no separation of concerns
// user-controller.js (2000 lines)
function getUser() { /* ... */ }
function createUser() { /* ... */ }
function deleteUser() { /* ... */ }
function validateInput() { /* ... */ }
function sendWelcomeEmail() { /* ... */ }
function generatePDF() { /* ... */ }
function processPayment() { /* ... */ }
// Hard to navigate, hard to test, hard to reuse
```

## Good Example

```javascript
// Named exports — tree-shakeable, explicit API
// math.js
export const PI = 3.14159;
export function add(a, b) { return a + b; }
export function multiply(a, b) { return a * b; }

// Default export — one main thing per module
// logger.js
export default class Logger {
  log(message) { console.log(`[LOG] ${message}`); }
}

// Named imports — only pull what you need
import { add, PI } from "./math.js";

// Default + named combined
import Logger, { add } from "./logger.js";

// Rename imports to avoid collisions
import { add as sum } from "./math.js";

// Dynamic import — code splitting, loads only when needed
async function loadChart() {
  const { Chart } = await import("./chart-module.js");
  return new Chart(canvas);
}

// Conditional loading
if (userPreferences.enableAnalytics) {
  const analytics = await import("./analytics.js");
  analytics.track("page_view");
}

// Barrel export — re-export from an index for clean imports
// utils/index.js
export { validateEmail, validatePhone } from "./validators.js";
export { formatDate, parseDate } from "./dates.js";
export { default as Logger } from "./logger.js";

// Consumer imports from one place
import { validateEmail, formatDate, Logger } from "./utils/index.js";
```

## Why

- **Tree-shaking**: ES module static imports let bundlers eliminate unused exports, reducing bundle size significantly compared to CommonJS `require`.
- **Organization**: Splitting code into focused modules with clear exports makes each file easier to understand, test, and reuse.
- **Performance**: Dynamic `import()` enables code splitting — heavy modules load only when needed instead of blocking initial page load.
