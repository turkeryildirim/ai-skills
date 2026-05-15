---
name: swiftui-architecture-guide
description: SwiftUI architecture pattern benchmarks (MVVM, TCA, MV pattern), state ownership rules, navigation patterns (NavigationStack, Coordinator), Swift Concurrency integration, and SwiftData design for architectural analysis.
type: reference
---

# SwiftUI Architecture Guide

Reference for analyzing SwiftUI-first iOS/macOS projects (Swift 5.9+ / iOS 16+).

## Maturity Levels

| Level | Signals |
|-------|---------|
| **Level 1** | All state and logic in View structs, no ViewModels |
| **Level 2** | `@State` for everything, some extracted subviews |
| **Level 3** | MVVM with `@StateObject` ViewModels, `.task {}` for async |
| **Level 4** | `@Observable` macro, NavigationStack with path, previews for all views |
| **Level 5** | TCA or clean MVVM, SwiftData, strict concurrency (`@MainActor`), >60% test coverage |

---

## Architectural Pattern Comparison

### MV Pattern (SwiftUI Native — small/medium apps)
```swift
// Pattern: Model drives View directly, no ViewModel layer
// ✅ Appropriate for: data-driven apps, SwiftData, simple CRUD

@Observable
final class OrderStore {
    var orders: [Order] = []
    func load() async { ... }
}

struct OrderListView: View {
    var store: OrderStore  // ✅ @Observable — no wrapper needed

    var body: some View {
        List(store.orders) { OrderRowView(order: $0) }
            .task { await store.load() }
    }
}

Signals: @Observable classes, no explicit ViewModel suffix
⚠️ Watch for: store logic growing too large (>200 lines → split by feature)
```

### MVVM (Recommended for medium–large apps)
```swift
// Pattern: View ← binds to → ViewModel ← calls → Services/Repositories

@MainActor
@Observable
final class OrderListViewModel {
    var orders: [Order] = []
    var isLoading = false
    private let service: OrderServiceProtocol

    init(service: OrderServiceProtocol = OrderService()) {
        self.service = service
    }

    func loadOrders() async {
        isLoading = true
        defer { isLoading = false }
        orders = (try? await service.fetchOrders()) ?? []
    }
}

struct OrderListView: View {
    @StateObject private var viewModel = OrderListViewModel()
    // or: var viewModel: OrderListViewModel  (with @Observable)
}

Signals: *ViewModel.swift files, @MainActor annotation, protocol dependencies
✅ ViewModel is testable without SwiftUI
⚠️ Watch for: ViewModels that import SwiftUI (should not)
```

### TCA (The Composable Architecture — large/team apps)
```swift
// Pattern: State → Action → Reducer → Effect → State (unidirectional)
// Library: pointfreeco/swift-composable-architecture

@Reducer
struct OrderListFeature {
    @ObservableState
    struct State: Equatable {
        var orders: [Order] = []
        var isLoading = false
    }
    enum Action {
        case loadOrders
        case ordersLoaded([Order])
    }
    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .loadOrders:
                state.isLoading = true
                return .run { send in
                    let orders = try await orderClient.fetch()
                    await send(.ordersLoaded(orders))
                }
            case let .ordersLoaded(orders):
                state.isLoading = false
                state.orders = orders
                return .none
            }
        }
    }
}

Signals: ReducerProtocol / @Reducer, Store, ViewStore, .run {}
⚠️ Watch for: mixing TCA Stores with @StateObject ViewModels in same feature
```

---

## Navigation Architecture

### NavigationStack (iOS 16+) — Recommended
```swift
// ✅ Path-based — supports deep linking and state restoration
@Observable
final class AppRouter {
    var path: [AppRoute] = []

    enum AppRoute: Hashable {
        case orderDetail(Order)
        case checkout
    }
}

struct ContentView: View {
    @State private var router = AppRouter()

    var body: some View {
        NavigationStack(path: $router.path) {
            OrderListView()
                .navigationDestination(for: AppRouter.AppRoute.self) { route in
                    switch route {
                    case .orderDetail(let order): OrderDetailView(order: order)
                    case .checkout:               CheckoutView()
                    }
                }
        }
        .environment(router)
    }
}

✅ Programmatic push: router.path.append(.orderDetail(order))
✅ Pop to root:        router.path = []
```

### NavigationView (Deprecated — iOS 13-15 only)
```swift
// ❌ Avoid in new code targeting iOS 16+
NavigationView { ... }  // → replace with NavigationStack
```

---

## SwiftData Design Benchmarks

```swift
// ✅ Healthy @Model class
@Model
final class Order {
    var id: UUID
    var createdAt: Date
    var status: OrderStatus  // ✅ Enum with RawValue
    @Relationship(deleteRule: .cascade) var items: [OrderItem]

    init(id: UUID = .init(), status: OrderStatus = .pending) {
        self.id = id
        self.createdAt = .now
        self.status = status
    }
}

// ✅ ModelContainer set up at app root
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Order.self, OrderItem.self])
    }
}

// ✅ @Query in views for reactive fetching
struct OrderListView: View {
    @Query(sort: \Order.createdAt, order: .reverse) var orders: [Order]
}

❌ Warning signals:
@Model class with computed properties doing network calls
ModelContext passed down through many views (use @Environment(\.modelContext))
Heavy SwiftData queries on MainActor without background context
```

---

## State Ownership Quick Reference

```
View-local ephemeral state:    @State private var isExpanded = false
View owns reference type:      @StateObject private var vm = MyViewModel()
View receives reference type:  @ObservedObject var vm: MyViewModel  (or just var with @Observable)
App-wide shared state:         @EnvironmentObject var session: AuthSession
Two-way binding into @Observable: @Bindable var vm: MyViewModel
SwiftData fetching:            @Query var items: [Item]
SwiftData context:             @Environment(\.modelContext) var context
```

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **Massive View Body** | >100 lines, inline network calls | Untestable, poor Previews |
| **Wrong state wrapper** | `@ObservedObject var vm = VM()` without `@StateObject` | VM recreated on every render |
| **@EnvironmentObject overuse** | Every sub-feature reads from global env | Hidden dependencies, hard to preview |
| **DispatchQueue in ViewModel** | `DispatchQueue.main.async` in new code | Should use `@MainActor` or `await MainActor.run` |
| **SwiftUI in ViewModel** | `import SwiftUI` in ViewModel file | Breaks testability, couples to framework |
| **Navigation in View body** | `NavigationLink(destination:)` without path binding | Cannot deep link or restore state |
| **No #Preview** | Views not previewable without full app | Slows development, no canvas |
| **Hardcoded API keys** | `let key = "sk-..."` | Security vulnerability |
| **Missing @MainActor** | `@Observable` class with no actor annotation | Data race under Swift 6 strict concurrency |
