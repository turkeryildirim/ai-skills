# WordPress Actions: User

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### check_passwords
**Params:** string $user_login, string &$pass1, string &$pass2
**Since:** 1.5.2 | **Tags:** #user
Fires when checking passwords during user authentication.

### lost_password
**Since:** 1.5.2 | **Tags:** #user
Fires before the lost password form is displayed.

### password_reset
**Params:** WP_User $user, string $new_pass
**Since:** 1.5.2 | **Tags:** #user
Fires before the user's password is reset via email.

### retrieve_password
**Params:** string $user_login
**Since:** 1.5.2 | **Tags:** #user
Fires before a new password is retrieved via the lost password form.

### user_register
**Params:** int $user_id
**Since:** 1.5.2 | **Tags:** #user
Fires immediately after a new user is created.

### wp_authenticate
**Params:** string $user_login, string $user_password
**Since:** 1.5.2 | **Tags:** #user
Fires before user authentication. Used to add custom authentication logic.

### wp_login
**Params:** string $user_login, WP_User $user
**Since:** 1.5.2 | **Tags:** #user
Fires when a user logs in successfully.

### wp_logout
**Params:** int $user_id
**Since:** 1.5.2 | **Tags:** #general
Fires when a user logs out.

### delete_user
**Params:** int $user_id, int|null $reassign
**Since:** 2.0 | **Tags:** #user
Fires immediately before a user is deleted.

### edit_user_profile
**Since:** 2.0 | **Tags:** #user
Fires when the related item is edited or updated.

### personal_options_update
**Since:** 2.0 | **Tags:** #options #update
Action hook fired during WordPress processing.

### profile_personal_options
**Since:** 2.0 | **Tags:** #options
Action hook fired during WordPress processing.

### profile_update
**Params:** int $user_id, WP_User $old_user_data
**Since:** 2.0 | **Tags:** #update
Fires immediately after an existing user is updated.

### show_user_profile
**Since:** 2.0 | **Tags:** #user
Action hook fired during WordPress processing.

### set_current_user
**Since:** 2.0.11 | **Tags:** #user
Action hook fired during WordPress processing.

### login_form
**Since:** 2.1 | **Tags:** #user
Action hook fired during WordPress processing.

### login_head
**Since:** 2.1 | **Tags:** #user
Action hook fired during WordPress processing.

### lostpassword_form
**Since:** 2.1 | **Tags:** #user
Action hook fired during WordPress processing.

### lostpassword_post
**Params:** WP_Error $errors, WP_User|false $user_data
**Since:** 2.1 | **Tags:** #post #user
Action hook fired during WordPress processing.

### register_form
**Since:** 2.1 | **Tags:** #general
Fires when an item is registered.

### register_post
**Since:** 2.1 | **Tags:** #post
Fires when an item is registered.

### retrieve_password_key
**Since:** 2.5 | **Tags:** #user
Action hook fired during WordPress processing.

### set_auth_cookie
**Since:** 2.5 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_login_failed
**Since:** 2.5 | **Tags:** #user
Action hook fired during WordPress processing.

### set_logged_in_cookie
**Since:** 2.6 | **Tags:** #general
Action hook fired during WordPress processing.

### auth_cookie_bad_hash
**Since:** 2.7 | **Tags:** #user
Action hook fired during WordPress processing.

### auth_cookie_bad_username
**Since:** 2.7 | **Tags:** #user
Action hook fired during WordPress processing.

### auth_cookie_expired
**Since:** 2.7 | **Tags:** #user
Action hook fired during WordPress processing.

### auth_cookie_malformed
**Since:** 2.7 | **Tags:** #user
Action hook fired during WordPress processing.

### auth_cookie_valid
**Since:** 2.7 | **Tags:** #user
Action hook fired during WordPress processing.

### clear_auth_cookie
**Since:** 2.7 | **Tags:** #user
Action hook fired during WordPress processing.

### edit_user_profile_update
**Since:** 2.7 | **Tags:** #user #update
Fires when the related item is edited or updated.

### personal_options
**Since:** 2.7 | **Tags:** #options
Action hook fired during WordPress processing.

### deleted_user
**Since:** 2.8 | **Tags:** #user
Fires when the related item is deleted.

### login_form_{$action}
**Since:** 2.8 | **Tags:** #variable #user
Action hook fired during WordPress processing.

