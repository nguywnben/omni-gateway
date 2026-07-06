const TRANSLATIONS = {
    en: {
    "app_title": "Omni Gateway",
    "panel_title": "Omni Gateway Management Console",
    "login_subtitle": "Enter your password to access the control panel.",
    "login_placeholder": "Enter password",
    "login_btn": "Sign in",
    "logout_btn": "Logout",
    "version_label": "Version",
    "check_update_btn": "Check for updates",
    "loading_text": "Loading...",
    "mirror_switch_warning": "Mirror reverse proxy setup switches API domains to proxy servers.",
    "copy_success": "Copied to clipboard.",
    "copy_fail": "Copy failed.",
    "btn_close": "Close",
    "btn_cancel": "Cancel",
    "btn_confirm": "Confirm",
    "btn_continue": "Continue",
    "confirm_action_title": "Confirm action",
    "input_required_title": "Input required",
    "dialog_tip": "Tip",
    "error_prefix": "Error: ",
    "tab_oauth": "OAuth auth",
    "tab_primary": "Provider auth",
    "tab_upload": "Batch upload",
    "tab_manage_creds": "Credentials",
    "manage_creds_title": "Credential management",
    "manage_creds_desc": "Select a credential provider to view and manage active API channels.",
    "tab_manage_code_assist": "Code Assist credentials",
    "tab_manage_code_assist_short": "Code Assist creds",
    "tab_manage_provider": "Provider credentials",
    "tab_manage_provider_short": "Provider credentials",
    "tab_config": "System config",
    "tab_logs": "Real-time logs",
    "tab_about": "About project",
    "oauth_banner_title": "Automation enabled:",
    "oauth_banner_text": "The system will detect and enable the required API services after authorization.",
    "oauth_advanced_title": "Advanced: specify Google Cloud Project ID (optional)",
    "oauth_advanced_note": "Leave blank to auto-detect and create project.",
    "oauth_link_btn": "Generate Google OAuth link",
    "oauth_auth_title": "Authorization link:",
    "oauth_auth_instruction": "Open this link to authorize your Google account.",
    "oauth_guide_title": "OAuth Interactive Guide:",
    "oauth_guide_1": "Click the link above, sign in, and grant access in the new tab.",
    "oauth_guide_2": "After the redirect, you may see a connection error at localhost:11451. This is expected.",
    "oauth_guide_3": "Return to this page, then click 'Get and Save Credentials' below.",
    "oauth_guide_4": "For remote servers or VPS without a browser, expand the callback tunnel below.",
    "oauth_callback_title": "No automatic redirect? Use the callback tunnel.",
    "oauth_callback_note": "Suitable for VPS, Docker, or port 11451 blocks.",
    "oauth_callback_instructions": "Copy the full URL from the address bar after redirection, even if the page shows an error, and paste it below.",
    "oauth_callback_btn": "Parse credentials from callback URL",
    "oauth_save_btn": "Get and save credentials",
    "oauth_success_title": "Authentication successful. Saved credentials:",
    "provider_banner_title": "Google provider authentication mode",
    "provider_banner_text": "Obtain Google Cloud SDK native authentication credentials.",
    "provider_link_btn": "Generate provider authorization link",
    "provider_link_title": "Provider authorization link:",
    "provider_link_instruction": "Open this link to authorize the provider credential flow.",
    "provider_guide_title": "Steps:",
    "provider_guide_1": "Click the link above to start Google OAuth authorization.",
    "provider_guide_2": "When the browser redirects to localhost:11451 and shows an error, return to this panel.",
    "provider_guide_3": "Click the button below to retrieve and save credentials directly.",
    "provider_guide_4": "If unable to auto-redirect, copy the final URL and parse it below.",
    "provider_save_btn": "Get and save provider credentials",
    "provider_success_title": "Saved provider credentials:",
    "provider_download_btn": "Download credentials file",
    "upload_title": "Batch upload credentials",
    "upload_desc": "Drag & drop or select JSON/ZIP credentials to upload.",
    "upload_code_assist_title": "Code Assist credential upload",
    "upload_code_assist_area_title": "Click to select or drag files here",
    "upload_code_assist_area_subtitle": "Supports .json or .zip format",
    "upload_code_assist_area_note": "ZIP archives will be automatically extracted to parse JSON credentials.",
    "upload_pending_code_assist": "Pending Code Assist files to upload:",
    "upload_start_btn": "Start upload",
    "upload_clear_btn": "Clear List",
    "upload_progress": "Upload Progress",
    "upload_provider_title": "Provider credential upload",
    "upload_provider_area_title": "Click to select or drag files here",
    "upload_provider_area_subtitle": "Supports .json or .zip format",
    "upload_provider_area_note": "ZIP archives will be extracted to parse provider credentials.",
    "upload_pending_provider": "Pending provider files to upload:",
    "code_assist_manage_title": "Code Assist credential management",
    "code_assist_manage_desc": "View and manage Code Assist API channels (batch verify, toggle, download, delete).",
    "provider_manage_title": "Provider credential management",
    "provider_manage_desc": "View and manage provider accounts and request quotas.",
    "endpoint_banner_title": "API endpoint addresses",
    "endpoint_openai": "OpenAI format:",
    "endpoint_claude": "Claude format:",
    "endpoint_gemini": "Gemini native:",
    "stat_total": "Total credentials",
    "stat_active": "Active",
    "stat_disabled": "Disabled",
    "btn_refresh": "Refresh list",
    "btn_download_all": "Download all (ZIP)",
    "batch_panel_title": "Batch operations",
    "batch_select_all": "Select all",
    "batch_selected_count": "Selected {count} items",
    "batch_enable": "Batch Enable",
    "batch_disable": "Batch Disable",
    "batch_delete": "Batch Delete",
    "batch_verify_id": "Batch verify Project ID",
    "batch_preview_toggle": "Batch toggle preview mode",
    "batch_refresh_emails": "Refresh emails",
    "batch_deduplicate": "Deduplicate by email",
    "batch_enable_credit": "Enable credit mode",
    "batch_disable_credit": "Disable credit mode",
    "filter_status": "Status:",
    "filter_all": "All",
    "filter_status_enabled": "Enabled",
    "filter_status_disabled": "Disabled",
    "filter_error": "Error Code:",
    "filter_error_none": "None",
    "filter_cooldown": "Cooldown:",
    "filter_cooldown_active": "In Cooldown",
    "filter_cooldown_none": "No Cooldown",
    "filter_preview": "Preview:",
    "filter_preview_on": "Preview Enabled",
    "filter_preview_off": "Preview Disabled",
    "filter_tier": "Tier:",
    "filter_per_page": "Per page:",
    "card_enabled": "Enabled",
    "card_disabled": "Disabled",
    "card_no_error": "No error",
    "card_error_code": "Error: {code}",
    "card_no_email": "Email not loaded",
    "card_loading_details": "Loading file content...",
    "card_loading_errors": "Loading error details...",
    "card_loading_quota": "Loading quota details...",
    "btn_card_enable": "Enable",
    "btn_card_disable": "Disable",
    "btn_card_view": "View content",
    "btn_card_download": "Download",
    "btn_card_email": "Email info",
    "btn_card_quota": "Quota details",
    "btn_card_close_credit": "Disable credit",
    "btn_card_open_credit": "Enable credit",
    "btn_card_set_preview": "Set preview",
    "btn_card_verify": "Verify",
    "btn_card_test": "Message test",
    "btn_card_error_details": "View errors",
    "btn_card_delete": "Delete",
    "config_title": "Global system settings",
    "config_desc": "Adjust network proxies, API endpoints, error limits, and retry configurations. Settings take effect immediately upon saving.",
    "btn_save_config": "Save global config",
    "btn_reload_config": "Reload configuration",
    "config_loading": "Syncing configuration settings with the server...",
    "group_network": "Listen and security settings",
    "config_host_label": "Server bind host IP address:",
    "config_host_note": "IP address to listen on (0.0.0.0 listens globally, requires restart).",
    "config_port_label": "Listen Port:",
    "config_port_note": "TCP Port to bind on (requires restart).",
    "config_api_pwd_label": "API access password:",
    "config_api_pwd_note": "Used for Bearer token validation when making proxy requests.",
    "config_panel_pwd_label": "Web panel login password:",
    "config_panel_pwd_note": "Protects this management console page.",
    "config_pwd_label": "Unified password override (optional):",
    "config_pwd_note": "If provided, overrides both API and Panel password. Recommended to leave blank.",
    "group_storage": "Storage and proxy settings",
    "config_storage_label": "Credentials storage path:",
    "config_storage_note": "Absolute path where JSON credentials are saved.",
    "config_proxy_label": "Global outbound proxy URL:",
    "config_proxy_note": "SOCKS5 or HTTP proxy URL for Google endpoints (leave blank for direct connection).",
    "group_endpoints": "API endpoint settings",
    "config_mirror_btn": "Use mirror proxies",
    "config_official_btn": "Restore official Google domains",
    "config_endpoint_code": "Code Assist API endpoint:",
    "config_endpoint_oauth": "OAuth auth endpoint:",
    "config_endpoint_apis": "Google APIs core endpoint:",
    "config_endpoint_resource": "Resource Manager endpoint:",
    "config_endpoint_service": "Service Usage endpoint:",
    "config_endpoint_provider": "Provider API endpoint:",
    "group_ban": "Auto-ban and fuse settings",
    "config_ban_checkbox": "Enable automatic ban/fuse for specified error codes",
    "config_ban_codes_label": "HTTP Error Codes to trigger ban (comma-separated):",
    "config_ban_codes_note": "Accounts receiving these errors will be automatically disabled (403 is highly recommended).",
    "group_retry": "Auto-retry and failover options",
    "config_retry_checkbox": "Automatically retry requests on alternative credentials upon failure",
    "config_retry_count": "Maximum retry attempts:",
    "config_retry_interval": "Interval between retries (seconds):",
    "group_compat": "Model protocol compatibility",
    "config_compat_checkbox": "Force compatibility mode (flattens system instructions into user messages)",
    "config_compat_note": "Solves empty response errors in older client libraries by avoiding system_instructions, with slight prompt quality trade-offs.",
    "config_thinking_checkbox": "Pass-through Gemini 2.0 Reasoning/Thinking process chain in responses",
    "config_thinking_note": "Outputs reasoning block contents for reasoning models. If disabled, trims thinking outputs.",
    "config_provider_stream_checkbox": "Compile provider streaming responses for non-stream clients.",
    "config_provider_retry_checkbox": "Auto-switch alternative credentials on provider request failure",
    "group_trunc": "Truncation recovery options",
    "config_trunc_count": "Max recovery attempts for truncated streams:",
    "config_trunc_note": "Maximum attempts to resume generation if a stream gets cut off (applicable to models suffixed with '-streaming anti-truncation').",
    "group_keepalive": "Application keep-alive settings",
    "config_keepalive_label": "Keep-alive heartbeat URL:",
    "config_keepalive_btn": "Detect and autofill the current keep-alive URL",
    "config_keepalive_interval": "Heartbeat interval (seconds):",
    "logs_title": "System logs console",
    "logs_desc": "Monitor request cycles, rotation decisions, and errors dispatched to Google Cloud APIs.",
    "btn_log_connect": "Connect Log Stream",
    "btn_log_disconnect": "Disconnect Stream",
    "btn_log_save": "Save Logs to File",
    "btn_log_clear": "Clear log window",
    "log_filter_level": "Filter level:",
    "log_scroll_lock": "Auto-scroll to bottom",
    "log_status_label": "WebSocket status:",
    "log_status_text": "Not connected",
    "log_waiting_text": "Awaiting logs from the server...",
    "about_title": "About Omni Gateway",
    "tab_dashboard": "Dashboard",
    "regenerate_keys_btn": "Regenerate Keys",
    "copy_btn": "Copy",
    "confirm_regenerate_key": "Are you sure you want to regenerate this API key? Previous key will become invalid immediately.",
    "regenerate_success": "API keys regenerated successfully.",
    "tooltip_total_calls": "Total number of API requests routed through this gateway in the last 24 hours.",
    "tooltip_total_files": "The number of active Google provider credentials currently configured and monitored.",
    "tooltip_avg_calls": "Average number of API requests processed per credential in the past 24 hours.",
    "api_keys_title": "API Key",
    "api_integration_title": "API Integration",
    "quick_info_title": "Quick Integration Info",
    "info_openai_header": "OpenAI Header:",
    "info_anthropic_header": "Anthropic Header:",
    "info_status": "Service Status:",
    "status_running": "Active",
    "api_key_label": "API Key:",
    "api_connection_title": "API Connection Details",
    "quick_guide_title": "Quick Integration Guide",
    "guide_openai_header": "OpenAI Compatibility:",
    "guide_anthropic_header": "Anthropic Compatibility:",
    "guide_tip_header": "Tips:",
    "guide_tip_content": "Click any field in the connection details card to copy. The single unified key works seamlessly with both OpenAI and Anthropic formatting clients.",
    "openai_key_label": "OpenAI API Key:",
    "anthropic_key_label": "Anthropic API Key:",
    "unified_endpoint_title": "API Integration Endpoint",
    "api_integration_card_title": "API Integration",
    "quick_integration_title": "Quick Integration",
    "integration_openai_title": "OpenAI Compatible Clients:",
    "integration_anthropic_title": "Anthropic Compatible Clients:",
    "integration_url_prefix": "Base URL:",
    "integration_key_prefix": "API Key:",
    "endpoint_base_label": "Base URL:",
    "dashboard_total_calls": "Total Requests (24h)",
    "dashboard_total_calls_desc": "Total number of API requests processed by the gateway in the last 24 hours.",
    "dashboard_total_files_desc": "Total number of active Code Assist and provider credential accounts currently loaded in the database.",
    "dashboard_avg_calls_desc": "Average number of API requests handled per active credential.",
    "dashboard_total_files": "Monitored Credentials",
    "dashboard_avg_calls": "Avg Requests / Credential",
    "dashboard_welcome": "Welcome to the Omni Gateway console. Use the sidebar to switch between management tasks. The system rotates active credentials for load balancing, failover, and retries when upstream rate limits or authorization errors occur.",
    "dashboard_breakdown": "24-Hour Request Breakdown",
    "oauth_desc": "Generate Google Cloud authorization credentials. Supports standard Code Assist OAuth and provider credential export.",
    "about_desc": "Omni Gateway is a universal AI router for coding tools. Features smart auto-fallback, token compression, and seamless format translation to maximize free and premium LLMs.",
    "about_github": "GitHub repository:",
    "about_notice": "Open-source notice: Omni Gateway is released under the MIT License. Review the license terms and attribution requirements before redistribution.",
    "about_features_title": "Key Features",
    "feat_1_title": "Quota Failover Rotation",
    "feat_1_desc": "Seamless failover between accounts prevents 429 quota exhaustion errors.",
    "feat_2_title": "Multi-Protocol Compatibility",
    "feat_2_desc": "Translate System & Thinking protocols bi-directionally without configuration overhead.",
    "feat_3_title": "Auto-Ban Fuse System",
    "feat_3_desc": "Identify and isolate 403 authorization failures dynamically.",
    "feat_4_title": "Anti-Truncation Recovery",
    "feat_4_desc": "Automatically resume aborted streams from point of cutoff.",
    "feat_5_title": "Single File Deployment",
    "feat_5_desc": "Extremely low memory footprint, optimized for PaaS and container engines.",
    "feat_6_title": "Responsive Interface",
    "feat_6_desc": "Responsive web management console following minimal aesthetic conventions.",
    "about_support_title": "Project Support",
    "about_support_desc": "Report bugs, request features, and follow roadmap work through GitHub Issues.",
    "about_support_cta": "Open GitHub Issues",
    "about_feedback_title": "Feedback & Bug Reports",
    "about_feedback_desc": "Report issues or submit feature requests through GitHub Issues. Pull requests are welcome.",
    "auth_fail_relogin": "Authentication failed. Please sign in again.",
    "check_update_info": "Checking for updates...",
    "update_success": "Update check completed.",
    "load_cred_stats": "Loaded stats for {count} credentials",
    "net_error": "Network connection error: {msg}",
    "confirm_delete_cred": "Are you sure you want to delete this credential?\\n{filename}",
    "save_config_success": "System configuration saved successfully.",
    "load_config_success": "System configuration loaded successfully.",
    "log_connected": "Log WebSocket connected.",
    "log_disconnected": "Log WebSocket disconnected.",
    "select_at_least_one": "Please select at least one credential first.",
    "confirm_batch_action": "Are you sure you want to execute {action} on {count} selected credentials?",
    "batch_action_success": "Batch {action} completed successfully.",
    "input_password_prompt": "Enter the password first.",
    "login_success": "Signed in successfully.",
    "login_failed": "Login failed. Please check your password.",
    "net_error_prefix": "Network error: ",
    "action_success_prefix": "Action succeeded: ",
    "action_fail_prefix": "Action failed: ",
    "upload_fail_prefix": "Upload failed: ",
    "check_update_fail_prefix": "Check update failed: ",
    "pagination_prev": "Previous Page",
    "pagination_next": "Next Page",
    "pagination_info": "Page {page} of {total} (Showing {start}-{end} of {count} items)",
    "code_assist_oauth_auth_title": "Code Assist OAuth Authentication",
    "oauth_guide_2_fail_suffix": ", which is expected.",
    "oauth_paste_url": "Paste the full URL below:",
    "provider_auth_title": "Provider authentication",
    "provider_guide_2_fail_suffix": ", then return to this panel.",
    "upload_file_or_zip": "file or ZIP archive",
    "click_to_copy": "Click to copy",
    "support_link_label": "GitHub Issues",
    "enable_only": "Enable Only",
    "disable_only": "Disable only",
    "click_to_open_link": "Click to open link",
    "right_click_to_copy_link": "Right click to copy link",
    "status_disabled": "Disabled",
    "status_enabled": "Enabled",
    "preview_supported_title": "This credential supports Preview models",
    "preview_not_supported_title": "This credential does not support Preview models",
    "tier_badge_title": "Credential tier",
    "credit_enabled_title": "Credit mode is currently enabled",
    "credit_disabled_title": "Credit mode is currently disabled",
    "other_models_title": "Other models",
    "btn_view_content": "View content",
    "btn_view_email": "View email",
    "btn_view_quota": "View quota",
    "btn_view_quota_title": "View quota usage info for this credential",
    "btn_disable_credit": "Disable credit",
    "btn_disable_credit_title": "Disable credit mode for this credential",
    "btn_enable_credit": "Enable credit",
    "btn_enable_credit_title": "Enable credit mode for this credential",
    "btn_setup_preview": "Set up Preview",
    "btn_setup_preview_title": "Configure the Preview channel and enable experimental features.",
    "btn_verify_id": "Verify",
    "btn_verify_id_title": "Retrieve the Project ID and recover from some 403 errors.",
    "btn_message_test": "Message test",
    "btn_message_test_title": "Test whether this credential is working.",
    "btn_view_errors": "View errors",
    "btn_view_errors_title": "View detailed error messages for this credential.",
    "email_not_fetched": "Email not fetched",
    "click_view_content_to_load": "Click 'View content' to load file details.",
    "click_view_errors_to_load": "Click 'View errors' to load error messages.",
    "click_view_quota_to_load": "Click 'View quota' to load quota usage details.",
    "status_loading_file_content": "Loading file content...",
    "status_test_failed": "Test failed: {error}",
    "remaining_label": "Remaining",
    "credits_label": "Credits",
    "all": "All",
    "provider_stream_transform_enabled": "Provider stream-to-non-stream response transformation is enabled.",
    "test_successful": "Test completed successfully.",
    "oauth_interaction_guide": "OAuth interaction guide:",
    "error_code": "Error code:",
    "no_logs_at_appstatecurrentlogfilter": "No logs are currently available at the {AppState_currentLogFilter} level.",
    "credential_file_name": "Credential file name",
    "nfailed_step_step": "\\nFailed Step: {step}",
    "batch_verification_completed_succes": "Batch verification completed: {successCount}/{selectedFiles_length} succeeded, {failCount} failed.",
    "currently_disabled": "Currently disabled",
    "primary_authentication_successf": "Provider authentication completed successfully. File saved to: {path}.",
    "loaded_usage_statistics_for_aggdata": "Loaded usage statistics for {aggData_total_files____Object_keys_AppState_usageStatsData__length} files",
    "upload_failed_connection_interrupte": "Upload failed: the connection was interrupted. Too many files ({this_selectedFiles_length}) or network instability may be the cause. Please upload in batches.",
    "please_select_the_primary_crede": "Please select provider credentials to verify first.",
    "downloaded_file_filename": "Downloaded file: {filename}",
    "oneclick_credential_deduplication": "One-click credential deduplication",
    "message_test": "Message test",
    "div_styletextalign_center_padding_2": "<div style=\"text-align: center; padding: 20px; color: #999;\">\n\n                                <div style=\"font-size: 48px; margin-bottom: 10px;\"></div>\n\n                                <div>No Quota Information Available</div>\n\n                            </div>",
    "primary_authentication_link": "Provider authentication link:",
    "authentication_steps": "Authentication steps:",
    "fetching_authentication_link": "Fetching authentication link...",
    "upload_failed_request_timeout_proce": "Upload failed: the request timed out. Processing took too long. Reduce the number of files or check your network connection.",
    "manual_project_id_specification_req": "A Google Cloud Project ID is required. Enter it in advanced options and try again.",
    "resource_manager_api_endpoint": "Resource Manager API endpoint:",
    "intelligently_capture_and_automatic": "Intelligently capture and automatically write current keep-alive heartbeat URL",
    "a_hrefhref_target_blank_relnoopener": "<a href=\"{href}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"message-link\" onclick=\"event.stopPropagation()\" title=\"Click to open link\\nRight-click to copy link\">{url}</a>",
    "this_is_not_a_valid_callback_url_pl": "This is not a valid callback URL. Please ensure:\\n1. Google OAuth authorization is complete.\\n2. You copied the full URL from the browser address bar.\\n3. The URL contains code and state parameters.",
    "file_filename_format_is_not_support": "File {file_name} format is not supported; only JSON and ZIP files are allowed.",
    "the_following_configurations_have_t": ", the following configurations have taken effect immediately: {list}",
    "click_the_link_above_to_proceed_wit": "Open the link above to proceed with Google OAuth authorization.",
    "unable_to_determine_if_updates_are": "Unable to determine if updates are available.",
    "please_select_the_credentials_to_ve": "Please select credentials to verify first.",
    "downloaded_file_name": "Downloaded file: {name}",
    "please_obtain_the_primary_authe": "Please obtain the provider authentication link and complete authorization first.",
    "refresh_credential_list": "Refresh credential list",
    "all_credential_files_have_been_down": "All credential files have been downloaded.",
    "preview_channel_configuration_succe": "Preview channel configured successfully.\\n\\nFile: {filename}\\n\\n{data_message}\\n\\nSetting ID: {data_setting_id_____N_A}\\nBinding ID: {data_binding_id_____N_A}",
    "all_verifications_successful_verifi": "All verifications passed. Verified {successCount}/{selectedFiles_length} provider credentials.",
    "are_you_sure_you_want_to_batch_veri": "Are you sure you want to batch verify project IDs for {selectedFiles_length} provider credentials?\\n\\nThey will be verified in parallel to speed up the process.",
    "failed_to_load_usage_statistics": "Failed to load usage statistics",
    "failed_to_download_logs_datadetail": "Failed to download logs: {data_detail____data_error}",
    "generating_authentication_link_usin": "Generating authentication link using the specified Project ID...",
    "not_enabled": "Not enabled",
    "download_credential_files_locally": "Download credential files locally",
    "average_calls_per_volume": "Average requests per credential",
    "failed_to_get_authentication_link_e": "Failed to get authentication link: {error}",
    "successfully_retrieved_email_dataus": "Successfully retrieved email: {data_user_email}",
    "code_assist_oauth_authentication": "Code Assist OAuth authentication",
    "failed_to_create_websocket_connecti": "Failed to create WebSocket connection:",
    "primary_batch_verification_comp": "Provider batch verification complete",
    "healthy_no_errors": "Healthy, no errors",
    "no_data_under_current_filter_condit": "No data under current filter conditions",
    "successfully_retrieved_email_email": "Successfully retrieved email: {email}",
    "get_google_oauth_authentication_lin": "Get Google OAuth authentication link",
    "failed_to_fetch_version_information": "Failed to fetch version information",
    "switch_to_mirror_proxy_address_with": "Switch to mirror proxy addresses with one click.",
    "enable_automatic_retry_of_failed_re": "Enable automatic retry of failed requests using other rotated credentials",
    "level": "Level:",
    "please_enter_password_to_login": "Please enter your password to sign in.",
    "failed_to_retrieve_credentials_from": "Failed to retrieve credentials from callback URL: {error}",
    "please_select_the_credentials_to_ve_dup": "Please select credentials to verify first.",
    "retrieved_authentication_link": "Retrieved authentication link:",
    "upload_failed_errordetail_errorerro": "Upload failed: {error_detail____error_error}",
    "are_you_sure_you_want_to_perform_on": "Are you sure you want to perform one-click credential deduplication?\\n\\nOnly one credential per email will be kept, and all others will be deleted.\\nThis action cannot be undone.",
    "primary_file_list_pending_uploa": "Provider files pending upload:",
    "successfully_imported_loadedtotal_c": "Successfully imported {loaded}/{total} credential files.",
    "keepalive_request_interval_seconds": "Keep-alive request interval (seconds):",
    "healthy_no_errors_dup": "Healthy, no errors",
    "clear_failed_datadetail_dataerror_u": "Clear failed: {data_detail____data_error}",
    "network_error_while_clearing_logs_e": "Network error while clearing logs: {error_message}",
    "save_log_file_as": "Save log file as...",
    "upload_failed_connection_interrupte_dup": "Upload failed: Connection interrupted - Likely cause: Too many files ({count}) or network instability. Please upload in batches.",
    "resultfilename_resultmessage_config": "{result_filename}: {result_message}",
    "disable_credits": "Disable Credits",
    "please_select_the_files_to_operate": "Please select files before continuing.",
    "batch_operation_failed_error": "Batch operation failed: {error}",
    "account_risk_control_and_circuit_br": "Account risk control and circuit-breaking strategy",
    "determine_account_downgrade_or_disa": "Determine account downgrade or disabling within seconds based on API errors.",
    "reset_statistics": "Reset Statistics",
    "google_primary_authentication": "Google provider authentication",
    "failed_to_download_package_error": "Failed to download package: {error}",
    "div_stylecolor_dc3545reason_escapeh": "<div style=\"color: #dc3545;\">Reason: {escapeHtml_detail_reason}</div>",
    "test_successful_dup": "Test completed successfully.",
    "are_you_sure_you_want_to_refresh_us": "Are you sure you want to refresh user emails for all credentials? This may take some time.",
    "filter_filter": "(Filter: {filter})",
    "view_content": "View content",
    "open_source_disclaimer_commercial_r": "Open-source notice: Omni Gateway is released under the MIT License. Include the required copyright and license notice when redistributing it.",
    "failed_to_save_configuration_error": "Failed to save configuration: {error}",
    "total_credentials": "Total credentials",
    "contact_and_feedback_channels": "Contact and feedback channels",
    "supports_json_credentials_or_zip_ar": "Supports .json credentials or .zip archives",
    "revert_to_google_official_address": "Revert to the official Google endpoint.",
    "failed_to_retrieve_primary_cred": "Failed to retrieve provider credentials from callback URL",
    "import_failed_datadetail_dataerror": "Import failed: {data_detail____data_error}",
    "new_version_foundncurrent_vversionn": "New version available.\\nCurrent: v{version}\\nLatest: v{latest}\\n\\nUpdate details: {log}",
    "network_error_msg": "Network error: {msg}",
    "unable_to_retrieve_user_email_error": "Unable to retrieve user email: {error}",
    "batch_action_operation_completed_su": "Batch {action} operation completed successfully.",
    "api_integration_endpoint_addresses": "API integration endpoint addresses",
    "system_runtime_log_stream": "System runtime log stream",
    "import_failed_error": "Import failed: {error}",
    "google_apis_core_endpoints": "Google APIs core endpoints:",
    "authentication_successful_saved_fil": "Authentication successful. Saved file content:",
    "click_the_view_quota_button_to_load": "Click \"View Quota\" to load quota information.",
    "waiting_to_fetch_the_latest_system": "Waiting for the latest system console log output...",
    "control_panel_login_password": "Control Panel Login Password:",
    "unable_to_autodetect_project_id_ple": "Unable to auto-detect Project ID. Please manually enter your Google Cloud Project ID:",
    "click_this_link_to_authorize_your_g": "Open this link to authorize your Google account.",
    "email_groupemailnkeep_groupkept_fil": "Email: {group_email}\\nKeep: {group_kept_file}\\nDelete: {group_deleted_files_join}\\n\\n",
    "primary_authentication_link_gen": "Provider authentication link generated. Open the link to complete authorization.",
    "check_successful_already_running_th": "Update check completed. You are already running the latest version.",
    "switched_to_official_endpoint_confi": "Switched to the official endpoint configuration. Click \"Save config\" to save the settings.",
    "nplease_enter_index_1dataavailable": "\\nPlease enter an index (1-{data_available_projects_length}):",
    "fetch_and_save_authentication_file": "Fetch and save authentication file",
    "failed_to_generate_authentication_l": "Failed to generate authentication link: {error}",
    "action": "Action",
    "save_config": "Save config",
    "fetch_primary_credentials": "Fetch provider credentials",
    "failed_to_generate_authentication_l_dup": "Failed to generate authentication link",
    "retry_using_the_selected_project": "Retrying with the selected project...",
    "div_styletextalign_center_padding_2_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\"></div>\n\n                        <div style=\"font-weight: bold; margin-bottom: 5px;\">Network Error</div>\n\n                        <div style=\"font-size: 13px; color: #666;\">{error_message}</div>\n\n                    </div>",
    "credential_available": "Credential available",
    "google_primary_authentication_m": "Google provider authentication mode",
    "zip_archive": "(ZIP Archive)",
    "are_you_sure_you_want_to_delete_fil": "Are you sure you want to delete {filename}?",
    "page_thiscurrentpage_of_totalpages": "Page {this_currentPage} of {totalPages} (Showing {startItem}-{endItem}, Total {this_totalCount})",
    "failed_to_clear_logs_datadetail_dat": "Failed to clear logs: {data_detail____data_error}",
    "please_select_the_credentials_to_co": "Please select credentials to configure Preview first.",
    "websocket_connected": "WebSocket connected",
    "enable_autoban_for_credentials_on_s": "Enable Auto-Ban for credentials on specific error codes",
    "preview_channel_configuration_faile": "Preview channel configuration failed.\\n\\nFile: {filename}\\n\\n{errorMsg}",
    "autobacksource_failed_use_the_quick": "Automatic callback failed? Use the quick callback channel.",
    "operation_failed_error": "Operation failed: {error}",
    "please_fetch_the_authentication_lin": "Please fetch the authentication link and complete authorization first.",
    "bidirectional_native_format_convers": "Bidirectional native format conversion",
    "oneclick_deduplication_failed_error": "One-click deduplication failed: {error}",
    "disable": "Disable",
    "provider_authorization_instruction": "Open this link to authorize the provider credential flow.",
    "deduplication_network_error_errorme": "Deduplication network error: {error_message}",
    "after_successful_authorization_the": "After successful authorization, the browser will redirect and may display a connection error for localhost:11451. This is expected.",
    "failed_to_get_environment_variable": "Failed to get environment variable status: {error}",
    "max_antitruncation_resume_attempts": "Max anti-truncation resume attempts:",
    "log_connection_channel_established": "Log connection channel established successfully.",
    "test_failednfile_filenamen": "Test failed.\\nFile: {filename}\\n",
    "global_configuration_saved_successf": "Global configuration saved successfully.",
    "executing_batch_actionlabel_operati": "Executing batch {actionLabel} operation...",
    "monitor_credential_count": "Monitor credential count",
    "switched_to_official_endpoint_confi_dup": "Switched to the official endpoint configuration. Remember to click the 'Save config' button to save the settings.",
    "local_credential_storage_absolute_p": "Local credential storage absolute path:",
    "click_to_open_linknrightclick_to_co": "Click to open link\\nRight-click to copy link",
    "upload_failed_http_xhrstatus": "Upload failed: HTTP {xhr_status}",
    "verification_successful": "Verification successful.",
    "force_enable_compatibility_mode_mer": "Force enable compatibility mode (merge System protocol messages into User)",
    "clear_buffer_logs": "Clear buffer logs",
    "div_stylefontsize_12px_color_666_ma": "<div style=\"font-size: 12px; color: #666; margin-bottom: 5px;\">Details:</div>",
    "error_dataerror_failed_to_get_authe": "Error: {data_error}",
    "select_all": "Select All",
    "if_this_field_is_configured_it_will": "If this field is configured, it will force-override the API and panel passwords. It is recommended to leave it blank.",
    "autologin_successful": "Auto-login completed successfully.",
    "failed_to_save_config_datadetail_da": "Failed to save configuration: {data_detail____data_error}",
    "batch_operation_completed_processed": "Batch operation completed. Processed {success}/{total} files successfully.",
    "tip_leave_blank_for_firsttime_use_t": "Tip: Leave blank for first-time use; the system will automatically allocate and detect.",
    "configuration_failed": "Configuration failed",
    "successfully_imported_dataloaded_co": "Successfully imported {data_loaded_count}/{data_total_count} credential files.",
    "switched_to_mirror_url_configuratio": "Switched to the mirror URL configuration. Click \"Save config\" to save the settings.",
    "zip_files_will_automatically_extrac": "ZIP files will automatically extract all JSON credential files.",
    "adjust_system_proxy_endpoint_addres": "Adjust system proxy, endpoint addresses, security policies, and high-frequency retry parameters. Most items take effect immediately after saving.",
    "loaded_count_type_credential_files": "Loaded {count} {type} credential files",
    "log_stream_connection_error": "Log stream connection error:",
    "quota_information_loaded_successful": "Quota information loaded successfully.",
    "failed_to_fetch_authentication_link": "Failed to fetch authentication link",
    "return_directly_to_the_current_cont": "Return to the current control panel page and click \"Fetch and save authentication file\" to complete integration.",
    "retry_interval_seconds": "Retry interval (seconds):",
    "autoban_circuit_breaker": "Auto-Ban Circuit Breaker",
    "usage_statistics_loaded_for_count_f": "Usage statistics loaded for {count} files",
    "operation_successful": "Operation successful:",
    "download": "Download",
    "new_version_available": "New version available",
    "openai_compatibility": "OpenAI Compatibility:",
    "verification_successfulnfile_filena": "Verification successful.\\nFile: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",
    "div_styletextalign_center_padding_2_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\"></div>\n\n                            <div style=\"font-weight: bold; margin-bottom: 5px;\">Failed to fetch quota info</div>\n\n                            <div style=\"font-size: 13px; color: #666;\">{errorMsg}</div>\n\n                        </div>",
    "delete": "Delete",
    "div_styletextalign_center_padding_2_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\"></div>\n\n                            <div style=\"font-weight: bold;\">Load failed</div>\n\n                            <div style=\"font-size: 12px; margin-top: 8px;\">{errorMsg}</div>\n\n                        </div>",
    "file_format_of_name_not_supported_o": "The file format for {name} is not supported. Only JSON and ZIP files are supported.",
    "project_info": "Project Info",
    "the_following_configurations_have_t_dup": ", the following configurations have taken effect immediately: {data_hot_updated_join}",
    "unable_to_fetch_user_email": "Unable to fetch user email",
    "failed_to_fetch_credentials_from_ca": "Failed to fetch credentials from callback URL",
    "advanced_settings_specify_google_cl": "Advanced Settings: Specify Google Cloud Project ID (Optional)",
    "starting_batch_project_id_verificat": "Starting batch Project ID verification...",
    "open_github_issues": "Open GitHub Issues",
    "when_google_apis_return_these_error": "When Google APIs return these error codes, the system will automatically disable this account. It is recommended to enable circuit breaking for 403 errors.",
    "failed_to_fetch_error_message": "Failed to fetch error message",
    "error_dataerror_failed_to_generate": "Error: {data_error}",
    "service_network_listening_configura": "Service network listening configuration",
    "connecting": "Connecting...",
    "credentials_fetched_successfully_fr": "Credentials fetched successfully from the callback URL.",
    "click_the_link_above_sign_in_to_you": "Click the link above, sign in to your Google account in a new browser tab, and grant authorization.",
    "primary_credential_file_managem": "Provider credential file management",
    "failed_to_configure_preview_channel": "Failed to configure Preview channel: {error_message}",
    "authentication_successful_project_i": "Authentication successful. Project ID automatically detected as {id}. File saved to: {path}.",
    "please_enter_a_valid_url_starting_w": "Please enter a valid URL starting with http:// or https://.",
    "successfully_updated_preview_channe": "Updated Preview channel status for {count} credential files.",
    "pending_code_assist_file_upload_list": "Pending Code Assist file upload list:",
    "exclusive_industrywide_support_for": "Exclusive industry-wide support for streaming resumable uploads.",
    "configuration_failed_for_all_failed": "Configuration failed for all credentials. Failed {failCount}/{selectedFiles_length} credentials.",
    "primary_batch_verification_comp_dup": "Provider batch verification complete.\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",
    "enabled": "Enabled",
    "display_and_maintain_your_code_assist_prox": "Display and maintain your Code Assist proxy channels, supporting individual or batch verification, download, status toggling, and deletion.",
    "batch_operation_network_error_error": "Batch operation network error: {error}",
    "retrying_with_manually_entered_proj": "Retrying with manually entered Project ID...",
    "get_primary_authentication_link": "Get provider authentication link",
    "json_file": "(JSON file)",
    "are_you_sure_you_want_to_deduplicat": "Are you sure you want to deduplicate provider credentials?\\n\\nOnly one credential per email will be kept, and all others will be deleted.\\nThis action cannot be undone.",
    "display_and_maintain_provider_accounts": "Display and maintain your provider accounts and associated usage quotas.",
    "supports_json_files_or_zip_archives": "Supports .json files or .zip archives",
    "code_assist_api_endpoint": "Code Assist API Endpoint:",
    "failed_to_fetch_error_message_error": "Failed to fetch error message: {errorMsg}",
    "failed_to_load_file_content": "Failed to load file content:",
    "div_stylebackground_white_borderlef": "<div style=\"background: var(--bg); border: 1px solid var(--border); border-left: 4px solid {percentageColor}; border-radius: var(--radius); padding: 8px 10px;\">\n\n                                    <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;\">\n\n                                        <div style=\"font-weight: bold; color: #333; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; margin-right: 8px;\" title=\"{modelName} - {remainingPercentage}% remaining - {resetTime}\">\n\n                                            {modelName}\n\n                                        </div>\n\n                                        <div style=\"font-size: 13px; font-weight: bold; color: {percentageColor}; white-space: nowrap;\">\n\n                                            {remainingPercentage}%\n\n                                        </div>\n\n                                    </div>\n\n                                    <div style=\"width: 100%; height: 8px; background-color: var(--bg-subtle); border-radius: var(--radius); overflow: hidden; margin-bottom: 4px;\">\n\n                                        <div style=\"width: {usedPercentage}%; height: 100%; background-color: {percentageColor}; transition: none;\"></div>\n\n                                    </div>\n\n                                    <div style=\"font-size: 10px; color: #666; text-align: right;\">\n\n                                        {resetTime______N_A___________resetTime}\n\n                                    </div>\n\n                                </div>",
    "failed_to_check_for_updates_error": "Failed to check for updates: {error}",
    "preview_channel_configuration_succe_dup": "Preview channel configured successfully.",
    "clear_selection_list": "Clear selection list",
    "logs_cleared_waiting_for_new_logs": "Logs cleared. Waiting for new logs...",
    "running_normally": "Running normally",
    "lightweight_singlefile_deployment": "Lightweight single-file deployment",
    "button_to_save_settings_success_fun": "Click the save button to apply these settings.",
    "test_successfulnfile_filenamenstatu": "Test completed successfully.\\nFile: {filename}\\nStatus: {data_message} ({data_status_code____200})",
    "full_version_datafull_hashncommit_m": "Full version: {data_full_hash}\\nCommit message: {data_message}\\nCommit time: {data_date}",
    "importing_credentials_from_environm": "Importing credentials from environment variables...",
    "server_bound_host_ip_address": "Server bound Host IP Address:",
    "verification_failed_for_all_failed": "Verification failed for all credentials. Failed {failCount}/{selectedFiles_length} provider credentials.",
    "github_issues_support": "GitHub Issues",
    "download_failed_name": "Download failed: {name}",
    "login_successful": "Signed in successfully.",
    "network_error_error": "Network error: {error}",
    "batch_verification_completennsucces": "Batch verification complete.\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",
    "http_error_codes_that_trigger_circu": "HTTP error codes that trigger circuit breaker/ban (comma separated):",
    "upload_failed_error": "Upload failed: {error}",
    "batch_verification_complete": "Batch verification complete",
    "storage_and_proxy_settings": "Storage and proxy settings",
    "performing_batch_action_operation": "Performing batch {action} operation...",
    "this_setting_may_slightly_reduce_co": "This setting may slightly reduce comprehension for complex prompts but perfectly resolves empty returns or streaming circuit breaker errors in specific third-party clients caused by missing system_instructions.",
    "fetching_environment_variable_statu": "Fetching environment variable status...",
    "nnerror_details_errordetail": "\\n\\nError details: {errorDetail}",
    "highquality_aesthetic_panel_layout": "High-quality, aesthetic panel layout, compatible with all modern browsers.",
    "load_failed_datadetail_dataerror_un": "Load failed: {data_detail____data_error}",
    "access_password_to_protect_this_con": "Access password to protect this console page from malicious tampering.",
    "if_running_on_a_remote_vps_or_a_hea": "If running on a remote VPS or a headless environment: please expand \"Unable to access origin shortcut channel\" below for instructions.",
    "log_file_download_successful_filena": "Log file download successful: {filename}",
    "automatically_switch_to_another_rot": "Automatically switch to another rotated credential on provider errors",
    "connected": "Connected",
    "brstrongavailable_projectsstrongbr": "<br><strong>Available projects:</strong><br>",
    "div_span_classfilenamefileicon_file": "<div>\n\n                        <span class=\"file-name\">{fileIcon} {file_name}</span>\n\n                        <span class=\"file-size\">({formatFileSize_file_size}{fileType})</span>\n\n                    </div>\n\n                    <button class=\"remove-btn\" onclick=\"{type______primary_____removePrimaryFile_____removeFile}({index})\">Delete</button>",
    "passthrough_model_thinking_process": "Pass-through model thinking process to frontend response",
    "log_connection_channel_disconnected": "Log connection channel disconnected.",
    "parallel_verifying_selectedfileslen": "Verifying {selectedFiles_length} credentials in parallel. Please wait...",
    "failed_to_retrieve_authentication_f": "Failed to retrieve authentication file: {error}",
    "applicable_to_the_latest_gemini_20": "Applicable to the latest Gemini 2.0 series models with reasoning capabilities. If disabled, thinking process content will be filtered out for cleaner direct responses.",
    "log_stream_connection_disconnected": "Log stream connection disconnected",
    "environment_variable_status_check_c": "Environment variable status check complete",
    "project_description": "Omni Gateway is a universal AI router for coding tools. Features smart auto-fallback, token compression, and seamless format translation to maximize free and premium LLMs.",
    "click_the_view_error_button_to_load": "Click \"View Error\" to load error information.",
    "loaded_datatotal_type_primary_a": "Loaded {data_total} {type______primary_____provider} credential files",
    "email_not_retrieved": "Email not retrieved",
    "tip": "Tip",
    "load_failed_error": "Load failed: {error}",
    "primary_credential_valid": "Provider credential is valid.",
    "in_cooldown": "In cooldown",
    "verification_failed": "Verification failed",
    "gemini_native": "Gemini Native:",
    "error_code_code": "Error code: {code}",
    "api_endpoint_proxy_setup": "API endpoint proxy setup",
    "login_failed_incorrect_password": "Incorrect password. Please try again.",
    "used_for_http_authorization_bearer": "Used for HTTP Authorization Bearer Token verification on proxy endpoint requests.",
    "enable_batch": "Enable batch",
    "failed_to_download_package_errormes": "Failed to download package: {error_message}",
    "batch_configuration_complete_succes": "Batch configuration complete: {successCount}/{selectedFiles_length} succeeded, {failCount} failed.",
    "claude_compatible": "Claude Compatible:",
    "verifying_primary_project_id_pl": "Verifying provider project ID. Please wait...",
    "invalid_selection_please_restart_th": "Invalid selection. Please restart the authentication process.",
    "error_code_dup": "Error code:",
    "configuration_data_loaded_successfu": "Configuration data loaded successfully.",
    "leave_blank_to_attempt_automatic_de": "Leave blank to attempt automatic detection and project creation.",
    "no_usage_breakdown_statistics_avail": "No usage breakdown statistics available",
    "all_verifications_successful_succes": "All verifications passed. Verified {successCount}/{selectedFiles_length} credentials.",
    "successfully_deleted_datadeleted_co": "Deleted {data_deleted_count} environment variable credential files.",
    "are_you_sure_you_want_to_delete_fil_dup": "Are you sure you want to delete {filename}?",
    "verify": "Verify",
    "click_to_select_files_or_drag_and_d": "Click to select files, or drag and drop files here",
    "configuration_successful": "Configuration successful.",
    "error": "Error:",
    "retrieving_credentials_from_callbac": "Retrieving credentials from callback URL...",
    "preview_channel_configuration_faile_dup": "Preview channel configuration failed",
    "n_restart_notice_datarestart_notice": "\\n Restart notice: {data_restart_notice}",
    "service_usage_api_status_management": "Service Usage API Status Management Endpoint:",
    "failed_to_retrieve_authentication_f_dup": "Failed to retrieve authentication file",
    "please_select_a_projectnnplease_ent": "Please select a project:\\n\\nPlease enter the sequence number (1-{count}):",
    "per_page": "Per page:",
    "failed_to_check_for_updates_dataerr": "Failed to check for updates: {data_error}",
    "network_error_errormessage": "Network error: {error_message}",
    "minimal_resource_footprint_perfectl": "Minimal resource footprint, perfectly adapted for all major PAAS and Docker environments.",
    "application_keepalive_settings": "Application keep-alive settings",
    "save_global_configuration": "Save global configuration",
    "failed_to_load_configuration_datade": "Failed to load configuration: {data_detail____data_error}",
    "uploading_and_extracting_zip_file": "Uploading and extracting ZIP file...",
    "are_you_sure_you_want_to_batch_veri_dup": "Are you sure you want to batch verify Project IDs for {selectedFiles_length} credentials?\\n\\nVerification will be processed in parallel to increase speed.",
    "refreshing_all_user_emails": "Refreshing all user emails...",
    "operation_failed_datadetail_dataerr": "Operation failed: {data_detail____data_error}",
    "are_you_sure_you_want_to_delete_the": "Are you sure you want to delete the {selectedFiles_length} selected files?\\nNote: This action cannot be undone.",
    "new_version_foundncurrent_vdatavers": "New version available.\\nCurrent: v{data_version}\\nLatest: v{data_latest_version}\\n\\nRelease notes: {data_latest_message}",
    "div_stylecolor_007bfftype_highlight": "<div style=\"color: #007bff;\">Type: {highlightedType}</div>",
    "failed_to_check_for_updates_errorme": "Failed to check for updates: {error_message}",
    "nerror_detailsndataerror": "\\nError details:\\n{data_error}",
    "primary_authentication_successf_dup": "Provider authentication completed successfully. File saved to: {data_file_path}.",
    "batch_verify_project_id": "Batch verify Project ID",
    "filter_thiscurrentstatusfilter_enab": "(Filter: {filter})",
    "are_you_sure_you_want_to_configure": "Are you sure you want to configure all endpoints to official addresses?",
    "perfect_responsive_support": "Perfect responsive support",
    "welcome_to_join_us_to_discuss_usage": "Welcome to join us to discuss usage and submit feature requests:",
    "successfully_deleted_count_environm": "Deleted {count} environment variable credential files.",
    "monitor_realtime_request_details_an": "Monitor real-time request details and rotation logic sent to the Google Cloud API to quickly troubleshoot network proxy or rate limiting issues.",
    "error_errormsg": "Error: {errorMsg}",
    "unlimited": "Unlimited",
    "drag_and_drop_or_select_your_existi": "Drag and drop or select your existing Code Assist or provider authentication JSON/ZIP file to upload to the server.",
    "authentication_successful_file_save": "Authentication successful. File saved to: {data_file_path}.",
    "connection_lost": "Connection lost",
    "batch_preview_channel_configuration": "Batch Preview channel configuration complete.\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",
    "are_you_sure_you_want_to_actionlabe": "Are you sure you want to {actionLabel} the {selectedFiles_length} selected files?",
    "page_page_of_total_showing_startend": "Page {page} of {total} (Showing {start}-{end}, {count} items in total)",
    "loading_file_content": "Loading file content...",
    "generating_authentication_link": "Generating authentication link...",
    "failed_to_refresh_emails": "Failed to refresh emails",
    "preview_only": "Preview only",
    "max_retries_on_failure": "Max retries on failure:",
    "batch_operation_complete_successful": "Batch operation complete. Processed {successCount}/{selectedFiles_length} files successfully.",
    "deduplication_detailsnn": "Deduplication details:\\n\\n",
    "synchronizing_current_system_config": "Synchronizing current system configuration to the server...",
    "ip_address_to_listen_on_0000_allows": "IP address to listen on. 0.0.0.0 allows public access. Requires a restart to apply changes.",
    "are_you_sure_you_want_to_reset_usag": "Are you sure you want to reset usage statistics for {filename}?",
    "please_select_at_least_one_credenti": "Please select at least one credential to proceed.",
    "authentication_successful_file_save_dup": "Authentication successful. File saved to: {path}.",
    "retrieving_primary_credentials": "Retrieving provider credentials from callback URL...",
    "configuring_preview_channel_please": "Configuring Preview channel. Please wait...",
    "verification_failed_error": "Verification failed: {error}",
    "please_select_the_primary_crede_dup": "Please select a provider credential to verify first.",
    "successfully_uploaded_datauploaded": "Uploaded {data_uploaded_count} {type______primary_____provider} file(s) successfully.",
    "dataexisting_env_files_count_files": "{data_existing_env_files_count} file(s)",
    "waiting_for_primary_oauth_callb": "Waiting for provider OAuth callback...",
    "model_protocol_compatibility_overri": "Model protocol compatibility override",
    "maximum_retries_for_resuming_stream": "Maximum retries for resuming stream data from the break point when calling models with the '-stream-truncation-prevention' suffix.",
    "successfully_uploaded_count_type_fi": "Uploaded {count} {type} file(s) successfully.",
    "failed_to_retrieve_credentials_from_dup": "Failed to retrieve credentials from callback URL: {error_message}",
    "enable_credits": "Enable Credits",
    "code_assist_creds__environment_variable_no": "CODE_ASSIST_CREDS_* environment variable not found",
    "autoscroll_to_bottom": "Auto-scroll to bottom",
    "please_select_the_credential_to_con": "Please select a credential before configuring Preview.",
    "please_select_the_file_to_upload_fi": "Please select a file to upload first.",
    "failed_to_check_for_updates": "Failed to check for updates:",
    "enabled_dup": "Enabled",
    "retrieve_the_latest_google_cloud_sd": "Retrieve the latest Google Cloud SDK provider-native authentication credentials.",
    "global_upstream_proxy_url": "Global upstream proxy URL:",
    "processing_credential_deduplication": "Processing credential deduplication...",
    "24h_total_calls": "24h Total Requests",
    "status": "Status:",
    "maximum_retry_limit_for_resuming_st": "Maximum retry limit for resuming stream output if it gets truncated while using models with the '-stream-truncation-prevention' suffix.",
    "primary_verification_successful": "Provider verification successful.\\n\\nFile: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",
    "all_configured_successfully_preview": "All credentials configured successfully. Preview channel configured for {successCount}/{selectedFiles_length} credentials.",
    "enable_credit": "Enable Credit",
    "24hour_call_breakdown_statistics": "24-hour request breakdown statistics",
    "are_you_sure_you_want_to_refresh_us_dup": "Are you sure you want to refresh user emails for all provider credentials? This may take some time.",
    "unable_to_retrieve_version_informat": "Unable to retrieve version information",
    "batch_disable_dup": "Batch disable",
    "div_styletextalign_center_padding_2_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\"></div>\n\n                        <div style=\"font-weight: bold;\">Network Error</div>\n\n                        <div style=\"font-size: 12px; margin-top: 8px;\">{error_message}</div>\n\n                    </div>",
    "upstream_network_proxy_required_for": "Upstream network proxy required for local access to Google APIs. Leave empty for direct connection.",
    "if_you_find_any_bugs_or_have_design": "If you find a bug or have a design suggestion, open an issue on GitHub. Pull requests are welcome.",
    "view_error": "View error",
    "verification_failednnerrormsg": "Verification failed.\\n\\n{errorMsg}",
    "failed_to_retrieve_primary_cred_dup": "Failed to retrieve provider credentials from callback URL: {error_message}",
    "code_assist_credential_batch_upload": "Code Assist Credential Batch Upload",
    "checking_for_updates": "Checking for updates...",
    "unknown_version": "Unknown version",
    "oneclick_credential_deduplication_i": "One-click credential deduplication in progress...",
    "operation_successful_action": "Operation successful: {action}",
    "download_failed_filename": "Download failed: {filename}",
    "retrieve_and_save_primary_crede": "Retrieve and save provider credentials",
    "provider_credentials": "Provider credentials",
    "view_quota": "View quota",
    "logged_out": "Logged out",
    "confirm_reset_usage_statistics": "Are you sure you want to reset all usage statistics?",
    "configuration_successfulnfile_filen": "Configuration successful.\\nFile: {filename}\\nStatus: {data_message}",
    "batch_delete_dup": "Batch delete",
    "modelname_remainingpercentage_remai": "{modelName} - {remainingPercentage}% remaining - {resetTime}",
    "configuration_management": "Configuration Management",
    "retrieving_user_emails": "Retrieving user emails...",
    "set_preview": "Set Preview",
    "authentication_successful_project_i_dup": "Authentication successful. Project ID automatically detected as {data_credentials_project_id}. File saved to: {data_file_path}.",
    "automatic_quota_avoidance_rotation": "Automatic Quota Avoidance Rotation",
    "reload_configuration_data": "Reload Configuration Data",
    "key_technical_highlights": "Key Technical Highlights",
    "clear_failed_error": "Clear failed: {error}",
    "generating_primary_authenticati": "Generating provider authentication link...",
    "upload_failed_errormessage": "Upload failed: {error_message}",
    "failed_to_update_preview_status_in": "Failed to update Preview status in bulk: {error}",
    "downloaded_filename": "Downloaded: {filename}",
    "bulk_upload_local_credentials": "Bulk Upload Local Credentials",
    "div_stylebackground_lineargradient1": "<div style=\"background: var(--bg-subtle); color: var(--text-primary); padding: 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 15px;\">\n\n                                <h4 style=\"margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;\">\n\n                                    <span style=\"font-size: 20px;\"></span>\n\n                                    <span>Quota Information Details</span>\n\n                                </h4>\n\n                                <div style=\"font-size: 12px; opacity: 0.9; margin-top: 5px;\">File: {filename}</div>\n\n                            </div>\n\n                            <div style=\"display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;\">",
    "automatic_retry_reconnection_mechan": "Automatic retry and reconnection mechanism",
    "download_all_credentials_as_archive": "Download All Credentials as Archive",
    "waiting_for_oauth_callback": "Waiting for OAuth callback...",
    "local_storage_directory_for_uploade": "Local storage directory for uploaded and authorized JSON files.",
    "bulk_preview_channel_configuration": "Bulk Preview channel configuration complete",
    "disable_credit": "Disable Credit",
    "no_logs_yet": "No logs yet...",
    "already_up_to_date": "Already up to date.",
    "test_successfulnfile_filenamenstatu_dup": "Test completed successfully.\\nFile: {filename}\\nStatus: {data_message} ({data_status_code____200})",
    "deduplication_complete_deleted_data": "Deduplication complete. Deleted {data_deleted_count} duplicate credentials and kept {data_kept_count} credentials ({data_unique_emails_count} unique emails).",
    "are_you_sure_you_want_to_perform_th": "Are you sure you want to perform the {action} bulk operation on the {count} selected credentials?",
    "bulk_operation_failed_datadetail_da": "Bulk operation failed: {data_detail____data_error}",
    "ncredit_datacredit_amount": "\\nCredit: {data_credit_amount}",
    "authentication_failed_please_log_in": "Authentication failed. Please sign in again.",
    "code_assist_credential_file_management": "Code Assist Credential File Management",
    "failed_to_retrieve_version_informat": "Failed to retrieve version information:",
    "filter_level": "Filter Level:",
    "failed_to_get_email_errormessage": "Failed to get email: {error_message}",
    "suitable_for_cloud_servervps_deploy": "Suitable for cloud server/VPS deployment, Docker container environments, or scenarios where port 11451 is blocked by a firewall.",
    "connection_error": "Connection error",
    "primary_credentials_successfull": "Provider credentials retrieved successfully from the callback URL.",
    "are_you_sure_you_want_to_configure_dup": "Are you sure you want to configure all endpoints as mirror URLs?",
    "sever_log_channel": "Server log channel",
    "configuration_loaded_successfully": "Configuration loaded successfully.",
    "unable_to_load_file_content": "Unable to load file content:",
    "bulk_enable_credit": "Bulk enable Credit",
    "live_connection_status": "Live connection status:",
    "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\"> Loading quota information...</div>",
    "connection_failed": "Connection failed",
    "oneclick_deduplication_complete_del": "One-click deduplication complete. Deleted {deleted} duplicate files and kept {kept} unique account files.",
    "verifying_project_id_please_wait": "Verifying Project ID. Please wait...",
    "email_refresh_network_error_errorme": "Email refresh network error: {error_message}",
    "waiting_for_oauth_callback_this_may": "Waiting for OAuth callback, this may take some time...",
    "project_id_required_to_complete_aut": "A Project ID is required to complete authentication. Restart the flow and enter the correct Project ID.",
    "error_code_datastatus_code_response": "Error code: {data_status_code____response_status}",
    "cooling_down": "Cooling down:",
    "start_bulk_upload": "Start bulk upload",
    "attempting_to_autodetect_project_id": "Attempting to auto-detect Project ID, generating authentication link...",
    "check_for_updates_failed_dataupdate": "Update check failed: {data_update_error}",
    "upload_failed": "Upload failed:",
    "all_verifications_failed_failed_fai": "All verifications failed. Failed {failCount}/{selectedFiles_length} credentials.",
    "upload_failed_server_response_forma": "Upload failed: Server response format error",
    "deduplication_failed": "Deduplication failed",
    "credit_resultcreditamount": "(Credit: {result_creditAmount})",
    "are_you_sure_you_want_to_delete_the_dup": "Are you sure you want to delete the credential file?\\n{filename}",
    "test_failed": "Test failed",
    "bulk_configure_preview_channels": "Bulk configure Preview channels",
    "github_open_source_repository": "GitHub Open Source Repository:",
    "test_failed_errormessage": "Test failed: {error_message}",
    "view_account_email": "View account email",
    "longtext_truncation_recovery_contro": "Long-text truncation recovery control",
    "automation_enabled": "Automation enabled:",
    "div_stylepadding_12px_marginbottom": "<div style=\"padding: 12px; margin-bottom: 10px; border-left: 3px solid #dc3545; background-color: #f8f9fa;\">\n\n                                    <div style=\"font-weight: bold; color: #dc3545; margin-bottom: 8px;\">Error code: {errorCode}</div>\n\n                                    <div style=\"line-height: 1.6; color: #333; white-space: pre-wrap; word-break: break-word;\">\n\n                                        {highlightedMsg}\n\n                                    </div>\n\n                                    {detailsHtml}\n\n                                </div>",
    "refresh_all_account_emails": "Refresh all account emails",
    "about_project_page": "About Omni Gateway",
    "get_authentication_file": "Get authentication file",
    "n_restart_reminder_notice": "\\n Restart Reminder: {notice}",
    "test_failed_datamessage_error_code": "Test failed: {data_message}",
    "service_keepalive_heartbeat_request": "Service keep-alive heartbeat request URL:",
    "after_the_google_authorization_redi": "After the Google authorization redirect, copy the full URL from your browser address bar (even if it shows a connection error) and paste it into the input box below.",
    "disabled": "Disabled",
    "upload_failed_http_status": "Upload failed: HTTP {status}",
    "disconnected": "Disconnected",
    "if_the_redirect_fails_and_shows_an": "If the redirect fails and shows an error about being unable to connect to localhost:11451, return to this control panel.",
    "unknown_error": "Unknown error",
    "testing_primary_credentials_ple": "Testing provider credentials. Please wait...",
    "if_you_cannot_return_to_the_source": "If you cannot return to the source, you can copy the full URL after the redirect and expand the quick channel below to parse it.",
    "verification_failed_errormessage": "Verification failed: {error_message}",
    "nerror_detailsnjsonstringifyerrorob": "\\nError details:\\n{JSON_stringify_errorObj__null__2}",
    "log_stream_connected_successfully": "Log stream connected successfully.",
    "clearing_environment_variable_crede": "Clearing environment variable credential files...",
    "get_authentication_link": "Get authentication link",
    "resulterror_step_resultstep": "{result_error} (Step: {result_step})",
    "network_error": "Network error:",
    "failed_to_retrieve_environment_vari": "Failed to retrieve environment variable status: {data_detail____data_error}",
    "count_items_selected": "{count} items selected",
    "are_you_sure_you_want_to_clear_all": "Are you sure you want to clear all credential files imported from environment variables?\\nThis will delete all authentication files starting with \"env-\".",
    "bulk_operation_network_error_errorm": "Bulk operation network error: {error_message}",
    "streaming_truncation_recovery": "-Streaming truncation recovery",
    "failed_to_get_quota_information": "Failed to get quota information.",
    "click_the_button_below_to_retrieve": "Click the button below to retrieve and automatically save the credential file.",
    "seamlessly_switch_to_idle_accounts": "Seamlessly switch to idle accounts to effectively avoid 429 rate limits.",
    "bind_the_listening_tcp_port_changes": "Bind the listening TCP port; changes require a restart to take effect.",
    "bulk_disable_credit": "Bulk disable Credit",
    "failed": "Failed",
    "reset_failed_datamessage_datadetail": "Reset failed: {data_message____data_detail____data_error}",
    "failed_to_get_quota_information_err": "Failed to get quota information: {error_message}",
    "realtime_logs": "Real-time logs",
    "please_enter_the_access_password": "Please enter the access password.",
    "zip_files_will_be_automatically_dec": "ZIP files will be automatically decompressed and filtered to extract JSON credentials.",
    "oauth_authentication_server_endpoin": "OAuth authentication server endpoint:",
    "are_you_sure_you_want_to_batch_set": "Are you sure you want to batch set the Preview channel for {selectedFiles_length} credentials?\\n\\nConfiguration will be processed in parallel for speed.",
    "settings_saved_successfully_success": "Settings saved successfully.",
    "configuration_saved_successfully": "Configuration saved successfully.",
    "preview_not_supported": "Preview not supported",
    "please_select_a_projectnn": "Please select a project:\\n\\n",
    "please_select_the_files_to_upload": "Please select files to upload.",
    "are_you_sure_you_want_to_action_the": "Are you sure you want to {action} the selected {count} files?",
    "a_hrefurl_target_blank_stylecolor_0": "<a href=\"{url}\" target=\"_blank\" style=\"color: #007bff; text-decoration: underline; word-break: break-all;\" title=\"Click to open: {url}\">{url}</a>",
    "retry_fetching_authentication_file": "Retry fetching authentication file",
    "manually_connect_log_channel": "Manually connect log channel",
    "error_information_loaded_successful": "Error information loaded successfully.",
    "universal_shortcut_override_passwor": "Universal shortcut override password (optional):",
    "login_failed_datadetail_dataerror_u": "Login failed. Please try again.",
    "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\"> Loading error information...</div>",
    "log_stream_connection_disconnected_dup": "Log stream connection disconnected",
    "system_configuration_saved_successf": "System configuration saved successfully.",
    "div_stylefontsize_12px_color_666sta": "<div style=\"font-size: 12px; color: #666;\">Status: {escapeHtml_parsedMsg_error_status}</div>",
    "api_access_authentication_password": "API access authentication password (API Key):",
    "parallel_testing_selectedfileslengt": "Testing {selectedFiles_length} provider credentials in parallel. Please wait...",
    "operation_failed": "Operation failed:",
    "all_primary_credentials_packed": "All provider credentials have been packed and downloaded.",
    "operation_successful_action_dup": "Operation successful: {action}",
    "primary_api_endpoint": "Provider API endpoint:",
    "authentication_link_generated_proje": "Authentication link generated for Project ID {data_detected_project_id}. Click the link to complete authorization.",
    "configuring_preview_channel_status": "Configuring Preview channel status in batch...",
    "after_successful_authorization_the_dup": "After successful authorization, the system will automatically detect and activate the required Gemini Cloud Assist API and Gemini for Google Cloud API services for your Google Cloud project. No manual configuration is required.",
    "batch_upload_primary_credential": "Batch upload provider credentials",
    "checking": "Checking...",
    "please_enter_the_callback_url": "Please enter the callback URL.",
    "extract_credentials_from_callback_l": "Extract credentials from callback link",
    "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #28a745;\"><div style=\"font-size: 48px; margin-bottom: 10px;\"></div><div style=\"font-weight: bold;\">No error records</div><div style=\"font-size: 12px; color: #666; margin-top: 8px;\">This credential is running normally</div></div>",
    "no_details_available": "No details available",
    "global_system_configuration": "Global system configuration",
    "network_error_while_downloading_log": "Network error while downloading logs: {error_message}",
    "authentication_link_generated_proje_dup": "Authentication link generated for Project ID {id}. Click the link to complete authorization.",
    "listening_port": "Listening Port:",
    "email_refresh_complete_successfully": "Email refresh complete. Retrieved {data_success_count}/{data_total_count} email addresses.",
    "already_up_to_date_dup": "Already up to date",
    "no_credential_files_available": "No credential files available",
    "validation_successfulnnfile_filenam": "Validation successful.\\n\\nFile: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",
    "selectedcount_items_selected": "{selectedCount} items selected",
    "click_the_view_content_button_to_lo": "Click the \"View content\" button to load file details...",
    "please_enter_the_password": "Please enter your password.",
    "upload_progress_dup": "Upload progress",
    "error_dataerror_failed_to_fetch_aut": "Error: {data_error}",
    "are_you_sure_you_want_to_delete_the_dup_dup": "Are you sure you want to delete the {count} selected files?\\nNote: This action cannot be undone.",
    "configuring_preview_channel_for_sel": "Configuring Preview channel for {selectedFiles_length} credentials. Please wait...",
    "none": "None",
    "this_is_not_a_valid_callback_url_pl_dup": "This is not a valid callback URL. Please ensure it includes code and state parameters.",
    "retrieved_credential_file_content": "Retrieved credential file content:",
    "enable": "Enable",
    "antitruncation_output_protection": "Anti-truncation Output protection",
    "authentication_link_generated_proje_dup_dup": "Authentication link generated. The Project ID will be detected after authorization. Click the link to complete authorization.",
    "failed_to_configure_preview_channel_dup": "Failed to configure Preview channel",
    "testing_credentials_please_wait": "Testing credentials. Please wait...",
    "validation_complete_processed_activ": "Validation complete. Processed: {active} valid, {changed} IDs updated, {disabled} marked invalid.",
    "login_successful_dup": "Signed in successfully.",
    "batch_task_control": "Batch task control",
    "24h_api_call_volume": "24H API Request Volume",
    "minimalist_parsing_mapping_for_cutt": "Minimalist parsing mapping for cutting-edge protocols like System/Thinking.",
    "multiple_projects_detected_please_s": "Multiple projects were detected. Specify a Project ID in advanced options:",
    "failed_to_fetch_error_information_e": "Failed to fetch error information: {error_message}",
    "status_net_error": "Network error: {error}",
    "status_no_filter_data": "No usage statistics found.",
    "table_calls": "Requests",
    "btn_reset_stats": "Reset Stats",
    "confirm_reset_stats": "Are you sure you want to reset statistics for {filename}?",
    "table_filename": "Credential file name",
    "table_actions": "Actions"
}
};

