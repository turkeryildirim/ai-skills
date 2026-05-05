# WordPress Actions: Content

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### delete_post
**Params:** int $post_id, WP_Post $post
**Since:** 1.2.1 | **Tags:** #post
Fires immediately before a post is deleted from the database.

### edit_comment
**Params:** int $comment_id
**Since:** 1.2.1 | **Tags:** #comment
Fires immediately after a comment is updated in the database.

### edit_post
**Params:** int $post_id, WP_Post $post
**Since:** 1.2.1 | **Tags:** #post
Fires when an existing post is updated.

### publish_phone
**Since:** 1.2.1 | **Tags:** #general
Action hook fired during WordPress processing.

### parse_query
**Params:** WP_Query $query
**Since:** 1.5.2 | **Tags:** #general
Fires after the WP_Query object is parsed. Allows modification of query variables before posts are fetched.

### save_post
**Params:** int $post_id, WP_Post $post, bool $update
**Since:** 1.5.2 | **Tags:** #post
Fires once a post has been saved. Receives the post ID, post object, and update flag.

### add_link
**Params:** int $link_id
**Since:** 2.0 | **Tags:** #general
Fires after a link is added.

### delete_link
**Since:** 2.0 | **Tags:** #general
Fires when the related item is deleted.

### edit_link
**Since:** 2.0 | **Tags:** #general
Fires when the related item is edited or updated.

### pre_ping
**Since:** 2.0 | **Tags:** #general
Fires before the related action is processed.

### wp_insert_post
**Params:** int $post_id, WP_Post $post, bool $update
**Since:** 2.0 | **Tags:** #post
Fires once a post has been inserted or updated via wp_insert_post().

### xmlrpc_publish_post
**Since:** 2.1 | **Tags:** #post #xmlrpc
Action hook fired during WordPress processing.

### deleted_link
**Since:** 2.2 | **Tags:** #general
Fires when the related item is deleted.

### deleted_post
**Since:** 2.2 | **Tags:** #post
Fires when the related item is deleted.

### created_term
**Since:** 2.3 | **Tags:** #taxonomy
Fires when a new item is created.

### created_{$taxonomy}
**Since:** 2.3 | **Tags:** #variable #taxonomy
Fires when a new item is created.

### create_term
**Since:** 2.3 | **Tags:** #taxonomy
Fires when a new item is created.

### create_{$taxonomy}
**Since:** 2.3 | **Tags:** #variable #taxonomy
Fires when a new item is created.

### delete_{$taxonomy}
**Since:** 2.3 | **Tags:** #variable #taxonomy
Fires when the related item is deleted.

### edited_term
**Since:** 2.3 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### edited_{$taxonomy}
**Since:** 2.3 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### edit_term
**Since:** 2.3 | **Tags:** #taxonomy
Fires when the related item is edited or updated.

### edit_{$taxonomy}
**Since:** 2.3 | **Tags:** #variable #taxonomy
Fires when the related item is edited or updated.

### posts_selection
**Since:** 2.3 | **Tags:** #post
Action hook fired during WordPress processing.

### transition_post_status
**Params:** string $new_status, string $old_status, WP_Post $post
**Since:** 2.3 | **Tags:** #post
Fires when a post transitions between statuses. Receives new status, old status, and post object.

### {$new_status}_{$post->post_type}
**Since:** 2.3 | **Tags:** #variable #post
Action hook fired during WordPress processing.

### {$old_status}_to_{$new_status}
**Since:** 2.3 | **Tags:** #variable
Action hook fired during WordPress processing.

### clean_object_term_cache
**Since:** 2.5 | **Tags:** #taxonomy #options
Fires when the related cache is cleaned.

### clean_page_cache
**Since:** 2.5 | **Tags:** #post #options
Fires when the related cache is cleaned.

### clean_post_cache
**Since:** 2.5 | **Tags:** #post #options
Fires when the related cache is cleaned.

