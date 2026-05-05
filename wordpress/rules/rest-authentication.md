---
title: REST Authentication
impact: CRITICAL
impactDescription: Incorrect auth causes 401/403 errors or security vulnerabilities
tags: rest, authentication, nonce, permissions
---

## REST Authentication

**Impact: CRITICAL (auth failures are the most common REST API issue)**

Cookie+nonce for same-site admin, Application Passwords for external access. `permission_callback` is for authorization, not authentication. Nonce is required even with valid cookies.

## Bad Example

```php
register_rest_route( 'my-plugin/v1', '/settings', [
    'methods'             => WP_REST_Server::EDITABLE,
    'callback'            => 'my_update_settings',
    'permission_callback' => '__return_true',
] );
```

## Good Example

```php
// Cookie auth — include nonce in JS
wp_localize_script( 'my-script', 'myApi', [
    'root'  => esc_url_raw( rest_url( 'my-plugin/v1/' ) ),
    'nonce' => wp_create_nonce( 'wp_rest' ),
] );

// JS sends: headers: { 'X-WP-Nonce': myApi.nonce }

// Route with proper authorization
register_rest_route( 'my-plugin/v1', '/settings', [
    'methods'             => WP_REST_Server::EDITABLE,
    'callback'            => 'my_update_settings',
    'permission_callback' => function() {
        return current_user_can( 'manage_options' );
    },
] );
```

## Why

- **Cookie + nonce (`wp_rest`)** — required for same-site admin requests. Missing nonce = treated as unauthenticated.
- **Application Passwords** — WordPress 5.6+ for external/programmatic access. Requires HTTPS.
- **`permission_callback` is authorization** — check capabilities, not just "is logged in"
- **`__return_true` only for public endpoints** — all write endpoints need real permission checks
- **`X-WP-Nonce` header** or `_wpnonce` query param — both work for cookie auth

Reference: [REST Authentication](https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/)
