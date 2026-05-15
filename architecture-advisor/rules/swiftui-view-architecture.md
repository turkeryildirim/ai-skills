---
title: SwiftUI View Architecture Analysis
impact: HIGH
impactDescription: "Massive View bodies mixing business logic, data fetching, and layout make SwiftUI apps untestable and hard to maintain"
tags: swiftui, view, composition, body, viewmodifier, navigation, preview
---

## SwiftUI View Architecture Analysis

**Impact: HIGH (Massive View bodies mixing business logic, data fetching, and layout make SwiftUI apps untestable and hard to maintain)**

SwiftUI encourages composition of small, focused View structs. When a view's `body` grows to include network calls, conditional business logic, and complex layout, it becomes a SwiftUI equivalent of the Massive ViewController.

## Incorrect

```swift
// ❌ Massive View — layout, network, business logic all mixed
struct OrderListView: View {
    @State private var orders: [Order] = []
    @State private var isLoading = false
    @State private var searchText = ""
    @State private var selectedFilter: OrderFilter = .all

    var body: some View {
        VStack {
            // ❌ Inline business logic in body
            if orders.filter({ $0.status == .pending }).count > 5 {
                Text("Warning: too many pending orders")
                    .foregroundColor(.red)
            }
            // ❌ Formatting logic in body
            ForEach(orders) { order in
                HStack {
                    Text(order.date, formatter: DateFormatter())  // ❌ new DateFormatter() each render
                    Spacer()
                    Text("$\(String(format: "%.2f", order.total))")
                    Circle().fill(order.status == .complete ? .green : .red)
                        .frame(width: 8, height: 8)
                }
            }
        }
        .onAppear {
            // ❌ Network call in view body
            URLSession.shared.dataTask(with: URL(string: "https://api.example.com/orders")!) { data, _, _ in
                // ❌ JSON decoding + state mutation in view
            }.resume()
        }
    }
}
```

## Correct

```swift
// ✅ Decomposed into focused subviews and a ViewModel

// View — layout and UI logic only
struct OrderListView: View {
    @StateObject private var viewModel = OrderListViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else {
                OrderListContent(orders: viewModel.filteredOrders)  // ✅ extracted subview
            }
        }
        .searchable(text: $viewModel.searchText)
        .task { await viewModel.loadOrders() }  // ✅ async, cancels on disappear
    }
}

// ✅ Extracted subview — small, focused, previewable
struct OrderListContent: View {
    let orders: [Order]

    var body: some View {
        List(orders) { order in
            OrderRowView(order: order)  // ✅ row extracted
        }
    }
}

// ✅ Row view — single responsibility
struct OrderRowView: View {
    let order: Order

    var body: some View {
        HStack {
            Text(order.formattedDate)   // ✅ formatting in domain model or ViewModel
            Spacer()
            Text(order.formattedTotal)
            OrderStatusIndicator(status: order.status)  // ✅ extracted ViewModifier or subview
        }
    }
}
```

## View Complexity Assessment

```
CRITICAL violations:
├── View body >100 lines
├── Network or database calls directly in body or onAppear without async/await
└── Business logic (calculations, conditions) embedded in body

HIGH violations:
├── DateFormatter or NumberFormatter created inline in body (new instance every render)
├── No ViewModel — all @State for non-trivial state
└── Navigation destination logic inside view body

MEDIUM violations:
├── No #Preview blocks — views cannot be developed without running the full app
├── Repeated UI patterns not extracted into subview or ViewModifier
└── NavigationLink with inline destination view (not .navigationDestination)

LOW violations:
├── View struct >200 lines total (even if body is extracted)
└── No file separation — 10 views in one Swift file
```

## View Decomposition Signals

```
✅ Healthy SwiftUI view folder:
Features/
└── Orders/
    ├── OrderListView.swift         → root screen view
    ├── OrderListViewModel.swift    → state and business logic
    ├── OrderRowView.swift          → single row component
    ├── OrderStatusBadge.swift      → reusable indicator
    └── OrderListView+Preview.swift → previews (optional separation)

❌ Warning signals:
OrdersScreen.swift > 300 lines  → decomposition needed
No ViewModel files              → logic lives in view
No Preview structs              → development friction
```

## Why

- **Struct rendering**: SwiftUI recreates View structs on every state change — expensive work in `body` runs on every render
- **Previews**: Small, focused views with injected data can be previewed in isolation; monolithic views require full app context
- **Testability**: Business logic in a `ViewModel` or `ObservableObject` is testable with XCTest; logic in a `View.body` is not