### clean_term_cache
**Since:** 2.5 | **Tags:** #taxonomy #options
Fires when the related cache is cleaned.

### delete_term
**Since:** 2.5 | **Tags:** #taxonomy
Fires when the related item is deleted.

### pre_post_update
**Params:** int $post_id, array $data
**Since:** 2.5 | **Tags:** #post #update
Fires before the related action is processed.

### wp_delete_post_revision
**Since:** 2.6 | **Tags:** #post
Action hook fired during WordPress processing.

### wp_restore_post_revision
**Since:** 2.6 | **Tags:** #post #rest
Action hook fired during WordPress processing.

### _wp_put_post_revision
**Since:** 2.6 | **Tags:** #post
Action hook fired during WordPress processing.

### set_object_terms
**Since:** 2.8 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### added_term_relationship
**Since:** 2.9 | **Tags:** #taxonomy
Fires when a new item is added.

### add_term_relationship
**Since:** 2.9 | **Tags:** #taxonomy
Fires when a new item is added.

### deleted_term_relationships
**Since:** 2.9 | **Tags:** #taxonomy
Fires when the related item is deleted.

### deleted_term_taxonomy
**Since:** 2.9 | **Tags:** #taxonomy
Fires when the related item is deleted.

### delete_postmeta
**Since:** 2.9 | **Tags:** #post
Fires when the related item is deleted.

### delete_term_relationships
**Since:** 2.9 | **Tags:** #taxonomy
Fires when the related item is deleted.

### delete_term_taxonomy
**Since:** 2.9 | **Tags:** #taxonomy
Fires when the related item is deleted.

### edited_terms
**Since:** 2.9 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### edited_term_taxonomies
**Since:** 2.9 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### edited_term_taxonomy
**Since:** 2.9 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### edit_terms
**Since:** 2.9 | **Tags:** #taxonomy
Fires when the related item is edited or updated.

### edit_term_taxonomies
**Since:** 2.9 | **Tags:** #taxonomy
Fires when the related item is edited or updated.

### edit_term_taxonomy
**Since:** 2.9 | **Tags:** #taxonomy
Fires when the related item is edited or updated.

### trashed_post
**Since:** 2.9 | **Tags:** #post
Fires when the related item is trashed.

### trashed_post_comments
**Since:** 2.9 | **Tags:** #post #comment
Fires when the related item is trashed.

### trash_post_comments
**Since:** 2.9 | **Tags:** #post #comment
Fires when the related item is trashed.

### untrashed_post
**Since:** 2.9 | **Tags:** #post
Fires when the related item is restored from trash.

### untrashed_post_comments
**Since:** 2.9 | **Tags:** #post #comment
Fires when the related item is restored from trash.

### untrash_post
**Params:** int $post_id
**Since:** 2.9 | **Tags:** #post
Fires when a post is restored from the trash.

### untrash_post_comments
**Since:** 2.9 | **Tags:** #post #comment
Fires when the related item is restored from trash.

### add_tag_form_fields
**Since:** 3.0 | **Tags:** #taxonomy
Fires when a new item is added.

### after-{$taxonomy}-table
**Since:** 3.0 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### clean_attachment_cache
**Since:** 3.0 | **Tags:** #media #options
Fires when the related cache is cleaned.

### post_updated
**Params:** int $post_id, WP_Post $post_after, WP_Post $post_before
**Since:** 3.0 | **Tags:** #post #update
Fires after an existing post has been updated in the database.

### {$taxonomy}_add_form
**Since:** 3.0 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### {$taxonomy}_add_form_fields
**Since:** 3.0 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### {$taxonomy}_edit_form
**Since:** 3.0 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### {$taxonomy}_edit_form_fields
**Since:** 3.0 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### {$taxonomy}_pre_add_form
**Since:** 3.0 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### {$taxonomy}_pre_edit_form
**Since:** 3.0 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### after_delete_post
**Since:** 3.2 | **Tags:** #post
Action hook fired during WordPress processing.

