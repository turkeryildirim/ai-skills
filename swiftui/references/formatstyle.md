# FormatStyle — Locale-Aware Formatting

Foundation's `FormatStyle` protocol for formatting values into human-readable strings (iOS 15+). Replaces all legacy `Formatter` subclasses with a type-safe, composable API.

## Core Rule

**Use `FormatStyle` for iOS 15+.** Never hardcode locales unless required for server communication.

## 1. Numbers

```swift
// Integer
count.formatted(.number)                           // "1,234"
count.formatted(.number.grouping(.never))          // "1234"
count.formatted(.number.notation(.compactName))    // "1.2K"
count.formatted(.number.notation(.scientific))     // "1.234E3"

// Floating point
ratio.formatted(.number.precision(.fractionLength(2)))  // "3.14"
value.formatted(.number.sign(strategy: .always()))      // "+42"

// Percentage
ratio.formatted(.percent)                          // "75%"
ratio.formatted(.percent.precision(.fractionLength(1))) // "75.0%"
```

## 2. Currency

```swift
// Standard currency formatting
price.formatted(.currency(code: "USD"))            // "$29.99"
price.formatted(.currency(code: "EUR"))            // "€29,99" (locale-dependent)
price.formatted(.currency(code: "TRY"))            // "₺29,99"

// Precision
price.formatted(.currency(code: "USD").precision(.fractionLength(0))) // "$30"
```

Always use ISO 4217 currency codes. Never hardcode currency symbols.

## 3. Dates and Times

```swift
// Component-based
Text(date, format: .dateTime.day().month(.wide).year())  // "15 May 2026"
Text(date, format: .dateTime.hour().minute())            // "3:45 PM"

// Predefined styles
Text(date, format: .dateTime.month(.abbreviated).day()) // "May 15"
date.formatted(date: .long, time: .shortened)           // "May 15, 2026 at 3:45 PM"
date.formatted(date: .omitted, time: .standard)         // "3:45:00 PM"

// Relative dates
Text(date, format: .relative(presentation: .numeric))   // "5 minutes ago"
Text(date, format: .relative(presentation: .named))     // "yesterday"

// ISO 8601
date.formatted(.iso8601)

// Date intervals
Text(start..<end, format: .interval)                    // "May 15 – May 20"
```

## 4. Durations (iOS 16+)

```swift
// Time-style (clock-like)
let duration = Duration.seconds(3661)
duration.formatted(.time(pattern: .hourMinuteSecond))  // "1:01:01"
duration.formatted(.time(pattern: .minuteSecond))      // "61:01"

// Units-style (labeled)
duration.formatted(.units(allowed: [.hours, .minutes]))        // "1 hr, 1 min"
duration.formatted(.units(width: .abbreviated, maximumUnitCount: 1)) // "1 hr"
```

Choose `.time(pattern:)` for compact clock display. Choose `.units(allowed:)` for labeled descriptions.

## 5. Measurements

```swift
// Auto-converts units by locale (km ↔ miles)
let distance = Measurement(value: 5, unit: UnitLength.kilometers)
distance.formatted(.measurement(width: .abbreviated))   // "5 km" or "3.1 mi"
distance.formatted(.measurement(width: .wide))          // "5 kilometers"

// Always include usage context for correct unit selection
let speed = Measurement(value: 100, unit: UnitSpeed.kilometersPerHour)
speed.formatted(.measurement(width: .abbreviated, usage: .road))
```

## 6. Person Names

```swift
let components = PersonNameComponents(givenName: "Türker", familyName: "Yıldırım")
components.formatted(.name(style: .default))   // "Türker Yıldırım"
components.formatted(.name(style: .short))     // "Türker"
components.formatted(.name(style: .abbreviated)) // "TY"
```

Respects locale, script direction, and user preferences automatically.

## 7. Lists

```swift
["Swift", "SwiftUI", "SwiftData"].formatted(.list(type: .and))    // "Swift, SwiftUI, and SwiftData"
["Apple", "Google"].formatted(.list(type: .or, width: .narrow))   // "Apple or Google"
```

## 8. Byte Counts

```swift
let bytes: Int64 = 1_500_000
ByteCountFormatStyle().format(bytes)           // "1.5 MB"
bytes.formatted(.byteCount(style: .file))      // "1.5 MB"
bytes.formatted(.byteCount(style: .memory))    // "1.4 MiB"
```

## 9. URLs

```swift
url.formatted(.url)                            // Full URL string
url.formatted(.url.scheme(.omitted))           // "example.com/path"
```

## 10. SwiftUI Integration

Prefer `Text(value, format:)` over pre-formatted strings:

```swift
// ✅ Enables efficient SwiftUI re-rendering and accessibility scaling
Text(price, format: .currency(code: "USD"))
Text(count, format: .number)
Text(date, format: .dateTime.month().day().year())

// ❌ Pre-formatted string bypasses SwiftUI formatting pipeline
Text(price.formatted(.currency(code: "USD")))
```

## 11. Custom FormatStyle

```swift
struct OrdinalFormatStyle: FormatStyle {
    func format(_ value: Int) -> String {
        let suffix: String
        switch value % 10 {
        case 1 where value % 100 != 11: suffix = "st"
        case 2 where value % 100 != 12: suffix = "nd"
        case 3 where value % 100 != 13: suffix = "rd"
        default: suffix = "th"
        }
        return "\(value)\(suffix)"
    }
}

// Usage
Text(rank, format: OrdinalFormatStyle())  // "1st", "2nd", "42nd"
```

Custom `FormatStyle` types must conform to `Codable` and `Hashable` for framework caching.

## 12. Review Checklist

## Cross References

- Related rules: `l10n-format-style`
- Related references: [`localization.md`](localization.md), [`accessibility.md`](accessibility.md), [`view-structure.md`](view-structure.md)

- [ ] `FormatStyle` used instead of `DateFormatter`, `NumberFormatter`, etc.
- [ ] SwiftUI `Text` uses `format:` parameter, not pre-formatted strings.
- [ ] No hardcoded locales (unless required for server communication).
- [ ] `Duration` uses correct style (`.time(pattern:)` vs `.units(allowed:)`).
- [ ] Currency uses ISO 4217 codes, not hardcoded symbols.
- [ ] Measurements include `usage:` parameter for correct unit context.
- [ ] Custom `FormatStyle` conforms to `Codable` and `Hashable`.
