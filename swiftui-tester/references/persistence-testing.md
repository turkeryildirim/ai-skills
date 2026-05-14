# Testing SwiftData and Persistence

Expert guidance for testing persistence layers and models in SwiftUI apps with Swift Testing.

## 1. In-Memory Containers

Always use an in-memory `ModelContainer` for tests — fast, isolated, and does not affect the user's local database.

```swift
import Testing
import SwiftData

@Suite("Order Persistence")
struct OrderPersistenceTests {
    let container: ModelContainer
    let context: ModelContext

    init() throws {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        container = try ModelContainer(for: Order.self, OrderItem.self, configurations: config)
        context = ModelContext(container)
    }

    @Test("inserting order persists correctly")
    func insertOrder() throws {
        let order = Order(title: "Test Order")
        context.insert(order)
        try context.save()

        let orders = try context.fetch(FetchDescriptor<Order>())
        #expect(orders.count == 1)
        #expect(orders.first?.title == "Test Order")
    }
}
```

Each test suite gets a fresh in-memory container via `init()`. Do not share `ModelContext` between suites.

## 2. Testing CRUD Operations

```swift
@Test("updating order title persists change")
func updateOrder() throws {
    let order = Order(title: "Original")
    context.insert(order)
    try context.save()

    order.title = "Updated"
    try context.save()

    let fetched = try context.fetch(FetchDescriptor<Order>()).first
    #expect(fetched?.title == "Updated")
}

@Test("deleting order removes it from store")
func deleteOrder() throws {
    let order = Order(title: "To Delete")
    context.insert(order)
    try context.save()

    context.delete(order)
    try context.save()

    let orders = try context.fetch(FetchDescriptor<Order>())
    #expect(orders.isEmpty)
}
```

## 3. Testing Relationship Delete Rules

```swift
@Test("deleting order cascades to its items")
func cascadeDelete() throws {
    let order = Order(title: "Parent")
    let item1 = OrderItem(name: "Item 1")
    let item2 = OrderItem(name: "Item 2")
    order.items = [item1, item2]
    context.insert(order)
    try context.save()

    context.delete(order)
    try context.save()

    let remainingItems = try context.fetch(FetchDescriptor<OrderItem>())
    #expect(remainingItems.isEmpty)  // Cascade delete applied
}
```

## 4. Testing Predicates

Insert a known dataset, fetch with the predicate, verify the exact result set:

```swift
@Test("predicate filters paid orders correctly")
func paidOrdersPredicate() throws {
    let paid = Order(title: "Paid", isPaid: true)
    let unpaid = Order(title: "Unpaid", isPaid: false)
    context.insert(paid)
    context.insert(unpaid)
    try context.save()

    let predicate = #Predicate<Order> { $0.isPaid == true }
    let descriptor = FetchDescriptor<Order>(predicate: predicate)
    let results = try context.fetch(descriptor)

    #expect(results.count == 1)
    #expect(results.first?.title == "Paid")
}

// Always test boundary cases
@Test("empty title predicate handles edge cases")
func emptyTitlePredicate() throws {
    let empty = Order(title: "")
    let filled = Order(title: "Valid")
    context.insert(empty)
    context.insert(filled)
    try context.save()

    let predicate = #Predicate<Order> { !$0.title.isEmpty }
    let descriptor = FetchDescriptor<Order>(predicate: predicate)
    let results = try context.fetch(descriptor)

    #expect(results.count == 1)
}
```

## 5. Dependency Injection for Testability

Inject `ModelContext` into services so they can be tested with the in-memory context:

```swift
class OrderRepository {
    private let context: ModelContext
    init(context: ModelContext) { self.context = context }

    func save(_ order: Order) throws {
        context.insert(order)
        try context.save()
    }
}

@Suite("Order Repository")
struct OrderRepositoryTests {
    var repository: OrderRepository
    var context: ModelContext

    init() throws {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: Order.self, configurations: config)
        context = ModelContext(container)
        repository = OrderRepository(context: context)
    }
}
```

## 6. MUST DO

- **Fresh container per suite:** Each `@Suite` creates its own in-memory `ModelContainer` in `init()`.
- **Positive and negative cases:** Test both "data found" and "data not found" for fetch descriptors.
- **Relationship testing:** Verify delete rules (cascade, nullify) behave as expected.
- **Boundary predicate data:** Test predicates with empty strings, nil values, edge cases.

## 7. MUST NOT DO

- **Shared disk containers:** Never use a persistent `ModelContainer` in tests.
- **Shared context between suites:** Each suite must have its own context for isolation.
- **Implicit data state:** Never assume data was inserted by another test — each test is independent.

## Cross References

- Related rules: `test-swiftdata-inmemory`, `test-predicate-validation`, `test-no-shared-state`
- Related references: [`swift-testing.md`](swift-testing.md), [`../../swiftui/references/swiftdata.md`](../../swiftui/references/swiftdata.md), [`../../swiftui/references/state-management.md`](../../swiftui/references/state-management.md)
