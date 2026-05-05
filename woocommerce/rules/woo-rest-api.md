---
title: WooCommerce REST API
impact: HIGH
impactDescription: REST API is the integration layer for headless and third-party systems
tags: woocommerce, rest-api, wc-api, crud
---

## WooCommerce REST API

**Impact: HIGH (REST API is the integration layer for headless and external systems)**

WooCommerce uses `wc/v3` namespace. Always provide `permission_callback`. Use WooCommerce's REST controllers as base. Handle batch operations properly.

## Bad Example

```php
add_action( 'rest_api_init', function() {
    register_rest_route( 'my-plugin/v1', '/products', [
        'methods'  => 'GET',
        'callback' => function() {
            global $wpdb;
            return $wpdb->get_results( "SELECT * FROM {$wpdb->posts} WHERE post_type = 'product'" );
        },
    ] );
} );
```

## Good Example

```php
add_action( 'rest_api_init', function() {
    register_rest_route( 'my-plugin/v1', '/custom-products', [
        'methods'             => \WP_REST_Server::READABLE,
        'callback'            => 'my_get_custom_products',
        'permission_callback' => function() {
            return current_user_can( 'read' );
        },
        'args'                => [
            'category' => [
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_text_field',
            ],
            'per_page' => [
                'type'    => 'integer',
                'default' => 10,
            ],
        ],
    ] );
} );

function my_get_custom_products( \WP_REST_Request $request ) {
    $args = [
        'status'   => 'publish',
        'limit'    => $request['per_page'],
        'category' => $request['category'] ?? '',
    ];

    $products = wc_get_products( $args );
    $data     = array_map( function( $product ) {
        return [
            'id'    => $product->get_id(),
            'name'  => $product->get_name(),
            'price' => $product->get_price(),
        ];
    }, $products );

    return rest_ensure_response( $data );
}
```

## Why

- **`wc/v3` namespace** — WooCommerce's official REST API versioning
- **`wc_get_products()`** — uses WC data layer with caching and hooks, not raw SQL
- **`rest_ensure_response()`** — proper REST response wrapping
- **WooCommerce variable hooks** — `woocommerce_rest_prepare_{post_type}`, `woocommerce_rest_{post_type}_query`
- **Batch operations** — WooCommerce supports batch create/update/delete via REST API
- **Authentication** — Application Passwords, OAuth 1.0, or WooCommerce API keys
- **`per_page` capped at 100** — WooCommerce enforces pagination limits

Reference: [WooCommerce REST API](https://woocommerce.github.io/woocommerce-rest-api-docs/)