// =====================================================================

// =====================================================================

function t(key, vars = {}) {

    const lang = AppState.lang || 'en';

    let text = (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) || (TRANSLATIONS['en'] && TRANSLATIONS['en'][key]) || key;

    for (const [k, v] of Object.entries(vars)) {

        text = text.replaceAll(`{${k}}`, v);

    }

    return text;

}

function changeLanguage(lang) {

    setLanguage('en');

    applyLanguage();

}

function initLanguage() {

    setLanguage('en');

    applyLanguage();

}

function setLanguage(lang) {

    if (!TRANSLATIONS[lang]) lang = 'en';

    AppState.lang = lang;

    localStorage.setItem('lang', lang);

    document.querySelectorAll('.lang-switcher').forEach(sw => {

        sw.value = lang;

    });

}

function applyLanguage() {

    const lang = AppState.lang || 'en';

    document.querySelectorAll('[data-i18n]').forEach(el => {

        const key = el.getAttribute('data-i18n');

        const text = t(key);

        if (text && text !== key) {

            el.innerHTML = text;

        }

    });

    document.querySelectorAll('[data-i18n-title]').forEach(el => {

        const key = el.getAttribute('data-i18n-title');

        const text = t(key);

        if (text && text !== key) {

            el.setAttribute('title', text);

        }

    });

    document.querySelectorAll('[data-i18n-alt]').forEach(el => {

        const key = el.getAttribute('data-i18n-alt');

        const text = t(key);

        if (text && text !== key) {

            el.setAttribute('alt', text);

        }

    });

}

