# WordPress Actions: Core

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### sanitize_title
**Params:** string $title, string $raw_title, string $context
**Since:** 1.2.1 | **Tags:** #general
Fires after a title is sanitized for use in URLs and slugs.

### shutdown
**Since:** 1.2.1 | **Tags:** #general
Fires just before PHP shuts down execution.

### generate_rewrite_rules
**Params:** WP_Rewrite $wp_rewrite
**Since:** 1.5.2 | **Tags:** #rewrite
Fires after rewrite rules are generated.

### init
**Since:** 1.5.2 | **Tags:** #general
Fires after WordPress has finished loading but before any headers are sent. Most plugins register post types, taxonomies, and handle admin init here.

### atom_entry
**Since:** 2.0 | **Tags:** #feed
Fires at the end of each Atom feed entry.

### atom_head
**Since:** 2.0 | **Tags:** #feed
Fires at the end of the Atom feed header.

### atom_ns
**Since:** 2.0 | **Tags:** #feed
Fires inside the Atom feed root element.

### pre_get_posts
**Since:** 2.0 | **Tags:** #post
Fires before the related action is processed.

### rdf_header
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### rdf_item
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### rdf_ns
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### rss2_head
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### rss2_item
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### rss2_ns
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### rss_head
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### rss_item
**Since:** 2.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### sanitize_comment_cookies
**Since:** 2.0.11 | **Tags:** #comment
Fires during comment-related processing.

### do_robots
**Since:** 2.1 | **Tags:** #general
Action hook fired during WordPress processing.

### do_robotstxt
**Since:** 2.1 | **Tags:** #general
Action hook fired during WordPress processing.

### parse_request
**Params:** WP $wp
**Since:** 2.1 | **Tags:** #general
Fires after the request has been parsed and before the main query is executed.

### send_headers
**Params:** WP $wp
**Since:** 2.1 | **Tags:** #general
Fires when sending HTTP headers. Used to add custom headers to responses.

### wp
**Params:** WP $wp
**Since:** 2.1 | **Tags:** #general
Fires once the WordPress query object has been parsed and the current request context is set.

### {$hook}
**Since:** 2.1 | **Tags:** #variable
Action hook fired during WordPress processing.

### phpmailer_init
**Params:** PHPMailer $phpmailer
**Since:** 2.2 | **Tags:** #mail
Fires after PHPMailer is initialized, before an email is sent.

### deprecated_file_included
**Since:** 2.5 | **Tags:** #deprecated
Fires when a deprecated function, hook, or argument is used.

### deprecated_function_run
**Since:** 2.5 | **Tags:** #deprecated
Fires when a deprecated function, hook, or argument is used.

### xmlrpc_call
**Params:** string $method
**Since:** 2.5 | **Tags:** #xmlrpc
Fires after the XML-RPC user has been authenticated but before the response.

### setup_theme
**Since:** 2.6 | **Tags:** #theme
Fires before the theme is loaded and setup. Used to register theme features early.

### after_db_upgrade
**Since:** 2.8 | **Tags:** #update #database
Action hook fired during WordPress processing.

### atom_comments_ns
**Since:** 2.8 | **Tags:** #comment #feed
Fires during comment-related processing.

### http_api_curl
**Since:** 2.8 | **Tags:** #general
Action hook fired during WordPress processing.

### http_api_debug
**Since:** 2.8 | **Tags:** #general
Action hook fired during WordPress processing.

### muplugins_loaded
**Since:** 2.8 | **Tags:** #plugin
Fires after all must-use plugins have been loaded, before regular plugins.

### permalink_structure_changed
**Since:** 2.8 | **Tags:** #rewrite
Fires after the permalink structure is updated.

### rss2_comments_ns
**Since:** 2.8 | **Tags:** #comment #feed
Fires during comment-related processing.

### added_option
**Since:** 2.9 | **Tags:** #options
Fires when a new item is added.

### added_usermeta
**Since:** 2.9 | **Tags:** #user
Fires when a new item is added.

### added_{$meta_type}_meta
**Since:** 2.9 | **Tags:** #variable
Fires when a new item is added.

### add_option
**Since:** 2.9 | **Tags:** #options
Fires when a new item is added.

### deleted_option
**Since:** 2.9 | **Tags:** #options
Fires when the related item is deleted.

### deleted_postmeta
**Since:** 2.9 | **Tags:** #post
Fires when the related item is deleted.

### deleted_{$meta_type}_meta
**Since:** 2.9 | **Tags:** #variable
Fires when the related item is deleted.

