---
name: javascript-architecture-guide
description: Vanilla JavaScript and browser JS architecture patterns, module system benchmarks, and tooling configuration reference for architectural analysis.
type: reference
---

# JavaScript Architecture Guide

Reference for analyzing vanilla JS / browser JS / build-tool frontend projects without a major UI framework.

## Maturity Levels

| Level | Description | Signals |
|-------|-------------|---------|
| **Level 1** | Script tags, globals | `<script src>` files, `window.myApp`, no module system |
| **Level 2** | Bundled | webpack/Vite entry, but all in one file |
| **Level 3** | Modular ESM | Clean `import`/`export`, feature folders |
| **Level 4** | TypeScript | `tsconfig.json`, `strict: true`, typed throughout |
| **Level 5** | Typed + Tested | TypeScript + Vitest/Jest, >60% coverage |

---

## Module System Quick Reference

### ESM (Modern — Preferred)
```javascript
// package.json: "type": "module"
export const calculateTax = (amount, rate) => amount * rate;
import { calculateTax } from './tax.js';
```

### CommonJS (Legacy)
```javascript
// No "type" field in package.json (default)
module.exports = { calculateTax: (amount, rate) => amount * rate };
const { calculateTax } = require('./tax');
```

### Detection
```bash
# Check module system:
cat package.json | grep '"type"'
# "type": "module" → ESM
# absent → CJS (default)

# Check for mixing:
grep -r "require(" src/ --include="*.js"  # Should be empty in ESM project
grep -r "^import " src/ --include="*.js"  # Should be empty in CJS project
```

---

## Healthy Project Structure

```
src/
├── features/            → Feature-based organization (preferred)
│   ├── cart/
│   │   ├── cart.js      → Cart state and logic
│   │   ├── cart-ui.js   → Cart DOM rendering
│   │   └── index.js     → Public API of feature
│   └── checkout/
├── shared/              → Shared across features
│   ├── api.js           → HTTP client
│   ├── storage.js       → localStorage/sessionStorage wrapper
│   └── events.js        → Custom event bus (if needed)
├── utils/               → Pure functions, no side effects
│   ├── format.js        → Date, currency, string formatting
│   └── validation.js    → Input validation functions
└── main.js              → Entry point, feature initialization
```

---

## Bundler Selection Guide

| Bundler | Best For | Avoid When |
|---------|----------|------------|
| **Vite** | SPAs, modern browser targets, fast dev | Library publishing |
| **Rollup** | Library publishing, small output | Complex app with many async chunks |
| **Webpack 5** | Legacy projects, complex chunk splitting | New projects (prefer Vite) |
| **esbuild** | CLI tools, build steps, simple scripts | Complex code splitting needs |
| **Parcel** | Zero-config prototypes | Production apps needing fine control |

---

## TypeScript Migration Signals

For JS projects without TypeScript, assess whether TypeScript adoption is warranted:

| Signal | Threshold | Recommendation |
|--------|-----------|----------------|
| File count | >20 JS files | TypeScript recommended |
| LOC | >3,000 lines | TypeScript recommended |
| Team size | >2 developers | TypeScript strongly recommended |
| Public API | Yes | TypeScript required |
| `any` workarounds in JSDoc | Frequent | Full TypeScript more practical |

### Gradual Migration Path
```
Phase 1: Add tsconfig.json with "allowJs": true, "checkJs": true
Phase 2: Rename files to .ts one-by-one, fix type errors
Phase 3: Enable "strict": true
Phase 4: Remove "allowJs" once all files are .ts
```

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **Global Namespace** | `window.myApp.*` for state | Implicit dependencies, testing impossible |
| **Mega utils.js** | Single file >300 lines | Not tree-shakeable, low discoverability |
| **Mixed Module Systems** | `require()` in ESM project | Build failures, broken tree-shaking |
| **No Source Maps** | Build config missing `sourcemap: true` | Production errors undebuggable |
| **Development Build in Prod** | `mode: 'development'` in webpack prod config | 3-5x larger bundle size |
| **Circular Imports** | A imports B, B imports A | Runtime `undefined` export bugs |
