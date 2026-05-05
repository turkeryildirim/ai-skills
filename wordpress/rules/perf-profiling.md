---
title: Performance Profiling
impact: HIGH
impactDescription: Measure before optimizing — blind fixes waste time and can regress
tags: performance, profiling, query-monitor, wp-cli
---

## Performance Profiling

**Impact: HIGH (measure first, fix one bottleneck at a time, verify improvement)**

Always capture a baseline before optimizing. Use WP-CLI `doctor` and `profile` for systematic diagnosis. Query Monitor for detailed query analysis. Fix one category at a time.

## Bad Example

```php
// Adding indexes without measuring
$wpdb->query( "ALTER TABLE {$wpdb->posts} ADD INDEX my_idx (post_title)" );

// Installing caching plugin without profiling
// "It feels slow, let's add a cache plugin"
```

## Good Example

```bash
# 1. Capture baseline
wp profile stage --url=https://example.com/slow-page/

# 2. Quick diagnostics
wp doctor check --all

# 3. Identify slow hooks
wp profile hook --url=https://example.com/slow-page/ --spotlight

# 4. Fix, then verify
wp profile stage --url=https://example.com/slow-page/
```

## Why

- **Measure first** — capture baseline TTFB before any changes
- **`wp doctor check`** — catches common foot-guns (autoload bloat, stale cron, missing indexes)
- **`wp profile stage`** — shows bootstrap/main_query/template timing breakdown
- **`wp profile hook --spotlight`** — identifies slow hooks and callbacks
- **Fix one bottleneck at a time** — verify each fix individually
- **Bottleneck categories:** DB queries, autoloaded options, object cache misses, HTTP calls, cron
- **`SAVEQUARIES`/Query Monitor add overhead** — don't run in production without approval

Reference: [WP-CLI Profile](https://developer.wordpress.org/cli/commands/profile/) | [Query Monitor](https://wordpress.org/plugins/query-monitor/)
