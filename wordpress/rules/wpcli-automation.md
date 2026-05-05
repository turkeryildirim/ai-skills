---
title: WP-CLI Automation
impact: MEDIUM
impactDescription: Proper automation prevents CI/CD failures and data loss
tags: wpcli, automation, ci-cd, wp-cli-yml
---

## WP-CLI Automation

**Impact: MEDIUM (automation scripts can cause widespread damage if not written carefully)**

Use `wp-cli.yml` for defaults. Shell scripts must use `set -euo pipefail`. Make destructive operations require explicit flags. CI jobs should be read-only by default.

## Bad Example

```bash
#!/bin/bash
wp plugin update --all
wp db optimize
wp cache flush
```

## Good Example

```yaml
# wp-cli.yml
path: /var/www/html
url: https://example.com
```

```bash
#!/bin/bash
set -euo pipefail

ENV="${1:-staging}"
APPLY="${2:-}"

echo ">>> Environment: $ENV"
echo ">>> wp plugin list"
wp plugin list --status=active

if [ "$APPLY" = "--apply" ]; then
    echo ">>> Applying updates..."
    wp plugin update --all
else
    echo ">>> Dry run. Pass --apply to execute."
    wp plugin update --all --dry-run
fi
```

## Why

- **`wp-cli.yml`** — stores path, URL, PHP settings; prevents `--path` flag on every command
- **`set -euo pipefail`** — script exits on any error, undefined variable, or pipe failure
- **Print commands before running** — aids debugging in CI logs
- **Explicit `--apply` flag** — destructive operations require opt-in, not opt-out
- **CI jobs read-only by default** — `wp core version`, `wp plugin list`, `wp theme list`
- **Log everything** — date/time, environment, exact commands, exit codes

Reference: [WP-CLI Config](https://make.wordpress.org/cli/handbook/references/config/)
