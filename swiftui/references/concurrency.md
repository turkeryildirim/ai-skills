# Swift Concurrency (Swift 6.3+)

Expert guidance for structured concurrency, actors, and strict concurrency checking in SwiftUI applications.

## Review Process (12-Step)

1. Scan for dangerous patterns (DispatchQueue, Thread, unsafe casts)
2. Check Swift 6.3 concurrency behaviors and default isolation
3. Validate actor usage for reentrancy and isolation
4. Ensure structured concurrency preference over unstructured tasks
5. Check unstructured task correctness
6. Verify proper cancellation handling
7. Validate async streams and continuations
8. Review sync/async bridging code
9. Assess legacy concurrency migrations (GCD → async/await)
10. Cross-check against common failure modes
11. Map strict-concurrency compiler diagnostics
12. Review async test patterns if applicable

## 1. Core Principles

- **Swift 6 Strict Checking:** All code must compile with "Strict Concurrency Checking" set to "Complete".
- **Structured Concurrency:** Prefer `TaskGroup` for multiple concurrent operations. Avoid unstructured `Task {}` unless bridging from non-async contexts.
- **Actor Isolation:** Use `actor` for shared mutable state. Use `@MainActor` for code that interacts with the UI.
- **GCD Replacement:** Favor Swift concurrency over Grand Central Dispatch for all new code.

## 2. Structured Concurrency

### Task Groups
Use `withTaskGroup` or `withThrowingTaskGroup` to manage child tasks:
```swift
let results = try await withThrowingTaskGroup(of: Item.self) { group in
    for id in ids {
        group.addTask { try await fetch(id: id) }
    }
    return try await group.reduce(into: []) { $0.append($1) }
}
```

- **Cooperative Cancellation:** Always check `Task.isCancelled` or call `try Task.checkCancellation()` in long-running loops.
- **Priority:** Set appropriate `TaskPriority` (`.userInitiated`, `.utility`, `.background`).

### Async/Await
- Prefer `async`/`await` over completion handlers for all new code.
- Use `withCheckedContinuation` only when wrapping legacy APIs (not as a pattern).

## 3. Actors and Isolation

- **Global Actors:** Use `@MainActor` on ViewModels and Views to ensure UI updates happen on the main thread.
- **Default Actor Isolation (Swift 6.2+):** Actors are more strictly isolated by default. Be explicit.
- **Sendable:** Types passed across concurrency boundaries must conform to `Sendable`. Prefer value types (structs, enums) as they are implicitly Sendable.
- **Nonisolated:** Use `nonisolated` for methods that don't access actor-isolated state — improves performance.
- **Reentrancy:** Actors can be re-entered between `await` points. Don't assume exclusive state between awaits.

## 4. Concurrency in SwiftUI

- **`.task` Modifier:** Use `.task { ... }` instead of `.onAppear { Task { ... } }`. Automatically cancels when view disappears.
- **Async Streams:** Use `AsyncStream` to bridge stream-based data (WebSockets, Location, NotificationCenter) into SwiftUI.
- **MainActor Inference:** Classes conforming to `@Observable` do NOT automatically become `@MainActor`. Mark explicitly when handling UI state.
- **Continuation Safety:** Each `withCheckedContinuation` must resume exactly once; use `withCheckedThrowingContinuation` for failable bridges.

## 5. Unstructured Tasks

- Use `Task { }` only when structured concurrency isn't available (e.g., in synchronous callbacks).
- Store the `Task` handle if cancellation from outside is needed.
- Do NOT use `Task {}` inside `ForEach` or similar loops — this creates unmanaged tasks.

## 6. Async Streams and Bridges

```swift
// Bridge delegate callbacks to AsyncStream
let (stream, continuation) = AsyncStream.makeStream(of: CLLocation.self)
// In delegate: continuation.yield(location)
// In view:
for await location in stream { update(location) }
```

## 7. Legacy Migration (GCD → Swift Concurrency)

| Legacy Pattern | Modern Replacement |
|---------------|-------------------|
| `DispatchQueue.main.async { }` | `await MainActor.run { }` or `@MainActor` |
| `DispatchQueue.global().async { }` | `Task.detached(priority: .background)` |
| Completion handlers | `async throws` functions |
| `OperationQueue` | `TaskGroup` |

## 8. MUST NOT DO

## Cross References

- Related rules: `conc-strict-checking`, `conc-actor-isolation`, `conc-task-groups`, `conc-cooperative-cancellation`, `conc-no-unchecked-sendable`, `swiftui-task-lifecycle`
- Related references: [`state-management.md`](state-management.md), [`navigation.md`](navigation.md), [`networking.md`](networking.md), [`performance.md`](performance.md)

- **@unchecked Sendable:** Never use this as a "quick fix". Solve the underlying data race instead; address the root cause.
- **Blocking the Main Thread:** Never perform heavy computation or I/O on the `@MainActor`. Use a background `Task` or separate `actor`.
- **Thread.sleep:** Never use in async code; use `try await Task.sleep(for: .seconds(1))`.
- **Third-Party Frameworks:** Do not introduce Combine, RxSwift, or other concurrency frameworks without user consent.
- **Unstructured in Loops:** Do NOT call `Task { }` inside a loop without the parent task collecting results.