document.addEventListener('DOMContentLoaded', initLanguage);

// =====================================================================

// =====================================================================

const ROUTE_MAP = {

    '/dashboard': 'dashboard',

    '/provider': 'manage',

    '/oauth': 'oauth',

    '/upload': 'upload',

    '/config': 'config',

    '/logs': 'logs',

    '/about': 'about'

};

const TAB_MAP = {};

for (const [route, tab] of Object.entries(ROUTE_MAP)) {

    TAB_MAP[tab] = route;

}

function navigate(path, pushState = true) {

    let targetPath = path || '/dashboard';

    if (targetPath === '/' || targetPath === '') {

        targetPath = '/dashboard';

    }

    const setupEl = document.getElementById('setupSection');

    const loginEl = document.getElementById('loginSection');

    const mainEl = document.getElementById('mainSection');

    if (AppState.setupRequired) {

        targetPath = '/setup';

        if (window.location.pathname !== '/setup') {

            history.replaceState(null, '', '/setup');

        }

        if (setupEl) setupEl.style.setProperty('display', 'flex', 'important');

        if (loginEl) loginEl.style.setProperty('display', 'none', 'important');

        if (mainEl) mainEl.style.setProperty('display', 'none', 'important');

        return;

    }

    const savedToken = localStorage.getItem('auth_token') || AppState.authToken;

    const isAuthenticated = !!savedToken;

    if (!isAuthenticated) {

        targetPath = '/login';

        if (window.location.pathname !== '/login') {

            history.replaceState(null, '', '/login');

        }

        if (setupEl) setupEl.style.setProperty('display', 'none', 'important');

        if (loginEl) loginEl.style.setProperty('display', 'flex', 'important');

        if (mainEl) mainEl.style.setProperty('display', 'none', 'important');

        return;

    } else {

        if (targetPath === '/login') {

            targetPath = '/dashboard';

        }

        if (targetPath === '/setup') {

            targetPath = '/dashboard';

        }

        if (setupEl) setupEl.style.setProperty('display', 'none', 'important');

        if (loginEl) loginEl.style.setProperty('display', 'none', 'important');

        if (mainEl) mainEl.style.setProperty('display', 'flex', 'important');

    }

    if (pushState && window.location.pathname !== targetPath) {

        history.pushState(null, '', targetPath);

    }

    const tabName = ROUTE_MAP[targetPath] || 'dashboard';

    // Close mobile menu instantly (Zero Animations!)

    const sidebar = document.querySelector('.dashboard-sidebar');

    const overlay = document.querySelector('.sidebar-overlay');

    if (sidebar && sidebar.classList.contains('open')) {

        sidebar.classList.remove('open');

        if (overlay) {

            overlay.classList.remove('open');

            overlay.style.display = 'none';

        }

    }

    const currentContent = document.querySelector('.tab-content.active');

    const targetContent = document.getElementById(tabName + 'Tab');

    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));

    const targetTabButton = document.querySelector(`.tab[onclick*="'${tabName}'"]`);

    if (targetTabButton) {

        targetTabButton.classList.add('active');

    }

    // Toggle panels instantly

    if (currentContent) {

        currentContent.classList.remove('active');

    }

    if (targetContent) {

        targetContent.classList.add('active');

        triggerTabDataLoad(tabName);

    }

}

