# SwiftData Persistence

Guidelines for using SwiftData (iOS 17+) for local and CloudKit-synced persistence.

## Review Process (5-Step)

1. Validate core SwiftData issues (autosaving, relationships, delete rules)
2. Assess predicate safety
3. For CloudKit projects, apply CloudKit-specific constraints
4. For iOS 18+, identify indexing opportunities
5. For iOS 26+, examine class inheritance patterns

## 1. Model Design

```swift
@Model
final class Order {
    var id: UUID = UUID()
    var title: String = ""
    var createdAt: Date = Date()

    @Relationship(deleteRule: .cascade)
    var items: [OrderItem] = []

    @Relationship(deleteRule: .nullify, inverse: \Customer.orders)
    var customer: Customer?
}
```

- **`@Model`:** Annotate classes with `@Model`.
- **Delete Rules:** **CRITICAL.** Always specify `deleteRule`. Use `.cascade` for parent-child ownership, `.nullify` for loose associations, `.deny` to prevent deletion when children exist.
- **`@Attribute(.unique)`:** Use for natural IDs to prevent duplicates.
- **Default Values:** Provide default values for all properties to simplify CloudKit integration.

## 2. Data Flow

```swift
// App entry point
.modelContainer(for: [Order.self, Customer.self])

// In views
@Environment(\.modelContext) private var context
@Query(sort: \Order.createdAt, order: .reverse) private var orders: [Order]

// Manual fetch (outside views)
let descriptor = FetchDescriptor<Order>(
    predicate: #Predicate { $0.title.contains(query) },
    sortBy: [SortDescriptor(\.createdAt, order: .reverse)]
)
let results = try context.fetch(descriptor)
```

- **`@Query`:** Use in views to fetch and automatically observe data.
- **`FetchDescriptor`:** Use for logic in ViewModels, services, and tests.
- **Avoid `@Query` in ViewModels:** It's designed for SwiftUI Views only.

## 3. Predicates

```swift
// ✅ Safe predicate
#Predicate<Order> { order in
    !order.title.isEmpty && order.isPaid == true
}

// ✅ Safe nil check  
#Predicate<Order> { $0.customer != nil }

// ❌ Crash-prone pattern in some versions
#Predicate<Order> { $0.title.isEmpty == false }  // Use !isEmpty instead
```

- Use the `#Predicate` macro exclusively — do not construct `NSPredicate` manually.
- Keep predicates simple; complex logic may not translate to SQL correctly.
- Avoid optional chaining chains (`.?.?.`) in predicates — move logic to computed properties.

## 4. Indexing (iOS 18+)

```swift
@Model
final class Article {
    @Attribute(.spotlight) var title: String = ""   // Spotlight indexing
    @Index var publishedAt: Date = Date()             // Database index
    @Index([\.publishedAt, \.authorID]) var _: Bool = false  // Composite index
}
```

Add `@Index` to properties frequently used in `FetchDescriptor` predicates or sort descriptors.

## 5. Class Inheritance (iOS 26+)

```swift
@Model
class Vehicle {
    var name: String = ""
    var year: Int = 0
}

// Subclassing supported in iOS 26+
@Model
class Car: Vehicle {
    var doors: Int = 4
}
```

- Prior to iOS 26, `@Model` classes cannot be subclassed — use composition instead.
- Gate subclassing patterns with `#available(iOS 26, *)`.

## 6. Schema Migration

```swift
enum AppSchema: VersionedSchema {
    static let versionIdentifier = Schema.Version(2, 0, 0)
    static let models: [any PersistentModel.Type] = [Order.self]
}

enum AppMigrationPlan: SchemaMigrationPlan {
    static let schemas: [any VersionedSchema.Type] = [AppSchemaV1.self, AppSchemaV2.self]
    static let stages: [MigrationStage] = [migrateV1toV2]

    static let migrateV1toV2 = MigrationStage.custom(
        fromVersion: AppSchemaV1.self,
        toVersion: AppSchemaV2.self,
        willMigrate: nil,
        didMigrate: { context in
            let orders = try context.fetch(FetchDescriptor<AppSchemaV2.Order>())
            orders.forEach { $0.updatedAt = $0.createdAt }
            try context.save()
        }
    )
}
```

## 7. CloudKit Integration

When enabling CloudKit sync:
- All properties must be optional or have default values.
- Relationships must be optional.
- Do NOT use `@Attribute(.unique)` — CloudKit handles uniqueness differently.
- No ordered relationships (use `createdAt` sort instead).
- `.deny` delete rules are not supported.

## 8. Batch Operations

For large datasets, use a background context to avoid blocking the UI:

```swift
Task.detached(priority: .utility) {
    let bgContext = ModelContext(container)
    // Perform bulk insert/update/delete
    try bgContext.save()
}
```

## 9. MUST NOT DO

## Cross References

- Related rules: `data-delete-rules`, `data-predicate-safety`, `data-query-usage`, `data-indexing`
- Related references: [`state-management.md`](state-management.md), [`architecture.md`](architecture.md), [`concurrency.md`](concurrency.md), [`../../swiftui-tester/references/persistence-testing.md`](../../swiftui-tester/references/persistence-testing.md)

- **Missing delete rules:** Always specify `deleteRule` — orphaned objects are a common bug.
- **`@Query` in ViewModels:** Use `FetchDescriptor` in non-view code.
- **Complex predicates:** Keep them simple; unsupported operations crash at runtime.
- **Core Data mixing:** Do not mix SwiftData and Core Data for the same persistent store.
- **Subclassing before iOS 26:** Use composition instead of inheritance on earlier targets.
