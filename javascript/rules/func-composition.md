---
title: Compose Functions with Pipe, Curry, and Memoize
impact: HIGH
impactDescription: Deeply nested calls are unreadable; repeated expensive computations waste CPU cycles
tags: functional, composition, pipe, curry, memoize
---

# Compose Functions with Pipe, Curry, and Memoize

Use `pipe`/`compose` to build linear data transformation pipelines instead of deeply nested calls. Use currying for reusable partial application and memoization to cache expensive results.

## Bad Example

```javascript
// Deeply nested function calls — read inside-out, hard to follow
const result = formatDisplay(
  calculateScore(
    normalizeData(
      validateInput(rawInput)
    )
  )
);

// Repeated expensive computation with same arguments
function calculateFibonacci(n) {
  if (n <= 1) return n;
  return calculateFibonacci(n - 1) + calculateFibonacci(n - 2);
}
// calculateFibonacci(40) recalculates the same values millions of times

// One-off multiplier functions instead of reusable curried factory
function double(x) { return x * 2; }
function triple(x) { return x * 3; }
function quadruple(x) { return x * 4; }
```

## Good Example

```javascript
// pipe — data flows top-to-bottom, easy to read and reorder
const pipe = (...fns) => (x) => fns.reduce((acc, fn) => fn(acc), x);

const processInput = pipe(
  validateInput,
  normalizeData,
  calculateScore,
  formatDisplay,
);
const result = processInput(rawInput);

// compose — same idea, right-to-left (mathematical order)
const compose = (...fns) => (x) => fns.reduceRight((acc, fn) => fn(acc), x);

// Currying — create specialized functions from a generic one
const multiply = (a) => (b) => a * b;
const double = multiply(2);
const triple = multiply(3);
const quadruple = multiply(4);

// Practical pipe with user data
const processUser = pipe(
  (user) => ({ ...user, name: user.name.trim() }),
  (user) => ({ ...user, email: user.email.toLowerCase() }),
  (user) => ({ ...user, age: parseInt(user.age, 10) }),
);

// Memoization with Map cache — compute once, reuse forever
function memoize(fn) {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}

const fibonacci = memoize((n) => {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
});
// fibonacci(40) now runs in O(n) instead of O(2^n)
```

## Why

- **Readability**: `pipe` reads top-to-bottom like a checklist; nested calls read inside-out and resist reordering.
- **Reusability**: Curried functions let you create specialized variants from a single generic function, eliminating duplication.
- **Performance**: Memoization caches results so repeated calls with the same arguments return instantly instead of recomputing.
