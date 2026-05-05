# WordPress Actions: Admin

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### admin_footer
**Params:** string $data
**Since:** 1.2.1 | **Tags:** #admin
Fires at the bottom of the admin footer. Used to add custom scripts or content to admin pages.

### admin_head
**Since:** 1.2.1 | **Tags:** #admin
Fires in the <head> section of admin pages. Used to add custom meta, styles, or scripts.

### admin_menu
**Since:** 1.5.2 | **Tags:** #admin #menu
Fires after the admin menu structure is in place. Add custom admin menu pages here.

### check_admin_referer
**Params:** int $action, string $result
**Since:** 1.5.2 | **Tags:** #admin
Fires after the admin referer is verified via check_admin_referer().

### edit_form_advanced
**Since:** 1.5.2 | **Tags:** #general
Fires when the related item is edited or updated.

### edit_page_form
**Since:** 1.5.2 | **Tags:** #post
Fires when the related item is edited or updated.

### manage_posts_custom_column
**Params:** string $column_name, int $post_id
**Since:** 1.5.2 | **Tags:** #post
Fires in each custom column in the Posts list table.

### plugins_loaded
**Since:** 1.5.2 | **Tags:** #plugin
Fires after all plugin files have been loaded. Use to initialize plugin functionality after all plugins are available.

### {$page_hook}
**Since:** 1.5.2 | **Tags:** #variable #post
Action hook fired during WordPress processing.

### activate_{$plugin}
**Since:** 2.0 | **Tags:** #variable #plugin
Action hook fired during WordPress processing.

### activity_box_end
**Since:** 2.0 | **Tags:** #general
Fires at the end of the activity box on the dashboard.

### deactivate_{$plugin}
**Since:** 2.0 | **Tags:** #variable #plugin
Action hook fired during WordPress processing.

### admin_notices
**Since:** 2.0.11 | **Tags:** #admin
Action hook fired during WordPress processing.

### dbx_post_sidebar
**Since:** 2.0.11 | **Tags:** #post #widget #database
Action hook fired during WordPress processing.

### admin_print_scripts
**Since:** 2.1 | **Tags:** #admin #assets
Fires when printing scripts in the admin header.

### blog_privacy_selector
**Since:** 2.1 | **Tags:** #multisite #privacy
Fires during multisite/network processing.

### check_ajax_referer
**Params:** int $action, string $result
**Since:** 2.1 | **Tags:** #general
Fires after an AJAX referer nonce is verified.

### load-{$pagenow}
**Since:** 2.1 | **Tags:** #variable #post
Action hook fired during WordPress processing.

### load-{$page_hook}
**Since:** 2.1 | **Tags:** #variable #post
Action hook fired during WordPress processing.

### load-{$plugin_page}
**Since:** 2.1 | **Tags:** #variable #post #plugin
Action hook fired during WordPress processing.

### manage_link_custom_column
**Since:** 2.1 | **Tags:** #general
Action hook fired during WordPress processing.

### restrict_manage_posts
**Since:** 2.1 | **Tags:** #post #rest
Action hook fired during WordPress processing.

### wp_ajax_{$action}
**Since:** 2.1 | **Tags:** #variable
Fires when an AJAX action is handled for authenticated users.

### admin_xml_ns
**Since:** 2.2 | **Tags:** #admin
Action hook fired during WordPress processing.

### _admin_menu
**Since:** 2.2 | **Tags:** #admin #menu
Action hook fired during WordPress processing.

### after_plugin_row
**Since:** 2.3 | **Tags:** #plugin
Action hook fired during WordPress processing.

### export_wp
**Since:** 2.3 | **Tags:** #general
Action hook fired during WordPress processing.

### load_feed_engine
**Since:** 2.3 | **Tags:** #feed
Action hook fired during WordPress processing.

### adminmenu
**Since:** 2.5 | **Tags:** #admin #menu
Action hook fired during WordPress processing.

### admin_head_{$content_func}
**Since:** 2.5 | **Tags:** #variable #admin
Action hook fired during WordPress processing.

