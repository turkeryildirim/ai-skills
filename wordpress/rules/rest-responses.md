---
title: REST Responses and Fields
impact: HIGH
impactDescription: Proper response shaping ensures API clients receive correct data
tags: rest, responses, fields, meta, links
---

## REST Responses and Fields

**Impact: HIGH (correct response shaping ensures clients get expected data)**

Never remove core fields from default endpoints — add fields instead. Use `register_rest_field` for computed fields, `register_meta` with `show_in_rest` for meta. Use `_fields` param for lean responses.

## Bad Example

```php
// Removing core fields — breaks wp-admin and other clients
add_filter( 'rest_prepare_post', function( $response ) {
    $data = $response->get_data();
    unset( $data['content'] );
    $response->set_data( $data );
    return $response;
} );
```

## Good Example

```php
// Add computed custom field
register_rest_field( 'post', 'reading_time', [
    'get_callback' => function( $post ) {
        $content = get_the_content( null, false, $post['id'] );
        return max( 1, ceil( str_word_count( strip_tags( $content ) ) / 200 ) );
    },
    'schema' => [ 'type' => 'integer' ],
] );

// Expose meta in REST
register_post_meta( 'post', 'my_meta_key', [
    'show_in_rest' => true,
    'single'       => true,
    'type'         => 'string',
] );

// Add links
add_filter( 'rest_prepare_post', function( $response, $post ) {
    $response->add_link( 'author', rest_url( "wp/v2/users/{$post->post_author}" ), [
        'embeddable' => true,
    ] );
    return $response;
}, 10, 2 );
```

## Why

- **Never remove core fields** — wp-admin and other clients depend on them
- **`register_rest_field()`** — add computed fields without modifying core response
- **`register_meta()` with `show_in_rest`** — exposes meta automatically with proper schema
- **`add_link()`** — enables `_embed` for related resources, reducing API calls
- **`_fields` query param** — clients can limit response size (`?_fields=id,title`)
- **`?context=edit`** — returns `content.raw` for unfiltered content (requires auth)

Reference: [REST Responses](https://developer.wordpress.org/rest-api/extending-the-rest-api/modifying-responses/)
