# WooCommerce Variable Hooks Reference

> WooCommerce hooks with dynamic names. These hooks contain `$VARIABLE` patterns resolved at runtime.
> The actual hook name is determined by context (product type, order status, gateway ID, etc.).

---

## Understanding Variable Hooks

Variable hooks have names that change based on runtime context. WooCommerce uses several patterns:

- `$THIS->PROPERTY` — Instance property of the current object (e.g., `$THIS->ID`, `$THIS->POST_TYPE`)
- `$PRODUCT->GET_TYPE` — Product type from the product object
- `$THIS->ORDER_TYPE` — Order type (shop_order, shop_order_refund)
- `$THIS->OBJECT_TYPE` — Data object type
- `$THIS->EXPORT_TYPE` — Export type (product, order, customer)
- `$THIS->SCREEN_ID` — Admin screen identifier
- `$COLUMN_ID` / `$KEY` — Dynamic column or field identifiers
- `$STATUS_TRANSITION` — Order status transition values

```php
// The hook name is built dynamically:
do_action( "woocommerce_order_status_{$status_transition['to']}", $order_id, $order );

// For a transition to "processing", this becomes:
do_action( 'woocommerce_order_status_processing', $order_id, $order );

// For a specific status transition:
do_action( 'woocommerce_order_status_pending_to_processing', $order_id, $order );
```

---

## Order Status Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_order_status_$STATUS_TRANSITION[to]` | `woocommerce_order_status_processing` | Action | Fires when order transitions to a specific status |
| `woocommerce_order_status_$STATUS_TRANSITION[from]_to_$STATUS_TRANSITION[to]` | `woocommerce_order_status_pending_to_processing` | Action | Fires for a specific status transition |
| `woocommerce_payment_complete_order_status_$THIS->GET_STATUS` | `woocommerce_payment_complete_order_status_processing` | Filter | Filter order status on payment complete |
| `woocommerce_receipt_$ORDER->GET_PAYMENT_METHOD` | `woocommerce_receipt_bacs` | Action | Fires on receipt page for specific payment method |
| `woocommerce_thankyou_$ORDER->GET_PAYMENT_METHOD` | `woocommerce_thankyou_bacs` | Action | Fires on thankyou page for specific payment method |

## Product Type Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_$PRODUCT_TYPE_add_to_cart` | `woocommerce_simple_add_to_cart` | Action | Renders add-to-cart button for product type |
| `woocommerce_$PRODUCT->GET_TYPE_add_to_cart` | `woocommerce_simple_add_to_cart` | Action | Renders add-to-cart button for product type (instance) |
| `__experimental_woocommerce_$PRODUCT_TYPE_add_to_cart_with_options_block_template_part` | — | Filter | Block template part for product type add-to-cart |
| `woocommerce_process_product_meta_$PRODUCT_TYPE` | `woocommerce_process_product_meta_simple` | Action | Save custom product meta for specific product type |
| `woocommerce_add_to_cart_handler_$ADD_TO_CART_HANDLER` | `woocommerce_add_to_cart_handler_simple` | Action | Custom add-to-cart handler |

## Data Object Variable Hooks (WC_Data)

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `WC_DATA->GET_HOOK_PREFIX$KEY` | `woocommerce_product_get_price` | Filter | Getter hook for WC_Data property |
| `WC_DATA->GET_HOOK_PREFIX$PROP` | `woocommerce_product_get_sku` | Filter | Getter hook for WC_Data property (alt) |
| `WC_ORDER->GET_HOOK_PREFIX$ADDRESS_TYPE_$PROP` | `woocommerce_order_get_billing_first_name` | Filter | Order address property getter |
| `WC_CUSTOMER->GET_HOOK_PREFIX$PROP` | `woocommerce_customer_get_first_name` | Filter | Customer property getter |
| `WC_CUSTOMER->GET_HOOK_PREFIX$ADDRESS_TYPE_$PROP` | `woocommerce_customer_get_billing_first_name` | Filter | Customer address property getter |
| `woocommerce_after_$THIS->OBJECT_TYPE_object_save` | `woocommerce_after_product_object_save` | Action | Fires after saving WC data object |
| `woocommerce_before_$THIS->OBJECT_TYPE_object_save` | `woocommerce_before_product_object_save` | Action | Fires before saving WC data object |
| `woocommerce_pre_delete_$THIS->OBJECT_TYPE` | `woocommerce_pre_delete_product` | Filter | Pre-filter before deleting data object |

