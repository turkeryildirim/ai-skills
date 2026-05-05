# WordPress Actions: Multisite

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### populate_options
**Since:** 2.6 | **Tags:** #options
Action hook fired during WordPress processing.

### activate_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### added_existing_user
**Since:** 3.0 | **Tags:** #user
Fires when a new item is added.

### add_site_option
**Since:** 3.0 | **Tags:** #options #multisite
Fires when a new item is added.

### add_site_option_{$option}
**Since:** 3.0 | **Tags:** #variable #options #multisite
Fires when a new item is added.

### add_user_to_blog
**Since:** 3.0 | **Tags:** #user #multisite
Fires when a new item is added.

### after_mu_upgrade
**Since:** 3.0 | **Tags:** #update
Action hook fired during WordPress processing.

### after_signup_form
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### archive_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### before_signup_form
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### deactivate_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### deleted_site_transient
**Since:** 3.0 | **Tags:** #options #multisite
Fires when the related item is deleted.

### delete_site_option
**Since:** 3.0 | **Tags:** #options #multisite
Fires when the related item is deleted.

### delete_site_option_{$option}
**Since:** 3.0 | **Tags:** #variable #options #multisite
Fires when the related item is deleted.

### delete_site_transient_{$transient}
**Since:** 3.0 | **Tags:** #variable #options #multisite
Fires when the related item is deleted.

### make_ham_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### make_spam_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### mu_activity_box_end
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### mu_rightnow_end
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### myblogs_allblogs_options
**Since:** 3.0 | **Tags:** #options #multisite
Fires during multisite/network processing.

### preprocess_signup_form
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### pre_delete_site_option_{$option}
**Since:** 3.0 | **Tags:** #variable #options #multisite
Fires before the related action is processed.

### remove_user_from_blog
**Since:** 3.0 | **Tags:** #user #multisite
Fires during multisite/network processing.

### set_site_transient_{$transient}
**Since:** 3.0 | **Tags:** #variable #options #multisite
Fires during multisite/network processing.

### signup_blogform
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### signup_extra_fields
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### signup_finished
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### signup_header
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### signup_hidden_fields
**Since:** 3.0 | **Tags:** #general
Action hook fired during WordPress processing.

### switch_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### unarchive_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### update_blog_public
**Since:** 3.0 | **Tags:** #multisite #update
Fires when an item is updated.

### update_site_option
**Since:** 3.0 | **Tags:** #options #multisite #update
Fires when an item is updated.

### update_site_option_{$option}
**Since:** 3.0 | **Tags:** #variable #options #multisite #update
Fires when an item is updated.

### update_wpmu_options
**Since:** 3.0 | **Tags:** #options #multisite #update
Fires when an item is updated.

### wpmuadminedit
**Since:** 3.0 | **Tags:** #admin #multisite
Action hook fired during WordPress processing.

### wpmuadminresult
**Since:** 3.0 | **Tags:** #admin #multisite
Action hook fired during WordPress processing.

### wpmublogsaction
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### wpmueditblogaction
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### wpmu_activate_blog
**Since:** 3.0 | **Tags:** #multisite
Fires during multisite/network processing.

### wpmu_activate_user
**Since:** 3.0 | **Tags:** #user #multisite
Action hook fired during WordPress processing.

### wpmu_blog_updated
**Since:** 3.0 | **Tags:** #multisite #update
Fires during multisite/network processing.

### wpmu_delete_user
**Since:** 3.0 | **Tags:** #user #multisite
Action hook fired during WordPress processing.

### wpmu_new_user
**Since:** 3.0 | **Tags:** #user #multisite
Action hook fired during WordPress processing.

### wpmu_options
**Since:** 3.0 | **Tags:** #options #multisite
Action hook fired during WordPress processing.

### wpmu_update_blog_options
**Since:** 3.0 | **Tags:** #options #multisite #update
Fires during multisite/network processing.

### wpmu_upgrade_page
**Since:** 3.0 | **Tags:** #post #multisite #update
Action hook fired during WordPress processing.

### wpmu_upgrade_site
**Since:** 3.0 | **Tags:** #multisite #update
Fires during multisite/network processing.

### mature_blog
**Since:** 3.1 | **Tags:** #multisite
Fires during multisite/network processing.

### network_admin_edit_{$action}
**Since:** 3.1 | **Tags:** #variable #admin #multisite
Fires during multisite/network processing.

### network_admin_menu
**Since:** 3.1 | **Tags:** #admin #menu #multisite
Fires during multisite/network processing.

### network_admin_notices
**Since:** 3.1 | **Tags:** #admin #multisite
Fires during multisite/network processing.