### before_delete_post
**Since:** 3.2 | **Tags:** #post
Action hook fired during WordPress processing.

### registered_post_type
**Params:** string $post_type, WP_Post_Type $post_type_obj
**Since:** 3.3 | **Tags:** #post
Fires after a post type is registered. Allows modification of post type arguments.

### registered_taxonomy
**Params:** string $taxonomy, array|string $object_type, WP_Taxonomy $taxonomy_obj
**Since:** 3.3 | **Tags:** #taxonomy
Fires after a taxonomy is registered. Allows modification of taxonomy arguments.

### wp_trash_post
**Since:** 3.3 | **Tags:** #post
Action hook fired during WordPress processing.

### parse_tax_query
**Params:** WP_Query $query
**Since:** 3.7 | **Tags:** #general
Action hook fired during WordPress processing.

### save_post_{$post->post_type}
**Since:** 3.7 | **Tags:** #variable #post
Fires when an item is saved.

### {$taxonomy}_term_edit_form_tag
**Since:** 3.7 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### {$taxonomy}_term_new_form_tag
**Since:** 3.7 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### pre_delete_term
**Since:** 4.1 | **Tags:** #taxonomy
Fires before the related action is processed.

### wp_creating_autosave
**Since:** 4.1 | **Tags:** #general
Action hook fired during WordPress processing.

### split_shared_term
**Since:** 4.2 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### unregistered_post_type
**Since:** 4.5 | **Tags:** #post
Fires when an item is unregistered.

### unregistered_taxonomy
**Since:** 4.5 | **Tags:** #taxonomy
Fires when an item is unregistered.

### {$taxonomy}_term_edit_form_top
**Since:** 4.5 | **Tags:** #variable #taxonomy
Action hook fired during WordPress processing.

### parse_term_query
**Params:** WP_Term_Query $query
**Since:** 4.6 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### post_stuck
**Since:** 4.6 | **Tags:** #post
Action hook fired during WordPress processing.

### post_unstuck
**Since:** 4.6 | **Tags:** #post
Action hook fired during WordPress processing.

### clean_taxonomy_cache
**Since:** 4.9 | **Tags:** #taxonomy #options
Fires when the related cache is cleaned.

### edit_post_{$post->post_type}
**Since:** 5.1 | **Tags:** #variable #post
Fires when the related item is edited or updated.

### registered_taxonomy_for_object_type
**Since:** 5.1 | **Tags:** #taxonomy
Fires when an item is registered.

### unregistered_taxonomy_for_object_type
**Since:** 5.1 | **Tags:** #taxonomy
Fires when an item is unregistered.

### saved_term
**Since:** 5.5 | **Tags:** #taxonomy
Fires when an item is saved.

### saved_{$taxonomy}
**Since:** 5.5 | **Tags:** #variable #taxonomy
Fires when an item is saved.

### wp_after_insert_post
**Params:** int $post_id, WP_Post $post, bool $update, WP_Post|null $post_before
**Since:** 5.6 | **Tags:** #post
Fires after a post and its meta data have been fully inserted/updated, including term relationships.

### registered_post_type_{$post_type}
**Since:** 6.0 | **Tags:** #variable #post
Fires when an item is registered.

### registered_taxonomy_{$taxonomy}
**Since:** 6.0 | **Tags:** #variable #taxonomy
Fires when an item is registered.

### deleted_post_{$post->post_type}
**Since:** 6.6 | **Tags:** #variable #post
Fires when the related item is deleted.

### delete_post_{$post->post_type}
**Since:** 6.6 | **Tags:** #variable #post
Fires when the related item is deleted.

### pre_post_insert
**Since:** 6.9 | **Tags:** #post
Fires before the related action is processed.

### update_term_count
**Since:** 6.9 | **Tags:** #taxonomy #update
Fires when an item is updated.

