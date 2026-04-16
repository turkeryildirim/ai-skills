---
title: Handle Async/Await with Proper Error Handling and Concurrency
impact: CRITICAL
impactDescription: Unhandled rejections crash processes; missing concurrency wastes time and resources
tags: async, await, error-handling, retry, timeout
---

# Handle Async/Await with Proper Error Handling and Concurrency

Every async function needs structured error handling. Independent async calls should run in parallel, and network operations need retry logic and timeouts.

## Bad Example

```typescript
// Unhandled rejection — crashes the process in Node.js
async function getUser(id: string) {
  const response = await fetch(`/api/users/${id}`);
  return response.json(); // no error handling at all
}

// Sequential awaits for independent calls
async function loadProfile(id: string) {
  const user = await fetchUser(id);
  const settings = await fetchSettings(id); // doesn't depend on user
  const permissions = await fetchPermissions(id); // doesn't depend on user
  return { user, settings, permissions };
}

// No retry or timeout — single network hiccup fails the whole operation
async function fetchData(url: string) {
  const response = await fetch(url);
  return response.json();
}
```

## Good Example

```typescript
// try/catch with typed error handling
async function getUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch user ${id}:`, error);
    throw error; // re-throw so callers can still handle it
  }
}

// Promise.all for independent parallel calls
async function loadProfile(id: string) {
  const [user, settings, permissions] = await Promise.all([
    fetchUser(id),
    fetchSettings(id),
    fetchPermissions(id),
  ]);
  return { user, settings, permissions };
}

// Retry with exponential backoff
async function fetchWithRetry(url: string, retries = 3): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
  throw new Error("Unreachable");
}

// Timeout wrapper with Promise.race
async function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
  );
  return Promise.race([promise, timeout]);
}

// Combined: retry + timeout
const data = await withTimeout(
  fetchWithRetry("https://api.example.com/data", 3),
  5000
);
```

## Why

- **Stability**: try/catch prevents unhandled promise rejections that crash Node.js processes or silently fail in browsers.
- **Performance**: `Promise.all` runs independent operations concurrently instead of sequentially.
- **Reliability**: Retry with backoff recovers from transient network failures; timeouts prevent hanging on unresponsive services.
