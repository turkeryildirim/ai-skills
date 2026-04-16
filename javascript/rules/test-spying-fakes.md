---
title: Spy on Functions and Use Fake Timers
impact: MEDIUM
impactDescription: Uncontrolled Date.now, real timers, and global side effects make tests non-deterministic and slow.
tags: testing, spying, timers, vitest, jest, best-practices
---

# Spy on Functions and Use Fake Timers

Use `vi.spyOn` to observe real functions and `vi.useFakeTimers` to control time-dependent behavior without real delays.

## Bad Example

```typescript
// Real Date.now makes assertions time-sensitive
it("records creation timestamp", () => {
  const entry = createLogEntry("event");
  expect(entry.createdAt).toBeLessThan(Date.now() + 1000);
  // Passes or fails depending on system clock jitter
});

// Real setTimeout slows the suite
it("debounces input", async () => {
  const fn = debounce(callback, 300);
  fn("a");
  await new Promise((r) => setTimeout(r, 350)); // actually waits 350ms
  expect(callback).toHaveBeenCalled();
});

// Spying without restore pollutes other tests
it("logs info", () => {
  vi.spyOn(logger, "info");
  service.process("order-1");
  // logger.info stays mocked forever
});
```

## Good Example

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("Time-dependent behavior", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.spyOn(Date, "now").mockReturnValue(
      new Date("2024-01-01T12:00:00Z").getTime(),
    );
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("should record deterministic timestamp", () => {
    const entry = createLogEntry("event");
    expect(entry.createdAt).toEqual(new Date("2024-01-01T12:00:00Z"));
  });

  it("should debounce input", () => {
    const callback = vi.fn();
    const fn = debounce(callback, 300);

    fn("a");
    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(300);
    expect(callback).toHaveBeenCalledWith("a");
  });

  it("should log with spy and restore", () => {
    const loggerSpy = vi.spyOn(logger, "info");

    service.process("order-1");

    expect(loggerSpy).toHaveBeenCalledWith("Processing order order-1");
    // afterEach restores the spy automatically
  });
});
```

## Why

- **Benefit**: Fake `Date.now` gives deterministic timestamps so assertions are exact, not approximate.
- **Benefit**: `vi.advanceTimersByTime` eliminates real waits, making timer tests instant.
- **Benefit**: `vi.restoreAllMocks` in `afterEach` prevents spies from leaking into sibling tests.