## Meta Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `added_$THIS->OBJECT_TYPE_meta` | `added_product_meta` | Action | Fires after adding meta for object type |
| `updated_$THIS->OBJECT_TYPE_meta` | `updated_product_meta` | Action | Fires after updating meta for object type |
| `deleted_$THIS->OBJECT_TYPE_meta` | `deleted_product_meta` | Action | Fires after deleting meta for object type |
| `woocommerce_data_store_wp_$THIS->META_TYPE_read_meta` | — | Filter | Filter meta read for data store |

## Email Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_email_recipient_$THIS->ID` | `woocommerce_email_recipient_customer_processing_order` | Filter | Filter recipient for specific email type |
| `woocommerce_email_subject_$THIS->ID` | `woocommerce_email_subject_customer_processing_order` | Filter | Filter subject for specific email type |
| `woocommerce_email_heading_$THIS->ID` | `woocommerce_email_heading_customer_processing_order` | Filter | Filter heading for specific email type |
| `woocommerce_email_enabled_$THIS->ID` | `woocommerce_email_enabled_customer_processing_order` | Filter | Enable/disable specific email type |
| `woocommerce_email_additional_content_$THIS->ID` | `woocommerce_email_additional_content_customer_processing_order` | Filter | Filter additional content for email type |
| `woocommerce_email_bcc_recipient_$THIS->ID` | — | Filter | Filter BCC recipient for email type |
| `woocommerce_email_cc_recipient_$THIS->ID` | — | Filter | Filter CC recipient for email type |
| `woocommerce_email_preheader$THIS->ID` | — | Filter | Filter preheader text for email type |
| `woocommerce_email_setting_column_$KEY` | — | Action | Render email setting column value |
| `woocommerce_email_downloads_column_$COLUMN_ID` | — | Action | Render downloads column in email |

## REST API Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_rest_$THIS->POST_TYPE_query` | `woocommerce_rest_product_query` | Filter | Filter REST query args for post type |
| `woocommerce_rest_$THIS->POST_TYPE_object_query` | `woocommerce_rest_product_object_query` | Filter | Filter REST object query args |
| `woocommerce_rest_$THIS->POST_TYPE_trashable` | `woocommerce_rest_product_trashable` | Filter | Filter whether post type is trashable via REST |
| `woocommerce_rest_$THIS->POST_TYPE_object_trashable` | `woocommerce_rest_product_object_trashable` | Filter | Filter whether object is trashable via REST |
| `woocommerce_rest_insert_$THIS->POST_TYPE` | `woocommerce_rest_insert_product` | Action | Fires after inserting post type via REST |
| `woocommerce_rest_insert_$THIS->POST_TYPE_object` | `woocommerce_rest_insert_product_object` | Action | Fires after inserting object via REST |
| `woocommerce_rest_delete_$THIS->POST_TYPE` | `woocommerce_rest_delete_product` | Action | Fires after deleting post type via REST |
| `woocommerce_rest_delete_$THIS->POST_TYPE_object` | `woocommerce_rest_delete_product_object` | Action | Fires after deleting object via REST |
| `woocommerce_rest_prepare_$THIS->POST_TYPE` | `woocommerce_rest_prepare_product` | Filter | Filter REST response for post type |
| `woocommerce_rest_prepare_$THIS->POST_TYPE_object` | `woocommerce_rest_prepare_product_object` | Filter | Filter REST response for object |
| `woocommerce_rest_prepare_$THIS->TAXONOMY` | `woocommerce_rest_prepare_product_cat` | Filter | Filter REST response for taxonomy |
| `woocommerce_rest_pre_insert_$THIS->POST_TYPE` | `woocommerce_rest_pre_insert_product` | Filter | Filter data before REST insert |
| `woocommerce_rest_pre_insert_$THIS->POST_TYPE_object` | `woocommerce_rest_pre_insert_product_object` | Filter | Filter object data before REST insert |
| `woocommerce_rest_$OBJECT_TYPE_schema` | `woocommerce_rest_product_schema` | Filter | Filter REST schema for object type |
| `woocommerce_rest_$TAXONOMY_query` | `woocommerce_rest_product_cat_query` | Filter | Filter REST query args for taxonomy |
| `woocommerce_rest_query_var-$VAR` | — | Filter | Filter REST query variable |
| `rest_$THIS->GET_OBJECT_TYPE_additional_fields` | — | Filter | Additional fields for REST object type |
| `rest_$THIS->POST_TYPE_collection_params` | `rest_product_collection_params` | Filter | Collection params for REST post type |

