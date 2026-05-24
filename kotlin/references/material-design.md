# Material Design 3 — Android Reference

## M3 Core Principles

| Principle     | Description                                                         | Implementation Focus                        |
| ------------- | ------------------------------------------------------------------- | ------------------------------------------- |
| Personal      | Dynamic color and user customization; reflect brand and preference | Dynamic color theming, Material You, monet   |
| Adaptive      | Responsive layouts across phone, tablet, foldable, desktop         | WindowSizeClass, canonical layouts, panes    |
| Expressive    | Rich motion, color, and typography to convey meaning               | Motion specs, elevation overlays, shapes     |
| Accessible    | Designed for all users including those with disabilities           | TalkBack, large text, high contrast, switches |

---

## App Style Selection

Choose a visual style based on app category to ensure tone-appropriate design.

| App Category  | Visual Style        | Characteristics                                                            |
| ------------- | ------------------- | -------------------------------------------------------------------------- |
| Utility       | Minimal, Functional | Neutral colors, sparse decoration, dense layouts, small corners            |
| Finance       | Trustworthy, Sober  | Dark or blue palettes, restrained animation, data-dense, compact spacing   |
| Health        | Calm, Clean         | Soft colors (green/blue), generous white space, rounded shapes, large text  |
| Kids          | Playful, Vibrant    | Saturated colors, large touch targets (56dp+), rounded corners, fun motion |
| Social        | Engaging, Expressive| Bold colors, card-based feeds, rich media, expressive transitions          |
| Productivity  | Efficient, Focused  | Neutral palette, flat surfaces, minimal chrome, keyboard-friendly          |
| E-commerce    | Premium, Guided     | High-quality imagery, clear CTAs, strong hierarchy, smooth animations      |

---

## Color Contrast Requirements

WCAG 2.1 compliance enforced by Android accessibility scanners.

| Element                 | Minimum Ratio | Standard         | How to Verify                               |
| ----------------------- | ------------- | ---------------- | ------------------------------------------- |
| Body text (< 18sp)      | 4.5 : 1       | WCAG AA         | Accessibility Scanner, `ScanLib`            |
| Large text (>= 18sp bold or >= 24sp) | 3 : 1 | WCAG AA | Accessibility Scanner                       |
| UI components & graphics | 3 : 1        | WCAG AA 1.4.11  | Contrast checker against background surface |

> Use `MaterialTheme.colorScheme` tokens. Never hard-code colors that bypass the theme.

---

## Touch Targets

| Target Type       | Size        | Notes                                          |
| ----------------- | ----------- | ---------------------------------------------- |
| Minimum           | 48 x 48 dp | Google Play policy requirement                 |
| Recommended       | 56 x 56 dp | M3 default for most interactive elements       |
| Kids / Accessible | 56 x 56 dp+| Larger targets reduce error rate               |
| Inter-element gap | 8 dp        | Minimum spacing between adjacent touch targets |

```kotlin
Modifier.size(48.dp)
Modifier.clickable(interactionSource, indication = null) { }
Modifier.padding(8.dp)
```

---

## 8dp Grid System

All spacing, sizing, and padding values should be multiples of 4dp, preferably 8dp.

| Token | Value | Usage                                      |
| ----- | ----- | ------------------------------------------ |
| xs    | 4 dp  | Inner padding, icon-to-label gaps          |
| sm    | 8 dp  | Minimum touch-target gap, list item padding|
| md    | 16 dp | Standard content padding, card padding     |
| lg    | 24 dp | Section spacing, dialog padding            |
| xl    | 32 dp | Large section gaps, header padding         |
| xxl   | 48 dp | Page margins on tablets, hero spacing      |

---

## Typography Scale

M3 type scale mapped to `MaterialTheme.typography` tokens.

| Role              | Token              | Default Size | Weight   | Line Height | Usage                        |
| ----------------- | ------------------ | ------------ | -------- | ----------- | ---------------------------- |
| Display Large     | `displayLarge`     | 57 sp        | Regular  | 64 sp       | Hero splash screens          |
| Display Medium    | `displayMedium`    | 45 sp        | Regular  | 52 sp       | Landing headlines            |
| Display Small     | `displaySmall`     | 36 sp        | Regular  | 44 sp       | Top-level headers            |
| Headline Large    | `headlineLarge`    | 32 sp        | Regular  | 40 sp       | Screen titles                |
| Headline Medium   | `headlineMedium`   | 28 sp        | Regular  | 36 sp       | Section headers              |
| Headline Small    | `headlineSmall`    | 24 sp        | Regular  | 32 sp       | Card titles                  |
| Title Large       | `titleLarge`       | 22 sp        | Regular  | 28 sp       | List item titles             |
| Title Medium      | `titleMedium`      | 16 sp        | Medium   | 24 sp       | Card subtitles, app bar      |
| Title Small       | `titleSmall`       | 14 sp        | Medium   | 20 sp       | Overlines, chip text         |
| Body Large        | `bodyLarge`        | 16 sp        | Regular  | 24 sp       | Primary body text            |
| Body Medium       | `bodyMedium`       | 14 sp        | Regular  | 20 sp       | Secondary body text          |
| Body Small        | `bodySmall`        | 12 sp        | Regular  | 16 sp       | Captions, helper text        |
| Label Large       | `labelLarge`       | 14 sp        | Medium   | 20 sp       | Buttons, tabs                |
| Label Medium      | `labelMedium`      | 12 sp        | Medium   | 16 sp       | Chips, badges                |
| Label Small       | `labelSmall`       | 11 sp        | Medium   | 16 sp       | Overlines, tiny badges       |