// =====================================================================

// =====================================================================

// =====================================================================

// =====================================================================

const AppState = {

    authToken: '',

    setupRequired: false,

    authInProgress: false,

    currentProjectId: '',

    primaryAuthState: null,

    primaryAuthInProgress: false,

    creds: createCredsManager('normal'),

    primaryCreds: createCredsManager('primary'),

    uploadFiles: createUploadManager('normal'),

    primaryUploadFiles: createUploadManager('primary'),

    currentConfig: {},

    envLockedFields: new Set(),

    logWebSocket: null,

    allLogs: [],

    filteredLogs: [],

    currentLogFilter: 'all',

    usageStatsData: {},

    cooldownTimerInterval: null

};

// =====================================================================

// =====================================================================

function createCredsManager(type) {

    const modeParam = type === 'primary' ? 'mode=provider' : 'mode=code_assist';

    return {

        type: type,

        data: {},

        filteredData: {},

        currentPage: 1,

        pageSize: 20,

        selectedFiles: new Set(),

        totalCount: 0,

        currentStatusFilter: 'all',

        currentErrorCodeFilter: 'all',

        currentCooldownFilter: 'all',

        currentPreviewFilter: 'all',

        currentTierFilter: 'all',

        statsData: { total: 0, normal: 0, disabled: 0 },

        getEndpoint: (action) => {

            const endpoints = {

                status: `./api/creds/status`,

                action: `./api/creds/action`,

                batchAction: `./api/creds/batch-action`,

                download: `./api/creds/download`,

                downloadAll: `./api/creds/download-all`,

                detail: `./api/creds/detail`,

                fetchEmail: `./api/creds/fetch-email`,

                refreshAllEmails: `./api/creds/refresh-all-emails`,

                deduplicate: `./api/creds/deduplicate-by-email`,

                verifyProject: `./api/creds/verify-project`,

                quota: `./api/creds/quota`

            };

            return endpoints[action] || '';

        },

        getModeParam: () => modeParam,

        getElementId: (suffix) => {

            if (type === 'primary') {

                return 'primary' + suffix.charAt(0).toUpperCase() + suffix.slice(1);

            }

            return suffix.charAt(0).toLowerCase() + suffix.slice(1);

        },

        async refresh() {

            const loading = document.getElementById(this.getElementId('CredsLoading'));

            const list = document.getElementById(this.getElementId('CredsList'));

            try {

                loading.style.display = 'block';

                list.innerHTML = '';

                const offset = (this.currentPage - 1) * this.pageSize;

                const errorCodeFilter = this.currentErrorCodeFilter || 'all';

                const cooldownFilter = this.currentCooldownFilter || 'all';

                const previewFilter = this.currentPreviewFilter || 'all';

                const tierFilter = this.currentTierFilter || 'all';

                const response = await fetch(

                    `${this.getEndpoint('status')}?offset=${offset}&limit=${this.pageSize}&status_filter=${this.currentStatusFilter}&error_code_filter=${errorCodeFilter}&cooldown_filter=${cooldownFilter}&preview_filter=${previewFilter}&tier_filter=${tierFilter}&${this.getModeParam()}`,

                    { headers: getAuthHeaders() }

                );

                const data = await response.json();

                if (response.ok) {

                    this.data = {};

                    data.items.forEach(item => {

                        this.data[item.filename] = {

                            filename: item.filename,

                            status: {

                                disabled: item.disabled,

                                error_codes: item.error_codes || [],

                                last_success: item.last_success,

                            },

                            user_email: item.user_email,

                            model_cooldowns: item.model_cooldowns || {},

                            preview: item.preview,

                            tier: item.tier || 'pro',

                            enable_credit: !!item.enable_credit

                        };

                    });

                    this.totalCount = data.total;

                    if (data.stats) {

                        this.statsData = data.stats;

                    } else {

                        this.calculateStats();

                    }

                    this.updateStatsDisplay();

                    this.filteredData = this.data;

                    this.renderList();

                    this.updatePagination();

                    let msg = t('status_loaded_creds', {count: data.total, type: type === 'primary' ? 'provider' : ''});

                    if (this.currentStatusFilter !== 'all') {

                        msg += t('status_filter_suffix', {filter: this.currentStatusFilter === 'enabled' ? t('enable_only') : t('disable_only')});

                    }

                    // showStatus(msg, 'success');

                } else {

                    showStatus(t('status_load_failed', {error: data.detail || data.error || t('unknown_error')}), 'error');

                }

            } catch (error) {

                showStatus(t('status_net_error', {error: error.message}), 'error');

            } finally {

                loading.style.display = 'none';

            }

        },

        calculateStats() {

            this.statsData = { total: this.totalCount, normal: 0, disabled: 0 };

            Object.values(this.data).forEach(credInfo => {

                if (credInfo.status.disabled) {

                    this.statsData.disabled++;

                } else {

                    this.statsData.normal++;

                }

            });

        },

        updateStatsDisplay() {

            document.getElementById(this.getElementId('StatTotal')).textContent = this.statsData.total;

            document.getElementById(this.getElementId('StatNormal')).textContent = this.statsData.normal;

            document.getElementById(this.getElementId('StatDisabled')).textContent = this.statsData.disabled;

        },

        renderList() {

            const list = document.getElementById(this.getElementId('CredsList'));

            list.innerHTML = '';

            const entries = Object.entries(this.filteredData);

            if (entries.length === 0) {

                const msg = this.totalCount === 0 ? t('status_no_creds') : t('status_no_filter_data');

                list.innerHTML = `<p style="text-align: center; color: #666;">${msg}</p>`;

                document.getElementById(this.getElementId('PaginationContainer')).style.display = 'none';

                return;

            }

            entries.forEach(([, credInfo]) => {

                list.appendChild(createCredCard(credInfo, this));

            });

            document.getElementById(this.getElementId('PaginationContainer')).style.display =

                this.getTotalPages() > 1 ? 'flex' : 'none';

            this.updateBatchControls();

        },

        getTotalPages() {

            return Math.ceil(this.totalCount / this.pageSize);

        },

        updatePagination() {

            const totalPages = this.getTotalPages();

            const startItem = (this.currentPage - 1) * this.pageSize + 1;

            const endItem = Math.min(this.currentPage * this.pageSize, this.totalCount);

            document.getElementById(this.getElementId('PaginationInfo')).textContent =

                t('status_page_info', {page: this.currentPage, total: totalPages, start: startItem, end: endItem, count: this.totalCount});

            document.getElementById(this.getElementId('PrevPageBtn')).disabled = this.currentPage <= 1;

            document.getElementById(this.getElementId('NextPageBtn')).disabled = this.currentPage >= totalPages;

        },

        changePage(direction) {

            const newPage = this.currentPage + direction;

            if (newPage >= 1 && newPage <= this.getTotalPages()) {

                this.currentPage = newPage;

                this.refresh();

            }

        },

        changePageSize() {

            this.pageSize = parseInt(document.getElementById(this.getElementId('PageSizeSelect')).value);

            this.currentPage = 1;

            this.refresh();

        },

        applyStatusFilter() {

            this.currentStatusFilter = document.getElementById(this.getElementId('StatusFilter')).value;

            const errorCodeFilterEl = document.getElementById(this.getElementId('ErrorCodeFilter'));

            const cooldownFilterEl = document.getElementById(this.getElementId('CooldownFilter'));

            const previewFilterEl = document.getElementById(this.getElementId('PreviewFilter'));

            const tierFilterEl = document.getElementById(this.getElementId('TierFilter'));

            this.currentErrorCodeFilter = errorCodeFilterEl ? errorCodeFilterEl.value : 'all';

            this.currentCooldownFilter = cooldownFilterEl ? cooldownFilterEl.value : 'all';

            this.currentPreviewFilter = previewFilterEl ? previewFilterEl.value : 'all';

            this.currentTierFilter = tierFilterEl ? tierFilterEl.value : 'all';

            this.currentPage = 1;

            this.refresh();

        },

        updateBatchControls() {

            const selectedCount = this.selectedFiles.size;

            document.getElementById(this.getElementId('SelectedCount')).textContent = t('status_selected_items', {count: selectedCount});

            const batchBtnNames = ['Enable', 'Disable', 'Delete', 'Verify', 'Preview'];

            if (this.type === 'primary') {

                batchBtnNames.push('EnableCredit');

                batchBtnNames.push('DisableCredit');

            }

            const batchBtns = batchBtnNames.map(action =>

                document.getElementById(this.getElementId(`Batch${action}Btn`))

            );

            batchBtns.forEach(btn => btn && (btn.disabled = selectedCount === 0));

            const selectAllCheckbox = document.getElementById(this.getElementId('SelectAllCheckbox'));

            if (!selectAllCheckbox) return;

            const checkboxes = document.querySelectorAll(`.${this.getElementId('file-checkbox')}`);

            const currentPageSelectedCount = Array.from(checkboxes)

                .filter(cb => this.selectedFiles.has(cb.getAttribute('data-filename'))).length;

            if (currentPageSelectedCount === 0) {

                selectAllCheckbox.indeterminate = false;

                selectAllCheckbox.checked = false;

            } else if (currentPageSelectedCount === checkboxes.length) {

                selectAllCheckbox.indeterminate = false;

                selectAllCheckbox.checked = true;

            } else {

                selectAllCheckbox.indeterminate = true;

            }

            checkboxes.forEach(cb => {

                cb.checked = this.selectedFiles.has(cb.getAttribute('data-filename'));

            });

        },

        async action(filename, action) {

            try {

                const response = await fetch(`${this.getEndpoint('action')}?${this.getModeParam()}`, {

                    method: 'POST',

                    headers: getAuthHeaders(),

                    body: JSON.stringify({ filename, action })

                });

                const data = await response.json();

                if (response.ok) {

                    showStatus(data.message || t('status_action_success', {action: action}), 'success');

                    await this.refresh();

                } else {

                    showStatus(t('status_action_failed', {error: data.detail || data.error || t('unknown_error')}), 'error');

                }

            } catch (error) {

                showStatus(t('status_net_error', {error: error.message}), 'error');

            }

        },

        async batchAction(action) {

            const selectedFiles = Array.from(this.selectedFiles);

            if (selectedFiles.length === 0) {

                showStatus(t('please_select_the_files_to_operate'), 'error');

                return;

            }

            const actionNames = {

                enable: t('action_enable'),

                disable: t('action_disable'),

                delete: t('action_delete'),

                enable_credit: t('action_enable_credit'),

                disable_credit: t('action_disable_credit')

            };

            const actionLabel = actionNames[action] || action;

            const confirmMsg = action === 'delete'

                ? t('confirm_batch_delete', {count: selectedFiles.length})

                : t('confirm_batch_action', {action: actionLabel, count: selectedFiles.length});

            if (!(await showConfirmModal(confirmMsg))) return;

            try {

                showStatus(t('status_batch_in_progress', {action: actionLabel}), 'info');

                const response = await fetch(`${this.getEndpoint('batchAction')}?${this.getModeParam()}`, {

                    method: 'POST',

                    headers: getAuthHeaders(),

                    body: JSON.stringify({ action, filenames: selectedFiles })

                });

                const data = await response.json();

                if (response.ok) {

                    const successCount = data.success_count || data.succeeded;

                    showStatus(t('status_batch_complete', {success: successCount, total: selectedFiles.length}), 'success');

                    this.selectedFiles.clear();

                    this.updateBatchControls();

                    await this.refresh();

                } else {

                    showStatus(t('status_batch_failed', {error: data.detail || data.error || t('unknown_error')}), 'error');

                }

            } catch (error) {

                showStatus(t('status_batch_net_error', {error: error.message}), 'error');

            }

        }

    };

}

// =====================================================================

// =====================================================================

function createUploadManager(type) {

    const modeParam = type === 'primary' ? 'mode=provider' : 'mode=code_assist';

    const endpoint = `./api/creds/upload?${modeParam}`;

    return {

        type: type,

        selectedFiles: [],

        getElementId: (suffix) => {

            if (type === 'primary') {

                return 'primary' + suffix.charAt(0).toUpperCase() + suffix.slice(1);

            }

            return suffix.charAt(0).toLowerCase() + suffix.slice(1);

        },

        handleFileSelect(event) {

            this.addFiles(Array.from(event.target.files));

        },

        addFiles(files) {

            files.forEach(file => {

                const isValid = file.type === 'application/json' || file.name.endsWith('.json') ||

                    file.type === 'application/zip' || file.name.endsWith('.zip');

                if (isValid) {

                    if (!this.selectedFiles.find(f => f.name === file.name && f.size === file.size)) {

                        this.selectedFiles.push(file);

                    }

                } else {

                    showStatus(t('status_invalid_file_format', {name: file.name}), 'error');

                }

            });

            this.updateFileList();

        },

        updateFileList() {

            const list = document.getElementById(this.getElementId('FileList'));

            const section = document.getElementById(this.getElementId('FileListSection'));

            if (!list || !section) {

                console.warn('File list elements not found:', this.getElementId('FileList'));

                return;

            }

            if (this.selectedFiles.length === 0) {

                section.classList.add('hidden');

                return;

            }

            section.classList.remove('hidden');

            list.innerHTML = '';

            this.selectedFiles.forEach((file, index) => {

                const isZip = file.name.endsWith('.zip');

                const fileIcon = isZip ? '' : '';

                const fileType = isZip ? t('label_zip_pack') : t('label_json_file');

                const fileItem = document.createElement('div');

                fileItem.className = 'file-item';

                fileItem.innerHTML = `

                    <div>

                        <span class="file-name">${fileIcon} ${file.name}</span>

                        <span class="file-size">(${formatFileSize(file.size)}${fileType})</span>

                    </div>

                    <button class="remove-btn" onclick="${type === 'primary' ? 'removePrimaryFile' : 'removeFile'}(${index})">${t('action_delete')}</button>

                `;

                list.appendChild(fileItem);

            });

        },

        removeFile(index) {

            this.selectedFiles.splice(index, 1);

            this.updateFileList();

        },

        clearFiles() {

            this.selectedFiles = [];

            this.updateFileList();

        },

        async upload() {

            if (this.selectedFiles.length === 0) {

                showStatus(t('status_select_upload_first'), 'error');

                return;

            }

            const progressSection = document.getElementById(this.getElementId('UploadProgressSection'));

            const progressFill = document.getElementById(this.getElementId('ProgressFill'));

            const progressText = document.getElementById(this.getElementId('ProgressText'));

            progressSection.classList.remove('hidden');

            const formData = new FormData();

            this.selectedFiles.forEach(file => formData.append('files', file));

            if (this.selectedFiles.some(f => f.name.endsWith('.zip'))) {

                showStatus(t('status_uploading_zip'), 'info');

            }

            try {

                const xhr = new XMLHttpRequest();

                xhr.timeout = 300000; // 5 minutes

                xhr.upload.onprogress = (event) => {

                    if (event.lengthComputable) {

                        const percent = (event.loaded / event.total) * 100;

                        progressFill.style.width = percent + '%';

                        progressText.textContent = Math.round(percent) + '%';

                    }

                };

                xhr.onload = () => {

                    if (xhr.status === 200) {

                        try {

                            const data = JSON.parse(xhr.responseText);

                            showStatus(t('status_upload_success', {count: data.uploaded_count, type: type === 'primary' ? 'provider' : ''}), 'success');

                            this.clearFiles();

                            progressSection.classList.add('hidden');

                        } catch (e) {

                            showStatus(t('status_upload_invalid_response'), 'error');

                        }

                    } else {

                        try {

                            const error = JSON.parse(xhr.responseText);

                            showStatus(t('status_upload_failed_details', {error: error.detail || error.error || t('unknown_error')}), 'error');

                        } catch (e) {

                            showStatus(t('status_upload_failed_http', {status: xhr.status}), 'error');

                        }

                    }

                };

                xhr.onerror = () => {

                    showStatus(t('status_upload_aborted', {count: this.selectedFiles.length}), 'error');

                    progressSection.classList.add('hidden');

                };

                xhr.ontimeout = () => {

                    showStatus(t('status_upload_timeout'), 'error');

                    progressSection.classList.add('hidden');

                };

                xhr.open('POST', endpoint);

                xhr.setRequestHeader('Authorization', `Bearer ${AppState.authToken}`);

                xhr.send(formData);

            } catch (error) {

                showStatus(t('status_upload_failed_details', {error: error.message}), 'error');

            }

        }

    };

}

// =====================================================================

// Shared frontend utility functions

// =====================================================================

function showStatus(message, type = 'info') {

    const statusSection = document.getElementById('statusSection');

    if (statusSection) {

        if (window._statusTimeout) {

            clearTimeout(window._statusTimeout);

        }

        statusSection.innerHTML = `<div class="status ${type}">${message}</div>`;

        const statusDiv = statusSection.querySelector('.status');

        statusDiv.offsetHeight;

        statusDiv.classList.add('show');

        window._statusTimeout = setTimeout(() => {

            statusDiv.classList.add('fade-out');

            setTimeout(() => {

                statusSection.innerHTML = '';

            }, 300);

        }, 3000);

    } else {

        showMessageModal(t('dialog_tip'), message, 'info');

    }

}

