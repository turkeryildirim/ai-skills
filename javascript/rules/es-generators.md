---
title: Use Generators for Lazy and Streaming Data Processing
impact: HIGH
impactDescription: Loading entire datasets into memory causes OOM crashes; generators produce values on demand
tags: es6, generators, iterators, async-generators, lazy-evaluation
---

# Use Generators for Lazy and Streaming Data Processing

Use generator functions with `yield` to produce values on demand instead of building full arrays in memory. Use async generators with `for await...of` for streaming paginated or chunked data.

## Bad Example

```javascript
// Loads all 10,000 rows into memory at once
async function getAllUsers() {
  const response = await fetch("/api/users?limit=10000");
  const users = await response.json();
  return users; // huge array held entirely in memory
}

// Builds full Fibonacci array — crashes on large N
function fibonacciList(n) {
  const result = [];
  let prev = 0, curr = 1;
  for (let i = 0; i < n; i++) {
    result.push(curr);
    [prev, curr] = [curr, prev + curr];
  }
  return result; // O(n) memory for a sequence you may only partially consume
}

// Manual iterator protocol — verbose and error-prone
const range = {
  from: 1,
  to: 5,
  [Symbol.iterator]() {
    return {
      current: this.from,
      last: this.to,
      next() {
        if (this.current <= this.last) {
          return { done: false, value: this.current++ };
        }
        return { done: true };
      },
    };
  },
};
```

## Good Example

```javascript
// Generator — simple range, values produced on demand
function* rangeGenerator(from, to) {
  for (let i = from; i <= to; i++) {
    yield i;
  }
}
for (const n of rangeGenerator(1, 5)) {
  console.log(n); // 1, 2, 3, 4, 5
}

// Infinite lazy sequence — only computes what you consume
function* fibonacci() {
  let [prev, curr] = [0, 1];
  while (true) {
    yield curr;
    [prev, curr] = [curr, prev + curr];
  }
}

// Take only what you need — O(k) memory, not O(n)
const first20 = [...fibonacci()].slice(0, 20); // but better:
function* take(iterable, n) {
  let count = 0;
  for (const item of iterable) {
    if (count++ >= n) break;
    yield item;
  }
}
const first20Lazy = [...take(fibonacci(), 20)];

// Async generator for paginated API — streams page by page
async function* fetchPages(url) {
  let page = 1;
  while (true) {
    const response = await fetch(`${url}?page=${page}`);
    const data = await response.json();
    if (data.length === 0) break;
    yield data;
    page++;
  }
}

// Consume with for await...of — processes each page as it arrives
for await (const page of fetchPages("/api/users")) {
  for (const user of page) {
    processUser(user); // handle users without loading all pages first
  }
}

// Lazy transform pipeline — nothing runs until consumed
function* lazyMap(iterable, transform) {
  for (const item of iterable) {
    yield transform(item);
  }
}
```

## Why

- **Memory**: Generators produce one value at a time, keeping memory usage constant regardless of dataset size.
- **Composability**: Lazy generators can be chained (filter, map, take) and nothing executes until the final consumer iterates.
- **Streaming**: Async generators with `for await...of` handle paginated APIs, file streams, and real-time data without buffering everything first.