### delete_option
**Since:** 2.9 | **Tags:** #options
Fires when the related item is deleted.

### updated_option
**Since:** 2.9 | **Tags:** #options #update
Fires when an item is updated.

### updated_postmeta
**Since:** 2.9 | **Tags:** #post #update
Fires when an item is updated.

### updated_usermeta
**Since:** 2.9 | **Tags:** #user #update
Fires when an item is updated.

### updated_{$meta_type}_meta
**Since:** 2.9 | **Tags:** #variable #update
Fires when an item is updated.

### update_option
**Since:** 2.9 | **Tags:** #options #update
Fires when an item is updated.

### update_postmeta
**Since:** 2.9 | **Tags:** #post #update
Fires when an item is updated.

### update_usermeta
**Since:** 2.9 | **Tags:** #user #update
Fires when an item is updated.

### update_{$meta_type}_meta
**Since:** 2.9 | **Tags:** #variable #update
Fires when an item is updated.

### add_option_{$option}
**Since:** 3.0 | **Tags:** #variable #options
Fires when a new item is added.

### deleted_transient
**Since:** 3.0 | **Tags:** #options
Fires when the related item is deleted.

### delete_option_{$option}
**Since:** 3.0 | **Tags:** #variable #options
Fires when the related item is deleted.

### delete_transient_{$transient}
**Since:** 3.0 | **Tags:** #variable #options
Fires when the related item is deleted.

### deprecated_argument_run
**Since:** 3.0 | **Tags:** #deprecated
Fires when a deprecated function, hook, or argument is used.

### opml_head
**Since:** 3.0 | **Tags:** #feed
Action hook fired during WordPress processing.

### set_transient_{$transient}
**Since:** 3.0 | **Tags:** #variable #options
Action hook fired during WordPress processing.

### unload_textdomain
**Since:** 3.0 | **Tags:** #i18n
Action hook fired during WordPress processing.

### update_option_{$option}
**Since:** 3.0 | **Tags:** #variable #options #update
Fires when an item is updated.

### wp_feed_options
**Since:** 3.0 | **Tags:** #options #feed
Action hook fired during WordPress processing.

### wp_loaded
**Since:** 3.0 | **Tags:** #general
Fires after WordPress, all plugins, and the theme are fully loaded and instantiated.

### add_{$meta_type}_meta
**Since:** 3.1 | **Tags:** #variable
Fires when a new item is added.

### delete_{$meta_type}_meta
**Since:** 3.1 | **Tags:** #variable
Fires when the related item is deleted.

### doing_it_wrong_run
**Since:** 3.1 | **Tags:** #general
Action hook fired during WordPress processing.

### pre_get_comments
**Since:** 3.1 | **Tags:** #comment
Fires before the related action is processed.

### atom_author
**Since:** 3.2 | **Tags:** #user #feed
Action hook fired during WordPress processing.

### _core_updated_successfully
**Since:** 3.3 | **Tags:** #update
Action hook fired during WordPress processing.

### deleted_{$meta_type}meta
**Since:** 3.4 | **Tags:** #variable
Fires when the related item is deleted.

### delete_{$meta_type}meta
**Since:** 3.4 | **Tags:** #variable
Fires when the related item is deleted.

### xmlrpc_call_success_blogger_deletePost
**Since:** 3.4 | **Tags:** #xmlrpc #multisite
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_blogger_editPost
**Since:** 3.4 | **Tags:** #xmlrpc #multisite
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_blogger_newPost
**Since:** 3.4 | **Tags:** #xmlrpc #multisite
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_mw_editPost
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_mw_newMediaObject
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_mw_newPost
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_wp_deleteCategory
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_wp_deleteComment
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_wp_deletePage
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_wp_editComment
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_wp_newCategory
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_call_success_wp_newComment
**Since:** 3.4 | **Tags:** #xmlrpc
Fires after a successful XML-RPC method call.

### xmlrpc_rsd_apis
**Since:** 3.5 | **Tags:** #xmlrpc
Action hook fired during WordPress processing.

### pre_get_search_form
**Since:** 3.6 | **Tags:** #general
Fires before the related action is processed.

### upgrader_process_complete
**Since:** 3.6 | **Tags:** #update
Action hook fired during WordPress processing.

### automatic_updates_complete
**Since:** 3.8 | **Tags:** #update
Action hook fired during WordPress processing.

### wp_install
**Since:** 3.9 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_maybe_auto_update
**Since:** 3.9 | **Tags:** #cron #update
Action hook fired during WordPress processing.