async function updateEndpointUrls() {
    const origin = window.location.origin;

    const unifiedEl = document.getElementById('unifiedEndpointUrl');
    if (unifiedEl) unifiedEl.textContent = `${origin}/v1`;

    try {
        const response = await fetch('./api/auth/keys', { headers: getAuthHeaders() });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const apiKeyEl = document.getElementById('apiKey');
                const apiKey = data.api_key || '';
                if (apiKeyEl) apiKeyEl.value = apiKey;
                const regenerateBtn = document.getElementById('regenerateApiKeyBtn');
                if (regenerateBtn) {
                    const managedByEnv = Boolean(data.managed_by_env);
                    regenerateBtn.disabled = managedByEnv;
                    regenerateBtn.title = managedByEnv
                        ? 'API key is managed by the API_KEY environment variable'
                        : 'Regenerate API key';
                }
            }
        }
    } catch (e) {
        console.error("Failed to fetch API key", e);
    }
}
function cpUrl(element) {
    const text = element.textContent || element.innerText;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
        showStatus(t('copy_success'), 'success');
    }).catch(err => {
        showStatus(t('copy_fail'), 'error');
    });
}

function toggleKeyVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';

    // Toggle eye icons
    const iconHidden = btn.querySelector('.eye-icon-hidden');
    const iconVisible = btn.querySelector('.eye-icon-visible');
    if (iconHidden && iconVisible) {
        if (isHidden) {
            iconHidden.style.display = 'none';
            iconVisible.style.display = 'block';
        } else {
            iconHidden.style.display = 'block';
            iconVisible.style.display = 'none';
        }
    }
}

function copyInputValue(inputId) {
    const input = document.getElementById(inputId);
    if (!input || !input.value || input.value === '...') return;
    const copyPromise = navigator.clipboard.writeText(input.value);
    if (document.activeElement === input) {
        input.blur();
    }
    copyPromise.then(() => {
        showStatus(t('copy_success'), 'success');
    }).catch(err => {
        showStatus(t('copy_fail'), 'error');
    });
}

async function regenerateApiKey() {
    if (!(await showConfirmModal(t('confirm_regenerate_key', 'Are you sure you want to regenerate this API key? Previous key will become invalid immediately.')))) {
        return;
    }
    try {
        const response = await fetch('./api/auth/keys/reset', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (response.ok) {
            if (data.success) {
                const el = document.getElementById('apiKey');
                const apiKey = data.api_key || '';
                if (el) el.value = apiKey;
                showStatus(t('regenerate_success', 'API Key regenerated successfully'), 'success');
            } else {
                showStatus(data.error || 'Failed to regenerate key', 'error');
            }
        } else {
            showStatus(data.detail || data.message || 'Failed to regenerate key', 'error');
        }
    } catch (e) {
        console.error("Failed to regenerate key", e);
        showStatus('Network error occurred', 'error');
    }
}

function linkifyText(text) {

    if (!text) return text;

    const urlPattern = /(https?:\/\/[^\s"'<>()[\]{}]+)|(www\.[^\s"'<>()[\]{}]+)/gi;

    return text.replace(urlPattern, function(url) {

        let href = url;

        if (url.startsWith('www.')) {

            href = 'https://' + url;

        }

        return `<a href="${href}" target="_blank" rel="noopener noreferrer" class="message-link" onclick="event.stopPropagation()" title="${t('click_to_open_link')}\n${t('right_click_to_copy_link')}">${url}</a>`;

    });

}

function showMessageModal(title, message, type = 'info') {

    const modal = document.createElement('div');

    modal.className = 'message-modal-overlay';

    modal.innerHTML = `

        <div class="message-modal ${type}">

            <div class="message-modal-header">

                <h3>${title}</h3>

                <button class="message-modal-close" onclick="this.closest('.message-modal-overlay').remove()">&times;</button>

            </div>

            <div class="message-modal-body">

                ${linkifyText(message).replace(/\n/g, '<br>')}

            </div>

            <div class="message-modal-footer">

                <button class="message-modal-btn" onclick="this.closest('.message-modal-overlay').remove()">${t('btn_close')}</button>

            </div>

        </div>

    `;

    document.body.appendChild(modal);

    modal.addEventListener('click', function(e) {

        if (e.target === modal) {

            modal.remove();

        }

    });

    const escHandler = function(e) {

        if (e.key === 'Escape') {

            modal.remove();

            document.removeEventListener('keydown', escHandler);

        }

    };

    document.addEventListener('keydown', escHandler);

}

function renderDialogMessage(message) {

    return escapeHtml(String(message || '')).replace(/\n/g, '<br>');

}

function showConfirmModal(message, options = {}) {

    return new Promise((resolve) => {

        const modal = document.createElement('div');

        modal.className = 'message-modal-overlay';

        const title = options.title || t('confirm_action_title');

        const confirmLabel = options.confirmLabel || t('btn_confirm');

        const cancelLabel = options.cancelLabel || t('btn_cancel');

        modal.innerHTML = `

            <div class="message-modal confirm">

                <div class="message-modal-header">

                    <h3>${escapeHtml(title)}</h3>

                    <button type="button" class="message-modal-close" data-dialog-cancel>&times;</button>

                </div>

                <div class="message-modal-body">

                    ${renderDialogMessage(message)}

                </div>

                <div class="message-modal-footer">

                    <button type="button" class="message-modal-btn" data-dialog-cancel>${escapeHtml(cancelLabel)}</button>

                    <button type="button" class="message-modal-btn message-modal-btn-primary" data-dialog-confirm>${escapeHtml(confirmLabel)}</button>

                </div>

            </div>

        `;

        let settled = false;

        const close = (value) => {

            if (settled) return;

            settled = true;

            document.removeEventListener('keydown', escHandler);

            modal.remove();

            resolve(value);

        };

        const escHandler = (event) => {

            if (event.key === 'Escape') close(false);

        };

        modal.addEventListener('click', (event) => {

            if (event.target === modal || event.target.closest('[data-dialog-cancel]')) close(false);

            if (event.target.closest('[data-dialog-confirm]')) close(true);

        });

        document.addEventListener('keydown', escHandler);

        document.body.appendChild(modal);

        modal.querySelector('[data-dialog-confirm]')?.focus();

    });

}

function showPromptModal(message, options = {}) {

    return new Promise((resolve) => {

        const modal = document.createElement('div');

        modal.className = 'message-modal-overlay';

        const title = options.title || t('input_required_title');

        const confirmLabel = options.confirmLabel || t('btn_continue');

        const cancelLabel = options.cancelLabel || t('btn_cancel');

        const initialValue = options.value || '';

        const placeholder = options.placeholder || '';

        modal.innerHTML = `

            <div class="message-modal prompt">

                <div class="message-modal-header">

                    <h3>${escapeHtml(title)}</h3>

                    <button type="button" class="message-modal-close" data-dialog-cancel>&times;</button>

                </div>

                <div class="message-modal-body">

                    <div class="message-modal-prompt-copy">${renderDialogMessage(message)}</div>

                    <input type="text" class="message-modal-input">

                </div>

                <div class="message-modal-footer">

                    <button type="button" class="message-modal-btn" data-dialog-cancel>${escapeHtml(cancelLabel)}</button>

                    <button type="button" class="message-modal-btn message-modal-btn-primary" data-dialog-confirm>${escapeHtml(confirmLabel)}</button>

                </div>

            </div>

        `;

        let settled = false;

        const input = () => modal.querySelector('.message-modal-input');

        const close = (value) => {

            if (settled) return;

            settled = true;

            document.removeEventListener('keydown', escHandler);

            modal.remove();

            resolve(value);

        };

        const escHandler = (event) => {

            if (event.key === 'Escape') close(null);

        };

        modal.addEventListener('click', (event) => {

            if (event.target === modal || event.target.closest('[data-dialog-cancel]')) close(null);

            if (event.target.closest('[data-dialog-confirm]')) close(input()?.value || '');

        });

        modal.addEventListener('keydown', (event) => {

            if (event.key === 'Enter' && event.target === input()) close(input()?.value || '');

        });

        document.addEventListener('keydown', escHandler);

        document.body.appendChild(modal);

        const inputEl = input();

        if (inputEl) {

            inputEl.value = initialValue;

            inputEl.placeholder = placeholder;

            inputEl.focus();

        }

    });

}

function getAuthHeaders() {

    return {

        'Content-Type': 'application/json',

        'Authorization': `Bearer ${AppState.authToken}`

    };

}

function formatFileSize(bytes) {

    if (bytes < 1024) return bytes + ' B';

    if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';

    return Math.round(bytes / (1024 * 1024)) + ' MB';

}

function formatCooldownTime(remainingSeconds) {

    const hours = Math.floor(remainingSeconds / 3600);

    const minutes = Math.floor((remainingSeconds % 3600) / 60);

    const seconds = remainingSeconds % 60;

    if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;

    if (minutes > 0) return `${minutes}m ${seconds}s`;

    return `${seconds}s`;

}

// =====================================================================

// =====================================================================

function createCredCard(credInfo, manager) {

    const div = document.createElement('div');

    const { status, filename } = credInfo;

    const managerType = manager.type;

    div.className = status.disabled ? 'cred-card disabled' : 'cred-card';

    let statusBadges = '';

    statusBadges += status.disabled

        ? `<span class="status-badge disabled">${t('status_disabled')}</span>`

        : `<span class="status-badge enabled">${t('status_enabled')}</span>`;

    if (status.error_codes && status.error_codes.length > 0) {

        statusBadges += `<span class="error-codes">${t('error_code_prefix')} ${status.error_codes.join(', ')}</span>`;

        const autoBan = status.error_codes.filter(c => c === 400 || c === 403);

        if (autoBan.length > 0 && status.disabled) {

            statusBadges += '<span class="status-badge danger">Auto-ban</span>';

        }

    } else {

        statusBadges += `<span class="status-badge success">${t('status_no_errors')}</span>`;

    }

    if (managerType !== 'primary' && credInfo.preview !== undefined) {

        if (credInfo.preview) {

            statusBadges += `<span class="status-badge success" title="${t('preview_supported_title')}">Preview: ON</span>`;

        } else {

            statusBadges += `<span class="status-badge muted" title="${t('preview_not_supported_title')}">Preview: OFF</span>`;

        }

    }

    const tier = (credInfo.tier || 'pro').toString().toLowerCase();

    const tierLabel = tier.toUpperCase();

    const tierClass = tier === 'ultra' ? 'tier-ultra' : (tier === 'free' ? 'tier-free' : 'tier-pro');

    statusBadges += `<span class="status-badge ${tierClass}" title="${t('tier_badge_title')}: ${tierLabel}">Tier: ${tierLabel}</span>`;

    if (managerType === 'primary') {

        if (credInfo.enable_credit) {

            statusBadges += `<span class="status-badge credit-on" title="${t('credit_enabled_title')}">Credit: ON</span>`;

        } else {

            statusBadges += `<span class="status-badge credit-off" title="${t('credit_disabled_title')}">Credit: OFF</span>`;

        }

    }

    if (credInfo.model_cooldowns && Object.keys(credInfo.model_cooldowns).length > 0) {

        const currentTime = Date.now() / 1000;

        const activeCooldowns = Object.entries(credInfo.model_cooldowns)

            .filter(([, until]) => until > currentTime)

            .map(([model, until]) => {

                const remaining = Math.max(0, Math.floor(until - currentTime));

                const shortModel = model.replace('gemini-', '').replace('-exp', '')

                    .replace('2.0-', '2-').replace('1.5-', '1.5-');

                return {

                    model: shortModel,

                    time: formatCooldownTime(remaining).replace(/s$/, '').replace(/ /g, ''),

                    fullModel: model

                };

            });

        if (activeCooldowns.length > 0) {

            activeCooldowns.slice(0, 2).forEach(item => {

                statusBadges += `<span class="cooldown-badge" title="${t('model_title')}: ${item.fullModel}">Cooldown ${item.model}: ${item.time}</span>`;

            });

            if (activeCooldowns.length > 2) {

                const remaining = activeCooldowns.length - 2;

                const remainingModels = activeCooldowns.slice(2).map(i => `${i.fullModel}: ${i.time}`).join('\n');

                statusBadges += `<span class="cooldown-badge" title="${t('other_models_title')}:\n${remainingModels}">+${remaining}</span>`;

            }

        }

    }

    const pathId = (managerType === 'primary' ? 'primary_' : '') + btoa(encodeURIComponent(filename)).replace(/[+/=]/g, '_');

    const actionButtons = `

        ${status.disabled

            ? `<button class="cred-btn enable" data-filename="${filename}" data-action="enable">${t('action_enable')}</button>`

            : `<button class="cred-btn disable" data-filename="${filename}" data-action="disable">${t('action_disable')}</button>`

        }

        <button class="cred-btn view" onclick="toggle${managerType === 'primary' ? 'Primary' : ''}CredDetails('${pathId}')">${t('btn_view_content')}</button>

        <button class="cred-btn download" onclick="download${managerType === 'primary' ? 'Primary' : ''}Cred('${filename}')">${t('btn_download')}</button>

        <button class="cred-btn email" onclick="fetch${managerType === 'primary' ? 'Primary' : ''}UserEmail('${filename}')">${t('btn_view_email')}</button>

        ${managerType === 'primary' ? `<button class="cred-btn" onclick="togglePrimaryQuotaDetails('${pathId}')" title="${t('btn_view_quota_title')}">${t('btn_view_quota')}</button>` : ''}

        ${managerType === 'primary' ? (credInfo.enable_credit

            ? `<button class="cred-btn" data-filename="${filename}" data-action="disable_credit" title="${t('btn_disable_credit_title')}">${t('btn_disable_credit')}</button>`

            : `<button class="cred-btn" data-filename="${filename}" data-action="enable_credit" title="${t('btn_enable_credit_title')}">${t('btn_enable_credit')}</button>`

        ) : ''}

        ${managerType !== 'primary' ? `<button class="cred-btn" onclick="configurePreviewChannel('${filename}')" title="${t('btn_setup_preview_title')}">${t('btn_setup_preview')}</button>` : ''}

        <button class="cred-btn" onclick="verify${managerType === 'primary' ? 'Primary' : ''}ProjectId('${filename}')" title="${t('btn_verify_id_title')}">${t('btn_verify_id')}</button>

        <button class="cred-btn" onclick="test${managerType === 'primary' ? 'Primary' : ''}Credential('${filename}')" title="${t('btn_message_test_title')}">${t('btn_message_test')}</button>

        <button class="cred-btn" onclick="toggle${managerType === 'primary' ? 'Primary' : ''}ErrorDetails('${pathId}')" title="${t('btn_view_errors_title')}">${t('btn_view_errors')}</button>

        <button class="cred-btn delete" data-filename="${filename}" data-action="delete">${t('action_delete')}</button>

    `;

    const emailInfo = credInfo.user_email

        ? `<div class="cred-email">${credInfo.user_email}</div>`

        : `<div class="cred-email empty">${t('email_not_fetched')}</div>`;

    const checkboxClass = manager.getElementId('file-checkbox');

    div.innerHTML = `

        <div class="cred-header">

            <div class="cred-title-row">

                <input type="checkbox" class="${checkboxClass}" data-filename="${filename}" onchange="toggle${managerType === 'primary' ? 'Primary' : ''}FileSelection('${filename}')">

                <div>

                    <div class="cred-filename">${filename}</div>

                    ${emailInfo}

                </div>

            </div>

            <div class="cred-status">${statusBadges}</div>

        </div>

        <div class="cred-actions">${actionButtons}</div>

        <div class="cred-details" id="details-${pathId}">

            <div class="cred-content" data-filename="${filename}" data-loaded="false">${t('click_view_content_to_load')}</div>

        </div>

        <div class="cred-details" id="errors-${pathId}">

            <div class="cred-content error-content" data-filename="${filename}" data-loaded="false">${t('click_view_errors_to_load')}</div>

        </div>

        ${managerType === 'primary' ? `

        <div class="cred-quota-details" id="quota-${pathId}">

            <div class="cred-quota-content" data-filename="${filename}" data-loaded="false">

                ${t('click_view_quota_to_load')}

            </div>

        </div>

        ` : ''}

    `;

    div.querySelectorAll('[data-filename][data-action]').forEach(button => {

        button.addEventListener('click', async function () {

            const fn = this.getAttribute('data-filename');

            const action = this.getAttribute('data-action');

            if (action === 'delete') {

                if (!(await showConfirmModal(t('confirm_delete_cred', {filename: fn})))) return;

            }

            manager.action(fn, action);


        });

    });

    return div;

}

// =====================================================================

// =====================================================================

async function toggleCredDetails(pathId) {

    await toggleCredDetailsCommon(pathId, AppState.creds);

}

async function togglePrimaryCredDetails(pathId) {

    await toggleCredDetailsCommon(pathId, AppState.primaryCreds);

}

async function toggleCredDetailsCommon(pathId, manager) {

    const details = document.getElementById('details-' + pathId);

    if (!details) return;

    const isShowing = details.classList.toggle('show');

    if (isShowing) {

        const contentDiv = details.querySelector('.cred-content');

        const filename = contentDiv.getAttribute('data-filename');

        const loaded = contentDiv.getAttribute('data-loaded');

        if (loaded === 'false' && filename) {

            contentDiv.textContent = t('status_loading_file_content');

            try {

                const modeParam = manager.type === 'primary' ? 'mode=provider' : 'mode=code_assist';

                const endpoint = `./api/creds/detail/${encodeURIComponent(filename)}?${modeParam}`;

                const response = await fetch(endpoint, { headers: getAuthHeaders() });

                const data = await response.json();

                if (response.ok && data.content) {

                    contentDiv.textContent = JSON.stringify(data.content, null, 2);

                    contentDiv.setAttribute('data-loaded', 'true');

                } else {

                    contentDiv.textContent = `${t('unable_to_load_file_content')} ${data.error || data.detail || t('unknown_error')}`;

                }

            } catch (error) {

                contentDiv.textContent = `${t('unable_to_load_file_content')} ${error.message}`;

            }

        }

    }

}

// =====================================================================

// =====================================================================

async function refreshSetupStatus() {

    try {

        const response = await fetch('./api/auth/setup/status');

        const data = await response.json();

        AppState.setupRequired = Boolean(data.setup_required);

        if (AppState.setupRequired) {

            localStorage.removeItem('auth_token');

            AppState.authToken = '';

        }

        return AppState.setupRequired;

    } catch (error) {

        AppState.setupRequired = false;

        return false;

    }

}

async function completeInitialSetup() {

    const password = document.getElementById('setupPassword')?.value || '';

    const confirmPassword = document.getElementById('setupPasswordConfirm')?.value || '';

    if (password.length < 8) {

        showStatus('Password must be at least 8 characters.', 'error');

        return;

    }

    if (password !== confirmPassword) {

        showStatus('Passwords do not match.', 'error');

        return;

    }

    try {

        const response = await fetch('./api/auth/setup', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ password, confirm_password: confirmPassword })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.setupRequired = false;

            AppState.authToken = data.token;

            localStorage.setItem('auth_token', AppState.authToken);

            showStatus('Initial setup completed.', 'success');

            navigate('/dashboard');

            await fetchAndDisplayVersion();

        } else {

            showStatus(data.detail || data.error || 'Initial setup failed.', 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

function handleSetupEnter(event) {

    if (event.key === 'Enter') completeInitialSetup();

}

async function login() {

    const password = document.getElementById('loginPassword').value;

    if (!password) {

        showStatus(t('please_enter_the_password'), 'error');

        return;

    }

    try {

        const response = await fetch('./api/auth/login', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ password })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.authToken = data.token;

            localStorage.setItem('auth_token', AppState.authToken);

            showStatus(t('login_successful_dup'), 'success');

            navigate('/dashboard');

            await fetchAndDisplayVersion();

        } else {

            if (response.status === 428) {

                AppState.setupRequired = true;

                navigate('/setup', false);

                return;

            }

            if (response.status === 401) {

                showStatus(t('login_failed_incorrect_password'), 'error');

                return;

            }

            showStatus(data.detail || data.error || t('login_failed'), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function autoLogin() {

    if (AppState.setupRequired) {

        navigate('/setup', false);

        return false;

    }

    const savedToken = localStorage.getItem('auth_token');

    if (!savedToken) {

        navigate('/login', false);

        return false;

    }

    AppState.authToken = savedToken;

    try {

        const response = await fetch('./api/config/get', {

            headers: {

                'Content-Type': 'application/json',

                'Authorization': `Bearer ${AppState.authToken}`

            }

        });

        if (response.ok) {

            // showStatus(t('autologin_successful'), 'success');

            navigate(window.location.pathname, false);

            return true;

        } else {

            localStorage.removeItem('auth_token');

            AppState.authToken = '';

            navigate('/login', false);

            return false;

        }

    } catch (error) {

        localStorage.removeItem('auth_token');

        AppState.authToken = '';

        navigate('/login', false);

        return false;

    }

}

function logout() {

    localStorage.removeItem('auth_token');

    AppState.authToken = '';

    showStatus(t('logged_out'), 'info');

    const passwordInput = document.getElementById('loginPassword');

    if (passwordInput) passwordInput.value = '';

    navigate('/login', false);

}

function handlePasswordEnter(event) {

    if (event.key === 'Enter') login();

}

// =====================================================================

// =====================================================================

function updateTabSlider(targetTab, animate = true) {

    const slider = document.querySelector('.tab-slider');

    const tabs = document.querySelector('.tabs');

    if (!slider || !tabs || !targetTab) return;

    const tabLeft = targetTab.offsetLeft;

    const tabWidth = targetTab.offsetWidth;

    const tabsWidth = tabs.scrollWidth;

    const rightValue = tabsWidth - tabLeft - tabWidth;

    if (animate) {

        slider.style.left = `${tabLeft}px`;

        slider.style.right = `${rightValue}px`;

    } else {

        slider.style.transition = 'none';

        slider.style.left = `${tabLeft}px`;

        slider.style.right = `${rightValue}px`;

        slider.offsetHeight;

        slider.style.transition = '';

    }

}

function initTabSlider() {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) {

        updateTabSlider(activeTab, false);

    }

}

document.addEventListener('DOMContentLoaded', initTabSlider);

window.addEventListener('resize', () => {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) updateTabSlider(activeTab, false);

});

function switchTab(tabName) {

    const route = TAB_MAP[tabName] || '/dashboard';

    navigate(route, true);

}

function triggerTabDataLoad(tabName) {

    if (tabName === 'dashboard') {

        refreshUsageStats();

        updateEndpointUrls();

    }

    if (tabName === 'manage') {
        AppState.primaryCreds.refresh();
    }

    if (tabName === 'config') loadConfig();

    if (tabName === 'logs') connectWebSocket();

}

// =====================================================================

// =====================================================================

async function startAuth() {

    const projectId = document.getElementById('projectId').value.trim();

    AppState.currentProjectId = projectId || null;

    const btn = document.getElementById('getAuthBtn');

    btn.disabled = true;

    btn.textContent = t('fetching_authentication_link');

    try {

        const requestBody = projectId ? { project_id: projectId } : {};

        showStatus(projectId ? t('generating_authentication_link_usin') : t('attempting_to_autodetect_project_id'), 'info');

        const response = await fetch('./api/auth/start', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify(requestBody)

        });

        const data = await response.json();

        if (response.ok) {

            document.getElementById('authUrl').href = data.auth_url;

            document.getElementById('authUrl').textContent = data.auth_url;

            document.getElementById('authUrlSection').classList.remove('hidden');

            const msg = data.auto_project_detection

                ? t('authentication_link_generated_proje_dup_dup')

                : t('authentication_link_generated_proje', {data_detected_project_id: data.detected_project_id});

            showStatus(msg, 'info');

            AppState.authInProgress = true;

        } else {

            showStatus(t('error_dataerror_failed_to_fetch_aut', {data_error: data.error || t('failed_to_fetch_authentication_link')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_authentication_link');

    }

}

async function getCredentials() {

    if (!AppState.authInProgress) {

        showStatus(t('please_fetch_the_authentication_lin'), 'error');

        return;

    }

    const btn = document.getElementById('getCredsBtn');

    btn.disabled = true;

    btn.textContent = t('waiting_for_oauth_callback');

    try {

        showStatus(t('waiting_for_oauth_callback_this_may'), 'info');

        const requestBody = AppState.currentProjectId ? { project_id: AppState.currentProjectId } : {};

        const response = await fetch('./api/auth/callback', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify(requestBody)

        });

        const data = await response.json();

        if (response.ok) {

            document.getElementById('credentialsContent').textContent = JSON.stringify(data.credentials, null, 2);

            const msg = data.auto_detected_project

                ? t('authentication_successful_project_i_dup', {data_credentials_project_id: data.credentials.project_id, data_file_path: data.file_path})

                : t('authentication_successful_file_save', {data_file_path: data.file_path});

            showStatus(msg, 'success');

            document.getElementById('credentialsSection').classList.remove('hidden');

            AppState.authInProgress = false;

        } else if (data.requires_project_selection && data.available_projects) {

            let projectOptions = t('please_select_a_projectnn');

            data.available_projects.forEach((project, index) => {

                projectOptions += `${index + 1}. ${project.name} (${project.project_id})\n`;

            });

            projectOptions += t('nplease_enter_index_1dataavailable', {data_available_projects_length: data.available_projects.length});

            const selection = await showPromptModal(projectOptions);

            const projectIndex = parseInt(selection) - 1;

            if (projectIndex >= 0 && projectIndex < data.available_projects.length) {

                AppState.currentProjectId = data.available_projects[projectIndex].project_id;

                btn.textContent = t('retry_fetching_authentication_file');

                showStatus(t('retry_using_the_selected_project'), 'info');

                setTimeout(() => getCredentials(), 1000);

                return;

            } else {

                showStatus(t('invalid_selection_please_restart_th'), 'error');

            }

        } else if (data.requires_manual_project_id) {

            const userProjectId = await showPromptModal(t('unable_to_autodetect_project_id_ple'));

            if (userProjectId && userProjectId.trim()) {

                AppState.currentProjectId = userProjectId.trim();

                btn.textContent = t('retry_fetching_authentication_file');

                showStatus(t('retrying_with_manually_entered_proj'), 'info');

                setTimeout(() => getCredentials(), 1000);

                return;

            } else {

                showStatus(t('project_id_required_to_complete_aut'), 'error');

            }

        } else {

            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: data.error || t('failed_to_retrieve_authentication_f_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_authentication_file');

    }

}

// =====================================================================

// =====================================================================

async function startPrimaryAuth() {

    const btn = document.getElementById('getPrimaryAuthBtn');

    btn.disabled = true;

    btn.textContent = t('generating_authentication_link');

    try {

        showStatus(t('generating_primary_authenticati'), 'info');

        const response = await fetch('./api/auth/start', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ mode: 'provider' })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.primaryAuthState = data.state;

            AppState.primaryAuthInProgress = true;

            const authUrlLink = document.getElementById('primaryAuthUrl');

            authUrlLink.href = data.auth_url;

            authUrlLink.textContent = data.auth_url;

            document.getElementById('primaryAuthUrlSection').classList.remove('hidden');

            showStatus(t('primary_authentication_link_gen'), 'success');

        } else {

            showStatus(t('error_dataerror_failed_to_generate', {data_error: data.error || t('failed_to_generate_authentication_l_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_primary_authentication_link');

    }

}

async function getPrimaryCredentials() {

    if (!AppState.primaryAuthInProgress) {

        showStatus(t('please_obtain_the_primary_authe'), 'error');

        return;

    }

    const btn = document.getElementById('getPrimaryCredsBtn');

    btn.disabled = true;

    btn.textContent = t('waiting_for_oauth_callback');

    try {

        showStatus(t('waiting_for_primary_oauth_callb'), 'info');

        const response = await fetch('./api/auth/callback', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ mode: 'provider' })

        });

        const data = await response.json();

        if (response.ok) {

            document.getElementById('primaryCredsContent').textContent = JSON.stringify(data.credentials, null, 2);

            document.getElementById('primaryCredsSection').classList.remove('hidden');

            AppState.primaryAuthInProgress = false;

            showStatus(t('primary_authentication_successf_dup', {data_file_path: data.file_path}), 'success');

        } else {

            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: data.error || t('failed_to_retrieve_authentication_f_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('fetch_primary_credentials');

    }

}

function downloadPrimaryCredentials() {

    const content = document.getElementById('primaryCredsContent').textContent;

    const blob = new Blob([content], { type: 'application/json' });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = `primary-credential-${Date.now()}.json`;

    a.click();

    window.URL.revokeObjectURL(url);

}

// =====================================================================

// =====================================================================

function toggleProjectIdSection() {

    const section = document.getElementById('projectIdSection');

    const icon = document.getElementById('projectIdToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(90deg)';

        icon.textContent = '';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '';

    }

}

function toggleCallbackUrlSection() {

    const section = document.getElementById('callbackUrlSection');

    const icon = document.getElementById('callbackUrlToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(180deg)';

        icon.textContent = '';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '';

    }

}

function togglePrimaryCallbackUrlSection() {

    const section = document.getElementById('primaryCallbackUrlSection');

    const icon = document.getElementById('primaryCallbackUrlToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(180deg)';

        icon.textContent = '';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '';

    }

}

async function processCallbackUrl() {

    const callbackUrl = document.getElementById('callbackUrlInput').value.trim();

    if (!callbackUrl) {

        showStatus(t('please_enter_the_callback_url'), 'error');

        return;

    }

    if (!callbackUrl.startsWith('http://') && !callbackUrl.startsWith('https://')) {

        showStatus(t('please_enter_a_valid_url_starting_w'), 'error');

        return;

    }

    if (!callbackUrl.includes('code=') || !callbackUrl.includes('state=')) {

        showStatus(t('this_is_not_a_valid_callback_url_pl'), 'error');

        return;

    }

    showStatus(t('retrieving_credentials_from_callbac'), 'info');

    try {

        const projectId = document.getElementById('projectId')?.value.trim() || null;

        const response = await fetch('./api/auth/callback-url', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ callback_url: callbackUrl, project_id: projectId })

        });

        const result = await response.json();

        if (result.credentials) {

            showStatus(result.message || t('credentials_fetched_successfully_fr'), 'success');

            document.getElementById('credentialsContent').innerHTML = '<pre>' + JSON.stringify(result.credentials, null, 2) + '</pre>';

            document.getElementById('credentialsSection').classList.remove('hidden');

        } else if (result.requires_manual_project_id) {

            showStatus(t('manual_project_id_specification_req'), 'error');

        } else if (result.requires_project_selection) {

            let msg = t('brstrongavailable_projectsstrongbr');

            result.available_projects.forEach(p => {

                msg += `- ${p.name} (ID: ${p.project_id})<br>`;

            });

            showStatus(t('multiple_projects_detected_please_s') + msg, 'error');

        } else {

            showStatus(result.error || t('failed_to_fetch_credentials_from_ca'), 'error');

        }

        document.getElementById('callbackUrlInput').value = '';

    } catch (error) {

        showStatus(t('failed_to_retrieve_credentials_from_dup', {error_message: error.message}), 'error');

    }

}

async function processPrimaryCallbackUrl() {

    const callbackUrl = document.getElementById('primaryCallbackUrlInput').value.trim();

    if (!callbackUrl) {

        showStatus(t('please_enter_the_callback_url'), 'error');

        return;

    }

    if (!callbackUrl.startsWith('http://') && !callbackUrl.startsWith('https://')) {

        showStatus(t('please_enter_a_valid_url_starting_w'), 'error');

        return;

    }

    if (!callbackUrl.includes('code=') || !callbackUrl.includes('state=')) {

        showStatus(t('this_is_not_a_valid_callback_url_pl_dup'), 'error');

        return;

    }

    showStatus(t('retrieving_primary_credentials'), 'info');

    try {

        const response = await fetch('./api/auth/callback-url', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ callback_url: callbackUrl, mode: 'provider' })

        });

        const result = await response.json();

        if (result.credentials) {

            showStatus(result.message || t('primary_credentials_successfull'), 'success');

            document.getElementById('primaryCredsContent').textContent = JSON.stringify(result.credentials, null, 2);

            document.getElementById('primaryCredsSection').classList.remove('hidden');

        } else {

            showStatus(result.error || t('failed_to_retrieve_primary_cred'), 'error');

        }

        document.getElementById('primaryCallbackUrlInput').value = '';

    } catch (error) {

        showStatus(t('failed_to_retrieve_primary_cred_dup', {error_message: error.message}), 'error');

    }

}

// =====================================================================

// =====================================================================

function refreshCredsStatus() { AppState.creds.refresh(); }

function applyStatusFilter() { AppState.creds.applyStatusFilter(); }

function changePage(direction) { AppState.creds.changePage(direction); }

function changePageSize() { AppState.creds.changePageSize(); }

function toggleFileSelection(filename) {

    if (AppState.creds.selectedFiles.has(filename)) {

        AppState.creds.selectedFiles.delete(filename);

    } else {

        AppState.creds.selectedFiles.add(filename);

    }

    AppState.creds.updateBatchControls();

}

function toggleSelectAll() {

    const checkbox = document.getElementById('selectAllCheckbox');

    const checkboxes = document.querySelectorAll('.file-checkbox');

    if (checkbox.checked) {

        checkboxes.forEach(cb => AppState.creds.selectedFiles.add(cb.getAttribute('data-filename')));

    } else {

        AppState.creds.selectedFiles.clear();

    }

    checkboxes.forEach(cb => cb.checked = checkbox.checked);

    AppState.creds.updateBatchControls();

}

function batchAction(action) { AppState.creds.batchAction(action); }

function downloadCred(filename) {

    fetch(`./api/creds/download/${filename}`, { headers: { 'Authorization': `Bearer ${AppState.authToken}` } })

        .then(r => r.ok ? r.blob() : Promise.reject())

        .then(blob => {

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = filename;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('status_download_success', {name: filename}), 'success');

        })

        .catch(() => showStatus(t('download_failed_filename', {filename: filename}), 'error'));

}

async function downloadAllCreds() {

    try {

        const response = await fetch('./api/creds/download-all', {

            headers: { 'Authorization': `Bearer ${AppState.authToken}` }

        });

        if (response.ok) {

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = 'credentials.zip';

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('all_credential_files_have_been_down'), 'success');

        }

    } catch (error) {

        showStatus(t('failed_to_download_package_errormes', {error_message: error.message}), 'error');

    }

}

function refreshPrimaryCredsList() { AppState.primaryCreds.refresh(); }

function applyPrimaryStatusFilter() { AppState.primaryCreds.applyStatusFilter(); }

function changePrimaryPage(direction) { AppState.primaryCreds.changePage(direction); }

function changePrimaryPageSize() { AppState.primaryCreds.changePageSize(); }

function togglePrimaryFileSelection(filename) {

    if (AppState.primaryCreds.selectedFiles.has(filename)) {

        AppState.primaryCreds.selectedFiles.delete(filename);

    } else {

        AppState.primaryCreds.selectedFiles.add(filename);

    }

    AppState.primaryCreds.updateBatchControls();

}

function toggleSelectAllPrimary() {

    const checkbox = document.getElementById('selectAllPrimaryCheckbox');

    const checkboxes = document.querySelectorAll('.primaryFile-checkbox');

    if (checkbox.checked) {

        checkboxes.forEach(cb => AppState.primaryCreds.selectedFiles.add(cb.getAttribute('data-filename')));

    } else {

        AppState.primaryCreds.selectedFiles.clear();

    }

    checkboxes.forEach(cb => cb.checked = checkbox.checked);

    AppState.primaryCreds.updateBatchControls();

}

function batchPrimaryAction(action) { AppState.primaryCreds.batchAction(action); }

function downloadPrimaryCred(filename) {

    fetch(`./api/creds/download/${filename}?mode=provider`, { headers: getAuthHeaders() })

        .then(r => r.ok ? r.blob() : Promise.reject())

        .then(blob => {

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = filename;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('downloaded_filename', {filename: filename}), 'success');

        })

        .catch(() => showStatus(t('download_failed_filename', {filename: filename}), 'error'));

}

