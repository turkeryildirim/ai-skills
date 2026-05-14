# SwiftUI Performance Optimization

Expert guidance for identifying and fixing performance bottlenecks in SwiftUI applications.

## 1. Understanding Re-rendering

SwiftUI re-renders a view when its `@State`, `@Binding`, or accessed `@Observable` properties change.
- **Minimal Property Access:** Access only the properties you need inside `body`.
- **Observation Tracking:** iOS 17+ tracks only properties *actually accessed* during body execution.
- **Equatable Views:** Add `Equatable` conformance to views with expensive bodies — SwiftUI skips re-render when inputs are equal.

## 2. Diagnostic Tools

- **`Self._printChanges()`:** Call inside `body` to see which property triggered a re-render.
- **Instruments (SwiftUI instrument):** Analyze view body execution times and invalidations.
- **Trace Analysis:** Record `.trace` files to identify "hot paths" and unnecessary work.
- **Xcode Preview performance:** Use `#Preview` with realistic data to catch layout issues early.

## 3. Efficient Collections

| Container | Performance Characteristic |
|-----------|---------------------------|
| `List` | Built-in row reuse, best for standard lists |
| `LazyVStack` + `ScrollView` | On-demand creation, best for custom layouts |
| `VStack` | Renders all immediately, only for small collections (<50 items) |

- **ForEach Identity:** Ensure `id:` is truly unique and stable. Unstable IDs cause full list re-renders and scroll position loss.
- **Never use array indices** as IDs: `ForEach(items.indices, id: \.self)` is an anti-pattern.

## 4. Expensive Operations

- **Body is for UI:** Never perform calculations, networking, or I/O in `body`.
- **Computed Properties:** Cache expensive computed properties if called from `body`.
- **Images:** Use `.resizable()` and appropriate `.frame()` to prevent loading full-resolution images in lists.
- **Shadows and Blurs:** Minimize `.shadow()`, `.blur()`, and `.mask()` in scrollable lists — they are compositing-expensive.

```swift
// ✅ Move expensive work out of body
.task {
    await viewModel.loadExpensiveData()
}

// ❌ Never in body
var body: some View {
    let processed = expensiveComputation() // Re-runs on every render
    return Text(processed)
}
```

## 5. Memory Management

- **Reference Cycles:** Use `[weak self]` in closures, especially in ViewModels or long-running `Task` blocks.
- **Large Assets:** Be mindful of memory when loading large images in `ForEach`. Prefer `AsyncImage` or a caching layer.
- **Task Cancellation:** Store `Task` handles when you need to cancel on view disappearance; `.task {}` modifier handles this automatically.

## 6. View Invalidation Strategies

```swift
// ✅ Extract subview to limit invalidation scope
struct MessageRow: View, Equatable {
    let message: Message  // Only re-renders when this message changes
    var body: some View { /* ... */ }
}

// ✅ Access only needed properties from @Observable
struct UserBadge: View {
    let user: User  // Only tracks what's accessed in body
    var body: some View {
        Text(user.displayName)  // Only user.displayName tracked, not entire User
    }
}
```

## 7. Animation Performance

- Use `withAnimation` with `value:` parameter to scope animation to specific changes.
- Avoid animating on every state change; be explicit about what triggers animations.
- Prefer `spring()` presets (`.smooth`, `.snappy`, `.bouncy`) over manual timing curves.

## 8. MUST NOT DO

## Cross References

- Related rules: `swiftui-view-extraction`, `swiftui-lazy-layouts`, `swiftui-animation-scope`, `swiftui-task-lifecycle`
- Related references: [`view-structure.md`](view-structure.md), [`animations.md`](animations.md), [`concurrency.md`](concurrency.md), [`gestures.md`](gestures.md)

- **Unnecessary Bindings:** Don't create `@Binding` if the subview only needs read access. Pass the value directly.
- **Frequent Global Updates:** Avoid triggering updates in a global `@Observable` accessed by many views unless necessary.
- **Blocking Body:** No synchronous file I/O, heavy computation, or network calls in `body`.
- **Shadow/blur in ForEach rows:** Compositing cost multiplies with scroll velocity.