### pre_get_users
**Since:** 4.0 | **Tags:** #user
Fires before the related action is processed.

### rss_tag_pre
**Since:** 4.0 | **Tags:** #taxonomy #feed
Action hook fired during WordPress processing.

### deprecated_constructor_run
**Since:** 4.3 | **Tags:** #deprecated
Fires when a deprecated function, hook, or argument is used.

### do_feed_{$feed}
**Since:** 4.4 | **Tags:** #variable #feed
Action hook fired during WordPress processing.

### pre_auto_update
**Since:** 4.4 | **Tags:** #cron #update
Fires before an automatic update is attempted.

### wp_verify_nonce_failed
**Since:** 4.4 | **Tags:** #security
Fires when a nonce verification fails.

### metadata_lazyloader_queued_objects
**Since:** 4.5 | **Tags:** #general
Action hook fired during WordPress processing.

### deprecated_hook_run
**Since:** 4.6 | **Tags:** #deprecated
Fires when a deprecated function, hook, or argument is used.

### pre_get_networks
**Since:** 4.6 | **Tags:** #multisite
Fires before the related action is processed.

### pre_get_sites
**Since:** 4.6 | **Tags:** #multisite
Fires before the related action is processed.

### pre_get_terms
**Since:** 4.6 | **Tags:** #taxonomy
Fires before the related action is processed.

### change_locale
**Since:** 4.7 | **Tags:** #i18n
Action hook fired during WordPress processing.

### requests-{$hook}
**Since:** 4.7 | **Tags:** #variable
Action hook fired during WordPress processing.

### restore_previous_locale
**Since:** 4.7 | **Tags:** #rest #i18n
Action hook fired during WordPress processing.

### switch_locale
**Since:** 4.7 | **Tags:** #i18n
Action hook fired during WordPress processing.

### wp_roles_init
**Since:** 4.7 | **Tags:** #general
Action hook fired during WordPress processing.

### {$args}
**Since:** 4.7 | **Tags:** #variable
Action hook fired during WordPress processing.

### generate_recovery_mode_key
**Since:** 5.2 | **Tags:** #general
Action hook fired during WordPress processing.

### {$arg}
**Since:** 5.3 | **Tags:** #variable
Action hook fired during WordPress processing.

### do_favicon
**Since:** 5.4 | **Tags:** #general
Action hook fired during WordPress processing.

### do_faviconico
**Since:** 5.4 | **Tags:** #general
Action hook fired during WordPress processing.

### register_setting
**Since:** 5.5 | **Tags:** #options
Fires when a setting is registered.

### set_404
**Since:** 5.5 | **Tags:** #general
Fires when a 404 response is set.

### unregister_setting
**Since:** 5.5 | **Tags:** #options
Fires when a setting is unregistered.

### upgrader_overwrote_package
**Since:** 5.5 | **Tags:** #update
Action hook fired during WordPress processing.

### after_core_auto_updates_settings
**Since:** 5.6 | **Tags:** #options #cron #update
Action hook fired during WordPress processing.

### do_all_pings
**Since:** 5.6 | **Tags:** #general
Fires when all pending pings are processed.

### is_wp_error_instance
**Since:** 5.6 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_error_added
**Since:** 5.6 | **Tags:** #general
Action hook fired during WordPress processing.

### {$hook_name}
**Since:** 5.8 | **Tags:** #variable
Action hook fired during WordPress processing.

### cron_reschedule_event_error
**Since:** 6.1 | **Tags:** #cron
Fires during cron event processing.

### cron_unschedule_event_error
**Since:** 6.1 | **Tags:** #cron
Fires during cron event processing.

### wp_cache_set_last_changed
**Since:** 6.3 | **Tags:** #options
Action hook fired during WordPress processing.

### deprecated_class_run
**Since:** 6.4 | **Tags:** #deprecated
Fires when a deprecated function, hook, or argument is used.

### wp_trigger_error_run
**Since:** 6.4 | **Tags:** #general
Action hook fired during WordPress processing.

### set_transient
**Since:** 6.8 | **Tags:** #options
Action hook fired during WordPress processing.

### wp_load_speculation_rules
**Since:** 6.8 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_abilities_api_categories_init
**Since:** 6.9 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_abilities_api_init
**Since:** 6.9 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_after_execute_ability
**Since:** 6.9 | **Tags:** #general
Fires after the related operation is completed.

### wp_before_execute_ability
**Since:** 6.9 | **Tags:** #general
Fires before the related operation is performed.