### admin_init
**Since:** 2.5 | **Tags:** #admin
Fires as an admin page initializes. Used for admin-only initialization, redirects, and option registration.

### admin_page_access_denied
**Since:** 2.5 | **Tags:** #post #admin
Action hook fired during WordPress processing.

### in_admin_footer
**Since:** 2.5 | **Tags:** #admin
Action hook fired during WordPress processing.

### manage_comments_nav
**Since:** 2.5 | **Tags:** #comment #menu
Fires during comment-related processing.

### manage_media_custom_column
**Since:** 2.5 | **Tags:** #media
Action hook fired during WordPress processing.

### manage_pages_custom_column
**Since:** 2.5 | **Tags:** #post
Action hook fired during WordPress processing.

### rightnow_end
**Since:** 2.5 | **Tags:** #general
Action hook fired during WordPress processing.

### submitlink_box
**Since:** 2.5 | **Tags:** #general
Action hook fired during WordPress processing.

### submitpage_box
**Since:** 2.5 | **Tags:** #post
Action hook fired during WordPress processing.

### submitpost_box
**Since:** 2.5 | **Tags:** #post
Action hook fired during WordPress processing.

### wp_dashboard_setup
**Since:** 2.5 | **Tags:** #admin
Fires when initializing the dashboard widgets.

### admin_action_{$action}
**Since:** 2.6 | **Tags:** #variable #admin
Action hook fired during WordPress processing.

### admin_print_styles
**Since:** 2.6 | **Tags:** #admin #assets
Fires when printing styles in the admin header.

### do_meta_boxes
**Since:** 2.6 | **Tags:** #general
Action hook fired during WordPress processing.

### admin_head-{$hook_suffix}
**Since:** 2.7 | **Tags:** #variable #admin
Action hook fired during WordPress processing.

### admin_print_scripts-{$hook_suffix}
**Since:** 2.7 | **Tags:** #variable #admin #assets
Fires when printing scripts in the admin context.

### admin_print_styles-{$hook_suffix}
**Since:** 2.7 | **Tags:** #variable #admin #assets
Fires when printing styles in the admin context.

### after_plugin_row_{$plugin_file}
**Since:** 2.7 | **Tags:** #variable #plugin
Action hook fired during WordPress processing.

### bulk_edit_custom_box
**Since:** 2.7 | **Tags:** #general
Action hook fired during WordPress processing.

### install_plugins_pre_{$tab}
**Since:** 2.7 | **Tags:** #variable #plugin
Action hook fired during WordPress processing.

### install_plugins_table_header
**Since:** 2.7 | **Tags:** #plugin
Action hook fired during WordPress processing.

### install_plugins_{$tab}
**Since:** 2.7 | **Tags:** #variable #plugin
Action hook fired during WordPress processing.

### post_submitbox_start
**Since:** 2.7 | **Tags:** #post
Action hook fired during WordPress processing.

### quick_edit_custom_box
**Since:** 2.7 | **Tags:** #general
Action hook fired during WordPress processing.

### uninstall_{$file}
**Since:** 2.7 | **Tags:** #variable
Action hook fired during WordPress processing.

### admin_enqueue_scripts
**Params:** string $hook_suffix
**Since:** 2.8 | **Tags:** #admin #assets
Fires when enqueuing scripts and styles for admin pages.

### admin_footer-{$hook_suffix}
**Since:** 2.8 | **Tags:** #variable #admin
Action hook fired during WordPress processing.

### admin_print_footer_scripts
**Since:** 2.8 | **Tags:** #admin #assets
Action hook fired during WordPress processing.

### auth_redirect
**Since:** 2.8 | **Tags:** #user #redirect
Fires before the authentication redirect is performed.

### install_themes_pre_{$tab}
**Since:** 2.8 | **Tags:** #variable #theme
Action hook fired during WordPress processing.

### install_themes_table_header
**Since:** 2.8 | **Tags:** #theme
Action hook fired during WordPress processing.

### install_themes_{$tab}
**Since:** 2.8 | **Tags:** #variable #theme
Action hook fired during WordPress processing.