---

## Animation Duration

| Category | Duration      | Easing                              | Usage                                |
| -------- | ------------- | ------------------------------------ | ------------------------------------ |
| Micro    | 50 – 100 ms   | `FastOutSlowInEasing`               | Ripple, toggle, checkbox             |
| Short    | 100 – 200 ms  | `FastOutLinearInEasing`             | Fade, color change, elevation shift |
| Medium   | 200 – 300 ms  | `EaseInOut` / `Spring`              | Sheet expand, card reveal            |
| Long     | 300 – 500 ms  | `LinearOutSlowInEasing`             | Page transition, shared element      |

```kotlin
animateColorAsState(
    targetValue = targetColor,
    animationSpec = tween(durationMillis = 150, easing = FastOutSlowInEasing)
)
AnimatedVisibility(visible = show, enter = fadeIn() + expandVertically())
```

---

## Component Dimensions

Standard M3 component heights for consistent layouts.

| Component          | Height  | Width        | Notes                                    |
| ------------------ | ------- | ------------ | ---------------------------------------- |
| Button (filled)    | 40 dp   | wrap_content | 64 dp minimum width                      |
| Button (outlined)  | 40 dp   | wrap_content | Same as filled                            |
| Text Button        | 40 dp   | wrap_content | No background                            |
| FAB                | 56 dp   | 56 dp        | Regular FAB                              |
| Small FAB          | 40 dp   | 40 dp        | `SmallFloatingActionButton`              |
| Large FAB          | 96 dp   | 96 dp        | `LargeFloatingActionButton`              |
| Extended FAB       | 56 dp   | wrap_content | Minimum 80 dp width                      |
| Text Field (filled)| 56 dp   | match_parent | Input container height                   |
| Text Field (outlined)| 56 dp | match_parent | Same as filled                            |
| Top App Bar        | 64 dp   | match_parent | `MediumTopAppBar` scrolls to 64dp        |
| Bottom Navigation  | 80 dp   | match_parent | `NavigationBar` in M3                    |
| Card               | wrap    | wrap / fill  | Elevation-driven shadow                  |
| Chip               | 32 dp   | wrap_content | Input / suggestion / filter              |
| Switch             | 52 dp x 32 dp | —      | Track dimensions                          |
| Slider             | wrap    | match_parent | 48 dp touch target height                |
| Snackbar           | 48 dp min | match_parent | Min 48dp for touch target                |
| Dialog             | 280 dp max | wrap_content | Max 560 dp width on tablets              |

---

## UI Anti-Patterns

| Anti-Pattern                                    | Why It Fails                                    | Fix                                              |
| ----------------------------------------------- | ------------------------------------------------ | ------------------------------------------------ |
| More than 5 bottom navigation items             | Cognitive overload, tiny tap targets             | Use 3–5 items; move overflow to drawer or rail   |
| Multiple visible FABs                           | Competes for attention, violates M3 hierarchy    | One primary FAB; secondary actions in sheet/menu |
| Touch targets smaller than 48 dp                | Play Store accessibility rejection               | Use `Modifier.size(48.dp)` minimum               |
| Inconsistent spacing (non-grid)                 | Visual misalignment, unpolished appearance       | Follow the 8dp grid system exclusively            |
| No dark theme support                           | Poor UX in low-light, Pixel default dark mode    | Provide `Theme(darkTheme = isSystemInDarkTheme())`|
| Hard-coded colors outside theme                 | Breaks dynamic color, dark mode, consistency     | Always use `MaterialTheme.colorScheme.*` tokens  |
| Nested scrolling conflicts                      | Janky scroll, ANR on low-end devices             | Use `nestedScroll`, `pullRefresh`, Compose 1.6+  |
| Custom back handling without predictive back    | Breaks Android 14+ predictive back animation     | Use `BackHandler` + `PredictiveBackHandler`      |
| Ignoring window size classes                    | Broken layouts on foldables and tablets          | Use `WindowSizeClass` for adaptive layouts       |
| Using ViewPager for vertical paging             | Performance issues, fling conflicts              | Use `LazyColumn` with `userScrollEnabled`        |

---

## Performance Anti-Patterns

