---
title: Swift Dependency Injection and Memory Management Analysis
impact: HIGH
impactDescription: "Missing DI and retain cycles cause untestable code and memory leaks"
tags: swift, dependency-injection, protocols, retain-cycles, weak-self, memory
---

## Swift Dependency Injection and Memory Management Analysis

**Impact: HIGH (Missing DI and retain cycles cause untestable code and memory leaks)**

Swift's reference counting (ARC) makes memory management explicit but error-prone. Closures that capture `self` strongly in objects that also hold the closure create retain cycles — the object never deallocates. Simultaneously, concrete type dependencies (no protocol abstraction) make unit testing impossible without real network calls and real databases.

## Incorrect

```swift
// ❌ Concrete dependencies — cannot mock in tests

class OrderViewModel {
    // ❌ Concrete type — cannot substitute with mock
    private let service = OrderAPIService()  // Hardcoded, makes real API calls in tests
    private let analytics = FirebaseAnalytics.shared  // Singleton, global state

    func loadOrders() async {
        let orders = try? await service.fetchOrders() // No protocol — cannot mock
    }
}

// ❌ Testing OrderViewModel requires a live network connection
```

```swift
// ❌ Retain cycle — ViewController never deallocates

class ProfileViewController: UIViewController {

    var onProfileUpdated: (() -> Void)?  // Closure stored by this VC

    override func viewDidLoad() {
        super.viewDidLoad()

        // ❌ Strong capture of self in a closure that self holds
        onProfileUpdated = {
            self.updateUI()  // self → onProfileUpdated → self (cycle)
        }

        // ❌ Timer strong-captures self, VC strong-references timer
        Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { timer in
            self.refresh()  // ❌ No [weak self]
        }
    }

    // deinit is never called — memory leak
}
```

```swift
// ❌ Hardcoded credentials in source
struct APIConfig {
    static let apiKey = "sk-prod-abc123secret"  // ❌ In version control
    static let baseURL = "https://api.example.com"
}
```

## Correct

```swift
// ✅ Protocol-based dependency injection — fully mockable

protocol OrderServiceProtocol {
    func fetchOrders() async throws -> [Order]
    func createOrder(_ dto: CreateOrderDTO) async throws -> Order
}

class OrderViewModel {
    private let service: OrderServiceProtocol  // ✅ Protocol, not concrete type
    private let analytics: AnalyticsProtocol

    // ✅ Constructor injection — explicit dependencies
    init(
        service: OrderServiceProtocol = OrderAPIService(),
        analytics: AnalyticsProtocol = AppAnalytics.shared
    ) {
        self.service = service
        self.analytics = analytics
    }

    func loadOrders() async {
        let orders = try? await service.fetchOrders()
    }
}

// ✅ In tests — inject mock, no network required
class MockOrderService: OrderServiceProtocol {
    var stubbedOrders: [Order] = []
    func fetchOrders() async throws -> [Order] { stubbedOrders }
    func createOrder(_ dto: CreateOrderDTO) async throws -> Order { stubbedOrders[0] }
}

let vm = OrderViewModel(service: MockOrderService(), analytics: MockAnalytics())
```

```swift
// ✅ Retain cycle prevention with [weak self]

class ProfileViewController: UIViewController {

    private var timer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()

        // ✅ [weak self] breaks the retain cycle
        onProfileUpdated = { [weak self] in
            self?.updateUI()
        }

        // ✅ Timer with [weak self]
        timer = Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { [weak self] _ in
            self?.refresh()
        }
    }

    deinit {
        timer?.invalidate()  // ✅ Cleanup in deinit — proves deinit is called
        print("ProfileViewController deallocated") // Use during debugging
    }
}
```

```swift
// ✅ Secrets via environment, not source code

// Info.plist reads from build settings → environment variables
struct APIConfig {
    static let apiKey = Bundle.main.infoDictionary?["API_KEY"] as? String ?? ""
    static let baseURL = Bundle.main.infoDictionary?["BASE_URL"] as? String ?? ""
}
// API_KEY set in Xcode build settings → pulled from CI environment variables
// Never committed to version control
```

## DI and Memory Assessment Checklist

```
Dependency Injection:
[ ] ViewModels/Interactors use protocol types for services, not concrete classes
[ ] Constructor injection used (not property injection or service locator)
[ ] No Singleton accessed directly inside feature code (inject instead)
[ ] DI container or factory used for dependency graph (if complex)

Memory Management:
[ ] All closures that capture self in long-lived objects use [weak self] or [unowned self]
[ ] Timer, NotificationCenter, and KVO observers invalidated/removed in deinit
[ ] deinit present in ViewControllers (proves no retain cycle during development)
[ ] No strong reference cycles visible in class relationships

Security:
[ ] No API keys, tokens, or passwords in Swift source files
[ ] Secrets loaded from environment / secure storage (Keychain, build vars)
[ ] No secrets in .plist files committed to version control
```

## Why

- **Testability**: Protocol dependencies can be replaced with lightweight test doubles — concrete singletons cannot
- **Memory safety**: Retain cycles in ViewControllers prevent deallocation, causing memory growth on every navigation event
- **Security**: Secrets in source files are visible to anyone with repository access, including in git history after deletion
