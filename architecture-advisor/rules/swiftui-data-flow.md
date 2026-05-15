---
title: SwiftUI Data Flow and Concurrency Analysis
impact: HIGH
impactDescription: "Mixed async models and main-actor violations cause data races and UI freezes in SwiftUI apps"
tags: swiftui, data-flow, async-await, mainactor, task, swiftdata, combine
---

## SwiftUI Data Flow and Concurrency Analysis

**Impact: HIGH (Mixed async models and main-actor violations cause data races and UI freezes in SwiftUI apps)**

SwiftUI's rendering engine runs on the main thread. All `@Observable` / `ObservableObject` mutations that trigger view updates must happen on the main actor. Mixing Swift Concurrency with legacy GCD or Combine without clear boundaries introduces data races and inconsistent UI state.

## Incorrect

```swift
// ❌ DispatchQueue used inside SwiftUI ViewModel — bypasses actor isolation
class OrderViewModel: ObservableObject {
    @Published var orders: [Order] = []

    func loadOrders() {
        URLSession.shared.dataTask(with: url) { data, _, _ in
            let decoded = try? JSONDecoder().decode([Order].self, from: data!)
            DispatchQueue.main.async {           // ❌ should be @MainActor or await MainActor.run
                self.orders = decoded ?? []
            }
        }.resume()
    }
}

// ❌ State mutation from background thread without @MainActor
@Observable
class CartViewModel {
    var items: [CartItem] = []

    func syncWithServer() {
        Task.detached {               // ❌ detached task, not on MainActor
            let fetched = await self.fetchItems()
            self.items = fetched      // ❌ mutating @Observable off MainActor = data race
        }
    }
}

// ❌ Long-running work blocking main actor
@MainActor
class ReportViewModel: ObservableObject {
    @Published var report: Report?

    func generateReport() async {
        report = await heavyComputation()  // ❌ if heavyComputation is sync/CPU-bound, blocks UI
    }
}
```

## Correct

```swift
// ✅ @MainActor on ViewModel — all property mutations are safe
@MainActor
@Observable
final class OrderViewModel {
    var orders: [Order] = []
    var isLoading = false

    func loadOrders() async {
        isLoading = true
        defer { isLoading = false }
        do {
            orders = try await orderService.fetchOrders()  // ✅ await suspends, does not block
        } catch {
            // handle error
        }
    }
}

// ✅ .task modifier — tied to view lifecycle, auto-cancelled on disappear
struct OrderListView: View {
    @StateObject private var viewModel = OrderListViewModel()

    var body: some View {
        List(viewModel.orders) { order in OrderRowView(order: order) }
            .task { await viewModel.loadOrders() }  // ✅ cancels on view disappear
    }
}

// ✅ CPU-bound work offloaded off MainActor
@MainActor
final class ReportViewModel: ObservableObject {
    @Published var report: Report?

    func generateReport() async {
        report = await Task.detached(priority: .userInitiated) {
            await heavyComputation()  // ✅ runs off main thread, result awaited on main
        }.value
    }
}
```

## Data Flow Compliance Assessment

```
CRITICAL violations:
├── @Observable or @Published properties mutated from non-MainActor context (data race)
├── URLSession.dataTask callbacks without DispatchQueue.main.async updating @Published state
└── SwiftData ModelContext accessed from background thread

HIGH violations:
├── DispatchQueue.main.async in new code targeting iOS 15+ (use await MainActor.run)
├── .onAppear with async code not wrapped in Task { } or using .task modifier
└── Combine sink mutating ObservableObject on background scheduler without .receive(on: DispatchQueue.main)

MEDIUM violations:
├── Both Combine and async/await used in the same ViewModel without clear boundary
├── Task.detached used without clear reason (prefer Task { } which inherits actor context)
└── No cancellation of in-flight tasks when view disappears

LOW violations:
├── .task(id:) not used when task should re-run on parameter change
└── async let not used where parallel fetches would improve performance
```

## Concurrency Model Comparison (SwiftUI context)

| Pattern | Verdict | Use When |
|---------|---------|----------|
| `.task { await vm.load() }` | ✅ Preferred | One-off load on appear, auto-cancelled |
| `.task(id: value) { await vm.load() }` | ✅ Preferred | Reload on parameter change |
| `.onAppear { Task { await vm.load() } }` | ⚠️ Acceptable | When .task is not available |
| `.onAppear { URLSession.dataTask... }` | ❌ Avoid | No cancellation, wrong thread |
| Combine `.sink` for UI updates | ⚠️ Legacy | Only in existing Combine-heavy codebases |
| `DispatchQueue.main.async` in ViewModel | ❌ Avoid | Replaced by `@MainActor` in Swift 5.5+ |

## Why

- **`@MainActor`**: Annotating the ViewModel class ensures all property mutations happen on the main thread by contract — Swift compiler enforces this, no runtime race conditions
- **`.task` modifier lifetime**: Unlike `onAppear + Task {}`, `.task {}` is automatically cancelled when the view is removed from the hierarchy, preventing stale updates to deallocated views
- **Swift 6 strict concurrency**: Projects targeting Swift 6 concurrency mode will produce compile errors for the `CRITICAL` violations above — addressing them in Swift 5.9 prevents future migration pain