## Admin & Settings Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_get_sections_$THIS->ID` | `woocommerce_get_sections_general` | Filter | Get sections for settings page |
| `woocommerce_get_settings_$THIS->ID` | `woocommerce_get_settings_general` | Filter | Get settings for settings page |
| `woocommerce_settings_api_form_fields_$THIS->ID` | — | Filter | Filter form fields for settings API |
| `woocommerce_settings_api_sanitized_fields_$THIS->ID` | — | Filter | Filter sanitized settings fields |
| `woocommerce_save_settings_$CURRENT_TAB` | `woocommerce_save_settings_general` | Filter | Filter save action for settings tab |
| `woocommerce_save_settings_$CURRENT_TAB_$CURRENT_SECTION` | `woocommerce_save_settings_general_tax` | Filter | Filter save for settings tab + section |
| `woocommerce_settings-$GROUP_ID` | — | Filter | Filter settings group |
| `woocommerce_update_options_$CURRENT_TAB` | `woocommerce_update_options_general` | Action | Save settings for tab |
| `woocommerce_update_options_$THIS->ID_$SECTION_ID` | — | Action | Save settings for gateway section |
| `woocommerce_update_options_payment_gateways_$GATEWAY->ID` | — | Action | Save payment gateway settings |
| `woocommerce_settings_tabs_$CURRENT_TAB` | `woocommerce_settings_tabs_general` | Action | Render settings tab |
| `woocommerce_sections_$CURRENT_TAB` | `woocommerce_sections_general` | Action | Render settings section |
| `woocommerce_settings_$CURRENT_TAB` | `woocommerce_settings_general` | Action | Render settings page content |
| `woocommerce_before_settings_$CURRENT_TAB` | — | Action | Before settings tab content |
| `woocommerce_after_settings_$CURRENT_TAB` | — | Action | After settings tab content |
| `woocommerce_admin_field_$VALUE[type]` | — | Action | Render custom admin field type |
| `woocommerce_admin_settings_sanitize_option_$OPTION_NAME` | — | Filter | Sanitize specific admin option |
| `woocommerce_admin_order_preview_line_item_column_sanitize_key$COLUMN` | — | Filter | Order preview line item column value |
| `woocommerce_admin_status_content_$CURRENT_TAB` | — | Action | Render admin status tab content |
| `woocommerce_settings_form_method_tab_$CURRENT_TAB` | — | Filter | Form method for settings tab |
| `woocommerce_settings_sanitize_title$VALUE[id]` | — | Action | Settings sanitize for field |
| `woocommerce_settings_sanitize_title$VALUE[id]_after` | — | Action | After settings sanitize for field |
| `woocommerce_settings_sanitize_title$VALUE[id]_end` | — | Action | End settings sanitize for field |
| `woocommerce_settings_save_$CURRENT_TAB` | — | Action | Save settings for tab |
| `add_meta_boxes_$THIS->SCREEN_ID` | — | Action | Register meta boxes for admin screen |
| `manage_$THIS->SCREEN->ID_custom_column` | — | Action | Custom column for admin screen |
| `handle_bulk_actions-$SCREEN` | — | Filter | Handle bulk actions for screen |

