---
title: REST Routes and Endpoints
impact: HIGH
impactDescription: Correct route registration prevents 404s and auth errors
tags: rest, routes, endpoints, api
---

## REST Routes and Endpoints

**Impact: HIGH (incorrect registration causes 404s, auth failures, and _doing_it_wrong notices)**

Register routes on `rest_api_init` with unique namespaces. Always provide `permission_callback`. Never use `wp/*` namespace for custom routes. Use `WP_REST_Server` constants for HTTP methods.

## Bad Example

```php
add_action( 'rest_api_init', function() {
    register_rest_route( 'wp/v2', '/my-endpoint', [
        'methods'  => 'GET',
        'callback' => 'my_handler',
    ] );
} );

function my_handler( $request ) {
    $data = $wpdb->get_results( "SELECT * FROM my_table" );
    wp_send_json( $data );
}
```

## Good Example

```php
add_action( 'rest_api_init', function() {
    register_rest_route( 'my-plugin/v1', '/items', [
        'methods'             => WP_REST_Server::READABLE,
        'callback'            => [ $this, 'get_items' ],
        'permission_callback' => function() {
            return current_user_can( 'read' );
        },
        'args'                => [
            'per_page' => [
                'type'              => 'integer',
                'default'           => 10,
                'sanitize_callback' => 'absint',
                'validate_callback' => function( $val ) {
                    return is_numeric( $val ) && $val <= 100;
                },
            ],
        ],
    ] );
} );
```

## Why

- **Unique namespace** (`my-plugin/v1`) — never use `wp/*` (reserved for core)
- **`permission_callback` required** — omitting triggers `_doing_it_wrong` notice. Use `__return_true` only for truly public endpoints.
- **`WP_REST_Server::READABLE/CREATABLE`** — use constants, not raw strings
- **Never use `wp_send_json()` in REST callbacks** — return `WP_REST_Response` or `rest_ensure_response()`
- **`args` with validation** — automatic validation via schema, custom via `validate_callback`
- **Error responses via `WP_Error`** — with explicit `status` parameter

Reference: [REST API Routes](https://developer.wordpress.org/rest-api/extending-the-rest-api/adding-custom-endpoints/)