### user_profile_update_errors
**Since:** 2.8 | **Tags:** #user #update
Action hook fired during WordPress processing.

### deleted_usermeta
**Since:** 2.9 | **Tags:** #user
Fires when the related item is deleted.

### delete_usermeta
**Since:** 2.9 | **Tags:** #user
Fires when the related item is deleted.

### set_user_role
**Since:** 2.9 | **Tags:** #user
Action hook fired during WordPress processing.

### granted_super_admin
**Since:** 3.0 | **Tags:** #admin
Action hook fired during WordPress processing.

### grant_super_admin
**Since:** 3.0 | **Tags:** #admin
Action hook fired during WordPress processing.

### make_ham_user
**Since:** 3.0 | **Tags:** #user
Action hook fired during WordPress processing.

### make_spam_user
**Since:** 3.0 | **Tags:** #user
Action hook fired during WordPress processing.

### pre_user_search
**Since:** 3.0 | **Tags:** #user
Fires before the related action is processed.

### revoked_super_admin
**Since:** 3.0 | **Tags:** #admin
Action hook fired during WordPress processing.

### revoke_super_admin
**Since:** 3.0 | **Tags:** #admin
Action hook fired during WordPress processing.

### user_edit_form_tag
**Since:** 3.0 | **Tags:** #user #taxonomy
Action hook fired during WordPress processing.

### user_new_form_tag
**Since:** 3.0 | **Tags:** #user #taxonomy
Action hook fired during WordPress processing.

### login_enqueue_scripts
**Since:** 3.1 | **Tags:** #user #assets
Fires when scripts and styles are being enqueued.

### login_footer
**Since:** 3.1 | **Tags:** #user
Action hook fired during WordPress processing.

### pre_user_query
**Since:** 3.1 | **Tags:** #user
Fires before the related action is processed.

### user_admin_menu
**Since:** 3.1 | **Tags:** #user #admin #menu
Action hook fired during WordPress processing.

### user_admin_notices
**Since:** 3.1 | **Tags:** #user #admin
Action hook fired during WordPress processing.

### wp_user_dashboard_setup
**Since:** 3.1 | **Tags:** #user #admin
Action hook fired during WordPress processing.

### login_init
**Since:** 3.2 | **Tags:** #user
Action hook fired during WordPress processing.

### validate_password_reset
**Since:** 3.5 | **Tags:** #user
Action hook fired during WordPress processing.

### user_new_form
**Since:** 3.7 | **Tags:** #user
Action hook fired during WordPress processing.

### resetpass_form
**Since:** 3.9 | **Tags:** #general
Action hook fired during WordPress processing.

### auth_cookie_bad_session_token
**Since:** 4.0 | **Tags:** #user
Action hook fired during WordPress processing.

### delete_user_form
**Since:** 4.0 | **Tags:** #user
Fires when the related item is deleted.

### add_user_role
**Since:** 4.3 | **Tags:** #user
Fires when a new item is added.

### remove_user_role
**Since:** 4.3 | **Tags:** #user
Action hook fired during WordPress processing.

### after_password_reset
**Since:** 4.4 | **Tags:** #user
Action hook fired during WordPress processing.

### clean_user_cache
**Since:** 4.4 | **Tags:** #user #options
Fires when the related cache is cleaned.

### edit_user_created_user
**Since:** 4.4 | **Tags:** #user
Fires when the related item is edited or updated.

### register_new_user
**Since:** 4.4 | **Tags:** #user
Fires when an item is registered.

### login_header
**Since:** 4.6 | **Tags:** #user
Action hook fired during WordPress processing.

### user_request_action_confirmed
**Since:** 5.0 | **Tags:** #user
Action hook fired during WordPress processing.

### application_password_did_authenticate
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### application_password_failed_authentication
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_authenticate_application_password_errors
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_authorize_application_password_form
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_authorize_application_password_request_errors
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_create_application_password
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_create_application_password_form
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_delete_application_password
**Since:** 5.6 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_update_application_password
**Since:** 5.6 | **Tags:** #user #update
Action hook fired during WordPress processing.

### wp_authorize_application_password_form_approved_no_js
**Since:** 5.7 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_set_password
**Since:** 6.2 | **Tags:** #user
Action hook fired during WordPress processing.

### wp_update_user
**Since:** 6.3 | **Tags:** #user #update
Action hook fired during WordPress processing.

