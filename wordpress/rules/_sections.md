# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Block Development (block)

**Impact:** CRITICAL
**Description:** Gutenberg block development covering block.json as source of truth, block registration patterns, handling deprecations for "Invalid block" prevention, dynamic rendering, and InnerBlocks composition. Follows WordPress 6.9+ block editor standards.

## 2. Plugin Development (plugin)

**Impact:** CRITICAL
**Description:** Plugin architecture patterns including hook-based loading, lifecycle management (activation/deactivation/uninstall), Settings API for admin UI, security baseline (nonces, capabilities, sanitization, escaping), and data storage strategies (Options API, custom tables, post meta, cron).

## 3. REST API (rest)

**Impact:** HIGH
**Description:** WordPress REST API development covering route registration, JSON Schema validation, authentication mechanisms (cookie+nonce, application passwords), permission callbacks, response shaping with register_rest_field/register_meta, pagination, and discovery.

## 4. Performance (perf)

**Impact:** HIGH
**Description:** WordPress performance optimization including profiling with Query Monitor and WP-CLI, caching strategies (transients, object cache, page cache), database query optimization, autoloaded option management, and N+1 query prevention.

## 5. WP-CLI (wpcli)

**Impact:** MEDIUM
**Description:** WP-CLI command patterns for WordPress operations including core commands, search-replace for URL migration, database operations, automation with wp-cli.yml, CI/CD integration, and multisite management.

## 6. Theme Development (theme)

**Impact:** CRITICAL
**Description:** Modern WordPress theme development covering block themes (theme.json, templates, patterns), theme.json configuration (settings vs styles, presets, per-block styles), HTML templates and template parts, pattern registration, and style variations. Includes classic theme fallback patterns.

## 7. Hooks System (hooks)

**Impact:** CRITICAL
**Description:** WordPress hooks system covering add_action/add_filter API, priority and accepted_args, variable hooks (dynamic hook names with ${variable} or - suffix), remove_action/remove_filter, hook registration best practices, and context-aware hook usage.
