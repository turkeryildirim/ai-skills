# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Backend Development (woo-backend)

**Impact:** CRITICAL
**Description:** WooCommerce backend PHP development conventions including class structure, PSR-4 autoloading, dependency injection, naming conventions, docblocks, and coding style. Derived from WooCommerce's own .ai/skills/woocommerce-backend-dev.

## 2. Hook Conventions (woo-hooks)

**Impact:** CRITICAL
**Description:** WooCommerce-specific hook callback conventions including naming (handle_{hook_name}), registration patterns, @internal annotation, and priority management.

## 3. Data Integrity (woo-data)

**Impact:** CRITICAL
**Description:** CRUD safety patterns for WooCommerce entities. Always verify entity state and ownership before delete/update. Handle race conditions in concurrent order processing.

## 4. Product Development (woo-product)

**Impact:** CRITICAL
**Description:** WooCommerce product management covering custom product types, pricing hooks, inventory management, variations, attributes, and product queries.

## 5. Order Processing (woo-order)

**Impact:** CRITICAL
**Description:** WooCommerce order lifecycle covering status transitions, line items, refunds, fulfillment hooks, payment completion, and order metadata.

## 6. Checkout (woo-checkout)

**Impact:** HIGH
**Description:** WooCommerce checkout customization covering field modification, validation hooks, order creation process, and checkout flow control.

## 7. Email Customization (woo-email)

**Impact:** HIGH
**Description:** WooCommerce email system covering per-email-type hooks (recipient, subject, heading, content), template overrides, and email triggering.

## 8. Shipping (woo-shipping)

**Impact:** HIGH
**Description:** WooCommerce shipping covering custom shipping methods, zone management, rate calculation, package handling, and shipping method settings.

## 9. REST API (woo-rest)

**Impact:** HIGH
**Description:** WooCommerce REST API covering wc/v3 endpoints, custom routes, schema definition, batch operations, and authentication.

## 10. Admin (woo-admin)

**Impact:** MEDIUM
**Description:** WooCommerce admin customization covering list table columns, settings pages, meta boxes, order preview, and admin order actions.

## 11. Payment Gateways (woo-payment)

**Impact:** CRITICAL
**Description:** WooCommerce payment gateway development covering gateway class extension, process_payment, webhook handling, refund support, and settings.

## 12. Performance (woo-performance)

**Impact:** HIGH
**Description:** WooCommerce performance optimization covering _prime_post_caches patterns, wp_prime_option_caches, bulk operation optimization, and query reduction. Derived from WooCommerce's own .ai/skills/woocommerce-performance.