## Order List Table Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_$THIS->ORDER_TYPE_list_table_columns` | — | Filter | Columns for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_css_classes` | — | Filter | CSS classes for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_custom_column` | — | Action | Custom column for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_default_statuses` | — | Filter | Default statuses for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_disable_months_filter` | — | Filter | Disable months filter for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_order_count` | — | Filter | Order count for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_order_css_classes` | — | Filter | CSS classes for orders in list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_prepare_items_query_args` | — | Filter | Query args for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_request` | — | Filter | Request params for order list table |
| `woocommerce_$THIS->ORDER_TYPE_list_table_should_render_blank_state` | — | Filter | Whether to render blank state |
| `woocommerce_$THIS->ORDER_TYPE_list_table_sortable_columns` | — | Filter | Sortable columns for order list table |
| `woocommerce_before_$THIS->ORDER_TYPE_list_table_view_links` | — | Filter | View links for order list table |

## Export Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_$THIS->EXPORT_TYPE_export_batch_limit` | — | Filter | Batch limit for export type |
| `woocommerce_$THIS->EXPORT_TYPE_export_column_names` | — | Filter | Column names for export type |
| `woocommerce_$THIS->EXPORT_TYPE_export_delimiter` | — | Filter | Delimiter for export type |
| `woocommerce_$THIS->EXPORT_TYPE_export_get_filename` | — | Filter | Filename for export type |
| `woocommerce_$THIS->EXPORT_TYPE_export_rows` | — | Filter | Export rows for export type |
| `woocommerce_export_$THIS->EXPORT_TYPE_column_$COLUMN_NAME` | — | Filter | Export column value |
| `woocommerce_export_$THIS->EXPORT_TYPE_row_data` | — | Filter | Export row data |
| `woocommerce_product_export_$THIS->EXPORT_TYPE_column_$COLUMN_ID` | — | Filter | Product export column value |
| `woocommerce_product_export_$THIS->EXPORT_TYPE_default_columns` | — | Filter | Product export default columns |
| `woocommerce_product_export_$THIS->EXPORT_TYPE_query_args` | — | Filter | Product export query args |

## Shipping Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_$THIS->ID_instance_option` | — | Filter | Shipping instance option |
| `woocommerce_$THIS->ID_instance_settings_values` | — | Filter | Shipping instance settings values |
| `woocommerce_$THIS->ID_is_available` | — | Filter | Whether shipping method is available |
| `woocommerce_$THIS->ID_option` | — | Filter | Shipping method option |
| `woocommerce_$THIS->ID_shipping_add_rate` | — | Action | Add shipping rate for method |
| `woocommerce_shipping_$THIS->ID_instance_option` | — | Filter | Shipping instance option (alt) |
| `woocommerce_shipping_$THIS->ID_instance_settings_values` | — | Filter | Shipping instance settings (alt) |
| `woocommerce_shipping_$METHOD->ID_instance_settings_values` | — | Filter | Shipping method instance settings |
| `woocommerce_shipping_instance_form_fields_$THIS->ID` | — | Filter | Form fields for shipping instance |
| `woocommerce_shipping_classes_column_$CLASS` | — | Action | Render shipping class column |
| `woocommerce_shipping_providers_column_$CLASS` | — | Action | Render shipping provider column |

## Payment Gateway Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_gateway_$GATEWAY->ID_settings_values` | — | Filter | Payment gateway settings values |
| `woocommerce_update_option_sanitize_title$OPTION[type]` | — | Action | Sanitize gateway option on update |

