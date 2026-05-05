---
title: WP-CLI Multisite Operations
impact: MEDIUM
impactDescription: Multisite commands affect wrong sites without proper targeting
tags: wpcli, multisite, network, site
---

## WP-CLI Multisite Operations

**Impact: MEDIUM (wrong site targeting is the most common multisite error)**

Always include `--url` when operating on a specific site. Use `--network` for network-wide operations. List sites first, then iterate per-site.

## Bad Example

```bash
wp option update blogname 'New Name'
wp plugin activate my-plugin
wp search-replace 'old.com' 'new.com'
```

## Good Example

```bash
# List all sites
wp site list --fields=blog_id,url

# Target specific site
wp option get siteurl --url=sub.example.com
wp plugin activate my-plugin --url=sub.example.com

# Network-wide activation
wp plugin activate my-plugin --network

# Per-site search-replace
for url in $( wp site list --field=url ); do
    echo ">>> Processing $url"
    wp search-replace 'old.com' 'new.com' --url="$url" --dry-run
done
```

## Why

- **`--url=<site-url>`** — targets a specific blog context; without it, commands run on the main site
- **`--network`** — applies network-wide where supported (plugin activation, etc.)
- **List sites first** — `wp site list` to understand what you're affecting
- **Iterate safely** — per-site operations with `--url` prevent cross-site contamination
- **Always dry-run first** — especially important in multisite where blast radius is larger
- **`wp site create/delete/archive/spam`** — site lifecycle management commands

Reference: [WP-CLI Multisite](https://developer.wordpress.org/cli/commands/site/)
