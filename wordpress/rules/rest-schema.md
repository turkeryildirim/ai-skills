---
title: REST Schema and Validation
impact: HIGH
impactDescription: Schema enables OPTIONS discovery, auto-validation, and client introspection
tags: rest, schema, validation, json-schema
---

## REST Schema and Validation

**Impact: HIGH (schema enables auto-validation, OPTIONS discovery, and OpenAPI generation)**

Use JSON Schema for endpoint arguments. Schema enables automatic validation and `OPTIONS` discovery. Cache generated schema on controller instances.

## Bad Example

```php
register_rest_route( 'my-plugin/v1', '/items', [
    'methods'  => 'POST',
    'callback' => 'my_create_item',
    'args'     => [
        'title' => [ 'required' => true ],
        'status' => [ 'default' => 'draft' ],
    ],
] );
```

## Good Example

```php
register_rest_route( 'my-plugin/v1', '/items', [
    'methods'  => WP_REST_Server::CREATABLE,
    'callback' => 'my_create_item',
    'args'     => [
        'title'  => [
            'type'              => 'string',
            'required'          => true,
            'sanitize_callback' => 'sanitize_text_field',
            'validate_callback' => 'rest_validate_request_arg',
        ],
        'status' => [
            'type'    => 'string',
            'default' => 'draft',
            'enum'    => [ 'draft', 'publish', 'pending' ],
        ],
    ],
] );
```

## Why

- **JSON Schema (draft 4 subset)** — WordPress validates against schema automatically
- **`validate_callback` + `sanitize_callback`** — validate first, then sanitize. Use `rest_validate_request_arg` to keep schema validation when providing custom sanitize.
- **`enum` for allowed values** — automatic validation without custom code
- **Common formats:** `date-time`, `uri`, `email`, `ip`, `uuid`, `hex-color`
- **For `array`/`object` types** — must define `items` or `properties` respectively
- **`get_endpoint_args_for_item_schema()`** — auto-wire args from controller schema

Reference: [REST Schema](https://developer.wordpress.org/rest-api/extending-the-rest-api/schema/)
