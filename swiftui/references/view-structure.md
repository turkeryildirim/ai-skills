# View Structure and Composition

Best practices for building efficient and maintainable SwiftUI view hierarchies, layout containers, and component patterns.

## 1. View Extraction

Small views compile faster and render more efficiently.
- **Extract to Structs:** Prefer extracting subviews into separate `struct` types over computed properties or methods.
- **Independent Invalidation:** Small views only re-render when their specific inputs change.
- **Focused Inputs:** Pass only the data a view needs, rather than entire large objects.
- **Equatable Conformance:** Add `Equatable` to views with expensive bodies to enable SwiftUI's diffing optimization.

```swift
// ✅ Extracted subview with focused input
struct UserAvatarView: View, Equatable {
    let name: String
    let imageURL: URL?
    var body: some View { /* ... */ }
}
```

## 2. @ViewBuilder

Use `@ViewBuilder` to create flexible container views.
- **Custom Containers:** Views that accept content closures (e.g., `CardView { Text("Content") }`).
- **Conditional Content:** `@ViewBuilder` handles `if`, `switch`, and `Optional` content automatically.
- **Never AnyView:** Use `@ViewBuilder` instead of returning `AnyView`.

```swift
struct CardView<Content: View>: View {
    @ViewBuilder let content: Content
    var body: some View {
        content
            .padding()
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}
```

## 3. View Modifiers

- **Order Matters:** `.padding().background()` vs `.background().padding()` produce different results.
- **Custom Modifiers:** Extract repetitive styling into `ViewModifier` or View extensions.

```swift
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
            .shadow(radius: 2)
    }
}
extension View {
    func cardStyle() -> some View { modifier(CardStyle()) }
}
```

## 4. Stack Layout Patterns

| Container | Renders | Best For |
|-----------|---------|----------|
| `VStack`/`HStack`/`ZStack` | All children immediately | Headers, forms, small fixed content |
| `LazyVStack`/`LazyHStack` | On demand inside `ScrollView` | Large or dynamic collections |
| `LazyVGrid`/`LazyHGrid` | On demand | Icon pickers, galleries, dense grids |
| `List` | Reuses rows | Feed-style content, settings, swipe actions |

```swift
// ✅ Grid for image gallery
LazyVGrid(columns: [GridItem(.adaptive(minimum: 100))]) {
    ForEach(photos) { photo in
        PhotoCell(photo: photo)
            .aspectRatio(1, contentMode: .fill)
    }
}

// ✅ List for settings
List {
    Section("Preferences") {
        Toggle("Notifications", isOn: $notificationsEnabled)
        Picker("Theme", selection: $theme) { /* ... */ }
    }
}
.listStyle(.insetGrouped)
```

## 5. ScrollView Patterns

```swift
ScrollView {
    LazyVStack(spacing: 16) {
        ForEach(items) { item in ItemRow(item: item) }
    }
}
// Programmatic scrolling (iOS 17+)
.scrollPosition(id: $scrolledItemID)

// Pin toolbar above keyboard
.safeAreaInset(edge: .bottom) {
    ComposerView()
}

// iOS 26 effects
.scrollEdgeEffectStyle(.soft, for: .top)
.backgroundExtensionEffect()
```

## 6. Form and Controls

```swift
Form {
    Section("Account") {
        TextField("Username", text: $username)
        SecureField("Password", text: $password)
    }
    Section("Preferences") {
        Toggle("Dark Mode", isOn: $isDarkMode)
        Slider(value: $fontSize, in: 12...24) { Text("Font Size") }
            .overlay(alignment: .trailing) { Text("\(Int(fontSize))pt") }
        DatePicker("Birthday", selection: $birthday, displayedComponents: .date)
    }
}
```

- Always display Slider current-value labels.
- Avoid `.pickerStyle(.segmented)` for more than 4 options.
- Use `@FocusState` for keyboard focus management.

## 7. Overlay and Presentation

```swift
// Transient UI (toast / banner)
.overlay(alignment: .top) {
    if showBanner {
        BannerView(message: message)
            .transition(.move(edge: .top).combined(with: .opacity))
    }
}

// Full-screen immersive
.fullScreenCover(item: $selectedMedia) { media in
    MediaPlayerView(media: media)
}
```

## 8. Searchable Pattern

```swift
.searchable(text: $query, placement: .navigationBarDrawer)
.searchScopes($scope) {
    Text("All").tag(SearchScope.all)
    Text("Photos").tag(SearchScope.photos)
}
.task(id: query) {
    guard !query.isEmpty else { return }
    await search(query)
}
```

Guard against empty queries. Show placeholder when search results are empty.

## 9. Critical Rules

1. Use lazy containers for large collections, NOT standard stacks.
2. Never nest `GeometryReader` inside lazy containers — defeats lazy loading.
3. Always use stable `Identifiable` IDs in `ForEach` (never array indices).
4. Avoid nesting scroll views on the same axis.
5. Omit `spacing:` parameters unless specific tight (0–4pt) or wide gaps are needed.
6. Add `.contentShape(Rectangle())` to tappable rows for full hit area.
7. Use `@FocusState` for keyboard focus management in forms.

## 10. MUST NOT DO

## Cross References

- Related rules: `swiftui-view-extraction`, `swiftui-lazy-layouts`, `layout-content-shape`
- Related references: [`performance.md`](performance.md), [`accessibility.md`](accessibility.md), [`gestures.md`](gestures.md), [`navigation.md`](navigation.md)

- **AnyView:** Never use for type erasure. Use `@ViewBuilder`, `Group`, or protocol-constrained generics.
- **GeometryReader in lazy containers:** Defeats lazy loading.
- **Array indices as ForEach IDs:** Causes full re-renders and scroll position loss.
- **Expensive shadows/blurs in lists:** `.shadow()`, `.blur()`, `.mask()` are expensive in scrollable lists.
- **Heavy UI in body:** Move computation to `.task {}` or model layer.
