---
title: Never Use time.Sleep in Tests — Use require.Eventually or Channels
impact: HIGH
impactDescription: time.Sleep makes tests slow and flaky — too short and they race, too long and they waste time
tags: testing, async, time.Sleep, eventually, channels
---

## Never Use time.Sleep in Tests

**Impact: HIGH — time.Sleep makes tests slow and flaky; too short races, too long wastes CI time**

Async conditions should be tested with `require.Eventually`, channels, or context cancellation — not `time.Sleep`.

## Bad Example

```go
func TestWorkerProcessesJob(t *testing.T) {
    worker := NewWorker()
    worker.Start()

    worker.Submit(job)

    time.Sleep(100 * time.Millisecond) // fragile: too short on slow CI, too long locally

    assert.Equal(t, 1, worker.ProcessedCount())

    worker.Stop()
}
```

## Good Example — require.Eventually

```go
func TestWorkerProcessesJob(t *testing.T) {
    t.Parallel()

    worker := NewWorker()
    worker.Start()
    t.Cleanup(worker.Stop)

    worker.Submit(job)

    // Polls until condition is true or timeout
    require.Eventually(t,
        func() bool { return worker.ProcessedCount() == 1 },
        5*time.Second,       // timeout — fail if not met
        10*time.Millisecond, // poll interval — check frequency
        "worker did not process job within 5 seconds",
    )
}
```

## Good Example — Channel Notification

```go
func TestWorkerNotifiesCompletion(t *testing.T) {
    t.Parallel()

    done := make(chan struct{}, 1)
    worker := NewWorker(WithOnComplete(func() {
        close(done)
    }))
    worker.Start()
    t.Cleanup(worker.Stop)

    worker.Submit(job)

    // Wait for completion signal with timeout
    select {
    case <-done:
        // success
    case <-time.After(5 * time.Second):
        t.Fatal("worker did not complete within 5 seconds")
    }
}
```

## Good Example — Context Timeout

```go
func TestStreamReadsAllMessages(t *testing.T) {
    t.Parallel()

    ctx, cancel := context.WithTimeout(t.Context(), 5*time.Second)
    defer cancel()

    stream := NewMessageStream()
    go stream.Publish(ctx, messages)

    received := collectMessages(ctx, stream)
    require.Len(t, received, len(messages))
}
```

## Why

- **Reliability** — `require.Eventually` polls at a defined interval; it succeeds as soon as the condition is met, fails only after the timeout
- **Speed** — tests finish faster because they don't wait for fixed sleep durations
- **No races** — sleep durations that "work locally" regularly fail on slower CI machines
- **Clear intent** — `require.Eventually(t, condition, timeout, interval)` expresses what you're waiting for

Reference: [Testify Assertions](https://github.com/stretchr/testify#assert-package) | [Assertions reference](../references/assertions.md)
See also: `golang-tester/references/assertions.md`
