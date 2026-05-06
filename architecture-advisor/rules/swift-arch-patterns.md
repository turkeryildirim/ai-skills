---
title: Swift Architectural Pattern Analysis
impact: CRITICAL
impactDescription: "Massive ViewControllers and absent architecture patterns make iOS codebases unmaintainable"
tags: swift, architecture, mvc, mvvm, viper, tca, viewcontroller
---

## Swift Architectural Pattern Analysis

**Impact: CRITICAL (Massive ViewControllers and absent architecture patterns make iOS codebases unmaintainable)**

The default iOS architectural pattern — Model-View-Controller — degrades quickly into Massive View Controller (MVC → MVC) when discipline isn't applied. ViewControllers accumulate network calls, business logic, navigation, and UI update code until they exceed 1,000 lines. Identifying the claimed vs actual architectural pattern is the first job of any Swift project analysis.

## Incorrect

```swift
// ❌ Massive ViewController — Networking + Business Logic + Navigation + UI

class OrderListViewController: UIViewController {

    // ❌ URLSession directly in ViewController
    private let session = URLSession.shared
    var orders: [Order] = []
    var filteredOrders: [Order] = []
    var selectedCategory: String = "all"

    override func viewDidLoad() {
        super.viewDidLoad()
        loadOrders()
    }

    // ❌ Network call in ViewController
    func loadOrders() {
        let url = URL(string: "https://api.example.com/orders")!
        session.dataTask(with: url) { data, response, error in
            guard let data = data else { return }
            self.orders = try! JSONDecoder().decode([Order].self, from: data) // ❌ try!
            DispatchQueue.main.async {
                // ❌ Business logic (filtering) in ViewController
                self.filteredOrders = self.orders.filter {
                    self.selectedCategory == "all" || $0.category == self.selectedCategory
                }
                self.tableView.reloadData()
            }
        }.resume()
    }

    // ❌ Navigation in ViewController
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let vc = OrderDetailViewController()
        vc.order = filteredOrders[indexPath.row]
        navigationController?.pushViewController(vc, animated: true)
    }

    // ... 400 more lines of UITableViewDelegate, UITableViewDataSource,
    // form handling, error alerts, pull-to-refresh, etc.
}
```

## Correct

```swift
// ✅ MVVM — ViewController handles only UI; ViewModel handles logic

// ViewModel: business logic, data transformation, state
@MainActor
class OrderListViewModel: ObservableObject {

    @Published var orders: [Order] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let orderService: OrderServiceProtocol // ✅ Protocol, not concrete

    init(orderService: OrderServiceProtocol = OrderService()) {
        self.orderService = orderService
    }

    func loadOrders() async {
        isLoading = true
        defer { isLoading = false }

        do {
            orders = try await orderService.fetchOrders() // ✅ async/await
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    var filteredOrders: [Order] {
        // ✅ Computed from state — pure, testable
        orders.filter { $0.category == selectedCategory || selectedCategory == "all" }
    }
}

// ViewController: ONLY UI wiring and lifecycle
class OrderListViewController: UIViewController {

    private var viewModel: OrderListViewModel
    private var cancellables = Set<AnyCancellable>()

    init(viewModel: OrderListViewModel) {
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        bindViewModel()
        Task { await viewModel.loadOrders() }
    }

    private func bindViewModel() {
        viewModel.$orders
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in self?.tableView.reloadData() } // ✅ [weak self]
            .store(in: &cancellables)
    }
}

// ✅ Protocol for navigation (Coordinator pattern)
protocol OrderCoordinator: AnyObject {
    func showOrderDetail(_ order: Order)
}
```

## Architectural Pattern Assessment

```
Pattern          │ Indicators to look for
─────────────────────────────────────────────────────────────────
MVC (plain)      │ UIViewController subclasses, no ViewModels, no Coordinators
                 │ ⚠ Check for Massive VC syndrome (>200 lines)
─────────────────────────────────────────────────────────────────
MVVM             │ ViewModel files, @Published/@State, Combine/async
                 │ ✅ Healthy if ViewControllers are <150 lines
─────────────────────────────────────────────────────────────────
VIPER            │ Interactor/, Presenter/, Router/ directories
                 │ ⚠ Check: is it full VIPER or just the folders?
─────────────────────────────────────────────────────────────────
TCA              │ ReducerProtocol, Store, ViewStore, Effect types
                 │ ✅ Generally well-structured if TCA is used correctly
─────────────────────────────────────────────────────────────────
SwiftUI native   │ View structs, @State/@StateObject, NavigationStack
                 │ ✅ Check: is state management appropriate for scale?
```

## Common Issues to Flag

| Issue | Severity | Rule |
|-------|----------|------|
| ViewController >300 lines with network + business logic | CRITICAL | `swift-arch-patterns` |
| `try!` or `as!` force casts outside of tests | HIGH | `swift-arch-patterns` |
| No architectural pattern — ad-hoc structure | CRITICAL | `swift-arch-patterns` |
| Claimed pattern (VIPER) but not actually applied | HIGH | `swift-arch-patterns` |
| `@EnvironmentObject` for local, non-shared state | MEDIUM | `swift-arch-patterns` |

## Why

- **Testability**: A ViewModel with protocol dependencies can be unit tested without UIKit — Massive VCs cannot
- **Maintainability**: 80-line ViewControllers can be understood in 5 minutes; 800-line VCs require 2 hours
- **Consistency**: Declared vs actual pattern mismatch means the team has no shared mental model
