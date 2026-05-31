# Figma Compliance Rate Checklist

## Overview

This document provides a detailed checklist to evaluate how closely generated Jetpack Compose code conforms to Figma design specifications.

## Compliance Rate Formula

```
Compliance Rate = (Earned weighted points / Total weighted points) × 100

Target: 95% or higher
```

---

## Checklist Categories

### 1. Color Compliance (30%)

#### 1-1. Accuracy of Color Definitions
- [ ] **Background Color**: Exactly matches the Figma rgba/hex value.
  ```kotlin
  // Figma: rgba(245, 245, 245, 1.0)
  // Compose: Color(0xFFF5F5F5)
  Match: ✅ / Mismatch: ❌
  ```
- [ ] **Text Color**: Exactly matches the Figma rgba/hex value.
  ```kotlin
  // Figma: rgba(51, 51, 51, 1.0)
  // Compose: Color(0xFF333333)
  Match: ✅ / Mismatch: ❌
  ```
- [ ] **Accent Color**: Exactly matches the Figma rgba/hex value.
  ```kotlin
  // Figma: rgba(0, 116, 196, 1.0)
  // Compose: Color(0xFF0074C4)
  Match: ✅ / Mismatch: ❌
  ```
- [ ] **Color Constant Naming**: Expresses clear purpose/intent.
  ```kotlin
  ❌ color1, blueColor
  ✅ tabActive, titleText, imagePlaceholder
  ```

**Scoring**:
- Exact color match: 5 points each (max 20 points)
- Naming appropriateness: 10 points

---

### 2. Typography Compliance (30%)

#### 2-1. Font Size
- [ ] **fontSize**: Exactly matches Figma px value (px to sp conversion).
  ```kotlin
  // Figma: font-size: 17px
  // Compose: fontSize = 17.sp
  Match: ✅ / Mismatch: ❌
  ```

#### 2-2. Font Weight
- [ ] **fontWeight**: Uses the corresponding FontWeight for the Figma value.
  ```kotlin
  // Figma: font-weight: 700
  // Compose: fontWeight = FontWeight.Bold
  Match: ✅ / Mismatch: ❌
  ```

#### 2-3. Line Height
- [ ] **lineHeight**: Precise calculation based on font size and ratio.
  ```kotlin
  // Figma: line-height: 1.35, font-size: 17px
  // Compose: lineHeight = 22.95.sp  // 17 * 1.35
  Match: ✅ / Mismatch: ❌
  ```

#### 2-4. Font Family
- [ ] **fontFamily**: Matches the specified Figma font or appropriate default fallback.
  ```kotlin
  // Figma: font-family: Inter
  // Compose: fontFamily = Inter
  Match: ✅ / Mismatch: ❌
  ```

**Scoring**:
- fontSize match: 8 points
- fontWeight match: 8 points
- lineHeight match: 8 points
- fontFamily appropriateness: 6 points

---

### 3. Layout & Structure Compliance (30%)

#### 3-1. Padding & Margin
- [ ] **padding**: Exactly matches Figma px value (px to dp conversion).
  ```kotlin
  // Figma: padding: 20px
  // Compose: .padding(20.dp)
  Match: ✅ / Mismatch: ❌
  ```
- [ ] **Directional padding**: Accurate in each direction.
  ```kotlin
  // Figma: padding-left: 10px, padding-top: 20px
  // Compose: .padding(start = 10.dp, top = 20.dp)
  Match: ✅ / Mismatch: ❌
  ```

#### 3-2. Spacing (gap/spacing)
- [ ] **gap**: Element interval inside Row/Column matches Figma.
  ```kotlin
  // Figma: gap: 10px
  // Compose: Arrangement.spacedBy(10.dp)
  Match: ✅ / Mismatch: ❌
  ```

#### 3-3. Corner Radius
- [ ] **border-radius**: Exactly matches Figma value (no guesswork).
  ```kotlin
  // Figma: border-radius: 4px
  // Compose: RoundedCornerShape(4.dp)
  Match: ✅ / Mismatch: ❌
  ```

#### 3-4. Size (width/height)
- [ ] **width/height**: Matches Figma value.
  ```kotlin
  // Figma: width: 100px, height: 76px
  // Compose: .size(100.dp, 76.dp)
  Match: ✅ / Mismatch: ❌
  ```