| Metric                        | Threshold   | Detection Tool            | Fix                                              |
| ----------------------------- | ----------- | ------------------------- | ------------------------------------------------ |
| Cold start time               | > 2 s       | Macrobenchmark, `adb shell am start -W` | Use Baseline Profiles, delay init, lazy columns |
| Frame rate                    | < 60 FPS    | JankStats, Perfetto       | Reduce recomposition, `derivedStateOf`, `key`    |
| Crash rate (daily)            | > 1.09 %    | Play Console, Firebase Crashlytics | Guard nulls, coroutine error handling   |
| ANR rate (daily)              | > 0.47 %    | Play Console, `StrictMode`| Move I/O off main thread, `withContext(Dispatchers.IO)` |
| APK size                      | > 20 MB     | `./gradlew assembleDebug --analyze` | App bundles, R8 shrinking, resource optimization |
| Memory allocation in draw     | > 0         | `compose-compiler` metrics| Avoid allocations in `drawBehind`, `drawWithContent` |

### Compose Performance Checklist

1. Use `remember` for expensive calculations inside composables
2. Use `derivedStateOf` to avoid unnecessary recomposition
3. Use `key` in `LazyColumn` / `LazyRow` items
4. Mark lambda parameters as `remember { { } }` when passed to children
5. Enable **strong skipping** mode (`androidx.compose.compiler.plugins.kotlin.features.nonSkippingGroupsOptimization`)
6. Use `immutable` data classes for state objects
7. Profile with `ComposeCompilerMetrics` and `ComposeLayoutMetrics`

---

## Accessibility Anti-Patterns

| Anti-Pattern                                         | Impact                               | Fix                                                    |
| ---------------------------------------------------- | ------------------------------------ | ------------------------------------------------------ |
| Missing `contentDescription` on `Image` / `Icon`    | TalkBack announces "unlabeled"       | Set `contentDescription = "descriptive text"`          |
| Element type included in labels ("Submit Button")    | TalkBack appends role automatically  | Use "Submit", not "Submit Button"                      |
| Complex multi-finger gestures for kids apps          | Motor skill barrier                  | Single-tap alternatives, large touch targets (56dp+)   |
| Color-only status indication                         | Inaccessible to color-blind users    | Add icons, patterns, or text labels                    |
| Fixed small text size (< 12sp body)                  | Fails large-text scaling             | Use M3 type scale; test with 200% font scaling         |
| Auto-playing media without controls                  | Disorienting, violates WCAG 1.4.2    | Provide pause/stop controls, no autoplay               |
| Focus order does not match visual order              | Disorienting keyboard/TalkBack users | Use `Modifier.focusRequester` chain, test with D-pad   |
| Custom views without `AccessibilityDelegate`         | Missing semantics                    | Use `Modifier.semantics { }` in Compose                |

---

## Review Checklist

Use this checklist when reviewing UI/UX code.

- [ ] All colors reference `MaterialTheme.colorScheme` tokens (no hard-coded hex)
- [ ] Typography uses `MaterialTheme.typography` tokens
- [ ] Spacing follows the 8dp grid (4, 8, 16, 24, 32, 48)
- [ ] Touch targets are >= 48dp with >= 8dp gaps
- [ ] Bottom navigation has 3–5 items
- [ ] Only one FAB visible at a time
- [ ] Dark theme is fully supported via `isSystemInDarkTheme()`
- [ ] Dynamic color works on Android 12+ (`MaterialTheme.dynamicColor`)
- [ ] Animations use M3 duration ranges (50–500ms)
- [ ] All images have meaningful `contentDescription` or `null` for decorative
- [ ] Labels do not include element type ("Submit" not "Submit Button")
- [ ] Focus order matches visual layout
- [ ] Window size classes are used for adaptive layouts
- [ ] Predictive back gesture supported on Android 14+
- [ ] `contentDescription` is `null` for purely decorative images
- [ ] App supports 200% font scaling without truncation
- [ ] Compose recomposition minimized (`remember`, `derivedStateOf`, `key`)
- [ ] Baseline Profiles configured for cold-start optimization

---

## External References

| Resource                                               | URL                                                        |
| ------------------------------------------------------ | ---------------------------------------------------------- |
| Material Design 3                                      | <https://m3.material.io/>                                  |
| Material 3 for Jetpack Compose                         | <https://developer.android.com/develop/ui/compose/designsystems/material3> |
| Material 3 Theme Builder                               | <https://m3.material.io/theme-builder>                     |
| Android Accessibility Checker                          | <https://developer.android.com/guide/topics/ui/accessibility/testing> |
| WCAG 2.1 Guidelines                                    | <https://www.w3.org/TR/WCAG21/>                            |
| Compose Performance                                    | <https://developer.android.com/develop/ui/compose/performance> |
| Android Baseline Profiles                              | <https://developer.android.com/topic/performance/baselineprofiles> |
| JankStats                                              | <https://developer.android.com/reference/kotlin/androidx/metrics/performance/JankStats> |
| Window Size Classes                                    | <https://developer.android.com/guide/topics/large-screens/support-different-screen-sizes> |
| Material 3 Motion                                      | <https://m3.material.io/styles/motion/overview>            |
