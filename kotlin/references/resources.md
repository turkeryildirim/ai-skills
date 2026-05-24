# Android Resource Management — Reference

## App Icon Requirements

| Density Bucket | DPI   | Launcher Icon Size | Play Store Icon | Web / Legacy |
| -------------- | ----- | ------------------ | --------------- | ------------ |
| mipmap-mdpi    | 160   | 48 x 48 px         | —               | 512 x 512    |
| mipmap-hdpi    | 240   | 72 x 72 px         | —               | —            |
| mipmap-xhdpi   | 320   | 96 x 96 px         | —               | —            |
| mipmap-xxhdpi  | 480   | 144 x 144 px       | —               | —            |
| mipmap-xxxhdpi | 640   | 192 x 192 px       | —               | —            |
| Play Store     | —     | —                  | 512 x 512 px    | —            |

> All icons must be PNG-24 with alpha. Provide adaptive icon XML for Android 8.0+.

---

## Adaptive Icon XML (Android 8+)

Adaptive icons consist of a foreground layer and a background layer, each 108 x 108 dp with the outer 18 dp on each side masked.

**File: `res/mipmap-anydpi-v26/ic_launcher.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />
</adaptive-icon>
```

| Layer       | Size (px at xxxhdpi) | Safe Zone   | Notes                                  |
| ----------- | -------------------- | ----------- | -------------------------------------- |
| Foreground  | 432 x 432            | Center 72%  | Logo / symbol; keep within safe zone   |
| Background  | 432 x 432            | Full bleed  | Solid color, gradient, or texture      |
| Monochrome  | 432 x 432            | Center 72%  | Android 13+ themed icon; single color  |

---

## Resource Naming Conventions

### Prefixes

| Resource Type | Prefix        | Example                              | Notes                                   |
| ------------- | ------------- | ------------------------------------ | --------------------------------------- |
| Layout        | `layout_`     | `layout_activity_main`               | Include component type in name          |
| Image (icon)  | `ic_`         | `ic_search`, `ic_nav_home`           | Vector drawables preferred              |
| Image (photo) | `img_`        | `img_hero_banner`, `img_placeholder` | Raster assets                           |
| Background    | `bg_`         | `bg_card_surface`, `bg_button_primary` | Shapes, gradients, surfaces          |
| Color         | `color_`      | `color_brand_primary`                | Semantic, not literal (`primary` not `blue`) |
| String        | descriptive   | `login_button_label`, `error_network` | Lowercase snake_case                  |
| Dimension     | descriptive   | `spacing_md`, `elevation_card`       | Group by usage category                |
| Style         | descriptive   | `Widget_App_Button`                  | `Widget_App_Component` convention      |
| Menu          | descriptive   | `menu_main`, `menu_overflow`         | Match associated activity/fragment     |
| Raw / Assets  | descriptive   | `config.json`, `terms_of_service.html` | Lowercase with underscores           |
| Animation     | descriptive   | `fade_in`, `slide_up`                | Short, descriptive names               |
| Font          | descriptive   | `font_roboto_regular`                | Include weight in name                 |
| Values        | descriptive   | `colors.xml`, `strings.xml`, `dimens.xml` | Standard Android filenames        |
| ID            | descriptive   | `et_email`, `rv_contacts`            | Prefix with widget type abbreviation   |

### ID Prefix Conventions

| Widget / Element | Prefix  | Example              |
| ---------------- | ------- | -------------------- |
| TextView         | `tv_`   | `tv_title`           |
| EditText         | `et_`   | `et_email`           |
| Button           | `btn_`  | `btn_submit`         |
| ImageView        | `iv_`   | `iv_avatar`          |
| RecyclerView     | `rv_`   | `rv_contacts`        |
| ViewPager2       | `vp_`   | `vp_onboarding`      |
| ProgressBar      | `pb_`   | `pb_loading`         |
| CheckBox         | `cb_`   | `cb_terms`           |
| RadioButton      | `rb_`   | `rb_option_a`        |
| Switch / Toggle  | `sw_`   | `sw_notifications`   |
| Fragment         | `f_`    | `f_settings`         |
| Layout           | `layout_` | `layout_item_card` |
| Navigation       | `nav_`  | `nav_main`           |

---

## Android Reserved Names to Avoid

Never use these names for custom resources — they clash with framework or support library identifiers.

### Colors