### in_plugin_update_message-{$file}
**Since:** 2.8 | **Tags:** #variable #plugin #update
Action hook fired during WordPress processing.

### load-widgets-php
**Since:** 2.8 | **Tags:** #widget
Action hook fired during WordPress processing.

### manage_comments_custom_column
**Since:** 2.8 | **Tags:** #comment
Fires during comment-related processing.

### tool_box
**Since:** 2.8 | **Tags:** #general
Action hook fired during WordPress processing.

### update-custom_{$action}
**Since:** 2.8 | **Tags:** #variable #update
Action hook fired during WordPress processing.

### wp_ajax_nopriv_{$action}
**Since:** 2.8 | **Tags:** #variable
Fires when an AJAX action is handled for authenticated users.

### activated_plugin
**Since:** 2.9 | **Tags:** #plugin
Action hook fired during WordPress processing.

### activate_plugin
**Since:** 2.9 | **Tags:** #plugin
Action hook fired during WordPress processing.

### admin_head-media-upload-popup
**Since:** 2.9 | **Tags:** #admin #media
Action hook fired during WordPress processing.

### admin_print_scripts-media-upload-popup
**Since:** 2.9 | **Tags:** #admin #media #assets
Fires when printing scripts in the admin context.

### admin_print_styles-media-upload-popup
**Since:** 2.9 | **Tags:** #admin #media #assets
Fires when printing styles in the admin context.

### core_upgrade_preamble
**Since:** 2.9 | **Tags:** #update
Action hook fired during WordPress processing.

### deactivated_plugin
**Since:** 2.9 | **Tags:** #plugin
Action hook fired during WordPress processing.

### deactivate_plugin
**Since:** 2.9 | **Tags:** #plugin
Action hook fired during WordPress processing.

### load_textdomain
**Since:** 2.9 | **Tags:** #i18n
Action hook fired during WordPress processing.

### post_submitbox_misc_actions
**Since:** 2.9 | **Tags:** #post
Action hook fired during WordPress processing.

### activate_header
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### activate_wp_head
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### add_meta_boxes
**Since:** 3.0 | **Tags:** #general
Fires when a new item is added.

### add_meta_boxes_comment
**Since:** 3.0 | **Tags:** #comment
Fires when a new item is added.

### add_meta_boxes_link
**Since:** 3.0 | **Tags:** #general
Fires when a new item is added.

### add_meta_boxes_{$post_type}
**Since:** 3.0 | **Tags:** #variable #post
Fires when a new item is added.

### admin_color_scheme_picker
**Since:** 3.0 | **Tags:** #admin
Action hook fired during WordPress processing.

### in_admin_header
**Since:** 3.0 | **Tags:** #admin
Action hook fired during WordPress processing.

### post_edit_form_tag
**Since:** 3.0 | **Tags:** #post #taxonomy
Action hook fired during WordPress processing.

### pre_current_active_plugins
**Since:** 3.0 | **Tags:** #plugin
Fires before the related action is processed.

### add_admin_bar_menus
**Since:** 3.1 | **Tags:** #admin #menu
Fires when a new item is added.

### admin_bar_init
**Since:** 3.1 | **Tags:** #admin
Action hook fired during WordPress processing.

### admin_bar_menu
**Since:** 3.1 | **Tags:** #admin #menu
Action hook fired during WordPress processing.

### after_theme_row
**Since:** 3.1 | **Tags:** #theme
Action hook fired during WordPress processing.

### all_admin_notices
**Since:** 3.1 | **Tags:** #admin
Action hook fired during WordPress processing.

### in_theme_update_message-{$theme_key}
**Since:** 3.1 | **Tags:** #variable #theme #update
Action hook fired during WordPress processing.

### load-categories-php
**Since:** 3.1 | **Tags:** #general
Action hook fired during WordPress processing.

### load-edit-link-categories-php
**Since:** 3.1 | **Tags:** #general
Action hook fired during WordPress processing.

### load-page-new-php
**Since:** 3.1 | **Tags:** #post
Action hook fired during WordPress processing.

### load-page-php
**Since:** 3.1 | **Tags:** #post
Action hook fired during WordPress processing.

