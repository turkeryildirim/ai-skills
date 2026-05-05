# WordPress Actions: Comment

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### comment_post
**Params:** int $comment_id, int|string $comment_approved
**Since:** 1.2.1 | **Tags:** #post #comment
Fires immediately after a comment is inserted into the database.

### delete_comment
**Params:** int $comment_id
**Since:** 1.2.1 | **Tags:** #comment
Fires immediately before a comment is deleted.

### trackback_post
**Params:** int $comment_id
**Since:** 1.2.1 | **Tags:** #post #comment
Fires after a trackback is added to a post.

### comment_closed
**Params:** int $comment_post_id
**Since:** 1.5.2 | **Tags:** #comment
Fires when a comment is attempted on a post with closed comments.

### comment_flood_trigger
**Since:** 1.5.2 | **Tags:** #comment
Fires when a comment flood is detected.

### comment_form
**Params:** int $post_id
**Since:** 1.5.2 | **Tags:** #comment
Fires at the bottom of the comment form. Used to add form fields or content.

### comment_id_not_found
**Params:** int $comment_post_id
**Since:** 1.5.2 | **Tags:** #comment
Fires when a comment is attempted on a non-existent post.

### comment_on_draft
**Params:** int $comment_post_id
**Since:** 1.5.2 | **Tags:** #comment
Fires when a comment is attempted on a draft post.

### pingback_post
**Params:** int $comment_id
**Since:** 1.5.2 | **Tags:** #post #comment
Fires after a pingback is added to a post.

### wp_set_comment_status
**Params:** int $comment_id, string $status
**Since:** 1.5.2 | **Tags:** #comment
Fires immediately after a comment status is changed.

### commentrss2_item
**Since:** 2.1 | **Tags:** #comment #feed
Fires during comment-related processing.

### comment_atom_entry
**Since:** 2.2 | **Tags:** #comment #feed
Fires during comment-related processing.

### comment_loop_start
**Since:** 2.2 | **Tags:** #comment
Fires during comment-related processing.

### check_comment_flood
**Since:** 2.3 | **Tags:** #comment
Fires during comment-related processing.

### commentsrss2_head
**Since:** 2.3 | **Tags:** #comment #feed
Fires during comment-related processing.

### wp_update_comment_count
**Since:** 2.3 | **Tags:** #comment #update
Fires during comment-related processing.

### akismet_spam_caught
**Since:** 2.5 | **Tags:** #general
Action hook fired during WordPress processing.

### comment_{$new_status}_{$comment->comment_type}
**Since:** 2.7 | **Tags:** #variable #comment
Fires during comment-related processing.

### comment_{$old_status}_to_{$new_status}
**Since:** 2.7 | **Tags:** #variable #comment
Fires during comment-related processing.

### transition_comment_status
**Params:** string $new_status, string $old_status, WP_Comment $comment
**Since:** 2.7 | **Tags:** #comment
Fires when a comment transitions between statuses.

### comments_atom_head
**Since:** 2.8 | **Tags:** #comment #feed
Fires during comment-related processing.

### pre_comment_on_post
**Since:** 2.8 | **Tags:** #post #comment
Fires before the related action is processed.

### wp_insert_comment
**Since:** 2.8 | **Tags:** #comment
Fires during comment-related processing.

### comment_on_trash
**Since:** 2.9 | **Tags:** #comment
Fires during comment-related processing.

### deleted_comment
**Since:** 2.9 | **Tags:** #comment
Fires when the related item is deleted.

### spammed_comment
**Since:** 2.9 | **Tags:** #comment
Fires during comment-related processing.

### spam_comment
**Since:** 2.9 | **Tags:** #comment
Fires during comment-related processing.

### trashed_comment
**Since:** 2.9 | **Tags:** #comment
Fires when the related item is trashed.

### trash_comment
**Since:** 2.9 | **Tags:** #comment
Fires when the related item is trashed.

### unspammed_comment
**Since:** 2.9 | **Tags:** #comment
Fires during comment-related processing.

### unspam_comment
**Since:** 2.9 | **Tags:** #comment
Fires during comment-related processing.