| Reserved Name       | Why Reserved                              |
| -------------------- | ------------------------------------------ |
| `background`         | `android:background` attribute             |
| `foreground`         | `android:foreground` attribute             |
| `transparent`        | `@android:color/transparent`               |
| `black`              | `@android:color/black`                     |
| `white`              | `@android:color/white`                     |
| `primary`            | M3 theme attribute `colorPrimary`          |
| `secondary`          | M3 theme attribute `colorSecondary`        |
| `surface`            | M3 theme attribute `colorSurface`          |
| `error`              | M3 theme attribute `colorError`            |
| `accent`             | Legacy AppCompat attribute                 |

### Icons / Drawables

| Reserved Name       | Why Reserved                              |
| -------------------- | ------------------------------------------ |
| `icon`               | `android:icon` manifest attribute          |
| `logo`               | `android:logo` manifest attribute          |
| `notification_icon`  | System notification icon slot             |
| `ic_launcher`        | Default launcher icon name                 |
| `ic_menu_*`          | Legacy options menu icons                  |

### Views / Layouts

| Reserved Name         | Why Reserved                              |
| --------------------- | ------------------------------------------ |
| `view`                | `android.view.View` class                  |
| `text`                | `android:text` attribute                   |
| `button`              | `android.widget.Button` class              |
| `list`                | `android.widget.ListView` class            |
| `grid`                | `android.widget.GridView` class            |
| `frame`               | `android.widget.FrameLayout` class         |
| `linear`              | `android.widget.LinearLayout` class        |
| `relative`            | `android.widget.RelativeLayout` class      |
| `recycler`            | `androidx.recyclerview` class              |
| `content`             | Common convention for `layout/content_*`   |
| `main`                | Convention clash; use `activity_main` instead |

### Attributes / Identifiers

| Reserved Name       | Why Reserved                              |
| -------------------- | ------------------------------------------ |
| `id`                 | `android:id` attribute                     |
| `name`               | `android:name` attribute                   |
| `type`               | `android:type` attribute                   |
| `style`              | `style` XML attribute                      |
| `theme`              | `android:theme` attribute                  |
| `tag`                | `android:tag` attribute                    |
| `src`                | `android:src` attribute                    |
| `drawable`           | `android:drawable` attribute               |
| `layout_width`       | `android:layout_width`                     |
| `layout_height`      | `android:layout_height`                    |

### System / Package Names

| Reserved Name       | Why Reserved                              |
| -------------------- | ------------------------------------------ |
| `app`                | Module namespace                           |
| `android`            | Android framework namespace                |
| `content`            | `android.content` package                  |
| `context`            | `android.content.Context` class            |
| `activity`           | `android.app.Activity` class               |
| `fragment`           | `androidx.fragment.app.Fragment` class     |
| `service`            | `android.app.Service` class                |
| `receiver`           | `android.content.BroadcastReceiver`        |
| `provider`           | `android.content.ContentProvider`          |
| `intent`             | `android.content.Intent` class             |
| `bundle`             | `android.os.Bundle` class                  |
| `parcelable`         | `android.os.Parcelable` interface          |

---

## Wrong vs Correct — Resource Naming

### Colors

| Wrong                         | Correct                         | Reason                                |
| ----------------------------- | ------------------------------- | ------------------------------------- |
| `<color name="blue">#2196F3</color>` | `<color name="color_brand_primary">#2196F3</color>` | Semantic, not literal          |
| `<color name="background">#FFFFFF</color>` | `<color name="color_surface_light">#FFFFFF</color>` | Avoids reserved name   |
| `<color name="red">#F44336</color>` | `<color name="color_error">#F44336</color>` | Describes role, not value      |

### Strings

| Wrong                                  | Correct                                    | Reason                           |
| -------------------------------------- | ------------------------------------------ | -------------------------------- |
| `<string name="text1">Submit</string>` | `<string name="login_button_label">Submit</string>` | Descriptive key          |
| `<string name="msg">Error occurred</string>` | `<string name="error_network_offline">Error occurred</string>` | Specific context |
| `<string name="hello">Hello %s</string>` | `<string name="greeting_welcome">Hello %s</string>` | Descriptive, translatable |

### Drawables

