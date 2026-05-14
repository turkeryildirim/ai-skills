# Localization and Internationalization

Expert guidance for iOS 16+ apps using String Catalogs, modern string types, FormatStyle, and RTL-aware layout.

## 1. String Catalogs (.xcstrings) — iOS 17+

Xcode 15+ unified format replacing `.strings` and `.stringsdict`. String Catalogs automatically extract:
- SwiftUI `Text("Welcome")` parameters
- `String(localized:)` calls
- `LocalizedStringResource` declarations

The catalog tracks translation states and supports native pluralization without XML.

### Generated Localizable Symbols (Xcode 26+)

Enable **Build Settings > Localization > "Generate String Catalog Symbols"** for compile-time verification:

```swift
// Key "room_available" generates:
Text(.roomAvailable)  // ✅ type-safe, no runtime string lookup
// Instead of:
Text("room_available") // ❌ string literal, no compile-time check
```

## 2. String Types Decision Matrix

| Context | Type | Why |
|---------|------|-----|
| SwiftUI view parameters | `LocalizedStringKey` | Automatic implicit conversion |
| View models, services, logic | `String(localized:)` | Resolved strings for business logic |
| App Intents, Widgets, extensions | `LocalizedStringResource` | Deferred resolution |

```swift
// ✅ View model / service
let message = String(localized: "welcome_message")

// ✅ SwiftUI view (implicit LocalizedStringKey)
Text("welcome_message")

// ✅ App Intent
let title = LocalizedStringResource("action_title")
```

## 3. String Interpolation

Interpolated values become reorderable positional arguments for translators:

```swift
// ✅ Correct
Text("Welcome, \(name)! You have \(count) new messages.")
// Catalog: "Welcome, %@! You have %lld new messages."
// Arabic can reorder: "%lld رسائل جديدة، مرحباً %@!"

// ❌ Wrong — concatenation breaks word order for other languages
Text("Welcome, " + name + "!")
```

## 4. Pluralization

String Catalogs detect integer interpolations and offer CLDR plural variants:

| Language | Variants |
|----------|---------|
| English | `one`, `other` |
| Arabic | `zero`, `one`, `two`, `few`, `many`, `other` |
| Russian | `one`, `few`, `many`, `other` |

Use the catalog UI — do NOT manually write `.stringsdict` XML for new projects.

## 5. FormatStyle (Locale-Aware Formatting)

Never hardcode date, number, or measurement formats. See [`references/formatstyle.md`](references/formatstyle.md) for full coverage.

```swift
// ✅ Dates
Text(appointment, format: .dateTime.month(.wide).day().year())
Text(Date.now, style: .relative)  // "5 minutes ago"

// ✅ Numbers
Text(count, format: .number)
Text(ratio, format: .percent)

// ✅ Currency
Text(price, format: .currency(code: "USD"))

// ✅ Measurements (auto-convert units by locale)
Text(distance, format: .measurement(width: .abbreviated))
```

## 6. Right-to-Left (RTL) Layout

SwiftUI auto-mirrors most layouts for Arabic, Hebrew, Urdu, and Persian.

```swift
// ✅ Always use directional modifiers
.padding(.leading, 16)   // mirrors to trailing in RTL
.frame(maxWidth: .infinity, alignment: .leading)  // mirrors in RTL

// ❌ Never use fixed directions
.padding(.left, 16)
.frame(maxWidth: .infinity, alignment: .left)

// ✅ Only flip directional icons, not content icons
Image(systemName: "chevron.right")
    .flipsForRightToLeftLayoutDirection(true)

// ✅ Test RTL in previews
.environment(\.layoutDirection, .rightToLeft)
```

## 7. Review Checklist

- [ ] All user-facing strings are localized (no raw string literals in UI).
- [ ] No string concatenation for visible text.
- [ ] `FormatStyle` used for all dates, numbers, currencies.
- [ ] Plural variants added in String Catalog (not stringsdict).
- [ ] Layout uses `.leading`/`.trailing`, not `.left`/`.right`.
- [ ] Generated symbols enabled (Xcode 26+).
- [ ] German (+30% text expansion) tested.
- [ ] Arabic/Hebrew RTL tested.
- [ ] Pseudolocalization tested.
- [ ] Stable symbol-style keys used (not English text as key).
- [ ] Translator context comments provided.

## 8. MUST NOT DO

## Cross References

- Related rules: `l10n-no-concatenation`, `l10n-format-style`
- Related references: [`formatstyle.md`](formatstyle.md), [`accessibility.md`](accessibility.md)

- **NSLocalizedString:** Do NOT use in new code. Use `String(localized:)` or String Catalogs.
- **Hardcoded date formats:** `"MM/dd/yyyy"` breaks for non-US locales.
- **String concatenation:** Word order varies; use interpolation with reorderable placeholders.
- **`.left`/`.right` alignment:** Use `.leading`/`.trailing` for RTL support.
- **Fixed-width layouts:** Text expands 30–40% in German; use flexible sizing.
- **Hardcoded locales:** Never `.locale(Locale(identifier: "en_US"))` unless required for server communication.
