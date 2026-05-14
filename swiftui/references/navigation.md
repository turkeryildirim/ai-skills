# SwiftUI Navigation

Guidelines for implementing robust, programmatic navigation in modern SwiftUI (iOS 17–26+).

## 1. NavigationStack (Push Navigation)

`NavigationStack` is the standard for stack-based navigation (iOS 16+).

```swift
@Observable @MainActor
class AppRouter {
    var path = NavigationPath()

    func push(_ destination: AppDestination) { path.append(destination) }
    func popToRoot() { path.removeLast(path.count) }
}

enum AppDestination: Hashable {
    case userProfile(userId: String)
    case orderDetail(orderId: Int)
}

NavigationStack(path: $router.path) {
    ContentView()
        .navigationDestination(for: AppDestination.self) { destination in
            switch destination {
            case .userProfile(let id): UserProfileView(userId: id)
            case .orderDetail(let id): OrderDetailView(orderId: id)
            }
        }
}
```

- **Router classes:** Must be `@MainActor` for Swift 6 isolation safety.
- **Store data, not views:** `NavigationPath` holds `Hashable` values, never view instances.
- **Decoupling:** Use `navigationDestination(for:)` to keep views unaware of each other.

## 2. NavigationSplitView (Multi-Column)

Use for sidebar-detail layouts on iPad and Mac (iOS 16+).
- **Sidebar, Content, Detail:** Standard 3-column or 2-column structures.
- **Selection:** Use a `@Binding` to track the selected item across columns.
- **Fallback:** Collapses to stack navigation on iPhone automatically.
- **Custom multi-column:** Use manual `HStack` splits with `horizontalSizeClass` for full column control.

## 3. Sheet Presentation

```swift
// Prefer .sheet(item:) when state represents a selected model
.sheet(item: $selectedOrder) { order in
    OrderDetailSheet(order: order)
}

// iOS 18+ presentation sizing
.presentationSizing(.form)   // form-width sheet
.presentationSizing(.page)   // full-page sheet
.presentationSizing(.fitted) // content-fitted sheet
```

- Sheets should handle their own dismissal via `@Environment(\.dismiss)`.
- Use `.fullScreenCover()` for immersive, full-screen experiences.

## 4. Tab-Based Navigation (iOS 16+)

```swift
// Modern Tab API (iOS 26+)
TabView(selection: $selection) {
    Tab("Home", systemImage: "house", value: AppTab.home) {
        NavigationStack(path: $homeRouter.path) { HomeView() }
    }
    Tab(role: .search) {
        SearchView()
    }
}
.tabBarMinimizeBehavior(.onScrollDown) // iOS 26+
```

- **Independent paths:** Each tab requires its own `NavigationPath` instance.
- **Legacy:** Use `.tabItem { }` only for iOS 16/17 targets; prefer `Tab(value:)` for iOS 26+.

## 5. Deep Linking

```swift
.onOpenURL { url in
    router.handle(url: url)
}
.onContinueUserActivity(NSUserActivityTypes.viewOrder) { activity in
    router.handle(activity: activity)
}
```

- Centralize URL parsing in router objects.
- Universal links require AASA file at `/.well-known/apple-app-site-association` plus Associated Domains entitlement.
- Custom URL schemes work but lack web fallback benefits.
- Handle deep links in one location only (the router), not scattered across views.

## 6. Alerts and Confirmation Dialogs

```swift
.alert("Delete Item?", isPresented: $showDeleteAlert) {
    Button("Delete", role: .destructive) { delete() }
    Button("Cancel", role: .cancel) { }
}
```

Use `.confirmationDialog` for action sheets with multiple choices.

## 7. Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `NavigationView` | Replace with `NavigationStack` |
| Sharing path across tabs | Each tab owns its own `NavigationPath` |
| `.sheet(isPresented:)` with model | Use `.sheet(item:)` instead |
| Storing views in `NavigationPath` | Store `Hashable` data only |
| Hard-coded sheet dimensions | Use `presentationSizing` (iOS 18+) |
| Deep link handling in multiple views | Centralize in router |

## 8. iOS 26 Navigation Enhancements

- `Tab(role: .search)` — dedicated search tab with special placement.
- `.tabBarMinimizeBehavior(.onScrollDown)` — tab bar auto-hides on scroll.
- `.tabViewBottomAccessory` — content below tab bar.
- `matchedTransitionSource` + `.navigationTransition(.zoom)` — zoom navigation transitions.

## 9. MUST NOT DO

## Cross References

- Related rules: `swiftui-navigation-stack`, `swiftui-task-lifecycle`, `conc-actor-isolation`
- Related references: [`architecture.md`](architecture.md), [`concurrency.md`](concurrency.md), [`animations.md`](animations.md), [`accessibility.md`](accessibility.md)

- **NavigationView:** Do NOT use legacy `NavigationView` for new code.
- **NavigationLink in Loops:** Avoid `NavigationLink` inside `ForEach` without `navigationDestination`. Use the data-driven approach.
- **Redundant Stacks:** Never nest one `NavigationStack` inside another.
- **View instances in path:** Never store view types in `NavigationPath`.
- **Router off MainActor:** Router classes must be `@MainActor` in Swift 6.
