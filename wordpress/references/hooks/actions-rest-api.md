# WordPress Actions: REST API

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### rest_api_init
**Params:** WP_REST_Server $server
**Since:** 4.4 | **Tags:** #rest
Fires when preparing to serve a REST API request. Register REST routes here.

### rest_delete_comment
**Since:** 4.7 | **Tags:** #comment #rest
Fires during REST API request processing.

### rest_delete_revision
**Since:** 4.7 | **Tags:** #rest
Fires during REST API request processing.

### rest_delete_user
**Since:** 4.7 | **Tags:** #user #rest
Fires during REST API request processing.

### rest_delete_{$this->post_type}
**Since:** 4.7 | **Tags:** #variable #post #rest
Fires during REST API request processing.

### rest_delete_{$this->taxonomy}
**Since:** 4.7 | **Tags:** #variable #taxonomy #rest
Fires during REST API request processing.

### rest_insert_attachment
**Since:** 4.7 | **Tags:** #media #rest
Fires during REST API request processing.

### rest_insert_comment
**Since:** 4.7 | **Tags:** #comment #rest
Fires during REST API request processing.

### rest_insert_user
**Since:** 4.7 | **Tags:** #user #rest
Fires during REST API request processing.

### rest_insert_{$this->post_type}
**Since:** 4.7 | **Tags:** #variable #post #rest
Fires during REST API request processing.

### rest_insert_{$this->taxonomy}
**Since:** 4.7 | **Tags:** #variable #taxonomy #rest
Fires during REST API request processing.

### rest_after_insert_attachment
**Since:** 5.0 | **Tags:** #media #rest
Fires after the related operation is completed.

### rest_after_insert_comment
**Since:** 5.0 | **Tags:** #comment #rest
Fires after the related operation is completed.

### rest_after_insert_user
**Since:** 5.0 | **Tags:** #user #rest
Fires after the related operation is completed.

### rest_after_insert_{$this->post_type}
**Since:** 5.0 | **Tags:** #variable #post #rest
Fires after the related operation is completed.

### rest_after_insert_{$this->taxonomy}
**Since:** 5.0 | **Tags:** #variable #taxonomy #rest
Fires after the related operation is completed.

### rest_after_insert_application_password
**Since:** 5.6 | **Tags:** #user #rest
Fires after the related operation is completed.

### rest_after_save_widget
**Since:** 5.8 | **Tags:** #widget #rest
Fires after the related operation is completed.

### rest_delete_widget
**Since:** 5.8 | **Tags:** #widget #rest
Fires during REST API request processing.

### rest_save_sidebar
**Since:** 5.8 | **Tags:** #widget #rest
Fires during REST API request processing.

### rest_after_insert_nav_menu_item
**Since:** 5.9 | **Tags:** #menu #rest
Fires after the related operation is completed.

### rest_delete_nav_menu_item
**Since:** 5.9 | **Tags:** #menu #rest
Fires during REST API request processing.

### rest_insert_nav_menu_item
**Since:** 5.9 | **Tags:** #menu #rest
Fires during REST API request processing.