### network_site_users_after_list_table
**Since:** 3.1 | **Tags:** #user #multisite
Fires after the related operation is completed.

### unmature_blog
**Since:** 3.1 | **Tags:** #multisite
Fires during multisite/network processing.

### wp_network_dashboard_setup
**Since:** 3.1 | **Tags:** #admin #multisite
Fires during multisite/network processing.

### make_delete_blog
**Since:** 3.5 | **Tags:** #multisite
Fires during multisite/network processing.

### make_undelete_blog
**Since:** 3.5 | **Tags:** #multisite
Fires during multisite/network processing.

### ms_site_not_found
**Since:** 3.9 | **Tags:** #multisite
Fires during multisite/network processing.

### wp_upgrade
**Since:** 3.9 | **Tags:** #update
Action hook fired during WordPress processing.

### after_signup_site
**Since:** 4.4 | **Tags:** #multisite
Fires during multisite/network processing.

### after_signup_user
**Since:** 4.4 | **Tags:** #user
Action hook fired during WordPress processing.

### before_signup_header
**Since:** 4.4 | **Tags:** #general
Action hook fired during WordPress processing.

### invite_user
**Since:** 4.4 | **Tags:** #user
Action hook fired during WordPress processing.

### ms_network_not_found
**Since:** 4.4 | **Tags:** #multisite
Fires during multisite/network processing.

### network_site_new_created_user
**Since:** 4.4 | **Tags:** #user #multisite
Fires during multisite/network processing.

### network_site_users_created_user
**Since:** 4.4 | **Tags:** #user #multisite
Fires during multisite/network processing.

### network_user_new_created_user
**Since:** 4.4 | **Tags:** #user #multisite
Fires during multisite/network processing.

### network_site_new_form
**Since:** 4.5 | **Tags:** #multisite
Fires during multisite/network processing.

### network_user_new_form
**Since:** 4.5 | **Tags:** #user #multisite
Fires during multisite/network processing.

### pre_network_site_new_created_user
**Since:** 4.5 | **Tags:** #user #multisite
Fires before the related action is processed.

### clean_network_cache
**Since:** 4.6 | **Tags:** #options #multisite
Fires when the related cache is cleaned.

### clean_site_cache
**Since:** 4.6 | **Tags:** #options #multisite
Fires when the related cache is cleaned.

### ms_loaded
**Since:** 4.6 | **Tags:** #general
Action hook fired during WordPress processing.

### parse_network_query
**Since:** 4.6 | **Tags:** #multisite
Fires during multisite/network processing.

### parse_site_query
**Since:** 4.6 | **Tags:** #multisite
Fires during multisite/network processing.

### mu_plugin_loaded
**Params:** string $mu_plugin
**Since:** 5.1 | **Tags:** #plugin
Fires after a single must-use plugin has loaded.

### network_plugin_loaded
**Since:** 5.1 | **Tags:** #plugin #multisite
Fires during multisite/network processing.

### wp_delete_site
**Since:** 5.1 | **Tags:** #multisite
Fires during multisite/network processing.

### wp_initialize_site
**Since:** 5.1 | **Tags:** #multisite
Fires during multisite/network processing.

### wp_insert_site
**Since:** 5.1 | **Tags:** #multisite
Fires during multisite/network processing.

### wp_uninitialize_site
**Since:** 5.1 | **Tags:** #multisite
Fires during multisite/network processing.

### wp_update_site
**Since:** 5.1 | **Tags:** #multisite #update
Fires during multisite/network processing.

### wp_validate_site_data
**Since:** 5.1 | **Tags:** #multisite
Fires during multisite/network processing.

### wp_validate_site_deletion
**Since:** 5.1 | **Tags:** #multisite
Fires during multisite/network processing.

### restrict_manage_sites
**Since:** 5.3 | **Tags:** #rest #multisite
Fires during multisite/network processing.

### network_site_info_form
**Since:** 5.6 | **Tags:** #multisite
Fires during multisite/network processing.

### site_health_tab_content
**Since:** 5.8 | **Tags:** #multisite
Fires during multisite/network processing.

### set_site_transient
**Since:** 6.8 | **Tags:** #options #multisite
Fires during multisite/network processing.

### after_populate_network
**Since:** 6.9 | **Tags:** #multisite
Fires during multisite/network processing.

### after_upgrade_to_multisite
**Since:** 6.9 | **Tags:** #multisite #update
Fires during multisite/network processing.

### before_populate_network
**Since:** 6.9 | **Tags:** #multisite
Fires during multisite/network processing.

