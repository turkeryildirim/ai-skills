# Figma → Compose Conversion Rules in Detail

## Overview

This document provides detailed rules for converting various Figma design elements into Jetpack Compose code.

---

## Color Conversion

### rgba → Color Format

#### Basic Conversion Formula
```
Figma: rgba(R, G, B, A)
↓
Compose: Color(0xAARRGGBB)

Conversion:
- A (Alpha): 0.0-1.0 → 0x00-0xFF
- R (Red): 0-255 → 0x00-0xFF
- G (Green): 0-255 → 0x00-0xFF
- B (Blue): 0-255 → 0x00-0xFF
```

#### Examples
```kotlin
// Example 1: Fully Opaque
Figma: rgba(0, 116, 196, 1.0)
Compose: Color(0xFF0074C4)

// Example 2: Semi-transparent
Figma: rgba(102, 102, 102, 0.5)
Compose: Color(0x80666666)  // 0.5 * 255 = 127.5 ≈ 128 (0x80)
```

---

## Typography Conversion

### font-size → fontSize
```
Figma: font-size: 17px
↓
Compose: fontSize = 17.sp
```

### font-weight → FontWeight
```
100 → FontWeight.Thin
200 → FontWeight.ExtraLight
300 → FontWeight.Light
400 → FontWeight.Normal
500 → FontWeight.Medium
600 → FontWeight.SemiBold
700 → FontWeight.Bold
800 → FontWeight.ExtraBold
900 → FontWeight.Black
```

### line-height → lineHeight
```kotlin
// Figma: line-height: 1.35, font-size: 17px
Compose: fontSize = 17.sp, lineHeight = (17 * 1.35).sp // 22.95.sp
```

---

## Layout Conversion

### padding → Modifier.padding

#### Uniform Padding
```kotlin
// Figma: padding: 20px
Compose: Modifier.padding(20.dp)
```

#### Directional Padding
```kotlin
// Figma: padding-left: 10px, padding-top: 20px
Compose: Modifier.padding(start = 10.dp, top = 20.dp)
```

### gap → Arrangement.spacedBy
```kotlin
// Figma: gap: 10px
Compose: Arrangement.spacedBy(10.dp)
```

### border-radius → RoundedCornerShape
```kotlin
// Figma: border-radius: 4px
Compose: RoundedCornerShape(4.dp)
```

---

## System Bar & Windows Inset Handling (Modern Android Best Practice)

When Figma designs contain top status bars or bottom navigation bars, **do not** implement them using fixed height spacers. Fixed heights will break across different device aspect ratios, foldables, and punch-hole cameras.

Instead, use **Compose Window Insets Modifiers**:

```kotlin
// ❌ Bad Example: Hardcoding status bar height (Figma status-bar: 52px)
Spacer(modifier = Modifier.height(52.dp))

// ✅ Good Example: Let WindowInsets handle the padding dynamically
Column(
    modifier = Modifier
        .fillMaxSize()
        .statusBarsPadding() // Dynamically offsets for status bar & notch
) {
    Content()
}
```

### Common Insets Modifiers:
- `.statusBarsPadding()`: Pads the container to avoid overlapping with the status bar.
- `.navigationBarsPadding()`: Pads the container to avoid overlapping with the bottom system navigation keys or gestures bar.
- `.safeDrawingPadding()`: Pads the container to completely avoid all system bars and IME (soft keyboard).

---

## Managing Layout Constants (Calculated Offsets)

### ❌ Bad Example: Magic Numbers
```kotlin
Box(modifier = Modifier.padding(start = 92.dp)) // Hardcoded magic number
```

### ✅ Good Example: Expressed via Layout Token Math
```kotlin
private object LayoutDimensions {
    val imagePadding = 10.dp
    val imageWidth = 72.dp
    val imageSpacing = 10.dp
    
    // Explicitly derived, self-explanatory offset
    val dividerStartPadding = imagePadding + imageWidth + imageSpacing // = 92.dp
}

// Usage
Box(modifier = Modifier.padding(start = LayoutDimensions.dividerStartPadding))
```