## Analytics Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_analytics_$FIELD` | — | Filter | Analytics field value |
| `woocommerce_analytics_$SNAKE_NAME_query_args` | — | Filter | Analytics query args |
| `woocommerce_analytics_$SNAKE_NAME_select_query` | — | Filter | Analytics select query |
| `woocommerce_analytics_$THIS->CONTEXT_query_args` | — | Filter | Analytics context query args |
| `woocommerce_analytics_$THIS->CONTEXT_select_query` | — | Filter | Analytics context select query |
| `woocommerce_analytics_clauses_$TYPE` | — | Filter | Analytics clauses by type |
| `woocommerce_analytics_clauses_$TYPE_$THIS->CONTEXT` | — | Filter | Analytics clauses by type and context |
| `woocommerce_analytics_orderby_enum_$THIS->REST_BASE` | — | Filter | Analytics orderby enum |

## Account & My Account Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_account_$KEY_endpoint` | `woocommerce_account_orders_endpoint` | Action | Render my account endpoint |
| `woocommerce_account_downloads_column_$COLUMN_ID` | — | Action | Render downloads column |
| `woocommerce_account_payment_methods_column_$COLUMN_ID` | — | Action | Render payment methods column |
| `woocommerce_endpoint_$ENDPOINT_title` | `woocommerce_endpoint_orders_title` | Filter | Filter endpoint title |
| `woocommerce_my_account_my_orders_column_$COLUMN_ID` | — | Action | Render my orders column |
| `woocommerce_before_edit_address_form_$LOAD_ADDRESS` | — | Action | Before edit address form |
| `woocommerce_after_edit_address_form_$LOAD_ADDRESS` | — | Action | After edit address form |

## Checkout Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `default_checkout_$INPUT` | `default_checkout_billing_country` | Filter | Default checkout field value |
| `woocommerce_process_checkout_$TYPE_field` | — | Filter | Process checkout field by type |
| `woocommerce_process_checkout_field_$KEY` | — | Filter | Process specific checkout field |
| `woocommerce_process_myaccount_field_$KEY` | — | Filter | Process my account field |

## Post Type & Taxonomy Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_delete_$POST_TYPE` | `woocommerce_delete_product` | Action | Fires before deleting WooCommerce post type |
| `woocommerce_before_delete_$POST_TYPE` | — | Action | Before deleting WooCommerce post type |
| `woocommerce_trash_$POST_TYPE` | `woocommerce_trash_product` | Action | Fires on trashing WooCommerce post type |
| `woocommerce_process_$POST->POST_TYPE_meta` | — | Action | Process meta for post type |
| `woocommerce_$OBJECT_TYPE_data_store` | `woocommerce_product_data_store` | Filter | Data store class for object type |
| `woocommerce_taxonomy_args_$NAME` | — | Filter | Taxonomy registration arguments |
| `woocommerce_taxonomy_args_$TAXONOMY_NAME` | — | Filter | Taxonomy args by name |
| `woocommerce_taxonomy_args_$TERM[domain]` | — | Filter | Taxonomy args by term domain |
| `woocommerce_taxonomy_objects_$NAME` | — | Filter | Object types for taxonomy |
| `woocommerce_taxonomy_objects_$TAXONOMY_NAME` | — | Filter | Object types by taxonomy name |
| `woocommerce_taxonomy_objects_$TERM[domain]` | — | Filter | Object types by term domain |

## Product Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_product_$KEY_tab_title` | `woocommerce_product_description_tab_title` | Filter | Product tab title |
| `woocommerce_grouped_product_list_column_$COLUMN_ID` | — | Filter | Grouped product column value |
| `woocommerce_grouped_product_list_after_$COLUMN_ID` | — | Action | After grouped product column |
| `woocommerce_grouped_product_list_before_$COLUMN_ID` | — | Action | Before grouped product column |
| `woocommerce_product_reviews_table_column_$COLUMN_NAME` | — | Action | Product reviews table column |
| `woocommerce_product_reviews_table_column_$COLUMN_NAME_content` | — | Filter | Product reviews column content |
| `woocommerce_product_export_$THIS->EXPORT_TYPE_column_$COLUMN_ID` | — | Filter | Product export column value |
| `woocommerce_store_api_product_quantity_$VALUE_TYPE` | — | Filter | Store API product quantity |

