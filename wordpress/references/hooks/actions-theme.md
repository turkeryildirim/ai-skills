# WordPress Actions: Theme

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### wp_head
**Since:** 1.2.1 | **Tags:** #general
Fires in the <head> section of the front-end. Used to add meta tags, styles, and scripts.

### switch_theme
**Params:** string $new_name, WP_Theme $new_theme, string $old_name, WP_Theme $old_theme
**Since:** 1.5.2 | **Tags:** #theme
Fires after the theme is switched to a new theme.

### template_redirect
**Since:** 1.5.2 | **Tags:** #theme #redirect
Fires before rendering the template. Used for redirects and loading alternative templates.

### wp_footer
**Since:** 1.5.2 | **Tags:** #general
Fires in the footer of the front-end. Used to add scripts and content before </body>.

### wp_meta
**Since:** 1.5.2 | **Tags:** #general
Fires by the wp_meta() function, typically in the sidebar.

### loop_end
**Since:** 2.0 | **Tags:** #general
Action hook fired during WordPress processing.

### loop_start
**Since:** 2.0 | **Tags:** #general
Action hook fired during WordPress processing.

### get_footer
**Params:** string|null $name
**Since:** 2.1 | **Tags:** #general
Fires before the footer template file is loaded.

### get_header
**Params:** string|null $name
**Since:** 2.1 | **Tags:** #general
Fires before the header template file is loaded.

### wp_print_scripts
**Since:** 2.1 | **Tags:** #assets
Action hook fired during WordPress processing.

### get_sidebar
**Params:** string|null $name
**Since:** 2.2 | **Tags:** #widget
Fires before the sidebar template file is loaded.

### sidebar_admin_page
**Since:** 2.2 | **Tags:** #post #admin #widget
Action hook fired during WordPress processing.

### sidebar_admin_setup
**Since:** 2.2 | **Tags:** #admin #widget
Action hook fired during WordPress processing.

### widgets_init
**Since:** 2.2 | **Tags:** #widget
Fires after widgets and sidebars have been registered.

### wp_default_scripts
**Since:** 2.6 | **Tags:** #assets
Action hook fired during WordPress processing.

### wp_default_styles
**Since:** 2.6 | **Tags:** #assets
Action hook fired during WordPress processing.

### wp_print_styles
**Since:** 2.6 | **Tags:** #assets
Action hook fired during WordPress processing.

### get_search_form
**Since:** 2.7 | **Tags:** #general
Action hook fired during WordPress processing.

### in_widget_form
**Since:** 2.8 | **Tags:** #widget
Action hook fired during WordPress processing.

### the_post
**Since:** 2.8 | **Tags:** #post
Action hook fired during WordPress processing.

### widgets-php
**Since:** 2.8 | **Tags:** #widget
Action hook fired during WordPress processing.

### wp_enqueue_scripts
**Since:** 2.8 | **Tags:** #assets
Fires when enqueuing front-end scripts and styles.

### wp_print_footer_scripts
**Since:** 2.8 | **Tags:** #assets
Action hook fired during WordPress processing.

### after_setup_theme
**Since:** 3.0 | **Tags:** #theme
Fires after the theme is loaded and initialized. Commonly used for add_theme_support() calls.

### dynamic_sidebar
**Since:** 3.0 | **Tags:** #widget
Action hook fired during WordPress processing.

### get_template_part_{$slug}
**Since:** 3.0 | **Tags:** #variable #theme
Action hook fired during WordPress processing.

### register_sidebar
**Since:** 3.0 | **Tags:** #widget
Fires when an item is registered.

### the_widget
**Since:** 3.0 | **Tags:** #widget
Action hook fired during WordPress processing.

### widgets_admin_page
**Since:** 3.0 | **Tags:** #post #admin #widget
Action hook fired during WordPress processing.

### wp_create_nav_menu
**Since:** 3.0 | **Tags:** #menu
Action hook fired during WordPress processing.

### wp_delete_nav_menu
**Since:** 3.0 | **Tags:** #menu
Action hook fired during WordPress processing.

### wp_register_sidebar_widget
**Since:** 3.0 | **Tags:** #widget
Action hook fired during WordPress processing.

### wp_unregister_sidebar_widget
**Since:** 3.0 | **Tags:** #widget
Action hook fired during WordPress processing.

### wp_update_nav_menu
**Since:** 3.0 | **Tags:** #menu #update
Action hook fired during WordPress processing.

### wp_update_nav_menu_item
**Since:** 3.0 | **Tags:** #menu #update
Action hook fired during WordPress processing.

### custom_header_options
**Since:** 3.1 | **Tags:** #options
Action hook fired during WordPress processing.

### after_switch_theme
**Since:** 3.3 | **Tags:** #theme
Action hook fired during WordPress processing.

### start_previewing_theme
**Since:** 3.4 | **Tags:** #theme
Action hook fired during WordPress processing.

### stop_previewing_theme
**Since:** 3.4 | **Tags:** #theme
Action hook fired during WordPress processing.

### dynamic_sidebar_after
**Since:** 3.9 | **Tags:** #widget
Action hook fired during WordPress processing.

### dynamic_sidebar_before
**Since:** 3.9 | **Tags:** #widget
Action hook fired during WordPress processing.

### wp_enqueue_editor
**Since:** 3.9 | **Tags:** #assets
Fires when assets are being enqueued.

### enqueue_embed_scripts
**Since:** 4.4 | **Tags:** #assets #embed
Fires when assets are being enqueued.

### wp_add_nav_menu_item
**Since:** 4.4 | **Tags:** #menu
Action hook fired during WordPress processing.

### loop_no_results
**Since:** 4.9 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_enqueue_code_editor
**Since:** 4.9 | **Tags:** #assets
Fires when assets are being enqueued.

### enqueue_block_assets
**Since:** 5.0 | **Tags:** #assets #block
Fires when assets are being enqueued.

### enqueue_block_editor_assets
**Since:** 5.0 | **Tags:** #assets #block
Fires when assets are being enqueued.

### get_template_part
**Since:** 5.2 | **Tags:** #theme
Action hook fired during WordPress processing.

### wp_body_open
**Since:** 5.2 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_nav_menu_item_custom_fields
**Since:** 5.4 | **Tags:** #menu
Action hook fired during WordPress processing.

### wp_nav_menu_item_custom_fields_customize_template
**Since:** 5.4 | **Tags:** #theme #menu #customizer
Fires during WordPress Customizer processing.

### wp_sitemaps_init
**Since:** 5.5 | **Tags:** #multisite
Fires during multisite/network processing.

### render_block_core_template_part_file
**Since:** 5.9 | **Tags:** #theme #block
Action hook fired during WordPress processing.

### render_block_core_template_part_none
**Since:** 5.9 | **Tags:** #theme #block
Action hook fired during WordPress processing.

### render_block_core_template_part_post
**Since:** 5.9 | **Tags:** #post #theme #block
Action hook fired during WordPress processing.

### wp_after_load_template
**Since:** 6.1 | **Tags:** #theme
Fires after the related operation is completed.

### wp_before_load_template
**Since:** 6.1 | **Tags:** #theme
Fires before the related operation is performed.

### wp_before_include_template
**Since:** 6.9 | **Tags:** #theme
Fires before the related operation is performed.

### wp_finalized_template_enhancement_output_buffer
**Since:** 6.9 | **Tags:** #theme
Action hook fired during WordPress processing.

### wp_template_enhancement_output_buffer_started
**Since:** 6.9 | **Tags:** #theme
Action hook fired during WordPress processing.