### manage_plugins_custom_column
**Since:** 3.1 | **Tags:** #plugin
Action hook fired during WordPress processing.

### manage_sites_custom_column
**Since:** 3.1 | **Tags:** #multisite
Fires during multisite/network processing.

### manage_themes_custom_column
**Since:** 3.1 | **Tags:** #theme
Action hook fired during WordPress processing.

### manage_{$post->post_type}_posts_custom_column
**Since:** 3.1 | **Tags:** #variable #post
Action hook fired during WordPress processing.

### post_comment_status_meta_box-options
**Since:** 3.1 | **Tags:** #post #comment #options
Fires during comment-related processing.

### wp_after_admin_bar_render
**Since:** 3.1 | **Tags:** #admin
Fires after the related operation is completed.

### wp_before_admin_bar_render
**Since:** 3.1 | **Tags:** #admin
Fires before the related operation is performed.

### _network_admin_menu
**Since:** 3.1 | **Tags:** #admin #menu #multisite
Fires during multisite/network processing.

### _user_admin_menu
**Since:** 3.1 | **Tags:** #user #admin #menu
Action hook fired during WordPress processing.

### after_wp_tiny_mce
**Since:** 3.2 | **Tags:** #general
Action hook fired during WordPress processing.

### before_wp_tiny_mce
**Since:** 3.2 | **Tags:** #general
Action hook fired during WordPress processing.

### update-core-custom_{$action}
**Since:** 3.2 | **Tags:** #variable #update
Action hook fired during WordPress processing.

### after_theme_row_{$stylesheet}
**Since:** 3.5 | **Tags:** #variable #theme #assets
Action hook fired during WordPress processing.

### edit_form_after_editor
**Since:** 3.5 | **Tags:** #general
Fires after the related operation is completed.

### edit_form_after_title
**Since:** 3.5 | **Tags:** #general
Fires after the related operation is completed.

### export_filters
**Since:** 3.5 | **Tags:** #general
Action hook fired during WordPress processing.

### load-importer-{$importer}
**Since:** 3.5 | **Tags:** #variable
Action hook fired during WordPress processing.

### restrict_manage_comments
**Since:** 3.5 | **Tags:** #comment #rest
Fires during comment-related processing.

### restrict_manage_users
**Since:** 3.5 | **Tags:** #user #rest
Action hook fired during WordPress processing.

### welcome_panel
**Since:** 3.5 | **Tags:** #general
Action hook fired during WordPress processing.

### after_menu_locations_table
**Since:** 3.6 | **Tags:** #menu
Action hook fired during WordPress processing.

### heartbeat_nopriv_tick
**Since:** 3.6 | **Tags:** #general
Action hook fired during WordPress processing.

### heartbeat_tick
**Since:** 3.6 | **Tags:** #general
Action hook fired during WordPress processing.

### post_locked_dialog
**Since:** 3.6 | **Tags:** #post
Action hook fired during WordPress processing.

### post_lock_lost_dialog
**Since:** 3.6 | **Tags:** #post
Action hook fired during WordPress processing.

### edit_form_top
**Since:** 3.7 | **Tags:** #general
Fires when the related item is edited or updated.

### admin_footer-widgets-php
**Since:** 3.9 | **Tags:** #admin #widget
Action hook fired during WordPress processing.

### admin_print_scripts-widgets-php
**Since:** 3.9 | **Tags:** #admin #widget #assets
Fires when printing scripts in the admin context.

### admin_print_styles-widgets-php
**Since:** 3.9 | **Tags:** #admin #widget #assets
Fires when printing styles in the admin context.

### wp_tiny_mce_init
**Since:** 3.9 | **Tags:** #general
Action hook fired during WordPress processing.

### admin_post
**Since:** 4.0 | **Tags:** #post #admin
Action hook fired during WordPress processing.

### admin_post_nopriv
**Since:** 4.0 | **Tags:** #post #admin
Action hook fired during WordPress processing.

### admin_post_nopriv_{$action}
**Since:** 4.0 | **Tags:** #variable #post #admin
Action hook fired during WordPress processing.