#### 3-5. System Bar Padding (Modern Best Practice)
- [ ] **No Brittle Spacers**: Uses system-provided insets instead of hardcoded spacers for status/navigation bars.
  ```kotlin
  ❌ Spacer(modifier = Modifier.height(52.dp)) // Hardcoded spacer
  ✅ Modifier.statusBarsPadding() or Modifier.safeDrawingPadding() // Modern inset
  Match: ✅ / Mismatch: ❌
  ```

#### 3-6. Magic Number Elimination
- [ ] **No hardcoded offsets**: All complex layout coordinates are calculated cleanly.
  ```kotlin
  ❌ .padding(start = 92.dp)  // Where does 92 come from?
  ✅ .padding(start = LayoutDimensions.dividerStartPadding)
     // = imagePadding + imageWidth + imageSpacing
  Match: ✅ / Mismatch: ❌
  ```

**Scoring**:
- padding match: 5 points
- spacing match: 5 points
- cornerRadius match: 5 points
- size match: 5 points
- system bar inset usage: 5 points
- magic number elimination: 5 points

---

### 4. Prohibition of Vibe-Coding (10%)

#### 4-1. No Additions or Omissions
- [ ] **No arbitrary corner radius not specified in Figma**
- [ ] **No arbitrary font modifications not specified in Figma**
- [ ] **No arbitrary spacers or elements added/omitted**

**Scoring**:
- No vibe-coding violations: 10 points

---

## Compliance Scorecard

### Basic Info
```markdown
## Compliance Scorecard

### Component: [ComponentName]
### Node ID: [node-id] (formatted with colon)
### Generated: [timestamp]
```

### Detailed Scores

```markdown
#### 1. Color Compliance: XX / 30 points
| Item | Figma Spec | Compose Impl | Match | Points | Earned |
|------|------------|--------------|-------|--------|--------|
| Background | rgba(245, 245, 245, 1.0) | Color(0xFFF5F5F5) | ✅ | 5 | 5 |
| Title | rgba(51, 51, 51, 1.0) | Color(0xFF333333) | ✅ | 5 | 5 |
| Accent | rgba(0, 116, 196, 1.0) | Color(0xFF0074C4) | ✅ | 5 | 5 |
| Meta | rgba(153, 153, 153, 1.0) | Color(0xFF999999) | ✅ | 5 | 5 |
| Naming | - | tabActive, titleText | ✅ | 10 | 10 |

**Subtotal**: 30 / 30 points

---

#### 2. Typography Compliance: XX / 30 points
| Item | Figma Spec | Compose Impl | Match | Points | Earned |
|------|------------|--------------|-------|--------|--------|
| fontSize | 17px | 17.sp | ✅ | 8 | 8 |
| fontWeight | 700 | FontWeight.Bold | ✅ | 8 | 8 |
| lineHeight | 1.35 (22.95px) | 22.95.sp | ✅ | 8 | 8 |
| fontFamily | Inter | Inter | ✅ | 6 | 6 |

**Subtotal**: 30 / 30 points

---

#### 3. Layout Compliance: XX / 30 points
| Item | Figma Spec | Compose Impl | Match | Points | Earned |
|------|------------|--------------|-------|--------|--------|
| padding | 20px | 20.dp | ✅ | 5 | 5 |
| gap | 10px | spacedBy(10.dp) | ✅ | 5 | 5 |
| cornerRadius | 4px | RoundedCornerShape(4.dp) | ✅ | 5 | 5 |
| imageSize | 100x76px | size(100.dp, 76.dp) | ✅ | 5 | 5 |
| systemInsets | status bar space | statusBarsPadding() | ✅ | 5 | 5 |
| magicNumbers | no hardcoded offsets | calculated layout values | ✅ | 5 | 5 |

**Subtotal**: 30 / 30 points

---

#### 4. Vibe-Coding Prohibited: XX / 10 points
| Item | Checklist | Result | Points | Earned |
|------|-----------|--------|--------|--------|
| No Vibe-Coding | Checked for arbitrary elements | ✅ | 10 | 10 |

**Subtotal**: 10 / 10 points
```

### Overall Score
```markdown
## Overall Compliance Score: 100 / 100 points (100%)

### Verdict: ✅ EXCELLENT (95% or higher)
```
