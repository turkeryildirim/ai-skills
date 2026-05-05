---
title: WP-CLI Commands
impact: MEDIUM
impactDescription: Proper WP-CLI usage prevents data loss and targeting errors
tags: wpcli, commands, database, search-replace
---

## WP-CLI Commands

**Impact: MEDIUM (incorrect commands can destroy production data)**

Always confirm environment before write operations. Always `--dry-run` for search-replace. Always backup before risky operations. Confirm targeting with `--path` and `--url`.

## Bad Example

```bash
wp search-replace 'http://old.com' 'https://new.com'
wp db reset
wp plugin update --all
```

## Good Example

```bash
# 1. Backup
wp db export backup.sql

# 2. Dry run first
wp search-replace 'http://old.com' 'https://new.com' --dry-run --report-changed-only

# 3. Real run with all tables
wp search-replace 'http://old.com' 'https://new.com' --all-tables-with-prefix

# 4. Flush caches after
wp cache flush && wp rewrite flush

# Plugin/theme management
wp plugin list --status=active
wp plugin update --all --dry-run
wp theme activate twentytwentyfive
```

## Why

- **Always backup first** — `wp db export` before any write operation
- **`--dry-run` first** — always preview search-replace changes before applying
- **`--all-tables-with-prefix`** — includes custom tables that may contain URLs
- **`--precise`** — slower but safer for complex serialized data
- **`--skip-columns`** — avoid touching binary/large columns (e.g., `guid`, `post_content`)
- **Flush after URL changes** — `wp cache flush && wp rewrite flush`
- **Never run on production without explicit confirmation**

Reference: [WP-CLI Commands](https://developer.wordpress.org/cli/commands/)