### admin_post_{$action}
**Since:** 4.0 | **Tags:** #variable #post #admin
Action hook fired during WordPress processing.

### edit_form_before_permalink
**Since:** 4.1 | **Tags:** #rewrite
Fires before the related operation is performed.

### deleted_plugin
**Since:** 4.4 | **Tags:** #plugin
Fires when the related item is deleted.

### delete_plugin
**Since:** 4.4 | **Tags:** #plugin
Fires when the related item is deleted.

### delete_widget
**Since:** 4.4 | **Tags:** #widget
Fires when the related item is deleted.

### manage_posts_extra_tablenav
**Since:** 4.4 | **Tags:** #post #menu
Action hook fired during WordPress processing.

### page_attributes_meta_box_template
**Since:** 4.4 | **Tags:** #post #theme
Action hook fired during WordPress processing.

### post_submitbox_minor_actions
**Since:** 4.4 | **Tags:** #post
Action hook fired during WordPress processing.

### load-edit-tags-php
**Since:** 4.5 | **Tags:** #taxonomy
Action hook fired during WordPress processing.

### pre_uninstall_plugin
**Since:** 4.5 | **Tags:** #plugin
Fires before the related action is processed.

### admin_print_footer_scripts-widgets-php
**Since:** 4.6 | **Tags:** #admin #widget #assets
Action hook fired during WordPress processing.

### admin_print_footer_scripts-{$hook_suffix}
**Since:** 4.6 | **Tags:** #variable #admin #assets
Action hook fired during WordPress processing.

### install_plugins_pre_upload
**Since:** 4.6 | **Tags:** #plugin #media
Action hook fired during WordPress processing.

### install_plugins_upload
**Since:** 4.6 | **Tags:** #plugin #media
Action hook fired during WordPress processing.

### post_action_{$action}
**Since:** 4.6 | **Tags:** #variable #post
Action hook fired during WordPress processing.

### wp_edit_form_attachment_display
**Since:** 4.6 | **Tags:** #media
Action hook fired during WordPress processing.

### print_default_editor_scripts
**Since:** 4.8 | **Tags:** #assets
Action hook fired during WordPress processing.

### manage_users_extra_tablenav
**Since:** 4.9 | **Tags:** #user #menu
Action hook fired during WordPress processing.

### page_attributes_misc_attributes
**Since:** 4.9 | **Tags:** #post
Action hook fired during WordPress processing.

### add_inline_data
**Since:** 5.0 | **Tags:** #general
Fires when a new item is added.

### block_editor_meta_box_hidden_fields
**Since:** 5.0 | **Tags:** #block
Action hook fired during WordPress processing.

### plugin_loaded
**Since:** 5.1 | **Tags:** #plugin
Action hook fired during WordPress processing.

### admin_email_confirm
**Since:** 5.3 | **Tags:** #admin #mail
Action hook fired during WordPress processing.

### admin_email_confirm_form
**Since:** 5.3 | **Tags:** #admin #mail
Action hook fired during WordPress processing.

### manage_sites_extra_tablenav
**Since:** 5.3 | **Tags:** #menu #multisite
Fires during multisite/network processing.

### manage_{$this->screen->id}_custom_column
**Since:** 5.6 | **Tags:** #variable
Action hook fired during WordPress processing.

### manage_{$this->screen->id}_custom_column_js_template
**Since:** 5.6 | **Tags:** #variable #theme
Action hook fired during WordPress processing.

### deleted_theme
**Since:** 5.8 | **Tags:** #theme
Fires when the related item is deleted.

### delete_theme
**Since:** 5.8 | **Tags:** #theme
Fires when the related item is deleted.

### bulk_edit_posts
**Since:** 6.3 | **Tags:** #post
Action hook fired during WordPress processing.

### wp_admin_notice
**Since:** 6.4 | **Tags:** #admin
Action hook fired during WordPress processing.

### after_plugin_row_meta
**Since:** 6.5 | **Tags:** #plugin
Action hook fired during WordPress processing.

### import_filters
**Since:** 6.8 | **Tags:** #general
Action hook fired during WordPress processing.