| Wrong                      | Correct                       | Reason                              |
| -------------------------- | ----------------------------- | ----------------------------------- |
| `icon.png`                 | `ic_launcher_foreground.png`  | Reserved name, missing density      |
| `button_bg.xml`            | `bg_button_primary.xml`       | Use `bg_` prefix, describe variant  |
| `photo.png`                | `img_hero_banner.png`         | Use `img_` prefix, descriptive name |

### Layouts

| Wrong                      | Correct                       | Reason                              |
| -------------------------- | ----------------------------- | ----------------------------------- |
| `main.xml`                 | `layout_activity_main.xml`    | Reserved name, missing prefix       |
| `item.xml`                 | `layout_item_contact.xml`     | Too generic, missing prefix         |
| `dialog.xml`               | `layout_dialog_confirmation.xml` | Too generic                      |

---

## RTL (Right-to-Left) Support

### Guidelines

1. Use `start` / `end` instead of `left` / `right` in layouts
2. Use `paddingStart` / `paddingEnd` instead of `paddingLeft` / `paddingRight`
3. Use `layout_marginStart` / `layout_marginEnd` instead of `margin` equivalents
4. Use `android:layoutDirection="locale"` for locale-driven direction
5. In Compose, use `LayoutDirection` from `LocalLayoutDirection`

```kotlin
val layoutDirection = LocalLayoutDirection.current
Modifier.padding(start = 16.dp)
```

### Verification

| Step | Action                                                      |
| ---- | ----------------------------------------------------------- |
| 1    | Enable "Force RTL layout direction" in Developer Options    |
| 2    | Visual inspection for mirrored layouts                      |
| 3    | Test with `ar`, `he`, `fa` locales                          |
| 4    | Verify text alignment is `TEXT_ALIGNMENT_VIEW_START`        |
| 5    | Check icons with directional cues have RTL variants         |

---

## Resource Qualifiers — Common Order

When providing alternative resources, qualifier order matters.

| Order | Qualifier              | Example              |
| ----- | ---------------------- | -------------------- |
| 1     | MCC and MNC            | `mcc310-mnc004`      |
| 2     | Language and region    | `en-rUS`, `ar`       |
| 3     | Layout direction       | `ldrtl`              |
| 4     | Smallest width         | `sw600dp`            |
| 5     | Available width        | `w720dp`             |
| 6     | Available height       | `h1024dp`            |
| 7     | Screen size            | `large`, `xlarge`    |
| 8     | Screen aspect          | `long`, `notlong`    |
| 9     | Round screen           | `round`, `notround`  |
| 10    | Wide color gamut       | `widecg`, `nowidecg` |
| 11    | High dynamic range     | `highdr`, `lowdr`    |
| 12    | Screen orientation     | `port`, `land`       |
| 13    | UI mode                | `car`, `desk`, `tv`  |
| 14    | Night mode             | `night`, `notnight`  |
| 15    | Screen pixel density   | `mdpi`, `hdpi`       |
| 16    | Touch screen type      | `notouch`, `finger`  |
| 17    | Keyboard availability  | `keyshidden`         |
| 18    | Primary text input     | `nokeys`, `qwerty`   |
| 19    | Navigation key avail.  | `navhidden`          |
| 20    | Primary non-touch nav  | `nonav`, `dpad`      |
| 21    | Platform version       | `v26`, `v34`         |

---

## Cross References

See related rules for resource management:

- **res-naming** — Enforced naming conventions for all resource types
- **res-colors** — Color token strategy, semantic naming, dark theme
- **res-strings** — String resource organization, plurals, formatting
- **res-drawables** — Vector drawable guidelines, density handling
- **res-layouts** — Layout file organization, naming, conventions
- **res-icons** — Icon design specs, adaptive icons, monochrome
- **res-rtl** — Right-to-left layout support and testing

---

## External References

| Resource                                         | URL                                                                  |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| Android Resource Guide                           | <https://developer.android.com/guide/topics/resources/>              |
| Providing Resources                              | <https://developer.android.com/guide/topics/resources/providing-resources> |
| Adaptive Icons                                   | <https://developer.android.com/develop/ui/views/launch/icon_design_adaptive> |
| App Icon Specifications                          | <https://developer.android.com/google/play/resources/icon-design-specifications> |
| RTL Support                                      | <https://developer.android.com/develop/ui/views/layout/rtl>          |
| Material Design Icons                            | <https://fonts.google.com/icons>                                     |
| Android Vector Drawables                         | <https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources> |