### untrashed_comment
**Since:** 2.9 | **Tags:** #comment
Fires when the related item is restored from trash.

### untrash_comment
**Since:** 2.9 | **Tags:** #comment
Fires when the related item is restored from trash.

### comment_duplicate_trigger
**Since:** 3.0 | **Tags:** #comment
Fires during comment-related processing.

### comment_form_after
**Since:** 3.0 | **Tags:** #comment
Fires during comment-related processing.

### comment_form_after_fields
**Since:** 3.0 | **Tags:** #comment
Fires after the related operation is completed.

### comment_form_before
**Since:** 3.0 | **Tags:** #comment
Fires during comment-related processing.

### comment_form_before_fields
**Since:** 3.0 | **Tags:** #comment
Fires before the related operation is performed.

### comment_form_comments_closed
**Since:** 3.0 | **Tags:** #comment
Fires during comment-related processing.

### comment_form_logged_in_after
**Since:** 3.0 | **Tags:** #comment
Fires during comment-related processing.

### comment_form_must_log_in_after
**Since:** 3.0 | **Tags:** #comment
Fires during comment-related processing.

### comment_form_top
**Since:** 3.0 | **Tags:** #comment
Fires during comment-related processing.

### comment_on_password_protected
**Since:** 3.0 | **Tags:** #comment #user
Fires during comment-related processing.

### akismet_submit_nonspam_comment
**Since:** 3.1 | **Tags:** #comment
Fires during comment-related processing.

### akismet_submit_spam_comment
**Since:** 3.1 | **Tags:** #comment
Fires during comment-related processing.

### comment_add_author_url
**Since:** 3.4 | **Tags:** #comment #user
Fires during comment-related processing.

### comment_remove_author_url
**Since:** 3.4 | **Tags:** #comment #user
Fires during comment-related processing.

### set_comment_cookies
**Params:** WP_Comment $comment, WP_User $user, bool $cookies_consent
**Since:** 3.4 | **Tags:** #comment
Fires during comment-related processing.

### akismet_comment_check_response
**Since:** 3.6 | **Tags:** #comment
Fires during comment-related processing.

### akismet_https_disabled
**Since:** 4.2 | **Tags:** #general
Action hook fired during WordPress processing.

### akismet_https_request_failure
**Since:** 4.2 | **Tags:** #general
Action hook fired during WordPress processing.

### akismet_https_request_pre
**Since:** 4.2 | **Tags:** #general
Action hook fired during WordPress processing.

### akismet_http_request_pre
**Since:** 4.2 | **Tags:** #general
Action hook fired during WordPress processing.

### akismet_request_failure
**Since:** 4.2 | **Tags:** #general
Action hook fired during WordPress processing.

### akismet_scheduled_recheck
**Since:** 4.2 | **Tags:** #cron
Action hook fired during WordPress processing.

### akismet_ssl_disabled
**Since:** 4.2 | **Tags:** #general
Action hook fired during WordPress processing.

### parse_comment_query
**Since:** 4.2 | **Tags:** #comment
Fires during comment-related processing.

### clean_comment_cache
**Since:** 4.5 | **Tags:** #comment #options
Fires when the related cache is cleaned.

### pre_trackback_post
**Since:** 4.7 | **Tags:** #post #comment
Fires before the related action is processed.

### akismet_delete_commentmeta_batch
**Since:** 4.8 | **Tags:** #comment
Fires during comment-related processing.

### akismet_delete_comment_batch
**Since:** 4.8 | **Tags:** #comment
Fires during comment-related processing.

### akismet_batch_delete_count
**Since:** 5.0 | **Tags:** #general
Action hook fired during WordPress processing.

### wp_check_comment_disallowed_list
**Since:** 5.5 | **Tags:** #comment
Fires during comment-related processing.

### comment_reply_to_unapproved_comment
**Since:** 6.2 | **Tags:** #comment
Fires during comment-related processing.

### akismet_webhook_received
**Since:** 6.5 | **Tags:** #general
Action hook fired during WordPress processing.

