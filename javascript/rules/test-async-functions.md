---
title: Test Async Functions with Proper Patterns
impact: HIGH
impactDescription: Missing await or unhandled rejections cause silent test failures and false positives.
tags: testing, async, vitest, jest, best-practices
---

# Test Async Functions with Proper Patterns

Async tests must properly await promises, assert rejections with dedicated matchers, and use fake timers instead of real delays.

## Bad Example

```typescript
// Forgetting await - promise is never settled, assertion never runs
it("fetches a user", () => {
  service.fetchUser("1").then((user) => {
    expect(user.name).toBe("John"); // silently skipped if promise rejects
  });
});

// Not testing the rejection path
it("handles not found", async () => {
  // This will throw an unhandled rejection
  const user = await service.fetchUser("999");
  expect(user).toBeNull();
});

// Using real timers makes tests slow and non-deterministic
it("retries after delay", async () => {
  await service.retryWithDelay(); // actually waits 5000ms!
  expect(fetch).toHaveBeenCalledTimes(3);
});
```

## Good Example

```typescript
describe("ApiService", () => {
  let service: ApiService;

  beforeEach(() => {
    service = new ApiService();
    vi.clearAllMocks();
  });

  it("should fetch user successfully", async () => {
    const mockUser = { id: "1", name: "John", email: "john@example.com" };
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    const user = await service.fetchUser("1");

    expect(user).toEqual(mockUser);
    expect(fetch).toHaveBeenCalledWith("https://api.example.com/users/1");
  });

  // Use rejects.toThrow for error paths
  it("should throw error if user not found", async () => {
    (fetch as any).mockResolvedValueOnce({ ok: false });

    await expect(service.fetchUser("999")).rejects.toThrow("User not found");
  });

  // Use fake timers instead of real delays
  it("should retry after delay", () => {
    vi.useFakeTimers();
    const callback = vi.fn();

    setTimeout(callback, 5000);
    vi.advanceTimersByTime(5000);

    expect(callback).toHaveBeenCalled();
    vi.useRealTimers();
  });
});
```

## Why

- **Benefit**: `await` ensures assertions actually execute; forgotten await is the most common source of false-green tests.
- **Benefit**: `rejects.toThrow` explicitly asserts rejection behavior instead of letting errors propagate as unhandled.
- **Benefit**: Fake timers make delay-dependent tests instant and deterministic, removing flakiness from CI.
