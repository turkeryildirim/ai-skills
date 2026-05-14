# SwiftUI Animations

Modern SwiftUI animation APIs (iOS 17+) for state-driven, multi-phase, keyframe, and symbol animations.

## Animation Type Selection

| Use Case | API |
|----------|-----|
| Simple state-driven | `withAnimation`, `.animation(_:value:)` |
| Sequenced multi-phase | `PhaseAnimator` |
| Complex choreography | `KeyframeAnimator` |
| Hero/shared element | `matchedGeometryEffect` |
| Navigation zoom | `matchedTransitionSource` + `.navigationTransition(.zoom)` |
| View insertion/removal | `.transition()` |
| SF Symbol effects | `.symbolEffect()` |
| In-place content change | `ContentTransition` |
| Custom shapes | `@Animatable` macro |

## 1. State-Driven Animations

```swift
// ✅ Scoped to specific value change
.animation(.spring(.bouncy), value: isExpanded)

// ✅ Explicit animation block
withAnimation(.easeInOut(duration: 0.3)) {
    isExpanded.toggle()
}

// ❌ Too broad — animates ALL state changes
.animation(.easeInOut)
```

## 2. Animation Curves

Prefer spring presets over traditional easing for natural motion:

```swift
.spring(.smooth)   // Gentle, no overshoot
.spring(.snappy)   // Quick, slight overshoot
.spring(.bouncy)   // Playful, visible overshoot

// Custom spring (perceptual model)
.spring(duration: 0.4, bounce: 0.25)

// Custom spring (physical model)
.spring(mass: 1, stiffness: 200, damping: 20)
```

## 3. PhaseAnimator

For sequenced animation phases cycling automatically:

```swift
enum PulsePhase: CaseIterable {
    case idle, expanded, normal
}

PhaseAnimator(PulsePhase.allCases) { phase in
    Circle()
        .scaleEffect(phase == .expanded ? 1.3 : 1.0)
        .opacity(phase == .idle ? 0.7 : 1.0)
} animation: { phase in
    switch phase {
    case .idle: .easeIn(duration: 0.5)
    case .expanded: .spring(.bouncy)
    case .normal: .easeOut(duration: 0.3)
    }
}
```

## 4. KeyframeAnimator

For multiple properties animated along independent timelines:

```swift
KeyframeAnimator(initialValue: AnimationValues()) { values in
    Circle()
        .scaleEffect(values.scale)
        .rotationEffect(values.rotation)
        .offset(y: values.verticalOffset)
} keyframes: { _ in
    KeyframeTrack(\.scale) {
        LinearKeyframe(1.0, duration: 0.2)
        SpringKeyframe(1.5, duration: 0.3)
        CubicKeyframe(1.0, duration: 0.3)
    }
    KeyframeTrack(\.rotation) {
        LinearKeyframe(.degrees(0), duration: 0.4)
        CubicKeyframe(.degrees(360), duration: 0.4)
    }
}
```

## 5. Matched Geometry Effect (Hero Transition)

```swift
@Namespace private var heroNamespace

// Source view
Image(item.image)
    .matchedGeometryEffect(id: item.id, in: heroNamespace)

// Destination view (in sheet or overlay)
Image(item.image)
    .matchedGeometryEffect(id: item.id, in: heroNamespace)
```

**CRITICAL:** Each ID must have exactly one source (not `isSource: false`). Multiple sources cause undefined behavior.

## 6. Navigation Zoom Transition (iOS 18+)

```swift
// Source (list row)
NavigationLink(value: item) {
    ThumbnailView(item: item)
        .matchedTransitionSource(id: item.id, in: namespace)
}

// Destination
ItemDetailView(item: item)
    .navigationTransition(.zoom(sourceID: item.id, in: namespace))
```

## 7. View Transitions

```swift
if isVisible {
    ContentView()
        .transition(.move(edge: .bottom).combined(with: .opacity))
}
```

## 8. SF Symbol Effects (iOS 17+)

```swift
Image(systemName: "bell.fill")
    .symbolEffect(.bounce, value: notificationReceived)
    .symbolEffect(.pulse, isActive: isLoading)
    .symbolRenderingMode(.hierarchical)
```

## 9. ContentTransition

For animating content changes in-place without view removal:

```swift
Text(count, format: .number)
    .contentTransition(.numericText())

Image(systemName: currentIcon)
    .contentTransition(.symbolEffect(.replace))
```

## 10. @Animatable Macro (iOS 26+)

Replaces manual `AnimatableData` boilerplate:

```swift
// ✅ iOS 26+
@Animatable
struct WaveShape: Shape {
    var amplitude: Double
    var frequency: Double
    // AnimatableData automatically synthesized
}

// ❌ Old pattern
struct WaveShape: Shape {
    var animatableData: AnimatablePair<Double, Double> { ... }
}
```

## 11. Accessibility

Always check Reduce Motion before playing intense animations:

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

var body: some View {
    content
        .animation(reduceMotion ? .none : .spring(.bouncy), value: isAnimating)
}
```

## 12. Common Pitfalls

## Cross References

- Related rules: `swiftui-animation-scope`, `swiftui-task-lifecycle`
- Related references: [`accessibility.md`](accessibility.md), [`performance.md`](performance.md), [`navigation.md`](navigation.md), [`gestures.md`](gestures.md)

| Pitfall | Fix |
|---------|-----|
| Over-broad animation scope | Use `.animation(_:value:)` with specific value |
| Expensive computation in animation closures | Move to `.task {}` or precompute |
| Missing Reduce Motion support | Check `accessibilityReduceMotion` |
| Multiple `matchedGeometryEffect` sources | Exactly one source per ID |
| `DispatchQueue` for animation delays | Use `withAnimation` + `.delay()` |
| Missing `ContentTransition` partner | Both insert and remove transitions needed |
| `.navigationTransition` on wrong view | Apply to destination view, not NavigationLink label |
| All animation declarations must include value parameters | Never use `.animation()` without `value:` |
