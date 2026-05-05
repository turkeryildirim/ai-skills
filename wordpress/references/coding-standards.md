# WordPress Coding Standards

> Key rules from WordPress coding standards. Full reference: https://developer.wordpress.org/coding-standards/wordpress-coding-standards/

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | lowercase with underscores | `my_plugin_function()` |
| Classes | StudlyCaps | `My_Plugin_Loader` |
| Methods | camelCase is discouraged; use underscores | `get_post_data()` |
| Variables | lowercase with underscores | `$post_type` |
| Constants | UPPERCASE with underscores | `MY_PLUGIN_VERSION` |
| Hooks | lowercase with underscores | `my_plugin_after_save` |
| Database tables | lowercase with underscores | `wp_my_plugin_data` |
| File names | lowercase with hyphens | `my-plugin-file.php` |
| CSS classes | lowercase with hyphens (BEM encouraged) | `.my-plugin__header` |

## PHP Standards

### Single and Double Quotes

```php
// Use single quotes unless evaluating variables
$name = 'WordPress';
$greeting = "Hello, $name!";
```

### Indentation

- Always use **tabs** for indentation (not spaces)
- Use spaces for alignment within a line

### Brace Style

```php
// Opening brace on same line for control structures
if ( condition ) {
    do_something();
}

// Opening brace on new line for functions/classes
function my_function() {
    // code
}

class My_Class {
    // code
}
```

### Spacing

```php
// Spaces inside parentheses for control structures
if ( $condition && $other ) {
    $array[ $index ];
    $function( $arg1, $arg2 );
}

// No spaces inside function call parentheses (for assignments)
$result = my_function( $arg1, $arg2 );

// Spaces around comparison operators
if ( $a === $b ) {}
if ( $a !== $b ) {}

// Spaces around assignment
$var = 'value';
```

### Yoda Conditions

```php
// Correct — variable on right (Yoda style)
if ( true === $result ) {}

// Wrong
if ( $result === true ) {}
```

### Strict Comparisons

```php
// Always use === and !==
if ( 0 === $count ) {}

// Never use == and != (loose comparison)
if ( 0 == $count ) {} // WRONG
```

### Escape Everything

```php
// HTML context
echo esc_html( $text );
echo '<a href="' . esc_url( $url ) . '">' . esc_html( $label ) . '</a>';
echo '<input value="' . esc_attr( $value ) . '">';

// Allow safe HTML
echo wp_kses_post( $rich_text );

// JavaScript context
echo '<script>var name = ' . wp_json_encode( $name ) . ';</script>';
```

### Database Queries

```php
// Always use $wpdb->prepare()
$results = $wpdb->get_results(
    $wpdb->prepare( "SELECT * FROM {$wpdb->prefix}my_table WHERE id = %d", $id )
);

// Or use helper methods
$wpdb->insert( $table, [ 'field' => $value ], [ '%s' ] );
$wpdb->delete( $table, [ 'id' => $id ], [ '%d' ] );
```

Reference: [WordPress Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/) | [PHP Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/)
