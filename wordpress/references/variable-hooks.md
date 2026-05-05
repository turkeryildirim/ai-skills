# Variable Hooks Reference

> WordPress hooks with dynamic names. These hooks contain `${variable}` patterns or end with `-`.
> The actual hook name is determined at runtime based on context.

---

## Understanding Variable Hooks

Variable hooks have names that change based on runtime context. They use `${variable}` syntax in their definition. Some also use `-` suffix to append context.

```php
// The hook name is built dynamically:
do_action( "save_post_{$post->post_type}", $post_ID, $post, $update );

// For a "product" post type, this becomes:
do_action( 'save_post_product', $post_ID, $post, $update );

// To hook into it:
add_action( 'save_post_product', 'my_product_handler', 10, 3 );
```

---

## Post Type & Content Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `save_post_{$post->post_type}` | `save_post_product` | Action | Fires after saving a specific post type |
| `{$old_status}_to_{$new_status}` | `draft_to_publish` | Action | Status transition for any post |
| `{$new_status}_{$post->post_type}` | `publish_product` | Action | Post reaches a specific status + type |
| `manage_{$post->post_type}_posts_custom_column` | `manage_product_posts_custom_column` | Action | Custom column content for post type list table |
| `manage_{$post_type}_posts_columns` | `manage_product_posts_columns` | Filter | Modify columns for post type list table |
| `bulk_edit_custom_box` | — | Action | Custom bulk edit fields |
| `quick_edit_custom_box` | — | Action | Custom quick edit fields |
| `wp_insert_post_data` | — | Filter | Filter post data before insert/update |
| `wp_unique_post_slug` | — | Filter | Filter unique post slug |

## Taxonomy Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `create_{$taxonomy}` | `create_category` | Action | Fires after creating a term in taxonomy |
| `edit_{$taxonomy}` | `edit_category` | Action | Fires after editing a term in taxonomy |
| `delete_{$taxonomy}` | `delete_category` | Action | Fires after deleting a term in taxonomy |
| `pre_{$taxonomy}_{$field}` | `pre_category_name` | Filter | Pre-filter a taxonomy field value |
| `{$taxonomy}_{$field}` | `category_name` | Filter | Filter a taxonomy field value |
| `manage_edit-{$taxonomy}_columns` | `manage_edit-category_columns` | Filter | Columns for taxonomy list table |
| `manage_{$taxonomy}_custom_column` | `manage_category_custom_column` | Filter | Custom column content for taxonomy |

## Options Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `pre_option_{$option}` | `pre_option_blogname` | Filter | Short-circuit option retrieval |
| `option_{$option}` | `option_blogname` | Filter | Filter option value after retrieval |
| `default_option_{$option}` | `default_option_blogname` | Filter | Default value when option doesn't exist |
| `pre_update_option_{$option}` | `pre_update_option_blogname` | Filter | Filter before updating specific option |
| `pre_set_theme_mod_{$name}` | `pre_set_theme_mod_custom_logo` | Filter | Filter theme mod before setting |
| `pre_site_option_{$option}` | `pre_site_option_siteurl` | Filter | Short-circuit site option retrieval |
| `site_option_{$option}` | `site_option_siteurl` | Filter | Filter site option value |

## Admin & Screen Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `admin_head-{$hook_suffix}` | `admin_head-post.php` | Action | Admin head for specific page |
| `admin_footer-{$hook_suffix}` | `admin_footer-post.php` | Action | Admin footer for specific page |
| `admin_print_scripts-{$hook_suffix}` | `admin_print_scripts-post.php` | Action | Print scripts for specific admin page |
| `admin_print_styles-{$hook_suffix}` | `admin_print_styles-post.php` | Action | Print styles for specific admin page |
| `load-{$pagenow}` | `load-edit.php` | Action | Fires before loading specific admin page |
| `{$page_hook}` | `settings_page_my-plugin` | Action | Fires when specific admin page loads |
| `add_meta_boxes_{$post_type}` | `add_meta_boxes_product` | Action | Register meta boxes for specific post type |

## REST API Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `rest_prepare_{$this->post_type}` | `rest_prepare_post` | Filter | Filter REST response for post type |
| `rest_insert_{$this->post_type}` | `rest_insert_post` | Action | Fires after inserting via REST |
| `rest_delete_{$this->post_type}` | `rest_delete_post` | Action | Fires after deleting via REST |
| `rest_after_insert_{$this->post_type}` | `rest_after_insert_post` | Action | Fires after REST insert + meta |
| `rest_{$this->post_type}_collection_params` | `rest_post_collection_params` | Filter | Filter collection params for post type |
| `rest_{$this->post_type}_query` | `rest_post_query` | Filter | Filter REST query args for post type |
| `rest_prepare_{$this->taxonomy}` | `rest_prepare_category` | Filter | Filter REST response for taxonomy |

## Meta Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `get_{$meta_type}_metadata` | `get_post_metadata` | Filter | Short-circuit metadata retrieval |
| `get_{$meta_type}_meta` | `get_post_meta` | Filter | Filter meta value after retrieval |
| `update_{$meta_type}_metadata` | `update_post_metadata` | Filter | Filter before updating metadata |
| `update_{$meta_type}_meta` | `update_post_meta` | Action | Fires after updating meta |
| `delete_{$meta_type}_meta` | `delete_post_meta` | Action | Fires before deleting meta |
| `deleted_{$meta_type}_meta` | `deleted_post_meta` | Action | Fires after deleting meta |
| `add_{$meta_type}_metadata` | `add_post_metadata` | Filter | Filter before adding metadata |
| `add_{$meta_type}_meta` | `add_post_meta` | Action | Fires after adding meta |
| `is_{$meta_type}_meta_value_same` | — | Filter | Compare meta values for update check |

## Plugin Lifecycle Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `activate_{$plugin}` | `activate_my-plugin/my-plugin.php` | Action | Fires on plugin activation |
| `deactivate_{$plugin}` | `deactivate_my-plugin/my-plugin.php` | Action | Fires on plugin deactivation |
| `uninstall_{$file}` | `uninstall_my-plugin/my-plugin.php` | Action | Fires on plugin uninstall |

## Comment Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `comment_{$old_status}_to_{$new_status}` | `comment_unapproved_to_approved` | Action | Comment status transition |
| `comment_{$new_status}_{$comment->comment_type}` | `comment_approved_comment` | Action | Comment reaches specific status + type |

## User Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `pre_user_{$field}` | `pre_user_email` | Filter | Filter user field before saving |
| `user_{$field}` | `user_email` | Filter | Filter user field after retrieval |

## AJAX Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `wp_ajax_{$action}` | `wp_ajax_my_action` | Action | Authenticated AJAX handler |
| `wp_ajax_nopriv_{$action}` | `wp_ajax_nopriv_my_action` | Action | Unauthenticated AJAX handler |

## Template Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `{$type}_template` | `single_template` | Filter | Filter template for content type |
| `{$type}_template_hierarchy` | `single_template_hierarchy` | Filter | Filter template hierarchy |
| `get_search_query` | — | Filter | Filter search query |
| `template_include` | — | Filter | Filter main template include path |

Reference: [WordPress Hooks Database](https://adambrown.info/p/wp_hooks) | [Plugin API](https://developer.wordpress.org/plugins/hooks/)