## Template & Rendering Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_$TYPEfields` | — | Filter | Filter fields by type |
| `woocommerce_shortcode_$THIS->TYPE_loop_no_results` | — | Action | Shortcode loop no results |
| `woocommerce_shortcode_after_$THIS->TYPE_loop` | — | Action | After shortcode loop |
| `woocommerce_shortcode_before_$THIS->TYPE_loop` | — | Action | Before shortcode loop |
| `woocommerce_generate_$TYPE_html` | — | Filter | Generate HTML for type |
| `woocommerce_form_field_$ARGS[type]` | — | Filter | Form field by type |
| `woocommerce_get_image_size_$IMAGE_SIZE` | — | Filter | Image size dimensions |
| `woocommerce_get_$PAGE_page_id` | — | Filter | Page ID for WooCommerce page |
| `woocommerce_get_$PAGE_page_permalink` | — | Filter | Permalink for WooCommerce page |
| `woocommerce_widget_field_$SETTING[type]` | — | Action | Widget field by type |
| `woocommerce_order_item_$ITEM->GET_TYPE_html` | — | Action | Order item HTML by type |
| `woocommerce_before_order_item_$ITEM->GET_TYPE_html` | — | Action | Before order item HTML |
| `woocommerce_download_file_$FILE_DOWNLOAD_METHOD` | — | Action | Download file by method |

## AJAX & API Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `wc_ajax_$ACTION` | `wc_ajax_get_refreshed_fragments` | Action | WooCommerce AJAX handler |
| `woocommerce_api_$API_REQUEST` | — | Action | Legacy API request handler |

## Block Template Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_block_template_area_$THIS->GET_ROOT_TEMPLATE->GET_AREA_after_add_block_$BLOCK->GET_ID` | — | Action | After adding block to template area |
| `woocommerce_block_template_area_$THIS->GET_ROOT_TEMPLATE->GET_AREA_after_remove_block_$BLOCK->GET_ID` | — | Action | After removing block from template area |
| `woocommerce_blocks_$THIS->REGISTRY_IDENTIFIER_registration` | — | Action | Block type registration |
| `woocommerce_blocks_validate_location_$LOCATION_fields` | — | Filter | Validate block location fields |

## Miscellaneous Variable Hooks

| Hook Pattern | Example Usage | Type | Description |
|---|---|---|---|
| `woocommerce_add_$NOTICE_TYPE` | `woocommerce_add_success` | Filter | Filter notice message |
| `woocommerce_hide_$NAME_notice` | — | Action | Hide specific admin notice |
| `woocommerce_note_action_$TRIGGERED_ACTION->NAME` | — | Action | Admin note action |
| `woocommerce_order_action_sanitize_title$ACTION` | — | Action | Order action by name |
| `woocommerce_get_default_value_for_$KEY` | — | Filter | Default value for setting key |
| `woocommerce_get_default_value_for_$MISSING_FIELD` | — | Filter | Default value for missing field |
| `woocommerce_geolocation_geoip_response_$SERVICE_NAME` | — | Filter | Geolocation service response |
| `woocommerce_translations_updates_for_$PLUGINS[$PLUGIN][slug]` | — | Filter | Translation updates for plugin |
| `wp_$BLOG_ID_wc_updater_cron` | — | Action | WooCommerce updater cron for site |
| `$SHORTCODE_shortcode_tag` | — | Filter | Shortcode tag filter |
| `$action` | — | Action | Generic action hook |
| `$filter_name` | — | Filter | Generic filter hook |
| `$hook` | — | Action | Dynamic action hook |
| `$old_hook` | — | Action | Deprecated hook migration |
| `$name` | — | Filter | Dynamic name filter |
| `$tag` | — | Filter | Dynamic tag filter |

Reference: [WooCommerce Code Reference - Hooks](https://woocommerce.github.io/code-reference/hooks/hooks.html)