async function deletePrimaryCred(filename) {

    if (await showConfirmModal(t('are_you_sure_you_want_to_delete_fil_dup', {filename: filename}))) {

        AppState.primaryCreds.action(filename, 'delete');

    }

}

async function downloadAllPrimaryCreds() {

    try {

        const response = await fetch('./api/creds/download-all?mode=provider', { headers: getAuthHeaders() });

        if (response.ok) {

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = `primary_credentials_${Date.now()}.zip`;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('all_primary_credentials_packed'), 'success');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

function handleFileSelect(event) { AppState.uploadFiles.handleFileSelect(event); }

function removeFile(index) { AppState.uploadFiles.removeFile(index); }

function clearFiles() { AppState.uploadFiles.clearFiles(); }

function uploadFiles() { AppState.uploadFiles.upload(); }

function handlePrimaryFileSelect(event) { AppState.primaryUploadFiles.handleFileSelect(event); }

function handlePrimaryFileDrop(event) {

    event.preventDefault();

    event.currentTarget.style.borderColor = '#007bff';

    event.currentTarget.style.backgroundColor = '#f8f9fa';

    AppState.primaryUploadFiles.addFiles(Array.from(event.dataTransfer.files));

}

function removePrimaryFile(index) { AppState.primaryUploadFiles.removeFile(index); }

function clearPrimaryFiles() { AppState.primaryUploadFiles.clearFiles(); }

function uploadPrimaryFiles() { AppState.primaryUploadFiles.upload(); }

function updateEmailDisplay(filename, email, managerType = 'normal') {

    const containerId = managerType === 'primary' ? 'primaryCredsList' : 'credsList';

    const container = document.getElementById(containerId);

    if (!container) return false;

    const checkbox = container.querySelector(`input[data-filename="${filename}"]`);

    if (!checkbox) return false;

    const card = checkbox.closest('.cred-card');

    if (!card) return false;

    const emailDiv = card.querySelector('.cred-email');

    if (emailDiv) {

        emailDiv.textContent = email;

        emailDiv.style.color = '#666';

        emailDiv.style.fontStyle = 'normal';

        return true;

    }

    return false;

}

async function fetchUserEmail(filename) {

    try {

        showStatus(t('retrieving_user_emails'), 'info');

        const response = await fetch(`./api/creds/fetch-email/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.user_email) {

            showStatus(t('successfully_retrieved_email_dataus', {data_user_email: data.user_email}), 'success');

            updateEmailDisplay(filename, data.user_email, 'normal');

        } else {

            showStatus(data.message || t('unable_to_fetch_user_email'), 'error');

        }

    } catch (error) {

        showStatus(t('failed_to_get_email_errormessage', {error_message: error.message}), 'error');

    }

}

async function fetchPrimaryUserEmail(filename) {

    try {

        showStatus(t('retrieving_user_emails'), 'info');

        const response = await fetch(`./api/creds/fetch-email/${encodeURIComponent(filename)}?mode=provider`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.user_email) {

            showStatus(t('successfully_retrieved_email_dataus', {data_user_email: data.user_email}), 'success');

            updateEmailDisplay(filename, data.user_email, 'primary');

        } else {

            showStatus(data.message || t('unable_to_fetch_user_email'), 'error');

        }

    } catch (error) {

        showStatus(t('failed_to_get_email_errormessage', {error_message: error.message}), 'error');

    }

}

async function verifyProjectId(filename) {

    try {

        showStatus(t('verifying_project_id_please_wait'), 'info');

        const response = await fetch(`./api/creds/verify-project/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            const tierLine = data.subscription_tier ? `\nTier: ${data.subscription_tier}` : '';

            const creditLine = data.credit_amount !== undefined && data.credit_amount !== null

                ? t('ncredit_datacredit_amount', {data_credit_amount: data.credit_amount})

                : '';

            const successMsg = t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message});

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal(t('verification_successful'), t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message}), 'success');

            await AppState.creds.refresh();

        } else {

            const errorMsg = data.message || t('verification_failed');

            showStatus(` ${errorMsg}`, 'error');

            showMessageModal(t('verification_failed'), t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(` ${errorMsg}`, 'error');

        showMessageModal(t('verification_failed'), ` ${errorMsg}`, 'error');

    }

}

async function verifyPrimaryProjectId(filename) {

    try {

        showStatus(t('verifying_primary_project_id_pl'), 'info');

        const response = await fetch(`./api/creds/verify-project/${encodeURIComponent(filename)}?mode=provider`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            const tierLine = data.subscription_tier ? `\nTier: ${data.subscription_tier}` : '';

            const creditLine = data.credit_amount !== undefined && data.credit_amount !== null

                ? t('ncredit_datacredit_amount', {data_credit_amount: data.credit_amount})

                : '';

            const successMsg = t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message});

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal(t('verification_successful'), t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message}), 'success');

            await AppState.primaryCreds.refresh();

        } else {

            const errorMsg = data.message || t('verification_failed');

            showStatus(` ${errorMsg}`, 'error');

            showMessageModal(t('verification_failed'), t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(` ${errorMsg}`, 'error');

        showMessageModal(t('verification_failed'), ` ${errorMsg}`, 'error');

    }

}

