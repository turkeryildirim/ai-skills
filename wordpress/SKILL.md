---
name: wordpress
description: Expert WordPress development covering blocks, plugins, REST API, themes, WP-CLI, and performance. Use when building WordPress plugins, themes, blocks, or working with hooks/actions/filters. Triggers on "WordPress", "WP", "Gutenberg block", "block theme", "wp-", "add_action", "add_filter", "WP-CLI", or "WooCommerce".
model: inherit
---

# WordPress Best Practices

Modern WordPress development patterns covering Block development, Plugin architecture, REST API, Theme development, WP-CLI operations, Performance optimization, and the Hooks system.

## Specialized Agents

Specialized personas for WordPress development. Load these from `agents/` to provide expert context.

| Agent | Role | Focus |
|-------|------|-------|
| **wordpress-pro** | WP Expert | Blocks, plugins, REST API, themes, WP-CLI, performance. |

## When to Use

Reference these guidelines when:
- Creating or modifying WordPress plugins or themes
- Working with Gutenberg blocks (`block.json`, `register_block_type`)
- Using WordPress hooks (actions and filters)
- Building REST API endpoints
- Optimizing WordPress performance
- Using WP-CLI for automation or operations
- Ensuring WordPress security and standards

## Step 1: Detect WordPress Environment

**Always check the project's WordPress version and setup before giving advice.**

```bash
# Check WP version
grep wp_version wp-includes/version.php
# Check active plugins
wp plugin list --status=active
```

Determine the project type (Block theme, Classic theme, Plugin, etc.) to apply the correct rules.

## Core Directives

### MUST DO

- Use `block.json` as the source of truth for block registration
- Follow hook-based loading for plugin architecture
- Implement nonces, capabilities, and sanitization for all user-facing logic
- Use the **Settings API** for plugin options
- Register REST routes with proper `permission_callback`
- Use WP-CLI for bulk operations and automation
- Follow PSR-12 (modified for WP) and WordPress Coding Standards

### MUST NOT DO

- Hardcode URLs or paths (use `plugins_url()`, `get_template_directory_uri()`)
- Run raw SQL queries when `WP_Query` or `wpdb` methods are available
- Load scripts or styles directly (use `wp_enqueue_script` / `wp_enqueue_style`)
- Perform heavy logic inside the `init` hook if it can be deferred
- Expose sensitive data in the REST API without proper permission checks
- Use deprecated hooks or functions

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference | Prefix | Rules |
|--:|----------|:------:|------------|-----------|--------|:-----:|
| 1 | Block Dev | CRITICAL | Building Gutenberg blocks, dynamic rendering | `rules/block-*` | `block-` | 5 |
| 2 | Plugin Dev | CRITICAL | Structuring plugins, lifecycle, settings | `rules/plugin-*` | `plugin-` | 5 |
| 3 | REST API | HIGH | Creating custom endpoints, schema, auth | `rules/rest-*` | `rest-` | 4 |
| 4 | Performance | HIGH | Profiling, caching, DB optimization | `rules/perf-*` | `perf-` | 4 |
| 5 | WP-CLI | MEDIUM | Automating tasks, multisite management | `rules/wpcli-*` | `wpcli-` | 3 |
| 6 | Theme Dev | CRITICAL | Block themes, theme.json, template parts | `rules/theme-*` | `theme-` | 4 |

## Hook Discovery Protocol

**DO NOT** read hook files blindly. Use this protocol:

1.  **Exact Search:** `grep_search(pattern='^### init$', include_pattern='references/hooks/*.md')`
2.  **Keyword Discovery:** `grep_search(pattern='save_post', include_pattern='references/hooks/*.md')`
3.  **Variable Hooks:** Check `references/variable-hooks.md` for dynamic patterns.

## Validation Checklist

- [ ] `block.json` is used for block metadata and registration
- [ ] Nonces and capability checks are present for all administrative actions
- [ ] Data is sanitized on input and escaped on output
- [ ] No N+1 queries in template loops or REST endpoints
- [ ] REST API routes have a `permission_callback` defined
- [ ] No deprecated functions or hooks are used
- [ ] Scripts and styles are properly enqueued via hooks
- [ ] WP-CLI commands are provided for complex operations

## External References

- [WordPress Developer Resources](https://developer.wordpress.org)
- [WordPress Coding Standards](https://make.wordpress.org/core/handbook/best-practices/coding-standards/)
- [Gutenberg Handbook](https://developer.wordpress.org/block-editor/)
- [WP-CLI Command Reference](https://developer.wordpress.org/cli/commands/)
