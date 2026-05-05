# WordPress Actions: Media

> Non-deprecated action hooks for WordPress 6.9+, organized by functional category.
> Full list: https://adambrown.info/p/wp_hooks/hook/actions

---

### add_attachment
**Params:** int $post_id
**Since:** 2.0 | **Tags:** #media
Fires once an attachment has been added to the database.

### delete_attachment
**Params:** int $post_id, WP_Post $post
**Since:** 2.0 | **Tags:** #media
Fires before an attachment is deleted.

### edit_attachment
**Params:** int $post_id
**Since:** 2.0 | **Tags:** #media
Fires once an existing attachment has been updated.

### media_buttons
**Since:** 2.5 | **Tags:** #media
Action hook fired during WordPress processing.

### media_upload_{$tab}
**Since:** 2.5 | **Tags:** #variable #media
Action hook fired during WordPress processing.

### media_upload_{$type}
**Since:** 2.5 | **Tags:** #variable #media
Action hook fired during WordPress processing.

### post-html-upload-ui
**Since:** 2.6 | **Tags:** #post #media
Action hook fired during WordPress processing.

### post-upload-ui
**Since:** 2.6 | **Tags:** #post #media
Action hook fired during WordPress processing.

### pre-html-upload-ui
**Since:** 2.6 | **Tags:** #media
Action hook fired during WordPress processing.

### pre-upload-ui
**Since:** 2.6 | **Tags:** #media
Action hook fired during WordPress processing.

### begin_fetch_post_thumbnail_html
**Since:** 2.9 | **Tags:** #post
Action hook fired during WordPress processing.

### end_fetch_post_thumbnail_html
**Since:** 2.9 | **Tags:** #post
Action hook fired during WordPress processing.

### post-plupload-upload-ui
**Since:** 3.3 | **Tags:** #post #media
Action hook fired during WordPress processing.

### pre-plupload-upload-ui
**Since:** 3.3 | **Tags:** #media
Action hook fired during WordPress processing.

### attachment_submitbox_misc_actions
**Since:** 3.5 | **Tags:** #media
Action hook fired during WordPress processing.

### print_media_templates
**Since:** 3.5 | **Tags:** #theme #media
Action hook fired during WordPress processing.

### upload_ui_over_quota
**Since:** 3.5 | **Tags:** #media
Action hook fired during WordPress processing.

### wp_enqueue_media
**Since:** 3.5 | **Tags:** #media #assets
Fires when assets are being enqueued.

### wp_playlist_scripts
**Since:** 3.9 | **Tags:** #assets
Action hook fired during WordPress processing.

### wp_ajax_crop_image_pre_save
**Since:** 4.3 | **Tags:** #media
Fires when an AJAX action is handled for authenticated users.

### attachment_updated
**Since:** 4.4 | **Tags:** #media #update
Action hook fired during WordPress processing.

### wp_media_attach_action
**Since:** 5.5 | **Tags:** #media
Action hook fired during WordPress processing.

