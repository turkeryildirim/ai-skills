---
title: Use Promise Combinators for Concurrent Operations
impact: CRITICAL
impactDescription: Sequential awaits for independent operations waste time; wrong combinator ignores partial failures
tags: async, promises, concurrency, performance
---

# Use Promise Combinators for Concurrent Operations

Choose the right Promise combinator based on whether all results matter, partial failures are acceptable, or only the first result is needed.

## Bad Example

```typescript
// Sequential awaits for independent operations — total time is additive
async function loadDashboard(userId: string) {
  const user = await fetchUser(userId);       // 200ms
  const posts = await fetchPosts(userId);     // 300ms
  const stats = await fetchStats(userId);     // 150ms
  return { user, posts, stats };              // Total: ~650ms
}

// Promise.all when one failure shouldn't block others
async function sendNotifications(emails: string[]) {
  const results = await Promise.all(
    emails.map(email => sendEmail(email))
  );
  return results; // One rejected email rejects everything
}
```

## Good Example

```typescript
// Promise.all — parallel execution for independent operations
async function loadDashboard(userId: string) {
  const [user, posts, stats] = await Promise.all([
    fetchUser(userId),    // 200ms
    fetchPosts(userId),   // 300ms
    fetchStats(userId),   // 150ms
  ]);                     // Total: ~300ms (slowest wins)
  return { user, posts, stats };
}

// Promise.allSettled — best-effort, partial failures tolerated
async function sendNotifications(emails: string[]) {
  const results = await Promise.allSettled(
    emails.map(email => sendEmail(email))
  );
  const succeeded = results.filter(r => r.status === "fulfilled");
  const failed = results.filter(r => r.status === "rejected");
  failed.forEach(r => console.error("Failed:", r.reason));
  return { sent: succeeded.length, failed: failed.length };
}

// Promise.race — first result wins (e.g., timeout pattern)
const data = await Promise.race([
  fetchFromCache(key),
  fetchFromNetwork(key),
]);

// Promise.any — first success wins (e.g., fastest mirror)
const response = await Promise.any([
  fetch("https://mirror1.example.com/api"),
  fetch("https://mirror2.example.com/api"),
]);
```

## Why

- **Parallelism**: `Promise.all` runs independent operations concurrently, cutting total wait to the slowest one instead of the sum of all.
- **Resilience**: `Promise.allSettled` prevents one failure from discarding all other successful results.
- **Responsiveness**: `Promise.race` and `Promise.any` let you act on the fastest available result instead of waiting for every source.
