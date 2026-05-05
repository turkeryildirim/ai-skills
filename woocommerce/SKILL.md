---
name: woocommerce
description: Expert WooCommerce development covering products, orders, cart, checkout, payments, shipping, emails, REST API, and admin. Extends WordPress agent with WooCommerce-specific hooks, data models, and patterns. Triggers on "WooCommerce", "WC_", "woocommerce_", "product", "order", "cart", "checkout", "payment gateway", "shipping method".
model: inherit
---

# WooCommerce Development

WooCommerce-specific development patterns extending WordPress best practices. Covers backend conventions, products, orders, checkout, and performance.

**This skill extends the `wordpress` skill.** All WordPress standards and security patterns apply.

## Specialized Agents

Specialized personas for WooCommerce development. Load these from `agents/` to provide expert context.

| Agent | Role | Focus |
|-------|------|-------|
| **woocommerce-pro** | WC Expert | Products, orders, cart/checkout, payments, shipping, REST API. |

## When to Use

Reference these guidelines when:
- Building WooCommerce extensions, plugins, or themes
- Customizing products, orders, cart, or checkout flows
- Creating custom payment gateways or shipping methods
- Extending the WooCommerce REST API
- Optimizing store performance and database queries
- Handling order status transitions and fulfillment logic

## Step 1: Detect WooCommerce Environment

**Always check WooCommerce version and active features before giving advice.**

```bash
# Check WC version
wp eval "echo WC_VERSION;"
# Check for specific features (e.g. HPOS)
wp option get woocommerce_custom_orders_table_enabled
```

## Core Directives

### MUST DO

- Use **CRUD classes** (`WC_Product`, `WC_Order`, etc.) instead of direct metadata access
- Follow WooCommerce naming conventions and hook priority standards
- Ensure **Data Integrity** by verifying entities before modification
- Implement proper logging via `WC_Logger`
- Support **HPOS (High-Performance Order Storage)** in all new code
- Use `WC_Query` for custom product/order lookups
- Redact sensitive data from checkout and email templates

### MUST NOT DO

- Access WooCommerce metadata directly via `get_post_meta` (use getters/setters)
- Modify core WooCommerce tables directly
- Hardcode currency symbols or price formats
- Perform expensive calculations inside the cart or checkout loop without caching
- Use deprecated hooks (e.g., `woocommerce_add_to_cart_redirect`)
- Overwrite template files if a hook-based solution is possible

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference | Prefix |
|--:|----------|:------:|------------|-----------|--------|
| 1 | Backend Dev | CRITICAL | Class structure, DI, naming conventions | `rules/woo-backend-*` | `woo-backend-` |
| 2 | Products | CRITICAL | Product types, inventory, pricing | `rules/woo-product-*` | `woo-product-` |
| 3 | Orders | CRITICAL | Statuses, fulfillment, refunds | `rules/woo-order-*` | `woo-order-` |
| 4 | Checkout | HIGH | Fields, validation, order creation | `rules/woo-checkout-*` | `woo-checkout-` |
| 5 | Performance | HIGH | Cache priming, query optimization | `rules/woo-performance-*` | `woo-performance-` |
| 6 | Payments | CRITICAL | Gateway development, webhooks | `rules/woo-payment-*` | `woo-payment-` |

## Hook Discovery Protocol

**DO NOT** read hook files blindly. Use this protocol:

1.  **Exact Search:** `grep_search(pattern='^### woocommerce_add_to_cart$', include_pattern='references/hooks/*.md')`
2.  **Keyword Discovery:** `grep_search(pattern='order_status', include_pattern='references/hooks/*.md')`
3.  **Variable Hooks:** Check `references/variable-hooks.md` for patterns like `woocommerce_order_status_{$status}`.

## Validation Checklist

- [ ] All data access uses WooCommerce CRUD methods (getters/setters)
- [ ] HPOS compatibility is verified
- [ ] Custom fields are properly sanitized and escaped
- [ ] No N+1 queries in product loops or order lists
- [ ] Payment and shipping methods follow the official base classes
- [ ] Email templates are customized via hooks, not just overrides
- [ ] Currency and price formatting uses native WC functions
- [ ] Order status transitions are handled via the appropriate hooks

## External References

- [WooCommerce Developer Documentation](https://developer.woocommerce.com)
- [WooCommerce Hook Reference](https://hooks.woocommerce.com)
- [WooCommerce REST API Documentation](https://woocommerce.github.io/woocommerce-rest-api-docs/)
- [HPOS Development Guide](https://github.com/woocommerce/woocommerce/wiki/High-Performance-Order-Storage-Upgrade-Guide)