async function testCredential(filename) {

    try {

        showStatus(t('testing_credentials_please_wait'), 'info');

        const response = await fetch(`./api/creds/test/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.status === 200) {

            const successMsg = `${t('status_action_success', {action: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n${t('log_status_label')} ${data.message || t('credential_available')} (${data.status_code || 200})`;

            showStatus(t('test_successful'), 'success');

            showMessageModal(t('test_successful_dup'), successMsg, 'success');

            await AppState.creds.refresh();

        }

        else {

            let errorDetails = `${t('status_action_failed', {error: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n`;

            if (data.error) {

                try {

                    const errorObj = JSON.parse(data.error);

                    errorDetails += t('nerror_detailsnjsonstringifyerrorob', {JSON_stringify_errorObj__null__2: JSON.stringify(errorObj, null, 2)});

                } catch {

                    errorDetails += t('nerror_detailsndataerror', {data_error: data.error});

                }

            } else {

                errorDetails += t('error_code_datastatus_code_response', {data_status_code____response_status: data.status_code || response.status});

            }

            showStatus(`Test failed: ${data.message || `${t('error_code_prefix')} ${data.status_code || response.status}`}`, 'error');

            showMessageModal(t('test_failed'), errorDetails, 'error');

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal(t('test_failed'), errorMsg, 'error');

    }

}

async function testPrimaryCredential(filename) {

    try {

        showStatus(t('testing_primary_credentials_ple'), 'info');

        const response = await fetch(`./api/creds/test/${encodeURIComponent(filename)}?mode=provider`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.status === 200) {

            const successMsg = `${t('status_action_success', {action: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n${t('log_status_label')} ${data.message || t('primary_credential_valid')} (${data.status_code || 200})`;

            showStatus(t('test_successful'), 'success');

            showMessageModal(t('test_successful_dup'), successMsg, 'success');

            await AppState.primaryCreds.refresh();

        }

        else {

            let errorDetails = `${t('status_action_failed', {error: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n`;

            if (data.error) {

                try {

                    const errorObj = JSON.parse(data.error);

                    errorDetails += t('nerror_detailsnjsonstringifyerrorob', {JSON_stringify_errorObj__null__2: JSON.stringify(errorObj, null, 2)});

                } catch {

                    errorDetails += t('nerror_detailsndataerror', {data_error: data.error});

                }

            } else {

                errorDetails += t('error_code_datastatus_code_response', {data_status_code____response_status: data.status_code || response.status});

            }

            showStatus(`Test failed: ${data.message || `${t('error_code_prefix')} ${data.status_code || response.status}`}`, 'error');

            showMessageModal(t('test_failed'), errorDetails, 'error');

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal(t('test_failed'), errorMsg, 'error');

    }

}

async function configurePreviewChannel(filename) {

    try {

        showStatus(t('configuring_preview_channel_please'), 'info');

        const response = await fetch(`./api/creds/configure-preview/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            const successMsg = `${t('status_action_success', {action: t('btn_setup_preview')})}\n${t('table_filename')}: ${filename}\n${t('log_status_label')} ${data.message}`;

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal(t('preview_channel_configuration_succe_dup'), `${t('status_action_success', {action: t('btn_setup_preview')})}\n\n${t('table_filename')}: ${filename}\n\n${data.message}\n\nSetting ID: ${data.setting_id || 'N/A'}\nBinding ID: ${data.binding_id || 'N/A'}`, 'success');

            await AppState.creds.refresh();

        } else {

            const errorMsg = data.message || t('configuration_failed');

            const errorDetail = data.error || '';

            const step = data.step || '';

            let alertMsg = `${t('status_action_failed', {error: t('btn_setup_preview')})}\n\n${t('table_filename')}: ${filename}\n\n${errorMsg}`;

            if (step) {

                alertMsg += t('nfailed_step_step', {step: step});

            }

            if (errorDetail) {

                alertMsg += t('nnerror_details_errordetail', {errorDetail: errorDetail});

            }

            showStatus(errorMsg, 'error');

            showMessageModal(t('preview_channel_configuration_faile_dup'), alertMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_configure_preview_channel', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal(t('failed_to_configure_preview_channel_dup'), errorMsg, 'error');

    }

}

async function togglePrimaryQuotaDetails(pathId) {

    const quotaDetails = document.getElementById('quota-' + pathId);

    if (!quotaDetails) return;

    const isShowing = quotaDetails.style.display === 'block';

    if (isShowing) {

        quotaDetails.style.display = 'none';

    } else {

        quotaDetails.style.display = 'block';

        const contentDiv = quotaDetails.querySelector('.cred-quota-content');

        const filename = contentDiv.getAttribute('data-filename');

        if (filename) {

            contentDiv.innerHTML = t('div_styletextalign_center_padding_2_dup_dup_dup_dup_dup');

            try {

                const response = await fetch(`./api/creds/quota/${encodeURIComponent(filename)}?mode=provider`, {

                    method: 'GET',

                    headers: getAuthHeaders()

                });

                const data = await response.json();

                if (response.ok && data.success) {

                    const models = data.models || {};

                    if (Object.keys(models).length === 0) {

                        contentDiv.innerHTML = `

                            <div style="text-align: center; padding: 20px; color: #999;">

                                <div>${t('status_no_quota_info')}</div>

                            </div>

                        `;

                    } else {

                        let quotaHTML = `

                            <div style="background: var(--bg-subtle); color: var(--text-primary); padding: 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 15px;">

                                <h4 style="margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;">

                                    <span style="font-size: 20px;"></span>

                                    <span>${t('quota_details')}</span>

                                </h4>

                                <div style="font-size: 12px; color: var(--text-muted); margin-top: 5px;">${t('table_filename')}: ${filename}</div>

                            </div>

                            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">

                        `;

                        for (const [modelName, quotaData] of Object.entries(models)) {

                            const remainingFraction = quotaData.remaining || 0;

                            const resetTime = quotaData.resetTime || 'N/A';

                            const usedPercentage = Math.round((1 - remainingFraction) * 100);

                            const remainingPercentage = Math.round(remainingFraction * 100);

                            let percentageColor = '#28a745';

                            if (usedPercentage >= 90) percentageColor = '#dc3545';

                            else if (usedPercentage >= 70) percentageColor = '#ffc107';

                            else if (usedPercentage >= 50) percentageColor = '#17a2b8';

                            quotaHTML += `

                                <div style="background: var(--bg); border: 1px solid var(--border); border-left: 4px solid ${percentageColor}; border-radius: var(--radius); padding: 8px 10px;">

                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">

                                        <div style="font-weight: bold; color: #333; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; margin-right: 8px;" title="${modelName} - ${t('remaining_label')}: ${remainingPercentage}% - ${resetTime}">

                                            ${modelName}

                                        </div>

                                        <div style="font-size: 13px; font-weight: bold; color: ${percentageColor}; white-space: nowrap;">

                                            ${remainingPercentage}%

                                        </div>

                                    </div>

                                    <div style="width: 100%; height: 8px; background-color: var(--bg-subtle); border-radius: var(--radius); overflow: hidden; margin-bottom: 4px;">

                                        <div style="width: ${usedPercentage}%; height: 100%; background-color: ${percentageColor};"></div>

                                    </div>

                                    <div style="font-size: 10px; color: #666; text-align: right;">

                                        ${resetTime !== 'N/A' ? 'Reset ' + resetTime : ''}

                                    </div>

                                </div>

                            `;

                        }

                        quotaHTML += '</div>';

                        contentDiv.innerHTML = quotaHTML;

                    }

                    // showStatus(t('quota_information_loaded_successful'), 'success');

                } else {

                    const errorMsg = data.error || t('failed_to_get_quota_information');

                    contentDiv.innerHTML = `

                        <div style="text-align: center; padding: 20px; color: #dc3545;">

                            <div style="font-weight: bold; margin-bottom: 5px;">${t('status_quota_failed')}</div>

                            <div style="font-size: 13px; color: #666;">${errorMsg}</div>

                        </div>

                    `;

                    showStatus(` ${errorMsg}`, 'error');

                }

            } catch (error) {

                contentDiv.innerHTML = `

                    <div style="text-align: center; padding: 20px; color: #dc3545;">

                        <div style="font-weight: bold; margin-bottom: 5px;">${t('net_error')}</div>

                        <div style="font-size: 13px; color: #666;">${error.message}</div>

                    </div>

                `;

                showStatus(t('failed_to_get_quota_information_err', {error_message: error.message}), 'error');

            }

        }

    }

}

// =====================================================================

// =====================================================================

async function toggleErrorDetails(pathId) {

    await toggleErrorDetailsCommon(pathId, AppState.creds);

}

async function togglePrimaryErrorDetails(pathId) {

    await toggleErrorDetailsCommon(pathId, AppState.primaryCreds);

}

async function toggleErrorDetailsCommon(pathId, manager) {

    const errorDetails = document.getElementById('errors-' + pathId);

    if (!errorDetails) return;

    const isShowing = errorDetails.classList.toggle('show');

    if (isShowing) {

        const contentDiv = errorDetails.querySelector('.cred-content');

        const filename = contentDiv.getAttribute('data-filename');

        if (filename) {

            contentDiv.innerHTML = t('div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup');

            try {

                const modeParam = manager.type === 'primary' ? 'mode=provider' : 'mode=code_assist';

                const response = await fetch(`./api/creds/errors/${encodeURIComponent(filename)}?${modeParam}`, {

                    method: 'GET',

                    headers: getAuthHeaders()

                });

                const data = await response.json();

                if (response.ok) {

                    const errorCodes = data.error_codes || [];

                    const errorMessages = data.error_messages || {};

                    if (errorCodes.length === 0) {

                        contentDiv.innerHTML = `

                            <div style="text-align: center; padding: 20px; color: #28a745;">

                                <div style="font-weight: bold;">${t('status_no_errors')}</div>

                                <div style="font-size: 12px; color: #666; margin-top: 8px;">${t('status_credential_normal')}</div>

                            </div>

                        `;

                    } else {

                        let errorHTML = '';

                        errorCodes.forEach((errorCode) => {

                            const messageStr = errorMessages[errorCode] || t('no_details_available');

                            let displayMsg = messageStr;

                            let detailsHtml = '';

                            try {

                                const parsedMsg = JSON.parse(messageStr);

                                if (parsedMsg.error) {

                                    if (parsedMsg.error.message) {

                                        displayMsg = parsedMsg.error.message;

                                    }

                                    if (parsedMsg.error.details && Array.isArray(parsedMsg.error.details)) {

                                        detailsHtml = '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed #ddd;">';

                                        detailsHtml += t('div_stylefontsize_12px_color_666_ma');

                                        parsedMsg.error.details.forEach((detail, idx) => {

                                            detailsHtml += '<div style="font-size: 12px; margin-left: 10px; margin-bottom: 5px;">';

                                            // Toggle element display @type

                                            if (detail['@type']) {

                                                const highlightedType = highlightHttpLinks(escapeHtml(detail['@type']));

                                                detailsHtml += t('div_stylecolor_007bfftype_highlight', {highlightedType: highlightedType});

                                            }

                                            // Toggle element display reason

                                            if (detail.reason) {

                                                detailsHtml += t('div_stylecolor_dc3545reason_escapeh', {escapeHtml_detail_reason: escapeHtml(detail.reason)});

                                            }

                                            if (detail.metadata) {

                                                detailsHtml += '<div style="margin-left: 10px; margin-top: 3px;">';

                                                for (const [key, value] of Object.entries(detail.metadata)) {

                                                    const highlightedValue = highlightHttpLinks(escapeHtml(String(value)));

                                                    detailsHtml += `<div style="color: #333;">${escapeHtml(key)}: ${highlightedValue}</div>`;

                                                }

                                                detailsHtml += '</div>';

                                            }

                                            detailsHtml += '</div>';

                                        });

                                        detailsHtml += '</div>';

                                    }

                                    if (parsedMsg.error.status) {

                                        if (!detailsHtml) {

                                            detailsHtml = '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed #ddd;">';

                                        }

                                        detailsHtml += t('div_stylefontsize_12px_color_666sta', {escapeHtml_parsedMsg_error_status: escapeHtml(parsedMsg.error.status)});

                                        if (!parsedMsg.error.details) {

                                            detailsHtml += '</div>';

                                        }

                                    }

                                }

                            } catch (e) {

                            }

                            const highlightedMsg = highlightHttpLinks(escapeHtml(displayMsg));

                            errorHTML += `

                                <div style="padding: 12px; margin-bottom: 10px; border-left: 3px solid #dc3545; background-color: #f8f9fa;">

                                    <div style="font-weight: bold; color: #dc3545; margin-bottom: 8px;">${t('error_code_prefix')} ${errorCode}</div>

                                    <div style="line-height: 1.6; color: #333; white-space: pre-wrap; word-break: break-word;">

                                        ${highlightedMsg}

                                    </div>

                                    ${detailsHtml}

                                </div>

                            `;

                        });

                        contentDiv.innerHTML = errorHTML;

                    }

                    // showStatus(t('error_information_loaded_successful'), 'success');

                } else {

                    const errorMsg = data.detail || data.error || t('failed_to_fetch_error_message');

                    contentDiv.innerHTML = `

                        <div style="text-align: center; padding: 20px; color: #dc3545;">

                            <div style="font-weight: bold;">${t('status_load_failed')}</div>

                            <div style="font-size: 12px; margin-top: 8px;">${errorMsg}</div>

                        </div>

                    `;

                    showStatus(t('failed_to_fetch_error_message_error', {errorMsg: errorMsg}), 'error');

                }

            } catch (error) {

                contentDiv.innerHTML = `

                    <div style="text-align: center; padding: 20px; color: #dc3545;">

                        <div style="font-weight: bold;">${t('net_error')}</div>

                        <div style="font-size: 12px; margin-top: 8px;">${error.message}</div>

                    </div>

                `;

                showStatus(t('failed_to_fetch_error_information_e', {error_message: error.message}), 'error');

            }

        }

    }

}

function escapeHtml(text) {

    const div = document.createElement('div');

    div.textContent = text;

    return div.innerHTML;

}

function highlightHttpLinks(text) {

    const urlRegex = /(https?:\/\/[^\s<>"]+)/gi;

    return text.replace(urlRegex, function(url) {

        return t('a_hrefurl_target_blank_stylecolor_0', {url: url, url: url, url: url});

    });

}

async function batchVerifyProjectIds() {

    const selectedFiles = Array.from(AppState.creds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_credentials_to_ve'), 'error');

        showMessageModal(t('tip'), t('please_select_the_credentials_to_ve_dup'), 'error');

        return;

    }

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_batch_veri_dup', {selectedFiles_length: selectedFiles.length})))) {

        return;

    }

    showStatus(t('parallel_verifying_selectedfileslen', {selectedFiles_length: selectedFiles.length}), 'info');

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./api/creds/verify-project/${encodeURIComponent(filename)}`, {

                method: 'POST',

                headers: getAuthHeaders()

            });

            const data = await response.json();

            if (response.ok && data.success) {

                return {

                    success: true,

                    filename,

                    projectId: data.project_id,

                    creditAmount: data.credit_amount,

                    message: data.message

                };

            } else {

                return { success: false, filename, error: data.message || t('failed') };

            }

        } catch (error) {

            return { success: false, filename, error: error.message };

        }

    });

    const results = await Promise.all(promises);

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            const creditSuffix = result.creditAmount !== undefined && result.creditAmount !== null

                ? ` (${t('credits_label')}: ${result.creditAmount})`

                : '';

            resultMessages.push(` ${result.filename}: ${result.projectId}${creditSuffix}`);

        } else {

            failCount++;

            resultMessages.push(` ${result.filename}: ${result.error}`);

        }

    });

    await AppState.creds.refresh();

    const summary = t('batch_verification_completennsucces', {successCount: successCount, failCount: failCount, selectedFiles_length: selectedFiles.length, resultMessages_join___n: resultMessages.join('\n')});

    if (failCount === 0) {

        showStatus(t('all_verifications_successful_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length}), 'success');

        showMessageModal(t('batch_verification_complete'), summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('all_verifications_failed_failed_fai', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal(t('batch_verification_complete'), summary, 'error');

    } else {

        showStatus(t('batch_verification_completed_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal(t('batch_verification_complete'), summary, 'info');

    }

    console.log(summary);

}

async function batchVerifyPrimaryProjectIds() {

    const selectedFiles = Array.from(AppState.primaryCreds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_primary_crede_dup'), 'error');

        showMessageModal(t('tip'), t('please_select_the_primary_crede'), 'error');

        return;

    }

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_batch_veri', {selectedFiles_length: selectedFiles.length})))) {

        return;

    }

    showStatus(t('parallel_testing_selectedfileslengt', {selectedFiles_length: selectedFiles.length}), 'info');

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./api/creds/verify-project/${encodeURIComponent(filename)}?mode=provider`, {

                method: 'POST',

                headers: getAuthHeaders()

            });

            const data = await response.json();

            if (response.ok && data.success) {

                return {

                    success: true,

                    filename,

                    projectId: data.project_id,

                    creditAmount: data.credit_amount,

                    message: data.message

                };

            } else {

                return { success: false, filename, error: data.message || t('failed') };

            }

        } catch (error) {

            return { success: false, filename, error: error.message };

        }

    });

    const results = await Promise.all(promises);

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            const creditSuffix = result.creditAmount !== undefined && result.creditAmount !== null

                ? ` (${t('credits_label')}: ${result.creditAmount})`

                : '';

            resultMessages.push(` ${result.filename}: ${result.projectId}${creditSuffix}`);

        } else {

            failCount++;

            resultMessages.push(` ${result.filename}: ${result.error}`);

        }

    });

    await AppState.primaryCreds.refresh();

    const summary = t('primary_batch_verification_comp_dup', {successCount: successCount, failCount: failCount, selectedFiles_length: selectedFiles.length, resultMessages_join___n: resultMessages.join('\n')});

    if (failCount === 0) {

        showStatus(t('all_verifications_successful_verifi', {successCount: successCount, selectedFiles_length: selectedFiles.length}), 'success');

        showMessageModal(t('primary_batch_verification_comp'), summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('verification_failed_for_all_failed', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal(t('primary_batch_verification_comp'), summary, 'error');

    } else {

        showStatus(t('batch_verification_completed_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal(t('primary_batch_verification_comp'), summary, 'info');

    }

    console.log(summary);

}

async function batchConfigurePreview() {

    const selectedFiles = Array.from(AppState.creds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_credential_to_con'), 'error');

        showMessageModal(t('tip'), t('please_select_the_credentials_to_co'), 'error');

        return;

    }

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_batch_set', {selectedFiles_length: selectedFiles.length})))) {

        return;

    }

    showStatus(t('configuring_preview_channel_for_sel', {selectedFiles_length: selectedFiles.length}), 'info');

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./api/creds/configure-preview/${encodeURIComponent(filename)}`, {

                method: 'POST',

                headers: getAuthHeaders()

            });

            const data = await response.json();

            if (response.ok && data.success) {

                return {

                    success: true,

                    filename,

                    message: data.message,

                    setting_id: data.setting_id,

                    binding_id: data.binding_id

                };

            } else {

                return {

                    success: false,

                    filename,

                    error: data.message || t('configuration_failed'),

                    step: data.step,

                    errorDetail: data.error

                };

            }

        } catch (error) {

            return { success: false, filename, error: error.message };

        }

    });

    const results = await Promise.all(promises);

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            resultMessages.push(t('resultfilename_resultmessage_config', {result_filename: result.filename, result_message: result.message || t('configuration_successful')}));

        } else {

            failCount++;

            const errorMsg = result.step ? t('resulterror_step_resultstep', {result_error: result.error, result_step: result.step}) : result.error;

            resultMessages.push(` ${result.filename}: ${errorMsg}`);

        }

    });

    await AppState.creds.refresh();

    const summary = t('batch_preview_channel_configuration', {successCount: successCount, failCount: failCount, selectedFiles_length: selectedFiles.length, resultMessages_join___n: resultMessages.join('\n')});

    if (failCount === 0) {

        showStatus(t('all_configured_successfully_preview', {successCount: successCount, selectedFiles_length: selectedFiles.length}), 'success');

        showMessageModal(t('bulk_preview_channel_configuration'), summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('configuration_failed_for_all_failed', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal(t('bulk_preview_channel_configuration'), summary, 'error');

    } else {

        showStatus(t('batch_configuration_complete_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal(t('bulk_preview_channel_configuration'), summary, 'info');

    }

    console.log(summary);

}

async function refreshAllEmails() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_refresh_us')))) return;

    try {

        showStatus(t('refreshing_all_user_emails'), 'info');

        const response = await fetch('./api/creds/refresh-all-emails', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            showStatus(t('email_refresh_complete_successfully', {data_success_count: data.success_count, data_total_count: data.total_count}), 'success');

            await AppState.creds.refresh();

        } else {

            showStatus(data.message || t('failed_to_refresh_emails'), 'error');

        }

    } catch (error) {

        showStatus(t('email_refresh_network_error_errorme', {error_message: error.message}), 'error');

    }

}

async function refreshAllPrimaryEmails() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_refresh_us_dup')))) return;

    try {

        showStatus(t('refreshing_all_user_emails'), 'info');

        const response = await fetch('./api/creds/refresh-all-emails?mode=provider', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            showStatus(t('email_refresh_complete_successfully', {data_success_count: data.success_count, data_total_count: data.total_count}), 'success');

            await AppState.primaryCreds.refresh();

        } else {

            showStatus(data.message || t('failed_to_refresh_emails'), 'error');

        }

    } catch (error) {

        showStatus(t('email_refresh_network_error_errorme', {error_message: error.message}), 'error');

    }

}

async function deduplicateByEmail() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_perform_on')))) return;

    try {

        showStatus(t('oneclick_credential_deduplication_i'), 'info');

        const response = await fetch('./api/creds/deduplicate-by-email', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            const msg = t('deduplication_complete_deleted_data', {data_deleted_count: data.deleted_count, data_kept_count: data.kept_count, data_unique_emails_count: data.unique_emails_count});

            showStatus(msg, 'success');

            await AppState.creds.refresh();

            if (data.duplicate_groups && data.duplicate_groups.length > 0) {

                let details = t('deduplication_detailsnn');

                data.duplicate_groups.forEach(group => {

                    details += t('email_groupemailnkeep_groupkept_fil', {group_email: group.email, group_kept_file: group.kept_file, group_deleted_files_join: group.deleted_files.join(', ')});

                });

                console.log(details);

            }

        } else {

            showStatus(data.message || t('deduplication_failed'), 'error');

        }

    } catch (error) {

        showStatus(t('deduplication_network_error_errorme', {error_message: error.message}), 'error');

    }

}

async function deduplicatePrimaryByEmail() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_deduplicat')))) return;

    try {

        showStatus(t('oneclick_credential_deduplication_i'), 'info');

        const response = await fetch('./api/creds/deduplicate-by-email?mode=provider', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            const msg = t('deduplication_complete_deleted_data', {data_deleted_count: data.deleted_count, data_kept_count: data.kept_count, data_unique_emails_count: data.unique_emails_count});

            showStatus(msg, 'success');

            await AppState.primaryCreds.refresh();

            if (data.duplicate_groups && data.duplicate_groups.length > 0) {

                let details = t('deduplication_detailsnn');

                data.duplicate_groups.forEach(group => {

                    details += t('email_groupemailnkeep_groupkept_fil', {group_email: group.email, group_kept_file: group.kept_file, group_deleted_files_join: group.deleted_files.join(', ')});

                });

                console.log(details);

            }

        } else {

            showStatus(data.message || t('deduplication_failed'), 'error');

        }

    } catch (error) {

        showStatus(t('deduplication_network_error_errorme', {error_message: error.message}), 'error');

    }

}

// =====================================================================

// =====================================================================

function connectWebSocket() {

    if (AppState.logWebSocket && AppState.logWebSocket.readyState === WebSocket.OPEN) {

        // showStatus(t('websocket_connected'), 'info');

        return;

    }

    try {

        const wsPath = new URL('./api/logs/stream', window.location.href).href;

        const wsUrl = wsPath.replace(/^http/, 'ws');

        const wsUrlWithAuth = `${wsUrl}?token=${encodeURIComponent(AppState.authToken)}`;

        document.getElementById('connectionStatusText').textContent = t('connecting');

        document.getElementById('logConnectionStatus').className = 'status info';

        AppState.logWebSocket = new WebSocket(wsUrlWithAuth);

        AppState.logWebSocket.onopen = () => {

            document.getElementById('connectionStatusText').textContent = t('connected');

            document.getElementById('logConnectionStatus').className = 'status success';

            // showStatus(t('log_stream_connected_successfully'), 'success');

            clearLogsDisplay();

        };

        AppState.logWebSocket.onmessage = (event) => {

            const logLine = event.data;

            if (logLine.trim()) {

                AppState.allLogs.push(logLine);

                if (AppState.allLogs.length > 1000) {

                    AppState.allLogs = AppState.allLogs.slice(-1000);

                }

                filterLogs();

                if (document.getElementById('autoScroll').checked) {

                    const logContainer = document.getElementById('logContainer');

                    logContainer.scrollTop = logContainer.scrollHeight;

                }

            }

        };

        AppState.logWebSocket.onclose = () => {

            document.getElementById('connectionStatusText').textContent = t('connection_lost');

            document.getElementById('logConnectionStatus').className = 'status error';

            // showStatus(t('log_stream_connection_disconnected'), 'info');

        };

        AppState.logWebSocket.onerror = (error) => {

            document.getElementById('connectionStatusText').textContent = t('connection_error');

            document.getElementById('logConnectionStatus').className = 'status error';

            showStatus(t('status_log_stream_error_prefix') + error, 'error');

        };

    } catch (error) {

        showStatus(t('status_log_stream_connection_failed') + error.message, 'error');

        document.getElementById('connectionStatusText').textContent = t('connection_failed');

        document.getElementById('logConnectionStatus').className = 'status error';

    }

}

function disconnectWebSocket() {

    if (AppState.logWebSocket) {

        AppState.logWebSocket.close();

        AppState.logWebSocket = null;

        document.getElementById('connectionStatusText').textContent = t('disconnected');

        document.getElementById('logConnectionStatus').className = 'status info';

        showStatus(t('log_stream_connection_disconnected_dup'), 'info');

    }

}

function clearLogsDisplay() {

    AppState.allLogs = [];

    AppState.filteredLogs = [];

    document.getElementById('logContent').textContent = t('logs_cleared_waiting_for_new_logs');

}

async function downloadLogs() {

    try {

        const response = await fetch('./api/logs/download', { headers: getAuthHeaders() });

        if (response.ok) {

            const contentDisposition = response.headers.get('Content-Disposition');

            let filename = 'logs.txt';

            if (contentDisposition) {

                const match = contentDisposition.match(/filename=(.+)/);

                if (match) filename = match[1];

            }

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = filename;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('log_file_download_successful_filena', {filename: filename}), 'success');

        } else {

            const data = await response.json();

            showStatus(t('failed_to_download_logs_datadetail', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('network_error_while_downloading_log', {error_message: error.message}), 'error');

    }

}

async function clearLogs() {

    try {

        const response = await fetch('./api/logs/clear', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            clearLogsDisplay();

            showStatus(data.message, 'success');

        } else {

            showStatus(t('failed_to_clear_logs_datadetail_dat', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        clearLogsDisplay();

        showStatus(t('network_error_while_clearing_logs_e', {error_message: error.message}), 'error');

    }

}

function filterLogs() {

    const filter = document.getElementById('logLevelFilter').value;

    AppState.currentLogFilter = filter;

    if (filter === 'all') {

        AppState.filteredLogs = [...AppState.allLogs];

    } else {

        AppState.filteredLogs = AppState.allLogs.filter(log => log.toUpperCase().includes(filter));

    }

    displayLogs();

}

function displayLogs() {

    const logContent = document.getElementById('logContent');

    if (AppState.filteredLogs.length === 0) {

        logContent.textContent = AppState.currentLogFilter === 'all' ?

            t('no_logs_yet') : t('no_logs_at_appstatecurrentlogfilter', {AppState_currentLogFilter: AppState.currentLogFilter});

    } else {

        logContent.textContent = AppState.filteredLogs.join('\n');

    }

}

// =====================================================================

// =====================================================================

async function checkEnvCredsStatus() {

    const loading = document.getElementById('envStatusLoading');

    const content = document.getElementById('envStatusContent');

    try {

        loading.style.display = 'block';

        content.classList.add('hidden');

        const response = await fetch('./api/auth/env-creds-status', { headers: getAuthHeaders() });

        const data = await response.json();

        if (response.ok) {

            const envVarsList = document.getElementById('envVarsList');

            envVarsList.textContent = Object.keys(data.available_env_vars).length > 0

                ? Object.keys(data.available_env_vars).join(', ')

                : t('code_assist_creds__environment_variable_no');

            const autoLoadStatus = document.getElementById('autoLoadStatus');

            autoLoadStatus.textContent = data.auto_load_enabled ? t('enabled') : t('not_enabled');

            autoLoadStatus.style.color = data.auto_load_enabled ? '#28a745' : '#dc3545';

            document.getElementById('envFilesCount').textContent = t('dataexisting_env_files_count_files', {data_existing_env_files_count: data.existing_env_files_count});

            const envFilesList = document.getElementById('envFilesList');

            envFilesList.textContent = data.existing_env_files.length > 0

                ? data.existing_env_files.join(', ')

                : t('none');

            content.classList.remove('hidden');

            // showStatus(t('environment_variable_status_check_c'), 'success');

        } else {

            showStatus(t('failed_to_retrieve_environment_vari', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        loading.style.display = 'none';

    }

}

async function loadEnvCredentials() {

    try {

        showStatus(t('importing_credentials_from_environm'), 'info');

        const response = await fetch('./api/auth/load-env-creds', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            if (data.loaded_count > 0) {

                showStatus(t('successfully_imported_dataloaded_co', {data_loaded_count: data.loaded_count, data_total_count: data.total_count}), 'success');

                setTimeout(() => checkEnvCredsStatus(), 1000);

            } else {

                showStatus(data.message, 'info');

            }

        } else {

            showStatus(t('import_failed_datadetail_dataerror', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function clearEnvCredentials() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_clear_all')))) {

        return;

    }

    try {

        showStatus(t('clearing_environment_variable_crede'), 'info');

        const response = await fetch('./api/auth/env-creds', {

            method: 'DELETE',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            showStatus(t('successfully_deleted_datadeleted_co', {data_deleted_count: data.deleted_count}), 'success');

            setTimeout(() => checkEnvCredsStatus(), 1000);

        } else {

            showStatus(t('clear_failed_datadetail_dataerror_u', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

// =====================================================================

// =====================================================================

const CONFIG_FIELD_KEYS = {
    host: 'host',
    port: 'port',
    configApiPassword: 'api_password',
    configPanelPassword: 'panel_password',
    configPassword: 'password',
    credentialsDir: 'credentials_dir',
    proxy: 'proxy',
    codeAssistEndpoint: 'code_assist_endpoint',
    oauthProxyUrl: 'oauth_url',
    googleapisProxyUrl: 'google_apis_url',
    resourceManagerApiUrl: 'resource_manager_url',
    serviceUsageApiUrl: 'service_usage_url',
    primaryApiUrl: 'api_url',
    autoBanEnabled: 'auto_disable_enabled',
    autoBanErrorCodes: 'auto_disable_error_codes',
    retry429Enabled: 'retry_429_enabled',
    retry429MaxRetries: 'retry_429_max_retries',
    retry429Interval: 'retry_429_interval',
    compatibilityModeEnabled: 'compatibility_mode_enabled',
    returnThoughtsToFrontend: 'return_thoughts_to_frontend',
    primaryStreamToNonstream: 'stream_to_nonstream',
    primarySwitchCredentialEnabled: 'switch_credential_enabled',
    antiTruncationMaxAttempts: 'anti_truncation_max_attempts',
    keepaliveUrl: 'keepalive_url',
    keepaliveInterval: 'keepalive_interval'
};

async function loadConfig() {

    const loading = document.getElementById('configLoading');

    const form = document.getElementById('configForm');

    try {

        loading.style.display = 'block';

        form.classList.add('hidden');

        const response = await fetch('./api/config/get', { headers: getAuthHeaders() });

        const data = await response.json();

        if (response.ok) {

            AppState.currentConfig = data.config;

            AppState.envLockedFields = new Set(data.env_locked || []);

            populateConfigForm();

            form.classList.remove('hidden');

            // showStatus(t('configuration_loaded_successfully'), 'success');

        } else {

            showStatus(t('failed_to_load_configuration_datade', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        loading.style.display = 'none';

    }

}

function populateConfigForm() {

    const c = AppState.currentConfig;

    setConfigField('host', c.host || '0.0.0.0');

    setConfigField('port', c.port || 7861);

    setConfigField('configApiPassword', c.api_password || '');

    setConfigField('configPanelPassword', c.panel_password || '');

    setConfigField('configPassword', c.password || '');

    setConfigField('credentialsDir', c.credentials_dir || '');

    setConfigField('proxy', c.proxy || '');

    setConfigField('codeAssistEndpoint', c.code_assist_endpoint || '');

    setConfigField('oauthProxyUrl', c.oauth_url || '');

    setConfigField('googleapisProxyUrl', c.google_apis_url || '');

    setConfigField('resourceManagerApiUrl', c.resource_manager_url || '');

    setConfigField('serviceUsageApiUrl', c.service_usage_url || '');

    setConfigField('primaryApiUrl', c.api_url || '');

    setConfigCheckbox('autoBanEnabled', Boolean(c.auto_disable_enabled));

    setConfigField('autoBanErrorCodes', (c.auto_disable_error_codes || []).join(','));

    setConfigCheckbox('retry429Enabled', Boolean(c.retry_429_enabled));

    setConfigField('retry429MaxRetries', c.retry_429_max_retries || 20);

    setConfigField('retry429Interval', c.retry_429_interval || 0.1);

    setConfigCheckbox('compatibilityModeEnabled', Boolean(c.compatibility_mode_enabled));

    setConfigCheckbox('returnThoughtsToFrontend', Boolean(c.return_thoughts_to_frontend !== false));

    setConfigCheckbox('primaryStreamToNonstream', Boolean(c.stream_to_nonstream !== false));

    setConfigCheckbox('primarySwitchCredentialEnabled', Boolean(c.switch_credential_enabled));

    setConfigField('antiTruncationMaxAttempts', c.anti_truncation_max_attempts || 3);

    setConfigField('keepaliveUrl', c.keepalive_url || '');

    setConfigField('keepaliveInterval', c.keepalive_interval || 60);

}

function setConfigField(fieldId, value) {

    const field = document.getElementById(fieldId);

    if (field) {

        field.value = value;

        const configKey = CONFIG_FIELD_KEYS[fieldId] || fieldId.replace(/([A-Z])/g, '_$1').toLowerCase();

        if (AppState.envLockedFields.has(configKey)) {

            field.disabled = true;

            field.classList.add('env-locked');

        } else {

            field.disabled = false;

            field.classList.remove('env-locked');

        }

    }

}

function setConfigCheckbox(fieldId, checked) {

    const field = document.getElementById(fieldId);

    if (!field) return;

    field.checked = checked;

    const configKey = CONFIG_FIELD_KEYS[fieldId] || fieldId.replace(/([A-Z])/g, '_$1').toLowerCase();

    const isLocked = AppState.envLockedFields.has(configKey);

    field.disabled = isLocked;

    field.classList.toggle('env-locked', isLocked);

    field.closest('.switch-row')?.classList.toggle('env-locked', isLocked);

}

async function saveConfig() {

    try {

        const getValue = (id, def = '') => document.getElementById(id)?.value.trim() || def;

        const getInt = (id, def = 0) => parseInt(document.getElementById(id)?.value) || def;

        const getFloat = (id, def = 0.0) => parseFloat(document.getElementById(id)?.value) || def;

        const getChecked = (id, def = false) => {
            const field = document.getElementById(id);
            return field ? field.checked : def;
        };

        const config = {

            host: getValue('host', '0.0.0.0'),

            port: getInt('port', 7861),

            api_password: getValue('configApiPassword'),

            panel_password: getValue('configPanelPassword'),

            password: getValue('configPassword'),

            code_assist_endpoint: getValue('codeAssistEndpoint'),

            credentials_dir: getValue('credentialsDir'),

            proxy: getValue('proxy'),

            oauth_url: getValue('oauthProxyUrl'),

            google_apis_url: getValue('googleapisProxyUrl'),

            resource_manager_url: getValue('resourceManagerApiUrl'),

            service_usage_url: getValue('serviceUsageApiUrl'),

            api_url: getValue('primaryApiUrl'),

            auto_disable_enabled: getChecked('autoBanEnabled'),

            auto_disable_error_codes: getValue('autoBanErrorCodes').split(',')

                .map(c => parseInt(c.trim())).filter(c => !isNaN(c)),

            retry_429_enabled: getChecked('retry429Enabled'),

            retry_429_max_retries: getInt('retry429MaxRetries', 20),

            retry_429_interval: getFloat('retry429Interval', 0.1),

            compatibility_mode_enabled: getChecked('compatibilityModeEnabled'),

            return_thoughts_to_frontend: getChecked('returnThoughtsToFrontend'),

            stream_to_nonstream: getChecked('primaryStreamToNonstream'),

            switch_credential_enabled: getChecked('primarySwitchCredentialEnabled'),

            anti_truncation_max_attempts: getInt('antiTruncationMaxAttempts', 3),

            keepalive_url: getValue('keepaliveUrl'),

            keepalive_interval: getInt('keepaliveInterval', 60)

        };

        const response = await fetch('./api/config/save', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ config })

        });

        const data = await response.json();

        if (response.ok) {

            let message = t('configuration_saved_successfully');

            if (data.hot_updated && data.hot_updated.length > 0) {

                message += t('the_following_configurations_have_t_dup', {data_hot_updated_join: data.hot_updated.join(', ')});

            }

            if (data.restart_required && data.restart_required.length > 0) {

                message += t('n_restart_notice_datarestart_notice', {data_restart_notice: data.restart_notice});

                showStatus(message, 'info');

            } else {

                showStatus(message, 'success');

            }

            setTimeout(() => loadConfig(), 1000);

        } else {

            showStatus(t('failed_to_save_config_datadetail_da', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

const mirrorUrls = {

    codeAssistEndpoint: 'https://cloudcode-pa.googleapis.com',

    oauthProxyUrl: 'https://oauth2.googleapis.com',

    googleapisProxyUrl: 'https://www.googleapis.com',

    resourceManagerApiUrl: 'https://cloudresourcemanager.googleapis.com',

    serviceUsageApiUrl: 'https://serviceusage.googleapis.com',

    primaryApiUrl: 'https://daily-cloudcode-pa.googleapis.com'

};

const officialUrls = {

    codeAssistEndpoint: 'https://cloudcode-pa.googleapis.com',

    oauthProxyUrl: 'https://oauth2.googleapis.com',

    googleapisProxyUrl: 'https://www.googleapis.com',

    resourceManagerApiUrl: 'https://cloudresourcemanager.googleapis.com',

    serviceUsageApiUrl: 'https://serviceusage.googleapis.com',

    primaryApiUrl: 'https://daily-cloudcode-pa.googleapis.com'

};

async function useMirrorUrls() {

    if (await showConfirmModal(t('are_you_sure_you_want_to_configure_dup'))) {

        for (const [fieldId, url] of Object.entries(mirrorUrls)) {

            const field = document.getElementById(fieldId);

            if (field && !field.disabled) field.value = url;

        }

        showStatus(t('switched_to_mirror_url_configuratio'), 'success');

    }

}

async function restoreOfficialUrls() {

    if (await showConfirmModal(t('are_you_sure_you_want_to_configure'))) {

        for (const [fieldId, url] of Object.entries(officialUrls)) {

            const field = document.getElementById(fieldId);

            if (field && !field.disabled) field.value = url;

        }

        showStatus(t('switched_to_official_endpoint_confi'), 'success');

    }

}

// =====================================================================

// =====================================================================

async function refreshUsageStats() {

    const loading = document.getElementById('usageLoading');

    const list = document.getElementById('usageList');

    try {

        loading.style.display = 'block';

        list.innerHTML = '';

        const [statsResponse, aggregatedResponse] = await Promise.all([

            fetch('./api/usage/stats', { headers: getAuthHeaders() }),

            fetch('./api/usage/aggregated', { headers: getAuthHeaders() })

        ]);

        if (statsResponse.status === 401 || aggregatedResponse.status === 401) {

            showStatus(t('authentication_failed_please_log_in'), 'error');

            setTimeout(() => location.reload(), 1500);

            return;

        }

        const statsData = await statsResponse.json();

        const aggregatedData = await aggregatedResponse.json();

        if (statsResponse.ok && aggregatedResponse.ok) {

            AppState.usageStatsData = statsData.success ? statsData.data : statsData;

            const aggData = aggregatedData.success ? aggregatedData.data : aggregatedData;

            document.getElementById('totalApiCalls').textContent = aggData.total_calls_24h || 0;

            document.getElementById('totalFiles').textContent = aggData.total_files || 0;

            document.getElementById('avgCallsPerFile').textContent = (aggData.avg_calls_per_file || 0).toFixed(1);

            renderUsageList();

            // showStatus(t('loaded_usage_statistics_for_aggdata', {aggData_total_files____Object_keys_AppState_usageStatsData__length: aggData.total_files || Object.keys(AppState.usageStatsData).length}), 'success');

        } else {

            const errorMsg = statsData.detail || aggregatedData.detail || t('failed_to_load_usage_statistics');

            showStatus(t('error_errormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        loading.style.display = 'none';

    }

}

function renderUsageList() {

    const list = document.getElementById('usageList');

    if (!list) return;

    list.innerHTML = '';

    if (Object.keys(AppState.usageStatsData).length === 0) {

        const tr = document.createElement('tr');

        tr.innerHTML = `<td colspan="3" style="text-align: center; color: var(--text-muted); padding: 18px 12px;">${t('status_no_filter_data')}</td>`;

        list.appendChild(tr);

        return;

    }

    for (const [filename, stats] of Object.entries(AppState.usageStatsData)) {

        const tr = document.createElement('tr');

        const calls24h = stats.calls_24h || 0;

        tr.innerHTML = `

            <td style="font-size: 13px; color: var(--color-ink); word-break: break-all;">${filename}</td>

            <td style="font-weight: 600; color: var(--color-primary); font-size: 14px;">${calls24h}</td>

            <td>

                <button class="btn btn-secondary btn-small" onclick="resetSingleUsageStats('${filename}')">${t('btn_reset_stats')}</button>

            </td>

        `;

        list.appendChild(tr);

    }

}

async function resetSingleUsageStats(filename) {

    if (!(await showConfirmModal(t('confirm_reset_stats', {filename: filename})))) return;

    try {

        const response = await fetch('./api/usage/reset', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ filename })

        });

        const data = await response.json();

        if (response.ok && data.success) {

            showStatus(data.message, 'success');

            await refreshUsageStats();

        } else {

            showStatus(t('reset_failed_datamessage_datadetail', {data_message____data_detail____data_error: data.message || data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function resetAllUsageStats() {

    if (!(await showConfirmModal(t('confirm_reset_usage_statistics')))) return;

    try {

        const response = await fetch('./api/usage/reset', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({})

        });

        const data = await response.json();

        if (response.ok && data.success) {

            showStatus(data.message, 'success');

            await refreshUsageStats();

        } else {

            showStatus(t('reset_failed_datamessage_datadetail', {data_message____data_detail____data_error: data.message || data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

// =====================================================================

// =====================================================================

function startCooldownTimer() {

    if (AppState.cooldownTimerInterval) {

        clearInterval(AppState.cooldownTimerInterval);

    }

    AppState.cooldownTimerInterval = setInterval(() => {

        updateCooldownDisplays();

    }, 1000);

}

function stopCooldownTimer() {

    if (AppState.cooldownTimerInterval) {

        clearInterval(AppState.cooldownTimerInterval);

        AppState.cooldownTimerInterval = null;

    }

}

function updateCooldownDisplays() {

    let needsRefresh = false;

    for (const credInfo of Object.values(AppState.creds.data)) {

        if (credInfo.model_cooldowns && Object.keys(credInfo.model_cooldowns).length > 0) {

            const currentTime = Date.now() / 1000;

            const hasExpiredCooldowns = Object.entries(credInfo.model_cooldowns).some(([, until]) => until <= currentTime);

            if (hasExpiredCooldowns) {

                needsRefresh = true;

                break;

            }

        }

    }

    if (needsRefresh) {

        AppState.creds.renderList();

        return;

    }

    document.querySelectorAll('.cooldown-badge').forEach(badge => {

        const card = badge.closest('.cred-card');

        const filenameEl = card?.querySelector('.cred-filename');

        if (!filenameEl) return;

        const filename = filenameEl.textContent;

        const credInfo = Object.values(AppState.creds.data).find(c => c.filename === filename);

        if (credInfo && credInfo.model_cooldowns) {

            const currentTime = Date.now() / 1000;

            const titleMatch = badge.getAttribute('title')?.match(/: (.+)/);

            if (titleMatch) {

                const model = titleMatch[1];

                const cooldownUntil = credInfo.model_cooldowns[model];

                if (cooldownUntil) {

                    const remaining = Math.max(0, Math.floor(cooldownUntil - currentTime));

                    if (remaining > 0) {

                        const shortModel = model.replace('gemini-', '').replace('-exp', '')

                            .replace('2.0-', '2-').replace('1.5-', '1.5-');

                        const timeDisplay = formatCooldownTime(remaining).replace(/s$/, '').replace(/ /g, '');

                        badge.innerHTML = `Cooldown ${shortModel}: ${timeDisplay}`;

                    }

                }

            }

        }

    });

}

// =====================================================================

// =====================================================================

async function fetchAndDisplayVersion() {

    try {

        const response = await fetch('./api/version/info');

        const data = await response.json();

        const versionText = document.getElementById('versionText');

        if (data.success) {

            versionText.textContent = `v${data.version}`;

            versionText.title = t('full_version_datafull_hashncommit_m', {data_full_hash: data.full_hash, data_message: data.message, data_date: data.date});

            versionText.style.cursor = 'help';

        } else {

            versionText.textContent = t('unknown_version');

            versionText.title = data.error || t('unable_to_retrieve_version_informat');

        }

    } catch (error) {

        console.error(t('failed_to_retrieve_version_informat'), error);

        const versionText = document.getElementById('versionText');

        if (versionText) {

            versionText.textContent = t('failed_to_fetch_version_information');

        }

    }

}

async function checkForUpdates() {

    const checkBtn = document.getElementById('checkUpdateBtn');

    if (!checkBtn) return;

    const originalText = checkBtn.textContent;

    try {

        checkBtn.textContent = t('checking');

        checkBtn.disabled = true;

        const response = await fetch('./api/version/info?check_update=true');

        const data = await response.json();

        if (data.success) {

            if (data.check_update === false) {

                showStatus(t('check_for_updates_failed_dataupdate', {data_update_error: data.update_error || t('unknown_error')}), 'error');

            } else if (data.has_update === true) {

                const updateMsg = t('new_version_foundncurrent_vdatavers', {data_version: data.version, data_latest_version: data.latest_version, data_latest_message: data.latest_message || t('none')});

                showStatus(updateMsg.replace(/\n/g, ' '), 'warning');

                checkBtn.style.backgroundColor = '#ffc107';

                checkBtn.textContent = t('new_version_available');

                setTimeout(() => {

                    checkBtn.style.backgroundColor = '#17a2b8';

                    checkBtn.textContent = originalText;

                }, 5000);

            } else if (data.has_update === false) {

                showStatus(t('already_up_to_date'), 'success');

                checkBtn.style.backgroundColor = '#28a745';

                checkBtn.textContent = t('already_up_to_date_dup');

                setTimeout(() => {

                    checkBtn.style.backgroundColor = '#17a2b8';

                    checkBtn.textContent = originalText;

                }, 3000);

            } else {

                showStatus(t('unable_to_determine_if_updates_are'), 'info');

            }

        } else {

            showStatus(t('failed_to_check_for_updates_dataerr', {data_error: data.error}), 'error');

        }

    } catch (error) {

        console.error(t('failed_to_check_for_updates'), error);

        showStatus(t('failed_to_check_for_updates_errorme', {error_message: error.message}), 'error');

    } finally {

        checkBtn.disabled = false;

        if (checkBtn.textContent === t('checking')) {

            checkBtn.textContent = originalText;

        }

    }

}

// =====================================================================

// =====================================================================

window.onload = async function () {

    // popstate listener

    window.addEventListener('popstate', () => {

        navigate(window.location.pathname, false);

    });

    const setupRequired = await refreshSetupStatus();

    if (setupRequired) {

        navigate('/setup', false);

        return;

    }

    const autoLoginSuccess = await autoLogin();

    if (autoLoginSuccess) {

        await fetchAndDisplayVersion();

    }

    startCooldownTimer();

    const primaryAuthBtn = document.getElementById('getPrimaryAuthBtn');

    if (primaryAuthBtn) {

        primaryAuthBtn.addEventListener('click', startPrimaryAuth);

    }

};

document.addEventListener('DOMContentLoaded', function () {

    const uploadArea = document.getElementById('uploadArea');

    if (uploadArea) {

        uploadArea.addEventListener('dragover', (event) => {

            event.preventDefault();

            uploadArea.classList.add('dragover');

        });

        uploadArea.addEventListener('dragleave', (event) => {

            event.preventDefault();

            uploadArea.classList.remove('dragover');

        });

        uploadArea.addEventListener('drop', (event) => {

            event.preventDefault();

            uploadArea.classList.remove('dragover');

            AppState.uploadFiles.addFiles(Array.from(event.dataTransfer.files));

        });

    }

});

function autoSetKeepaliveUrl() {

    const url = `${window.location.protocol}//${window.location.host}`;

    document.getElementById('keepaliveUrl').value = url;

}



function toggleMobileMenu() {
    const sidebar = document.querySelector('.dashboard-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    if (sidebar && overlay) {
        const isOpen = sidebar.classList.contains('open');
        if (isOpen) {
            sidebar.classList.remove('open');
            overlay.classList.remove('open');
            overlay.style.display = 'none';
        } else {
            sidebar.classList.add('open');
            overlay.classList.add('open');
            overlay.style.display = 'block';
        }
    }
}
