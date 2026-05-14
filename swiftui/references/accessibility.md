# Accessibility in SwiftUI

Guidelines for making SwiftUI applications inclusive and usable by everyone, following WCAG and Apple HIG standards.

## 1. Text and Labels

- **Icon Buttons:** Always provide `accessibilityLabel` for buttons containing only an image.
- **Dynamic Type:** Use standard font styles (`.title`, `.body`, `.caption`) so text scales correctly.
- **String Catalogs:** Use for all user-facing text to support localization and pluralization.

```swift
// ✅ Icon-only button
Button(action: share) {
    Image(systemName: "square.and.arrow.up")
}
.accessibilityLabel("Share")

// ✅ Prefer Button over onTapGesture for single-tap actions
Button("View Profile") { openProfile() }
// onTapGesture lacks accessibility traits and is not activatable by VoiceOver by default
```

## 2. Traits and Actions

```swift
// Declare semantic role
Text("Section Header")
    .accessibilityAddTraits(.isHeader)

// Group related elements
HStack {
    Image(systemName: "star.fill")
    Text("4.8")
    Text("(1,243 reviews)")
}
.accessibilityElement(children: .combine)
.accessibilityLabel("Rated 4.8 out of 5, 1,243 reviews")

// Custom action for non-standard gestures
.accessibilityAction(named: "Delete") { delete() }
```

## 3. Gestures and Accessibility

- **Single-tap actions:** Use `Button` instead of `onTapGesture` — Buttons have correct accessibility traits.
- **Custom gestures:** Provide `.accessibilityAction` alternatives for non-standard interactions.
- **Drag/drop:** Supplement with accessibility actions for users who cannot perform drag gestures.

```swift
// ❌ Not accessible by default
.onTapGesture { openItem() }

// ✅ Accessible
Button { openItem() } label: { ItemView() }

// ✅ Custom gesture with accessibility fallback
.gesture(dragGesture)
.accessibilityAction(.default) { /* same action via accessibility */ }
```

## 4. Motion and Visuals

```swift
// Respect Reduce Motion preference
@Environment(\.accessibilityReduceMotion) private var reduceMotion

var animation: Animation {
    reduceMotion ? .none : .spring(.bouncy)
}

// Ensure sufficient contrast (use system colors)
// Don't rely on color alone for information
HStack {
    Image(systemName: "exclamationmark.triangle.fill")
        .foregroundStyle(.red)
    Text("Error occurred")  // Both icon AND text convey the error
}
```

## 5. VoiceOver Navigation

```swift
// Hide decorative elements
Image("background-pattern")
    .accessibilityHidden(true)

// Provide reading order for custom layouts
VStack {
    Text("Price")
    Text("$29.99")
        .font(.title)
}
.accessibilityElement(children: .combine)

// Sorting accessibility elements
.accessibilitySortPriority(2)  // Higher number = read first
```

## 6. Testing Accessibility

- **Accessibility Inspector (Xcode):** Audit views in Simulator without a device.
- **VoiceOver:** Test on a real device with VoiceOver enabled — Simulator VoiceOver is not equivalent.
- **Accessibility Labels audit:** Run `XCUIApplication().accessibilityAudit()` in UI tests.
- **Dynamic Type:** Test all text size presets including "Accessibility Large" sizes.

## 7. MUST DO

- **Accessibility Grouping:** Use `.accessibilityElement(children: .combine)` for label+value pairs.
- **Hidden Decoratives:** Use `.accessibilityHidden(true)` for elements that don't add VoiceOver value.
- **Button vs Gesture:** Use `Button` for all tappable elements; `onTapGesture` for supplemental interactions only.
- **Color + Shape:** Never rely on color alone to convey state (add icons or text).
- **Focus Management:** Use `@AccessibilityFocusState` to direct focus after navigation or sheet dismissal.

## 8. MUST NOT DO

## Cross References

- Related rules: `swiftui-gesture-state`, `swiftui-animation-scope`, `layout-content-shape`, `layout-focus-state`
- Related references: [`gestures.md`](gestures.md), [`animations.md`](animations.md), [`view-structure.md`](view-structure.md), [`../../swiftui-tester/references/ui-testing.md`](../../swiftui-tester/references/ui-testing.md)

- **Color-only information:** Error states need an icon or text, not just red color.
- **Missing labels on interactive elements:** Every `Button`, `Toggle`, `TextField` needs a clear label.
- **Intense animations without Reduce Motion check:** Check `accessibilityReduceMotion` before animating.
- **`onTapGesture` for primary actions:** Use `Button` — it provides correct traits and keyboard/switch access.
