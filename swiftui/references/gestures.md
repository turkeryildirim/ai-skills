# SwiftUI Gestures

Implementing and reviewing SwiftUI gesture handling for iOS 17+, with proper state management and conflict resolution.

## Gesture Types

### Discrete Gestures (fire once at `.onEnded`)

| Gesture | iOS | Notes |
|---------|-----|-------|
| `TapGesture` | 13+ | Single, double, multi-tap |
| `LongPressGesture` | 13+ | Hold-based with configurable duration |
| `SpatialTapGesture` | 16+ | Location-aware tapping |

### Continuous Gestures (stream `.onChanged`)

| Gesture | iOS | Notes |
|---------|-----|-------|
| `DragGesture` | 13+ | Translation, velocity, predicted end |
| `MagnifyGesture` | 17+ | Pinch-to-zoom (replaces `MagnificationGesture`) |
| `RotateGesture` | 17+ | Two-finger rotation (replaces `RotationGesture`) |

## 1. State Management

```swift
// ✅ @GestureState — auto-resets to initial value when gesture ends
@GestureState private var dragOffset: CGSize = .zero
@GestureState private var isPressing: Bool = false

// ✅ @State — persists across gesture lifecycles
@State private var finalOffset: CGSize = .zero

// Combine both for live feedback + persistence
let drag = DragGesture()
    .updating($dragOffset) { value, state, _ in
        state = value.translation  // Live feedback
    }
    .onEnded { value in
        finalOffset.width += value.translation.width  // Persist
        finalOffset.height += value.translation.height
    }
```

## 2. Drag Gesture

```swift
@GestureState private var dragOffset: CGSize = .zero
@State private var position: CGSize = .zero

var body: some View {
    Circle()
        .offset(x: position.width + dragOffset.width,
                y: position.height + dragOffset.height)
        .gesture(
            DragGesture()
                .updating($dragOffset) { value, state, _ in
                    state = value.translation
                }
                .onEnded { value in
                    position.width += value.translation.width
                    position.height += value.translation.height
                    // Clamp to bounds if needed
                    position.width = max(-200, min(200, position.width))
                }
        )
}
```

## 3. Magnify and Rotate (iOS 17+)

```swift
@GestureState private var magnifyBy: CGFloat = 1.0
@GestureState private var rotateBy: Angle = .zero
@State private var currentScale: CGFloat = 1.0
@State private var currentRotation: Angle = .zero

// ✅ MagnifyGesture (iOS 17+)
let magnify = MagnifyGesture()
    .updating($magnifyBy) { value, state, _ in state = value.magnification }
    .onEnded { value in currentScale *= value.magnification }

// ✅ RotateGesture (iOS 17+)
let rotate = RotateGesture()
    .updating($rotateBy) { value, state, _ in state = value.rotation }
    .onEnded { value in currentRotation += value.rotation }

// Combine simultaneously
.gesture(magnify.simultaneously(with: rotate))
```

## 4. Long Press

```swift
@GestureState private var isPressing: Bool = false

let longPress = LongPressGesture(minimumDuration: 0.5)
    .updating($isPressing) { value, state, _ in state = value }
    .onEnded { _ in triggerContextMenu() }

// Visual feedback during press
.scaleEffect(isPressing ? 0.95 : 1.0)
.animation(.easeInOut(duration: 0.1), value: isPressing)
.gesture(longPress)
```

## 5. Gesture Composition

```swift
// Both fire simultaneously
.gesture(magnify.simultaneously(with: rotate))

// Second activates only after first completes
.gesture(longPress.sequenced(before: drag))

// Only one succeeds; first has priority
.gesture(singleTap.exclusively(before: doubleTap))
```

## 6. Hierarchy Conflict Resolution

```swift
// Default — child gesture wins
content.gesture(tapGesture)

// Parent takes precedence
.highPriorityGesture(swipeGesture)

// Both parent and child fire
.simultaneousGesture(analytics.track())
```

## 7. Custom Gestures

```swift
struct TwoFingerDoubleTap: Gesture {
    var body: some Gesture {
        TapGesture(count: 2)
            .simultaneously(with: TapGesture(count: 2))
    }
}

extension View {
    func onTwoFingerDoubleTap(perform action: @escaping () -> Void) -> some View {
        gesture(TwoFingerDoubleTap().onEnded { _ in action() })
    }
}
```

## 8. Critical Rules

1. Keep `.onChanged()` closures **lightweight** — they run 60–120 times per second. Defer heavy work to `.onEnded()`.
2. Use `@GestureState` for intermediate values that auto-reset; `@State` for persisted values.
3. Use `Button` for single-tap actions, not `onTapGesture` — Button provides correct accessibility traits.
4. Always include `.updating()` for intermediate visual feedback in continuous gestures.
5. Clamp persisted values to valid bounds in `.onEnded()`.
6. Test gesture conflicts when parent and child views both have gestures.

## 9. Accessibility

Every custom gesture must have an accessibility alternative:

```swift
// ✅ Drag to reorder — add accessibility action fallback
.gesture(reorderDrag)
.accessibilityAction(named: "Move Up") { moveUp() }
.accessibilityAction(named: "Move Down") { moveDown() }

// ✅ Pinch to zoom — add accessibility action
.gesture(magnifyGesture)
.accessibilityAction(named: "Zoom In") { scale *= 1.2 }
.accessibilityAction(named: "Zoom Out") { scale /= 1.2 }
```

## 10. MUST NOT DO

## Cross References

- Related rules: `swiftui-gesture-state`, `layout-content-shape`
- Related references: [`accessibility.md`](accessibility.md), [`animations.md`](animations.md), [`view-structure.md`](view-structure.md)

| Anti-pattern | Fix |
|--------------|-----|
| `MagnificationGesture` on iOS 17+ | Use `MagnifyGesture` |
| `RotationGesture` on iOS 17+ | Use `RotateGesture` |
| Heavy computation in `.onChanged()` | Move to `.onEnded()` |
| Missing intermediate feedback | Add `.updating()` with `@GestureState` |
| `onTapGesture` for primary actions | Use `Button` |
| Unresolved parent/child conflicts | Use `.highPriorityGesture()` or `.simultaneousGesture()` |
| Missing accessibility alternatives | Add `.accessibilityAction()` |
