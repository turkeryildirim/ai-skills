# SwiftUI Architecture

Guidelines for selecting and structuring SwiftUI applications, from simple MV patterns to enterprise architectures.

## Architecture Selection Framework

Use this decision tree:
1. Simple CRUD / small app → **MV Pattern**
2. Complex business logic / unit testing → **MVVM**
3. State machines / side effects → **MVI or TCA**
4. Large modular apps / exhaustive tests → **TCA or Clean Architecture**
5. Complex UIKit navigation → Add **Coordinator** (UIKit only)

## 1. The MV Pattern (Recommended Starting Point)

For most SwiftUI apps, a simple Model-View pattern using `@Observable` is preferred.
- **Model:** The data and logic (often `@Observable` classes).
- **View:** The UI and interaction logic.
- **Direct Access:** Views access and modify `@Observable` models via `@Bindable`.
- **Best for:** Small-to-medium apps, low complexity, rapid prototyping.

```swift
@Observable
class UserModel {
    var name: String = ""
    var isLoading = false
}

struct UserView: View {
    @State private var model = UserModel()
    var body: some View {
        TextField("Name", text: $model.name)
    }
}
```

## 2. MVVM (When Complexity Demands)

Use MVVM when business logic is complex enough to warrant separation for unit testing or bridging to non-SwiftUI components.
- **ViewModel:** `@Observable` class acting as coordinator between Model and View.
- **State Ownership:** The View owns the ViewModel via `@State`.
- **Testability:** ViewModels are testable without instantiating SwiftUI views.
- **Best for:** Medium-complexity apps with significant business logic.

```swift
@Observable @MainActor
class ProfileViewModel {
    var user: User?
    var errorMessage: String?

    func loadProfile() async {
        do { user = try await userService.fetch() }
        catch { errorMessage = error.localizedDescription }
    }
}
```

## 3. MVI (Model-View-Intent)

Implements unidirectional data flow: Intents → Reducer → State → View.
- **Predictable:** State transitions are explicit and loggable.
- **Intent replay:** Supports debugging via intent logging.
- **Best for:** Feature modules with complex state machines and side effects.

## 4. TCA (The Composable Architecture)

Provides composable reducers and structured dependency injection.
- **Composable reducers:** Features are isolated and composed together.
- **Exhaustive testing:** Every state mutation is testable.
- **Best for:** Large apps requiring strict modularity and comprehensive test coverage.
- **Note:** High complexity; introduce only when team is aligned.

## 5. Clean Architecture

Layered approach: **Domain → Data → Presentation**. Dependencies flow inward.
- Domain: Use cases, entities, repository protocols.
- Data: Repository implementations, API clients, persistence.
- Presentation: ViewModels, Views.
- **Best for:** Enterprise apps, teams with strict separation-of-concerns requirements.

## 6. Dependency Injection (DI)

Inject dependencies to ensure testability and flexibility.
- **Environment:** Use `.environment(dependency)` for global services (networking, database).
- **Initializer Injection:** Pass dependencies into View/ViewModel initializers for local logic.
- **Protocols:** Define service interfaces as protocols so mocks can be substituted in tests.

## 7. Feature-Based Organization

Organize code by feature, not by type:
```
Features/
  UserProfile/
    Models/
    Views/
    Services/
  Orders/
    Models/
    Views/
    Services/
```

## 8. Architectural Escalation Path

1. **MV:** Use `@Observable` models directly in views.
2. **MVVM:** Add a ViewModel when logic grows.
3. **MVI/TCA:** Use for strict state management requirements.
4. **Clean/TCA:** Only for large-scale enterprise apps.

## 9. Common Pitfalls

- Using deprecated `ObservableObject` instead of `@Observable`.
- Over-engineering simple features with MVVM or TCA.
- Massive view models mixing UI, business, and data logic.
- Inconsistent pattern adoption across feature modules.
- Sharing `NavigationPath` across tabs (each tab must own its own path).

## 10. MUST NOT DO

## Cross References

- Related rules: `swiftui-state-observable`, `conc-actor-isolation`, `data-query-usage`, `net-protocol-client`
- Related references: [`state-management.md`](state-management.md), [`navigation.md`](navigation.md), [`swiftdata.md`](swiftdata.md), [`networking.md`](networking.md)

- **Singletons:** Avoid `static let shared` for anything that needs to be mocked in tests.
- **Coordinators in SwiftUI:** Do NOT use UIKit Coordinator pattern. Use `NavigationStack` with `NavigationPath`.
- **Logic in Body:** Keep business logic, networking, and direct data manipulation out of the `body` property.
- **Mixed Patterns:** Do not mix `ObservableObject` and `@Observable` within the same feature module.
