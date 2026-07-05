const TRANSLATIONS = {

    en: {

        "app_title": "Omni Gateway",

        "panel_title": "Omni Gateway Management Console",

        "login_subtitle": "Please enter passcode to access control panel",

        "login_placeholder": "Enter password",

        "login_btn": "Login",

        "logout_btn": "Logout",

        "version_label": "Version",

        "check_update_btn": "Check for Updates",

        "loading_text": "Loading...",

        "mirror_switch_warning": "Mirror reverse proxy setup switches API domains to proxy servers.",

        "copy_success": "Copied to clipboard!",

        "copy_fail": "Copy failed!",

        "btn_close": "Close",

        "dialog_tip": "Tip",

        "error_prefix": "Error: ",

        "tab_oauth": "OAuth Auth",

        "tab_omni": "Omni Auth",

        "tab_upload": "Batch Upload",

        "tab_manage_creds": "Credentials",
        "manage_creds_title": "Credentials Management",
        "manage_creds_desc": "Select a credential provider to view and manage active API channels.",
        "tab_manage_code_assist": "Code Assist Credentials",

        "tab_manage_code_assist_short": "Code Assist Creds",

        "tab_manage_ag": "Omni Credentials",

        "tab_manage_ag_short": "AG Creds",

        "tab_config": "System Config",

        "tab_logs": "Real-time Logs",

        "tab_about": "About Project",

        "oauth_banner_title": "Automation Enabled:",

        "oauth_banner_text": "System will auto-detect and enable necessary API services (Gemini Cloud Assist API, Gemini for Google Cloud API) after login.",

        "oauth_advanced_title": "Advanced: Specify Google Cloud Project ID (Optional)",

        "oauth_advanced_note": "Leave blank to auto-detect and create project.",

        "oauth_link_btn": "Get Google OAuth Auth Link",

        "oauth_auth_title": "Auth Link:",

        "oauth_auth_instruction": "Click this link to authorize Google Account",

        "oauth_guide_title": "OAuth Interactive Guide:",

        "oauth_guide_1": "Click the link above, log in and grant access in the new tab;",

        "oauth_guide_2": "After redirection, you may see a connection failed error at localhost:11451, which is normal;",

        "oauth_guide_3": "Return to this page, and click 'Get & Save Credentials' below;",

        "oauth_guide_4": "For remote servers or VPS without a browser, expand the callback tunnel below.",

        "oauth_callback_title": "No Auto-Redirection? Use Callback Tunnel",

        "oauth_callback_note": "Suitable for VPS, Docker, or port 11451 blocks.",

        "oauth_callback_instructions": "Copy the full URL from address bar after redirection (even if it shows failure) and paste below.",

        "oauth_callback_btn": "Parse Credentials from Callback URL",

        "oauth_save_btn": "Get & Save Credentials",

        "oauth_success_title": "Authentication Successful! Saved credentials:",

        "ag_banner_title": "Google Omni Auth Mode",

        "ag_banner_text": "Obtain Google Cloud SDK native authentication credentials.",

        "ag_link_btn": "Get Omni Auth Link",

        "ag_link_title": "Omni Auth Link:",

        "ag_link_instruction": "Click this link to authorize Omni mode",

        "ag_guide_title": "Steps:",

        "ag_guide_1": "Click the link above to perform Google OAuth authorization;",

        "ag_guide_2": "When redirected to localhost:11451 showing failure, return to this panel;",

        "ag_guide_3": "Click the button below to retrieve and save credentials directly;",

        "ag_guide_4": "If unable to auto-redirect, copy the final URL and parse it below.",

        "ag_save_btn": "Get & Save Omni Credentials",

        "ag_success_title": "Saved Omni Credentials:",

        "ag_download_btn": "Download Credentials File",

        "upload_title": "Batch Upload Credentials",

        "upload_desc": "Drag & drop or select JSON/ZIP credentials to upload.",

        "upload_code_assist_title": "Code Assist Credentials Upload",

        "upload_code_assist_area_title": "Click to select or drag files here",

        "upload_code_assist_area_subtitle": "Supports .json or .zip format",

        "upload_code_assist_area_note": "ZIP archives will be automatically extracted to parse JSON credentials.",

        "upload_pending_code_assist": "Pending Code Assist files to upload:",

        "upload_start_btn": "Start Upload",

        "upload_clear_btn": "Clear List",

        "upload_progress": "Upload Progress",

        "upload_ag_title": "Omni Credentials Upload",

        "upload_ag_area_title": "Click to select or drag files here",

        "upload_ag_area_subtitle": "Supports .json or .zip format",

        "upload_ag_area_note": "ZIP archives will be extracted to parse Omni credentials.",

        "upload_pending_ag": "Pending Omni files to upload:",

        "code_assist_manage_title": "Code Assist Credentials Management",

        "code_assist_manage_desc": "View and manage Code Assist API channels (batch verify, toggle, download, delete).",

        "ag_manage_title": "Omni Credentials Management",

        "ag_manage_desc": "View and manage Omni accounts and request quotas.",

        "endpoint_banner_title": "API Endpoint Addresses",

        "endpoint_openai": "OpenAI format:",

        "endpoint_claude": "Claude format:",

        "endpoint_gemini": "Gemini Native:",

        "stat_total": "Total Credentials",

        "stat_active": "Active",

        "stat_disabled": "Disabled",

        "btn_refresh": "Refresh List",

        "btn_download_all": "Download All (ZIP)",

        "batch_panel_title": "Batch Operations",

        "batch_select_all": "Select All",

        "batch_selected_count": "Selected {count} items",

        "batch_enable": "Batch Enable",

        "batch_disable": "Batch Disable",

        "batch_delete": "Batch Delete",

        "batch_verify_id": "Batch Verify Project ID",

        "batch_preview_toggle": "Batch Toggle Preview Mode",

        "batch_refresh_emails": "Refresh Emails",

        "batch_deduplicate": "Deduplicate by Email",

        "batch_enable_credit": "Enable Credit Mode",

        "batch_disable_credit": "Disable Credit Mode",

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

        "card_no_error": "No Error",

        "card_error_code": "Error: {code}",

        "card_no_email": "No Email Loaded",

        "card_loading_details": "Loading file content...",

        "card_loading_errors": "Loading error details...",

        "card_loading_quota": "Loading quota details...",

        "btn_card_enable": "Enable",

        "btn_card_disable": "Disable",

        "btn_card_view": "View Content",

        "btn_card_download": "Download",

        "btn_card_email": "Email Info",

        "btn_card_quota": "Quota Details",

        "btn_card_close_credit": "Disable Credit",

        "btn_card_open_credit": "Enable Credit",

        "btn_card_set_preview": "Set Preview",

        "btn_card_verify": "Verify",

        "btn_card_test": "Message Test",

        "btn_card_error_details": "View Errors",

        "btn_card_delete": "Delete",

        "config_title": "Global System Settings",

        "config_desc": "Adjust network proxies, API endpoints, error limits, and retry configurations. Settings take effect immediately upon saving.",

        "btn_save_config": "Save Global Config",

        "btn_reload_config": "Reload Configuration",

        "config_loading": "Syncing configuration settings with server...",

        "group_network": "⚙️ Listen & Security Settings",

        "config_host_label": "Server Bind Host IP Address:",

        "config_host_note": "IP address to listen on (0.0.0.0 listens globally, requires restart).",

        "config_port_label": "Listen Port:",

        "config_port_note": "TCP Port to bind on (requires restart).",

        "config_api_pwd_label": "API Access Password (API Key):",

        "config_api_pwd_note": "Used for Bearer Token validation when making proxy requests.",

        "config_panel_pwd_label": "Web Panel Login Password:",

        "config_panel_pwd_note": "Protects this management console page.",

        "config_pwd_label": "Unified Password Override (Optional):",

        "config_pwd_note": "If provided, overrides both API and Panel password. Recommended to leave blank.",

        "group_storage": "📂 Storage & Proxy Settings",

        "config_storage_label": "Credentials Storage Path:",

        "config_storage_note": "Absolute path where JSON credentials are saved.",

        "config_proxy_label": "Global Outbound Proxy URL:",

        "config_proxy_note": "SOCKS5 or HTTP proxy URL for Google endpoints (leave blank for direct connection).",

        "group_endpoints": "🔗 API Endpoint Settings",

        "config_mirror_btn": "🚀 Switch to Mirror Proxies",

        "config_official_btn": "🔄 Restore Google Official Domains",

        "config_endpoint_code": "Code Assist API Endpoint:",

        "config_endpoint_oauth": "OAuth Auth Endpoint:",

        "config_endpoint_apis": "Google APIs Core Endpoint:",

        "config_endpoint_resource": "Resource Manager Endpoint:",

        "config_endpoint_service": "Service Usage Endpoint:",

        "config_endpoint_ag": "Omni API Endpoint:",

        "group_ban": "🛡️ Auto-Ban & Fuse Settings",

        "config_ban_checkbox": "Enable automatic ban/fuse for specified error codes",

        "config_ban_codes_label": "HTTP Error Codes to trigger ban (comma-separated):",

        "config_ban_codes_note": "Accounts receiving these errors will be automatically disabled (403 is highly recommended).",

        "group_retry": "🔁 Auto-Retry & Failover Options",

        "config_retry_checkbox": "Automatically retry requests on alternative credentials upon failure",

        "config_retry_count": "Maximum retry attempts:",

        "config_retry_interval": "Interval between retries (seconds):",

        "group_compat": "🧩 Model Protocol Compatibility",

        "config_compat_checkbox": "Force compatibility mode (flattens system instructions into user messages)",

        "config_compat_note": "Solves empty response errors in older client libraries by avoiding system_instructions, with slight prompt quality trade-offs.",

        "config_thinking_checkbox": "Pass-through Gemini 2.0 Reasoning/Thinking process chain in responses",

        "config_thinking_note": "Outputs reasoning block contents for reasoning models. If disabled, trims thinking outputs.",

        "config_ag_stream_checkbox": "Enable stream compilation for Omni mode (Stream to Non-stream)",

        "config_ag_retry_checkbox": "Auto-switch alternative credentials on Omni request failure",

        "group_trunc": "⏱️ Truncation Recovery Options",

        "config_trunc_count": "Max recovery attempts for truncated streams:",

        "config_trunc_note": "Maximum attempts to resume generation if a stream gets cut off (applicable to models suffixed with '-流式抗截断').",

        "group_keepalive": "☕ Application Keep-Alive Settings",

        "config_keepalive_label": "Keep-Alive Heartbeat URL:",

        "config_keepalive_btn": "Detect and Auto-fill current Keep-Alive URL",

        "config_keepalive_interval": "Heartbeat interval (seconds):",

        "logs_title": "System Logs Console",

        "logs_desc": "Monitor request cycles, rotation decisions, and errors dispatched to Google Cloud APIs.",

        "btn_log_connect": "Connect Log Stream",

        "btn_log_disconnect": "Disconnect Stream",

        "btn_log_save": "Save Logs to File",

        "btn_log_clear": "Clear Log Window",

        "log_filter_level": "Filter Level:",

        "log_scroll_lock": "Auto-scroll to bottom",

        "log_status_label": "Websocket Status:",

        "log_status_text": "Not Connected",

        "log_waiting_text": "Awaiting logs from the server...",

        "about_title": "About Omni Gateway",

        "tab_dashboard": "Dashboard",
        "regenerate_keys_btn": "Regenerate Keys",
        "copy_btn": "Copy",
        "confirm_regenerate_key": "Are you sure you want to regenerate this API key? Previous key will become invalid immediately.",
        "regenerate_success": "API Keys regenerated successfully",
        "tooltip_total_calls": "Total number of API requests sent to the Gateway in the past 24 hours.",
        "tooltip_total_files": "Total number of active Code Assist and Omni credential files in the system.",
        "tooltip_avg_calls": "Average number of API requests processed per credential in the past 24 hours.",
        "tooltip_total_calls": "Total number of API requests routed through this gateway in the last 24 hours.",
        "tooltip_total_files": "The number of active Google/Omni credentials currently configured and monitored.",
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
        "dashboard_total_files_desc": "Total number of active Code Assist and Omni credential accounts currently loaded in the database.",
        "dashboard_avg_calls_desc": "Average number of API requests handled per active credential.",
        "dashboard_total_files": "Monitored Credentials",
        "dashboard_avg_calls": "Avg Requests / Credential",
        "dashboard_welcome": "Welcome to the redesigned Omni Gateway console! You can quickly switch management tasks in the sidebar. The system automatically rotates active credentials for load balancing, performing failover and retries on rate limits (429) or ban (403) errors to ensure high availability.",
        "dashboard_breakdown": "24-Hour Request Breakdown",
        "oauth_desc": "Generate Google Cloud authorization credentials. Supports standard Code Assist OAuth and Omni credentials export.",

        "about_desc": "Omni Gateway is a universal AI router for coding tools. Features smart auto-fallback, token compression, and seamless format translation to maximize free and premium LLMs.",

        "about_github": "GitHub Repository:",

        "about_notice": "Disclaimer: This software is open-source. Commercial reselling or distribution is strictly prohibited. For educational and research purposes only.",

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

        "about_feedback_desc": "Report issues or submit feature requests directly on our GitHub Issues page. PRs are welcome!",

        "auth_fail_relogin": "Authentication failed. Re-authenticating...",

        "check_update_info": "Checking for updates...",

        "update_success": "Checked successfully!",

        "load_cred_stats": "Loaded stats for {count} credentials",

        "net_error": "Network connection error: {msg}",

        "confirm_delete_cred": "Are you sure you want to delete this credential?\\n{filename}",

        "save_config_success": "System configuration saved successfully!",

        "load_config_success": "System configuration loaded successfully!",

        "log_connected": "Log websocket connected.",

        "log_disconnected": "Log websocket disconnected.",

        "select_at_least_one": "Please select at least one credential first!",

        "confirm_batch_action": "Are you sure you want to execute {action} on {count} selected credentials?",

        "batch_action_success": "Batch {action} executed successfully!",

        "input_password_prompt": "Enter password first!",

        "login_success": "Logged in successfully!",

        "login_failed": "Login failed! Please check your passcode.",

        "net_error_prefix": "Network error: ",

        "action_success_prefix": "Action succeeded: ",

        "action_fail_prefix": "Action failed: ",

        "upload_fail_prefix": "Upload failed: ",

        "check_update_fail_prefix": "Check update failed: ",

        "pagination_prev": "Previous Page",

        "pagination_next": "Next Page",

        "pagination_info": "Page {page} of {total} (Showing {start}-{end} of {count} items)",

        "code_assist_oauth_auth_title": "Code Assist OAuth Authentication",

        "oauth_guide_2_fail_suffix": ", which is normal;",

        "oauth_paste_url": "Paste the full URL below:",

        "ag_auth_title": "Omni Authentication",

        "ag_guide_2_fail_suffix": ", return to this panel;",

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

        "tier_badge_title": "Credential Tier",

        "credit_enabled_title": "Credit mode is currently enabled",

        "credit_disabled_title": "Credit mode is currently disabled",

        "other_models_title": "Other models",

        "btn_view_content": "View Content",

        "btn_view_email": "View Email",

        "btn_view_quota": "View Quota",

        "btn_view_quota_title": "View quota usage info for this credential",

        "btn_disable_credit": "Disable Credit",

        "btn_disable_credit_title": "Disable credit mode for this credential",

        "btn_enable_credit": "Enable Credit",

        "btn_enable_credit_title": "Enable credit mode for this credential",

        "btn_setup_preview": "Setup Preview",

        "btn_setup_preview_title": "Configure Preview channel, enable experimental features",

        "btn_verify_id": "Verify",

        "btn_verify_id_title": "Retrieve Project ID, can recover from 403 errors",

        "btn_message_test": "Message Test",

        "btn_message_test_title": "Test if the credential is functional",

        "btn_view_errors": "View Errors",

        "btn_view_errors_title": "View detailed error messages for this credential",

        "email_not_fetched": "Email not fetched",

        "click_view_content_to_load": "Click 'View Content' button to load file details...",

        "click_view_errors_to_load": "Click 'View Errors' button to load error messages...",

        "click_view_quota_to_load": "Click 'View Quota' button to load quota usage details...",

        "status_loading_file_content": "Loading file content...",

        "status_test_failed": "❌ Test failed - {error}",

        "remaining_label": "Remaining",

        "credits_label": "Credits",

        "all": "All",

        "omni_mode_enabled_streamtono": "Omni mode enabled stream-to-non-stream response transformation",

        "test_successful": "✅ Test successful!",

        "oauth_interaction_guide": "OAuth Interaction Guide:",

        "error_code": "Error Code:",

        "no_logs_at_appstatecurrentlogfilter": "No logs at {AppState_currentLogFilter} level currently...",

        "credential_file_name": "Credential File Name",

        "nfailed_step_step": "\\nFailed Step: {step}",

        "batch_verification_completed_succes": "⚠️ Batch verification completed: {successCount}/{selectedFiles_length} succeeded, {failCount} failed",

        "currently_disabled": "Currently Disabled",

        "omni_authentication_successf": "✅ Omni authentication successful! File saved to: {path}",

        "loaded_usage_statistics_for_aggdata": "Loaded usage statistics for {aggData_total_files____Object_keys_AppState_usageStatsData__length} files",

        "upload_failed_connection_interrupte": "Upload failed: Connection interrupted - Likely cause: Too many files ({this_selectedFiles_length}) or network instability. Please upload in batches.",

        "please_select_the_omni_crede": "Please select the Omni credentials to verify first",

        "downloaded_file_filename": "Downloaded file: {filename}",

        "oneclick_credential_deduplication": "One-click Credential Deduplication",

        "message_test": "Message Test",

        "div_styletextalign_center_padding_2": "<div style=\"text-align: center; padding: 20px; color: #999;\">\n\n                                <div style=\"font-size: 48px; margin-bottom: 10px;\">📊</div>\n\n                                <div>No Quota Information Available</div>\n\n                            </div>",

        "omni_authentication_link": "Omni Authentication Link:",

        "authentication_steps": "Authentication Steps:",

        "fetching_authentication_link": "Fetching authentication link...",

        "upload_failed_request_timeout_proce": "Upload failed: Request timeout - Processing time is too long, please reduce the number of files or check your network connection.",

        "manual_project_id_specification_req": "Manual Project ID specification required. Please enter the Google Cloud Project ID in advanced options and try again.",

        "resource_manager_api_endpoint": "Resource Manager API Endpoint:",

        "intelligently_capture_and_automatic": "Intelligently capture and automatically write current keep-alive heartbeat URL",

        "a_hrefhref_target_blank_relnoopener": "<a href=\"{href}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"message-link\" onclick=\"event.stopPropagation()\" title=\"Click to open link\\nRight-click to copy link\">{url}</a>",

        "this_is_not_a_valid_callback_url_pl": "❌ This is not a valid callback URL! Please ensure:\\n1. Google OAuth authorization is completed\\n2. You have copied the full URL from the browser address bar\\n3. The URL contains code and state parameters",

        "file_filename_format_is_not_support": "File {file_name} format is not supported; only JSON and ZIP files are allowed.",

        "the_following_configurations_have_t": ", the following configurations have taken effect immediately: {list}",

        "click_the_link_above_to_proceed_wit": "Click the link above to proceed with Google OAuth authorization;",

        "unable_to_determine_if_updates_are": "Unable to determine if updates are available",

        "please_select_the_credentials_to_ve": "❌ Please select the credentials to verify first",

        "downloaded_file_name": "Downloaded file: {name}",

        "please_obtain_the_omni_authe": "Please obtain the Omni authentication link and complete authorization first",

        "refresh_credential_list": "Refresh Credential List",

        "all_credential_files_have_been_down": "All credential files have been downloaded",

        "preview_channel_configuration_succe": "✅ Preview channel configuration successful!\\n\\nFile: {filename}\\n\\n{data_message}\\n\\nSetting ID: {data_setting_id_____N_A}\\nBinding ID: {data_binding_id_____N_A}",

        "all_verifications_successful_verifi": "✅ All verifications successful! Verified {successCount}/{selectedFiles_length} Omni credentials",

        "are_you_sure_you_want_to_batch_veri": "Are you sure you want to batch verify Project IDs for {selectedFiles_length} Omni credentials?\\n\\nThey will be verified in parallel to speed up the process.",

        "failed_to_load_usage_statistics": "Failed to load usage statistics",

        "failed_to_download_logs_datadetail": "Failed to download logs: ${data.detail || data.error || 'Unknown error'}",

        "generating_authentication_link_usin": "Generating authentication link using the specified Project ID...",

        "not_enabled": "❌ Not Enabled",

        "download_credential_files_locally": "Download credential files locally",

        "average_calls_per_volume": "Average Requests per Credential",

        "failed_to_get_authentication_link_e": "Failed to get authentication link: {error}",

        "successfully_retrieved_email_dataus": "Successfully retrieved email: {data_user_email}",

        "code_assist_oauth_authentication": "Code Assist OAuth Authentication",

        "failed_to_create_websocket_connecti": "Failed to create WebSocket connection:",

        "omni_batch_verification_comp": "Omni Batch Verification Completed",

        "healthy_no_errors": "Healthy, no errors",

        "no_data_under_current_filter_condit": "No data under current filter conditions",

        "successfully_retrieved_email_email": "Successfully retrieved email: {email}",

        "get_google_oauth_authentication_lin": "Get Google OAuth Authentication Link",

        "failed_to_fetch_version_information": "Failed to fetch version information",

        "switch_to_mirror_proxy_address_with": "🚀 Switch to Mirror Proxy Address with one click",

        "enable_automatic_retry_of_failed_re": "Enable automatic retry of failed requests using other rotated credentials",

        "level": "Level:",

        "please_enter_password_to_login": "Please enter password to login",

        "failed_to_retrieve_credentials_from": "Failed to retrieve credentials from callback URL: {error}",

        "please_select_the_credentials_to_ve_dup": "Please select the credentials to verify first",

        "retrieved_authentication_link": "Retrieved Authentication Link:",

        "upload_failed_errordetail_errorerro": "Upload failed: ${error.detail || error.error || 'Unknown error'}",

        "are_you_sure_you_want_to_perform_on": "Are you sure you want to perform one-click credential deduplication?\\n\\nOnly one credential per email will be kept, others will be deleted.\\nThis action cannot be undone!",

        "omni_file_list_pending_uploa": "Omni file list pending upload:",

        "successfully_imported_loadedtotal_c": "✅ Successfully imported {loaded}/{total} credential files",

        "keepalive_request_interval_seconds": "Keep-alive request interval (seconds):",

        "healthy_no_errors_dup": "Healthy, no errors",

        "clear_failed_datadetail_dataerror_u": "Clear failed: ${data.detail || data.error || 'Unknown error'}",

        "network_error_while_clearing_logs_e": "Network error while clearing logs: {error_message}",

        "save_log_file_as": "Save log file as...",

        "upload_failed_connection_interrupte_dup": "Upload failed: Connection interrupted - Likely cause: Too many files ({count}) or network instability. Please upload in batches.",

        "resultfilename_resultmessage_config": "✅ {result_filename}: ${result.message || 'Configuration successful'}",

        "disable_credits": "Disable Credits",

        "please_select_the_files_to_operate": "Please select the files to operate on first",

        "batch_operation_failed_error": "Batch operation failed: {error}",

        "account_risk_control_and_circuit_br": "🛡️ Account Risk Control and Circuit Breaking Strategy",

        "determine_account_downgrade_or_disa": "Determine account downgrade or disabling within seconds based on API errors.",

        "reset_statistics": "Reset Statistics",

        "google_omni_authentication": "Google Omni Authentication",

        "failed_to_download_package_error": "Failed to download package: {error}",

        "div_stylecolor_dc3545reason_escapeh": "<div style=\"color: #dc3545;\">Reason: {escapeHtml_detail_reason}</div>",

        "test_successful_dup": "Test successful",

        "are_you_sure_you_want_to_refresh_us": "Are you sure you want to refresh user emails for all credentials? This may take some time.",

        "filter_filter": "(Filter: {filter})",

        "view_content": "View Content",

        "open_source_disclaimer_commercial_r": "Open Source Disclaimer: Commercial resale or distribution of Hippy in any form is prohibited. For testing, personal research, and academic exchange purposes only.",

        "failed_to_save_configuration_error": "Failed to save configuration: {error}",

        "total_credentials": "Total Credentials",

        "contact_and_feedback_channels": "Contact and Feedback Channels",

        "supports_json_credentials_or_zip_ar": "Supports .json credentials or .zip archives",

        "revert_to_google_official_address": "🔄 Revert to Google official address",

        "failed_to_retrieve_omni_cred": "Failed to retrieve Omni credentials from callback URL",

        "import_failed_datadetail_dataerror": "Import failed: ${data.detail || data.error || 'Unknown error'}",

        "new_version_foundncurrent_vversionn": "New version found!\\nCurrent: v{version}\\nLatest: v{latest}\\n\\nUpdate details: {log}",

        "network_error_msg": "Network error: {msg}",

        "unable_to_retrieve_user_email_error": "Unable to retrieve user email: {error}",

        "batch_action_operation_completed_su": "Batch {action} operation completed successfully!",

        "api_integration_endpoint_addresses": "API Integration Endpoint Addresses",

        "system_runtime_log_stream": "System Runtime Log Stream",

        "import_failed_error": "Import failed: {error}",

        "google_apis_core_endpoints": "Google APIs Core Endpoints:",

        "authentication_successful_saved_fil": "Authentication successful! Saved file content:",

        "click_the_view_quota_button_to_load": "Click the \"View Quota\" button to load quota information...",

        "waiting_to_fetch_the_latest_system": "Waiting to fetch the latest system console log output...",

        "control_panel_login_password": "Control Panel Login Password:",

        "unable_to_autodetect_project_id_ple": "Unable to auto-detect Project ID. Please manually enter your Google Cloud Project ID:",

        "click_this_link_to_authorize_your_g": "Click this link to authorize your Google account",

        "email_groupemailnkeep_groupkept_fil": "Email: {group_email}\\nKeep: {group_kept_file}\\nDelete: {group_deleted_files_join}\\n\\n",

        "omni_authentication_link_gen": "✅ Omni authentication link generated! Please click the link to complete authorization.",

        "check_successful_already_running_th": "Check successful! Already running the latest version.",

        "switched_to_official_endpoint_confi": "✅ Switched to official endpoint configuration. Remember to click the \"Save Config\" button to save settings.",

        "nplease_enter_index_1dataavailable": "\\nPlease enter index (1-{data_available_projects_length}):",

        "fetch_and_save_authentication_file": "Fetch and Save Authentication File",

        "failed_to_generate_authentication_l": "❌ Failed to generate authentication link: {error}",

        "action": "Action",

        "save_config": "Save Config",

        "fetch_omni_credentials": "Fetch Omni Credentials",

        "failed_to_generate_authentication_l_dup": "Failed to generate authentication link",

        "retry_using_the_selected_project": "Retry using the selected project...",

        "div_styletextalign_center_padding_2_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                        <div style=\"font-weight: bold; margin-bottom: 5px;\">Network Error</div>\n\n                        <div style=\"font-size: 13px; color: #666;\">{error_message}</div>\n\n                    </div>",

        "credential_available": "Credential available",

        "google_omni_authentication_m": "Google Omni Authentication Mode",

        "zip_archive": "(ZIP Archive)",

        "are_you_sure_you_want_to_delete_fil": "Are you sure you want to delete {filename}?",

        "page_thiscurrentpage_of_totalpages": "Page {this_currentPage} of {totalPages} (Showing {startItem}-{endItem}, Total {this_totalCount})",

        "failed_to_clear_logs_datadetail_dat": "Failed to clear logs: ${data.detail || data.error || 'Unknown error'}",

        "please_select_the_credentials_to_co": "Please select the credentials to configure Preview first",

        "websocket_connected": "WebSocket connected",

        "enable_autoban_for_credentials_on_s": "Enable Auto-Ban for credentials on specific error codes",

        "preview_channel_configuration_faile": "❌ Preview channel configuration failed\\n\\nFile: {filename}\\n\\n{errorMsg}",

        "autobacksource_failed_use_the_quick": "Auto-back-source failed? Use the quick callback channel",

        "operation_failed_error": "Operation failed: {error}",

        "please_fetch_the_authentication_lin": "Please fetch the authentication link and complete authorization first",

        "bidirectional_native_format_convers": "Bidirectional native format conversion",

        "oneclick_deduplication_failed_error": "One-click deduplication failed: {error}",

        "disable": "Disable",

        "click_this_link_to_authorize_antigr": "Click this link to authorize Omni mode",

        "deduplication_network_error_errorme": "Deduplication network error: {error_message}",

        "after_successful_authorization_the": "After successful authorization, the browser will redirect and display a connection error for localhost:11451; this is normal behavior;",

        "failed_to_get_environment_variable": "Failed to get environment variable status: {error}",

        "max_antitruncation_resume_attempts": "Max anti-truncation resume attempts:",

        "log_connection_channel_established": "Log connection channel established successfully.",

        "test_failednfile_filenamen": "❌ Test failed\\nFile: {filename}\\n",

        "global_configuration_saved_successf": "Global configuration saved successfully!",

        "executing_batch_actionlabel_operati": "Executing batch {actionLabel} operation...",

        "monitor_credential_count": "Monitor credential count",

        "switched_to_official_endpoint_confi_dup": "Switched to official endpoint configuration. Remember to click the 'Save Config' button to save settings.",

        "local_credential_storage_absolute_p": "Local credential storage absolute path:",

        "click_to_open_linknrightclick_to_co": "Click to open link\\nRight-click to copy link",

        "upload_failed_http_xhrstatus": "Upload failed: HTTP {xhr_status}",

        "verification_successful": "Verification successful",

        "force_enable_compatibility_mode_mer": "Force enable compatibility mode (merge System protocol messages into User)",

        "clear_buffer_logs": "Clear buffer logs",

        "div_stylefontsize_12px_color_666_ma": "<div style=\"font-size: 12px; color: #666; margin-bottom: 5px;\">Details:</div>",

        "error_dataerror_failed_to_get_authe": "❌ Error: ${data.error || 'Failed to get authentication file'}",

        "select_all": "Select All",

        "if_this_field_is_configured_it_will": "If this field is configured, it will force-override the API and panel passwords. It is recommended to leave it blank.",

        "autologin_successful": "Auto-login successful",

        "failed_to_save_config_datadetail_da": "Failed to save config: ${data.detail || data.error || 'Unknown error'}",

        "batch_operation_completed_processed": "Batch operation completed: Processed {success}/{total} files successfully.",

        "tip_leave_blank_for_firsttime_use_t": "Tip: Leave blank for first-time use; the system will automatically allocate and detect.",

        "configuration_failed": "Configuration failed",

        "successfully_imported_dataloaded_co": "✅ Successfully imported {data_loaded_count}/{data_total_count} credential files",

        "switched_to_mirror_url_configuratio": "✅ Switched to mirror URL configuration. Remember to click the \"Save Config\" button to save settings.",

        "zip_files_will_automatically_extrac": "ZIP files will automatically extract all JSON credential files.",

        "adjust_system_proxy_endpoint_addres": "Adjust system proxy, endpoint addresses, security policies, and high-frequency retry parameters. Most items take effect immediately after saving.",

        "loaded_count_type_credential_files": "Loaded {count} {type} credential files",

        "log_stream_connection_error": "Log stream connection error:",

        "quota_information_loaded_successful": "✅ Quota information loaded successfully",

        "failed_to_fetch_authentication_link": "Failed to fetch authentication link",

        "return_directly_to_the_current_cont": "Return directly to the current control panel page and click the \"Fetch and Save Authentication File\" button below to complete integration;",

        "retry_interval_seconds": "Retry interval (seconds):",

        "autoban_circuit_breaker": "Auto-Ban Circuit Breaker",

        "usage_statistics_loaded_for_count_f": "Usage statistics loaded for {count} files",

        "operation_successful": "Operation successful:",

        "download": "Download",

        "new_version_available": "New version available",

        "openai_compatibility": "OpenAI Compatibility:",

        "verification_successfulnfile_filena": "✅ Verification successful!\\nFile: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "div_styletextalign_center_padding_2_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                            <div style=\"font-weight: bold; margin-bottom: 5px;\">Failed to fetch quota info</div>\n\n                            <div style=\"font-size: 13px; color: #666;\">{errorMsg}</div>\n\n                        </div>",

        "delete": "Delete",

        "div_styletextalign_center_padding_2_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                            <div style=\"font-weight: bold;\">Load failed</div>\n\n                            <div style=\"font-size: 12px; margin-top: 8px;\">{errorMsg}</div>\n\n                        </div>",

        "file_format_of_name_not_supported_o": "File format of {name} not supported; only JSON and ZIP files are supported",

        "project_info": "Project Info",

        "the_following_configurations_have_t_dup": ", the following configurations have taken effect immediately: {data_hot_updated_join}",

        "unable_to_fetch_user_email": "Unable to fetch user email",

        "failed_to_fetch_credentials_from_ca": "Failed to fetch credentials from callback URL",

        "advanced_settings_specify_google_cl": "Advanced Settings: Specify Google Cloud Project ID (Optional)",

        "starting_batch_project_id_verificat": "Starting batch Project ID verification task...",

        "open_github_issues": "Open GitHub Issues",

        "when_google_apis_return_these_error": "When Google APIs return these error codes, the system will automatically disable this account. It is recommended to enable circuit breaking for 403 errors.",

        "failed_to_fetch_error_message": "Failed to fetch error message",

        "error_dataerror_failed_to_generate": "❌ Error: ${data.error || 'Failed to generate authentication link'}",

        "service_network_listening_configura": "⚙️ Service Network Listening Configuration",

        "connecting": "Connecting...",

        "credentials_fetched_successfully_fr": "Credentials fetched successfully from callback URL!",

        "click_the_link_above_sign_in_to_you": "Click the link above, sign in to your Google account in a new browser tab, and grant authorization.",

        "omni_credential_file_managem": "Omni Credential File Management",

        "failed_to_configure_preview_channel": "Failed to configure Preview channel: {error_message}",

        "authentication_successful_project_i": "✅ Authentication successful! Project ID automatically detected as: {id}, file saved to: {path}",

        "please_enter_a_valid_url_starting_w": "Please enter a valid URL (starting with http:// or https://)",

        "successfully_updated_preview_channe": "Successfully updated Preview channel status for {count} credential files",

        "pending_code_assist_file_upload_list": "Pending Code Assist file upload list:",

        "exclusive_industrywide_support_for": "Exclusive industry-wide support for streaming resumable uploads.",

        "configuration_failed_for_all_failed": "❌ Configuration failed for all! Failed {failCount}/{selectedFiles_length} credentials",

        "omni_batch_verification_comp_dup": "Omni batch verification complete!\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",

        "enabled": "✅ Enabled",

        "display_and_maintain_your_code_assist_prox": "Display and maintain your Code Assist proxy channels, supporting individual or batch verification, download, status toggling, and deletion.",

        "batch_operation_network_error_error": "Batch operation network error: {error}",

        "retrying_with_manually_entered_proj": "Retrying with manually entered Project ID...",

        "get_omni_authentication_link": "Get Omni authentication link",

        "json_file": "(JSON file)",

        "are_you_sure_you_want_to_deduplicat": "Are you sure you want to deduplicate Omni credentials?\\n\\nOnly one credential per email will be kept, and others will be deleted.\\nThis action cannot be undone!",

        "display_and_maintain_your_antigravi": "Display and maintain your Omni proxy accounts and associated usage quotas.",

        "supports_json_files_or_zip_archives": "Supports .json files or .zip archives",

        "code_assist_api_endpoint": "Code Assist API Endpoint:",

        "failed_to_fetch_error_message_error": "❌ Failed to fetch error message: {errorMsg}",

        "failed_to_load_file_content": "Failed to load file content:",

        "div_stylebackground_white_borderlef": "<div style=\"background: var(--bg); border: 1px solid var(--border); border-left: 4px solid {percentageColor}; border-radius: var(--radius); padding: 8px 10px;\">\n\n                                    <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;\">\n\n                                        <div style=\"font-weight: bold; color: #333; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; margin-right: 8px;\" title=\"{modelName} - {remainingPercentage}% remaining - {resetTime}\">\n\n                                            {modelName}\n\n                                        </div>\n\n                                        <div style=\"font-size: 13px; font-weight: bold; color: {percentageColor}; white-space: nowrap;\">\n\n                                            {remainingPercentage}%\n\n                                        </div>\n\n                                    </div>\n\n                                    <div style=\"width: 100%; height: 8px; background-color: var(--bg-subtle); border-radius: var(--radius); overflow: hidden; margin-bottom: 4px;\">\n\n                                        <div style=\"width: {usedPercentage}%; height: 100%; background-color: {percentageColor}; transition: none;\"></div>\n\n                                    </div>\n\n                                    <div style=\"font-size: 10px; color: #666; text-align: right;\">\n\n                                        {resetTime______N_A___________resetTime}\n\n                                    </div>\n\n                                </div>",

        "failed_to_check_for_updates_error": "Failed to check for updates: {error}",

        "preview_channel_configuration_succe_dup": "Preview channel configuration successful",

        "clear_selection_list": "Clear selection list",

        "logs_cleared_waiting_for_new_logs": "Logs cleared, waiting for new logs...",

        "running_normally": "Running normally",

        "lightweight_singlefile_deployment": "Lightweight single-file deployment",

        "button_to_save_settings_success_fun": "button to save settings', 'success');\n\n    }\n\n}\n\n\n\nfunction restoreOfficialUrls() {\n\n    if (confirm('Are you sure you want to reset all endpoints to official URLs?')) {\n\n        for (const [fieldId, url] of Object.entries(officialUrls)) {\n\n            const field = document.getElementById(fieldId);\n\n            if (field && !field.disabled) field.value = url;\n\n        }\n\n        showStatus('✅ Switched to official endpoint configuration, remember to click",

        "test_successfulnfile_filenamenstatu": "✅ Test successful!\\nFile: {filename}\\nStatus: ${data.message || 'Omni credential valid'} ({data_status_code____200})",

        "full_version_datafull_hashncommit_m": "Full version: {data_full_hash}\\nCommit message: {data_message}\\nCommit time: {data_date}",

        "importing_credentials_from_environm": "Importing credentials from environment variables...",

        "server_bound_host_ip_address": "Server bound Host IP Address:",

        "verification_failed_for_all_failed": "❌ Verification failed for all! Failed {failCount}/{selectedFiles_length} Omni credentials",

        "github_issues_support": "GitHub Issues",

        "download_failed_name": "Download failed: {name}",

        "login_successful": "Login successful!",

        "network_error_error": "Network error: {error}",

        "batch_verification_completennsucces": "Batch verification complete!\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",

        "http_error_codes_that_trigger_circu": "HTTP error codes that trigger circuit breaker/ban (comma separated):",

        "upload_failed_error": "Upload failed: {error}",

        "batch_verification_complete": "Batch verification complete",

        "storage_and_proxy_settings": "📂 Storage and Proxy Settings",

        "performing_batch_action_operation": "Performing batch {action} operation...",

        "this_setting_may_slightly_reduce_co": "This setting may slightly reduce comprehension for complex prompts but perfectly resolves empty returns or streaming circuit breaker errors in specific third-party clients caused by missing system_instructions.",

        "fetching_environment_variable_statu": "Fetching environment variable status...",

        "nnerror_details_errordetail": "\\n\\nError details: {errorDetail}",

        "highquality_aesthetic_panel_layout": "High-quality, aesthetic panel layout, compatible with all modern browsers.",

        "load_failed_datadetail_dataerror_un": "Load failed: ${data.detail || data.error || 'Unknown error'}",

        "access_password_to_protect_this_con": "Access password to protect this console page from malicious tampering.",

        "if_running_on_a_remote_vps_or_a_hea": "If running on a remote VPS or a headless environment: please expand \"Unable to access origin shortcut channel\" below for instructions.",

        "log_file_download_successful_filena": "Log file download successful: {filename}",

        "automatically_switch_to_another_rot": "Automatically switch to another rotated credential on Omni errors",

        "connected": "Connected",

        "brstrongavailable_projectsstrongbr": "<br><strong>Available projects:</strong><br>",

        "div_span_classfilenamefileicon_file": "<div>\n\n                        <span class=\"file-name\">{fileIcon} {file_name}</span>\n\n                        <span class=\"file-size\">({formatFileSize_file_size}{fileType})</span>\n\n                    </div>\n\n                    <button class=\"remove-btn\" onclick=\"{type______omni_____removeOmniFile_____removeFile}({index})\">Delete</button>",

        "passthrough_model_thinking_process": "Pass-through model thinking process to frontend response",

        "log_connection_channel_disconnected": "Log connection channel disconnected.",

        "parallel_verifying_selectedfileslen": "🔍 Parallel verifying {selectedFiles_length} credentials, please wait...",

        "failed_to_retrieve_authentication_f": "❌ Failed to retrieve authentication file: {error}",

        "applicable_to_the_latest_gemini_20": "Applicable to the latest Gemini 2.0 series models with reasoning capabilities. If disabled, thinking process content will be filtered out for cleaner direct responses.",

        "log_stream_connection_disconnected": "Log stream connection disconnected",

        "environment_variable_status_check_c": "Environment variable status check complete",

        "project_description": "Omni Gateway is a universal AI router for coding tools. Features smart auto-fallback, token compression, and seamless format translation to maximize free and premium LLMs.",

        "click_the_view_error_button_to_load": "Click the \"View Error\" button to load error information...",

        "loaded_datatotal_type_omni_a": "Loaded {data_total} {type______omni_____Omni} credential files",

        "email_not_retrieved": "Email not retrieved",

        "tip": "Tip",

        "load_failed_error": "Load failed: {error}",

        "omni_credential_valid": "Omni credential valid",

        "in_cooldown": "In cooldown",

        "verification_failed": "Verification failed",

        "gemini_native": "Gemini Native:",

        "error_code_code": "Error code: {code}",

        "api_endpoint_proxy_setup": "🔗 API Endpoint Proxy Setup",

        "login_failed_incorrect_password": "Login failed! Incorrect password.",

        "used_for_http_authorization_bearer": "Used for HTTP Authorization Bearer Token verification on proxy endpoint requests.",

        "enable_batch": "Enable batch",

        "failed_to_download_package_errormes": "Failed to download package: {error_message}",

        "batch_configuration_complete_succes": "⚠️ Batch configuration complete: {successCount}/{selectedFiles_length} successful, {failCount} failed",

        "claude_compatible": "Claude Compatible:",

        "verifying_omni_project_id_pl": "🔍 Verifying Omni Project ID, please wait...",

        "invalid_selection_please_restart_th": "Invalid selection, please restart the authentication process",

        "error_code_dup": "Error code:",

        "configuration_data_loaded_successfu": "Configuration data loaded successfully!",

        "leave_blank_to_attempt_automatic_de": "Leave blank to attempt automatic detection and project creation.",

        "no_usage_breakdown_statistics_avail": "No usage breakdown statistics available",

        "all_verifications_successful_succes": "✅ All verifications successful! Successfully verified {successCount}/{selectedFiles_length} credentials",

        "successfully_deleted_datadeleted_co": "✅ Successfully deleted {data_deleted_count} environment variable credential files",

        "are_you_sure_you_want_to_delete_fil_dup": "Are you sure you want to delete {filename}?",

        "verify": "Verify",

        "click_to_select_files_or_drag_and_d": "Click to select files, or drag and drop files here",

        "configuration_successful": "Configuration successful",

        "error": "Error:",

        "retrieving_credentials_from_callbac": "Retrieving credentials from callback URL...",

        "preview_channel_configuration_faile_dup": "Preview channel configuration failed",

        "n_restart_notice_datarestart_notice": "\\n⚠️ Restart notice: {data_restart_notice}",

        "service_usage_api_status_management": "Service Usage API Status Management Endpoint:",

        "failed_to_retrieve_authentication_f_dup": "Failed to retrieve authentication file",

        "please_select_a_projectnnplease_ent": "Please select a project:\\n\\nPlease enter the sequence number (1-{count}):",

        "per_page": "Per page:",

        "failed_to_check_for_updates_dataerr": "Failed to check for updates: {data_error}",

        "network_error_errormessage": "Network error: {error_message}",

        "minimal_resource_footprint_perfectl": "Minimal resource footprint, perfectly adapted for all major PAAS and Docker environments.",

        "application_keepalive_settings": "☕ Application Keep-Alive Settings",

        "save_global_configuration": "Save global configuration",

        "failed_to_load_configuration_datade": "Failed to load configuration: ${data.detail || data.error || 'Unknown error'}",

        "uploading_and_extracting_zip_file": "Uploading and extracting ZIP file...",

        "are_you_sure_you_want_to_batch_veri_dup": "Are you sure you want to batch verify Project IDs for {selectedFiles_length} credentials?\\n\\nVerification will be processed in parallel to increase speed.",

        "refreshing_all_user_emails": "Refreshing all user emails...",

        "operation_failed_datadetail_dataerr": "Operation failed: ${data.detail || data.error || 'Unknown error'}",

        "are_you_sure_you_want_to_delete_the": "Are you sure you want to delete the {selectedFiles_length} selected files?\\nNote: This action cannot be undone!",

        "new_version_foundncurrent_vdatavers": "New version found!\\nCurrent: v{data_version}\\nLatest: v{data_latest_version}\\n\\nRelease Notes: ${data.latest_message || 'None'}",

        "div_stylecolor_007bfftype_highlight": "<div style=\"color: #007bff;\">Type: {highlightedType}</div>",

        "failed_to_check_for_updates_errorme": "Failed to check for updates: {error_message}",

        "nerror_detailsndataerror": "\\nError details:\\n{data_error}",

        "omni_authentication_successf_dup": "✅ Omni authentication successful! File saved to: {data_file_path}",

        "batch_verify_project_id": "Batch verify Project ID",

        "filter_thiscurrentstatusfilter_enab": "(Filter: ${this.currentStatusFilter === 'enabled' ? 'Enabled only' : 'Disabled only'})",

        "are_you_sure_you_want_to_configure": "Are you sure you want to configure all endpoints to official addresses?",

        "perfect_responsive_support": "Perfect responsive support",

        "welcome_to_join_us_to_discuss_usage": "Welcome to join us to discuss usage and submit feature requests:",

        "successfully_deleted_count_environm": "✅ Successfully deleted {count} environment variable credential files",

        "monitor_realtime_request_details_an": "Monitor real-time request details and rotation logic sent to the Google Cloud API to quickly troubleshoot network proxy or rate limiting issues.",

        "error_errormsg": "Error: {errorMsg}",

        "unlimited": "Unlimited",

        "drag_and_drop_or_select_your_existi": "Drag and drop or select your existing Code Assist or Omni authentication JSON/ZIP file to upload to the server.",

        "authentication_successful_file_save": "✅ Authentication successful! File saved to: {data_file_path}",

        "connection_lost": "Connection lost",

        "batch_preview_channel_configuration": "Batch Preview channel configuration complete!\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",

        "are_you_sure_you_want_to_actionlabe": "Are you sure you want to {actionLabel} the {selectedFiles_length} selected files?",

        "page_page_of_total_showing_startend": "Page {page} of {total} (Showing {start}-{end}, {count} items in total)",

        "loading_file_content": "Loading file content...",

        "generating_authentication_link": "Generating authentication link...",

        "failed_to_refresh_emails": "Failed to refresh emails",

        "preview_only": "Preview only",

        "max_retries_on_failure": "Max retries on failure:",

        "batch_operation_complete_successful": "Batch operation complete: Successfully processed {successCount}/{selectedFiles_length} files",

        "deduplication_detailsnn": "Deduplication details:\\n\\n",

        "synchronizing_current_system_config": "Synchronizing current system configuration to the server...",

        "ip_address_to_listen_on_0000_allows": "IP address to listen on. 0.0.0.0 allows public access. Requires a restart to apply changes.",

        "are_you_sure_you_want_to_reset_usag": "Are you sure you want to reset usage statistics for {filename}?",

        "please_select_at_least_one_credenti": "Please select at least one credential to proceed!",

        "authentication_successful_file_save_dup": "✅ Authentication successful! File saved to: {path}",

        "retrieving_omni_credentials": "Retrieving Omni credentials from callback URL...",

        "configuring_preview_channel_please": "🔧 Configuring Preview channel, please wait...",

        "verification_failed_error": "Verification failed: {error}",

        "please_select_the_omni_crede_dup": "❌ Please select the Omni credential to verify first",

        "successfully_uploaded_datauploaded": "Successfully uploaded {data_uploaded_count} {type______omni_____Omni} file(s)",

        "dataexisting_env_files_count_files": "{data_existing_env_files_count} file(s)",

        "waiting_for_omni_oauth_callb": "Waiting for Omni OAuth callback...",

        "model_protocol_compatibility_overri": "🧩 Model Protocol Compatibility Override",

        "maximum_retries_for_resuming_stream": "Maximum retries for resuming stream data from the break point when calling models with the '-stream-truncation-prevention' suffix.",

        "successfully_uploaded_count_type_fi": "Successfully uploaded {count} {type} file(s)",

        "failed_to_retrieve_credentials_from_dup": "Failed to retrieve credentials from callback URL: {error_message}",

        "enable_credits": "Enable Credits",

        "code_assist_creds__environment_variable_no": "CODE_ASSIST_CREDS_* environment variable not found",

        "autoscroll_to_bottom": "Auto-scroll to bottom",

        "please_select_the_credential_to_con": "❌ Please select the credential to configure Preview for first",

        "please_select_the_file_to_upload_fi": "Please select the file to upload first",

        "failed_to_check_for_updates": "Failed to check for updates:",

        "enabled_dup": "Enabled",

        "retrieve_the_latest_google_cloud_sd": "Retrieve the latest Google Cloud SDK Omni native authentication credentials.",

        "global_upstream_proxy_url": "Global upstream proxy URL:",

        "processing_credential_deduplication": "Processing credential deduplication...",

        "24h_total_calls": "24h Total Requests",

        "status": "Status:",

        "maximum_retry_limit_for_resuming_st": "Maximum retry limit for resuming stream output if it gets truncated while using models with the '-stream-truncation-prevention' suffix.",

        "omni_verification_successful": "✅ Omni verification successful!\\n\\nFile: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "all_configured_successfully_preview": "✅ All configured successfully! Preview channel configured for {successCount}/{selectedFiles_length} credentials",

        "enable_credit": "Enable Credit",

        "24hour_call_breakdown_statistics": "24-hour request breakdown statistics",

        "are_you_sure_you_want_to_refresh_us_dup": "Are you sure you want to refresh user emails for all Omni credentials? This may take some time.",

        "unable_to_retrieve_version_informat": "Unable to retrieve version information",

        "batch_disable_dup": "Batch disable",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                        <div style=\"font-weight: bold;\">Network Error</div>\n\n                        <div style=\"font-size: 12px; margin-top: 8px;\">{error_message}</div>\n\n                    </div>",

        "upstream_network_proxy_required_for": "Upstream network proxy required for local access to Google APIs. Leave empty for direct connection.",

        "if_you_find_any_bugs_or_have_design": "If you find any bugs or have design suggestions, feel free to open Issues on our GitHub repository. Pull Requests are also welcome to help enrich the ecosystem.",

        "view_error": "View error",

        "verification_failednnerrormsg": "❌ Verification failed\\n\\n{errorMsg}",

        "failed_to_retrieve_omni_cred_dup": "Failed to retrieve Omni credentials from callback URL: {error_message}",

        "code_assist_credential_batch_upload": "Code Assist Credential Batch Upload",

        "checking_for_updates": "Checking for updates...",

        "unknown_version": "Unknown version",

        "oneclick_credential_deduplication_i": "One-click credential deduplication in progress...",

        "operation_successful_action": "Operation successful: {action}",

        "download_failed_filename": "Download failed: {filename}",

        "retrieve_and_save_omni_crede": "Retrieve and save Omni credentials",

        "ag_credentials": "AG Credentials",

        "view_quota": "View quota",

        "logged_out": "Logged out",

        "are_you_sure_you_want_to_reset_usag_dup": "Are you sure you want to reset usage statistics for all files? This action cannot be undone!",

        "configuration_successfulnfile_filen": "✅ Configuration successful!\\nFile: {filename}\\nStatus: {data_message}",

        "batch_delete_dup": "Batch delete",

        "modelname_remainingpercentage_remai": "{modelName} - {remainingPercentage}% remaining - {resetTime}",

        "configuration_management": "Configuration Management",

        "retrieving_user_emails": "Retrieving user emails...",

        "set_preview": "Set Preview",

        "authentication_successful_project_i_dup": "✅ Authentication successful! Project ID automatically detected as: {data_credentials_project_id}, file saved to: {data_file_path}",

        "automatic_quota_avoidance_rotation": "Automatic Quota Avoidance Rotation",

        "reload_configuration_data": "Reload Configuration Data",

        "key_technical_highlights": "Key Technical Highlights",

        "clear_failed_error": "Clear failed: {error}",

        "generating_omni_authenticati": "Generating Omni authentication link...",

        "upload_failed_errormessage": "Upload failed: {error_message}",

        "failed_to_update_preview_status_in": "Failed to update Preview status in bulk: {error}",

        "downloaded_filename": "✅ Downloaded: {filename}",

        "bulk_upload_local_credentials": "Bulk Upload Local Credentials",

        "div_stylebackground_lineargradient1": "<div style=\"background: var(--bg-subtle); color: var(--text-primary); padding: 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 15px;\">\n\n                                <h4 style=\"margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;\">\n\n                                    <span style=\"font-size: 20px;\">📊</span>\n\n                                    <span>Quota Information Details</span>\n\n                                </h4>\n\n                                <div style=\"font-size: 12px; opacity: 0.9; margin-top: 5px;\">File: {filename}</div>\n\n                            </div>\n\n                            <div style=\"display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;\">",

        "automatic_retry_reconnection_mechan": "🔁 Automatic Retry & Reconnection Mechanism",

        "download_all_credentials_as_archive": "Download All Credentials as Archive",

        "waiting_for_oauth_callback": "Waiting for OAuth callback...",

        "local_storage_directory_for_uploade": "Local storage directory for uploaded and authorized JSON files.",

        "bulk_preview_channel_configuration": "Bulk Preview channel configuration complete",

        "disable_credit": "Disable Credit",

        "no_logs_yet": "No logs yet...",

        "already_up_to_date": "Already up to date!",

        "test_successfulnfile_filenamenstatu_dup": "✅ Test successful!\\nFile: {filename}\\nStatus: ${data.message || 'Credentials available'} ({data_status_code____200})",

        "deduplication_complete_deleted_data": "Deduplication complete: Deleted {data_deleted_count} duplicate credentials, kept {data_kept_count} credentials ({data_unique_emails_count} unique emails)",

        "are_you_sure_you_want_to_perform_th": "Are you sure you want to perform the {action} bulk operation on the {count} selected credentials?",

        "bulk_operation_failed_datadetail_da": "Bulk operation failed: ${data.detail || data.error || 'Unknown error'}",

        "ncredit_datacredit_amount": "\\nCredit: {data_credit_amount}",

        "authentication_failed_please_log_in": "Authentication failed, please log in again",

        "code_assist_credential_file_management": "Code Assist Credential File Management",

        "failed_to_retrieve_version_informat": "Failed to retrieve version information:",

        "filter_level": "Filter Level:",

        "failed_to_get_email_errormessage": "Failed to get email: {error_message}",

        "suitable_for_cloud_servervps_deploy": "Suitable for cloud server/VPS deployment, Docker container environments, or scenarios where port 11451 is blocked by a firewall.",

        "connection_error": "Connection error",

        "omni_credentials_successfull": "Omni credentials successfully retrieved from callback URL!",

        "are_you_sure_you_want_to_configure_dup": "Are you sure you want to configure all endpoints as mirror URLs?",

        "sever_log_channel": "Sever log channel",

        "configuration_loaded_successfully": "Configuration loaded successfully",

        "unable_to_load_file_content": "Unable to load file content:",

        "bulk_enable_credit": "Bulk enable Credit",

        "live_connection_status": "Live connection status:",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\">📊 Loading quota information...</div>",

        "connection_failed": "Connection failed",

        "oneclick_deduplication_complete_del": "One-click deduplication complete! Deleted {deleted} duplicate files, kept {kept} unique account files.",

        "verifying_project_id_please_wait": "🔍 Verifying Project ID, please wait...",

        "email_refresh_network_error_errorme": "Email refresh network error: {error_message}",

        "waiting_for_oauth_callback_this_may": "Waiting for OAuth callback, this may take some time...",

        "project_id_required_to_complete_aut": "Project ID required to complete authentication, please restart and enter the correct Project ID",

        "error_code_datastatus_code_response": "Error code: {data_status_code____response_status}",

        "cooling_down": "Cooling down:",

        "start_bulk_upload": "Start bulk upload",

        "attempting_to_autodetect_project_id": "Attempting to auto-detect Project ID, generating authentication link...",

        "check_for_updates_failed_dataupdate": "Check for updates failed: ${data.update_error || 'Unknown error'}",

        "upload_failed": "Upload failed:",

        "all_verifications_failed_failed_fai": "❌ All verifications failed! Failed {failCount}/{selectedFiles_length} credentials",

        "upload_failed_server_response_forma": "Upload failed: Server response format error",

        "deduplication_failed": "Deduplication failed",

        "credit_resultcreditamount": "(Credit: {result_creditAmount})",

        "are_you_sure_you_want_to_delete_the_dup": "Are you sure you want to delete the credential file?\\n{filename}",

        "test_failed": "Test failed",

        "bulk_configure_preview_channels": "Bulk configure Preview channels",

        "github_open_source_repository": "GitHub Open Source Repository:",

        "test_failed_errormessage": "Test failed: {error_message}",

        "view_account_email": "View account email",

        "longtext_truncation_recovery_contro": "⏱️ Long-text Truncation Recovery Control",

        "automation_enabled": "Automation enabled:",

        "div_stylepadding_12px_marginbottom": "<div style=\"padding: 12px; margin-bottom: 10px; border-left: 3px solid #dc3545; background-color: #f8f9fa;\">\n\n                                    <div style=\"font-weight: bold; color: #dc3545; margin-bottom: 8px;\">Error code: {errorCode}</div>\n\n                                    <div style=\"line-height: 1.6; color: #333; white-space: pre-wrap; word-break: break-word;\">\n\n                                        {highlightedMsg}\n\n                                    </div>\n\n                                    {detailsHtml}\n\n                                </div>",

        "refresh_all_account_emails": "Refresh all account emails",

        "about_omni-gateway": "About Omni Gateway",

        "get_authentication_file": "Get authentication file",

        "n_restart_reminder_notice": "\\n⚠️ Restart Reminder: {notice}",

        "test_failed_datamessage_error_code": "❌ Test failed - ${data.message || 'Error code: ' + (data.status_code || response.status)}",

        "service_keepalive_heartbeat_request": "Service keep-alive heartbeat request URL:",

        "after_the_google_authorization_redi": "After the Google authorization redirect, copy the full URL from your browser address bar (even if it shows a connection error) and paste it into the input box below.",

        "disabled": "Disabled",

        "upload_failed_http_status": "Upload failed: HTTP {status}",

        "disconnected": "Disconnected",

        "if_the_redirect_fails_and_shows_an": "If the redirect fails and shows an error about being unable to connect to localhost:11451, return to this control panel;",

        "unknown_error": "Unknown error",

        "testing_omni_credentials_ple": "🧪 Testing Omni credentials, please wait...",

        "if_you_cannot_return_to_the_source": "If you cannot return to the source, you can copy the full URL after the redirect and expand the quick channel below to parse it.",

        "verification_failed_errormessage": "Verification failed: {error_message}",

        "nerror_detailsnjsonstringifyerrorob": "\\nError details:\\n{JSON_stringify_errorObj__null__2}",

        "log_stream_connected_successfully": "Log stream connected successfully",

        "clearing_environment_variable_crede": "Clearing environment variable credential files...",

        "get_authentication_link": "Get authentication link",

        "resulterror_step_resultstep": "{result_error} (Step: {result_step})",

        "network_error": "Network error:",

        "failed_to_retrieve_environment_vari": "Failed to retrieve environment variable status: ${data.detail || data.error || 'Unknown error'}",

        "count_items_selected": "{count} items selected",

        "are_you_sure_you_want_to_clear_all": "Are you sure you want to clear all credential files imported from environment variables?\\nThis will delete all authentication files starting with \"env-\".",

        "bulk_operation_network_error_errorm": "Bulk operation network error: {error_message}",

        "streaming_truncation_recovery": "-Streaming truncation recovery",

        "failed_to_get_quota_information": "Failed to get quota information",

        "click_the_button_below_to_retrieve": "Click the button below to retrieve and automatically save the credential file directly;",

        "seamlessly_switch_to_idle_accounts": "Seamlessly switch to idle accounts to effectively avoid 429 rate limits.",

        "bind_the_listening_tcp_port_changes": "Bind the listening TCP port; changes require a restart to take effect.",

        "bulk_disable_credit": "Bulk disable Credit",

        "failed": "Failed",

        "reset_failed_datamessage_datadetail": "Reset failed: ${data.message || data.detail || data.error || 'Unknown error'}",

        "failed_to_get_quota_information_err": "❌ Failed to get quota information: {error_message}",

        "realtime_logs": "Real-time logs",

        "please_enter_the_access_password": "Please enter the access password!",

        "zip_files_will_be_automatically_dec": "ZIP files will be automatically decompressed and filtered to extract JSON credentials.",

        "oauth_authentication_server_endpoin": "OAuth authentication server endpoint:",

        "are_you_sure_you_want_to_batch_set": "Are you sure you want to batch set the Preview channel for {selectedFiles_length} credentials?\\n\\nConfiguration will be processed in parallel for speed.",

        "settings_saved_successfully_success": "Settings saved successfully",

        "configuration_saved_successfully": "Configuration saved successfully",

        "preview_not_supported": "Preview not supported",

        "please_select_a_projectnn": "Please select a project:\\n\\n",

        "please_select_the_files_to_upload": "Please select the files to upload",

        "are_you_sure_you_want_to_action_the": "Are you sure you want to {action} the selected {count} files?",

        "a_hrefurl_target_blank_stylecolor_0": "<a href=\"{url}\" target=\"_blank\" style=\"color: #007bff; text-decoration: underline; word-break: break-all;\" title=\"Click to open: {url}\">{url}</a>",

        "retry_fetching_authentication_file": "Retry fetching authentication file",

        "manually_connect_log_channel": "Manually connect log channel",

        "error_information_loaded_successful": "✅ Error information loaded successfully",

        "universal_shortcut_override_passwor": "Universal shortcut override password (optional):",

        "login_failed_datadetail_dataerror_u": "Login failed: ${data.detail || data.error || 'Unknown error'}",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\">⏳ Loading error information...</div>",

        "log_stream_connection_disconnected_dup": "Log stream connection disconnected",

        "system_configuration_saved_successf": "✅ System configuration saved successfully",

        "div_stylefontsize_12px_color_666sta": "<div style=\"font-size: 12px; color: #666;\">Status: {escapeHtml_parsedMsg_error_status}</div>",

        "api_access_authentication_password": "API access authentication password (API Key):",

        "parallel_testing_selectedfileslengt": "🔍 Parallel testing {selectedFiles_length} Omni credentials, please wait...",

        "operation_failed": "Operation failed:",

        "all_omni_credentials_packed": "✅ All Omni credentials packed and downloaded",

        "operation_successful_action_dup": "Operation successful: {action}",

        "omni_api_endpoint": "Omni API endpoint:",

        "authentication_link_generated_proje": "Authentication link generated (Project ID: {data_detected_project_id}), please click the link to complete authorization",

        "configuring_preview_channel_status": "Configuring Preview channel status in batch...",

        "after_successful_authorization_the_dup": "After successful authorization, the system will automatically detect and activate the necessary Gemini Cloud Assist API and Gemini for Google Cloud API services for your Google Cloud project, no manual configuration required.",

        "batch_upload_omni_credential": "Batch upload Omni credentials",

        "checking": "Checking...",

        "please_enter_the_callback_url": "Please enter the callback URL",

        "extract_credentials_from_callback_l": "Extract credentials from callback link",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #28a745;\"><div style=\"font-size: 48px; margin-bottom: 10px;\">✅</div><div style=\"font-weight: bold;\">No error records</div><div style=\"font-size: 12px; color: #666; margin-top: 8px;\">This credential is running normally</div></div>",

        "no_details_available": "No details available",

        "global_system_configuration": "Global system configuration",

        "network_error_while_downloading_log": "Network error while downloading logs: {error_message}",

        "authentication_link_generated_proje_dup": "Authentication link generated (Project ID: {id}), please click the link to complete authorization",

        "listening_port": "Listening Port:",

        "email_refresh_complete_successfully": "Email refresh complete: Successfully retrieved {data_success_count}/{data_total_count} email addresses",

        "already_up_to_date_dup": "Already up to date",

        "no_credential_files_available": "No credential files available",

        "validation_successfulnnfile_filenam": "✅ Validation successful!\\n\\nFile: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "selectedcount_items_selected": "{selectedCount} items selected",

        "click_the_view_content_button_to_lo": "Click the \"View Content\" button to load file details...",

        "please_enter_the_password": "Please enter the password",

        "upload_progress_dup": "Upload progress",

        "error_dataerror_failed_to_fetch_aut": "Error: ${data.error || 'Failed to fetch authentication link'}",

        "are_you_sure_you_want_to_delete_the_dup_dup": "Are you sure you want to delete the {count} selected files?\\nNote: This action cannot be undone!",

        "configuring_preview_channel_for_sel": "🔧 Configuring Preview channel for {selectedFiles_length} credentials, please wait...",

        "none": "None",

        "this_is_not_a_valid_callback_url_pl_dup": "❌ This is not a valid callback URL! Please ensure it includes code and state parameters",

        "retrieved_credential_file_content": "Retrieved credential file content:",

        "enable": "Enable",

        "antitruncation_output_protection": "Anti-truncation Output protection",

        "authentication_link_generated_proje_dup_dup": "Authentication link generated (Project ID will be detected after authorization), please click the link to complete authorization",

        "failed_to_configure_preview_channel_dup": "Failed to configure Preview channel",

        "testing_credentials_please_wait": "🧪 Testing credentials, please wait...",

        "validation_complete_processed_activ": "Validation complete! Processed: {active} valid, {changed} IDs updated, {disabled} marked invalid",

        "login_successful_dup": "Login successful",

        "batch_task_control": "Batch task control",

        "24h_api_call_volume": "24H API Request Volume",

        "minimalist_parsing_mapping_for_cutt": "Minimalist parsing mapping for cutting-edge protocols like System/Thinking.",

        "multiple_projects_detected_please_s": "Multiple projects detected, please specify a Project ID in advanced options:",

        "failed_to_fetch_error_information_e": "❌ Failed to fetch error information: {error_message}",

        "loaded_usage_statistics_for_aggdata": "Loaded usage statistics for {aggData_total_files____Object_keys_AppState_usageStatsData__length} files",
        "failed_to_load_usage_statistics": "Failed to load usage statistics",
        "error_errormsg": "Error: {errorMsg}",
        "status_net_error": "Network error: {error}",
        "status_no_filter_data": "No usage statistics found.",
        "table_calls": "Requests",
        "btn_reset_stats": "Reset Stats",
        "confirm_reset_stats": "Are you sure you want to reset statistics for {filename}?",
        "reset_failed_datamessage_datadetail": "Reset failed: {data_message____data_detail____data_error}",
        "are_you_sure_you_want_to_reset_usag_dup": "Are you sure you want to reset ALL usage statistics?",
        "table_filename": "Credential File Name",
        "table_actions": "Actions"

    },

    zh: {

        "app_title": "Omni Gateway",

        "panel_title": "Omni Gateway 管理控制台",

        "login_subtitle": "请输入访问密码管理您的代理通道",

        "login_placeholder": "输入控制面板密码",

        "login_btn": "登录",

        "logout_btn": "退出登录",

        "version_label": "版本号",

        "check_update_btn": "检查更新",

        "loading_text": "加载中...",

        "mirror_switch_warning": "镜像反代设置会切换 API 的解析域名，通常需要前置代理支持。",

        "copy_success": "复制成功！",

        "copy_fail": "复制失败！",

        "btn_close": "关闭",

        "dialog_tip": "提示",

        "error_prefix": "错误: ",

        "tab_oauth": "OAuth认证",

        "tab_omni": "Omni认证",

        "tab_upload": "批量上传",

        "tab_manage_creds": "凭证管理",
        "manage_creds_title": "凭证管理",
        "manage_creds_desc": "选择凭证服务商以查看和管理活跃的 API 通道。",
        "tab_manage_code_assist": "Code Assist凭证管理",

        "tab_manage_code_assist_short": "Code Assist凭证",

        "tab_manage_ag": "Omni凭证管理",

        "tab_manage_ag_short": "AG凭证",

        "tab_config": "配置管理",

        "tab_logs": "实时日志",

        "tab_about": "项目信息",

        "oauth_banner_title": "自动化已启用：",

        "oauth_banner_text": "系统在授权成功后，会自动检测并为您的谷歌云项目激活 Gemini Cloud Assist API 和 Gemini for Google Cloud API 必要的API服务，无需任何手动配置。",

        "oauth_advanced_title": "高级设置：指定 Google Cloud Project ID (可选)",

        "oauth_advanced_note": "留空将尝试自动检测并创建项目。",

        "oauth_link_btn": "获取 Google OAuth 认证链接",

        "oauth_auth_title": "获取到的认证链接：",

        "oauth_auth_instruction": "点击此链接授权 Google 账号",

        "oauth_guide_title": "OAuth 交互指南：",

        "oauth_guide_1": "点击上面的链接，在新浏览器标签页中登录您的 Google 账号并同意授权；",

        "oauth_guide_2": "授权成功后浏览器会自动跳转并报错提示无法连接 localhost:11451，这是正常现象；",

        "oauth_guide_3": "直接返回当前控制面板页面，点击下方的 \"获取并保存认证文件\" 按钮完成接入；",

        "oauth_guide_4": "如果是在远程VPS或无浏览器桌面环境运行：请展开下方“无法回源快捷通道”进行处理。",

        "oauth_callback_title": "无法自动回源？使用快捷回调通道",

        "oauth_callback_note": "适用于云服务器/VPS部署、Docker容器环境、或者防火墙拦截 11451 端口的场景。",

        "oauth_callback_instructions": "在谷歌授权同意跳转后，复制浏览器地址栏里的完整 URL 地址（即便显示连接失败），粘贴到下方输入框中即可。",

        "oauth_callback_btn": "从回调链接解析获取凭证",

        "oauth_save_btn": "获取并保存认证文件",

        "oauth_success_title": "认证成功！保存的文件内容：",

        "ag_banner_title": "Google Omni 认证模式",

        "ag_banner_text": "获取谷歌最新版本的 Cloud SDK Omni原生鉴权凭证。",

        "ag_link_btn": "获取 Omni 认证链接",

        "ag_link_title": "Omni 认证链接：",

        "ag_link_instruction": "点击此链接授权 Omni 模式",

        "ag_guide_title": "认证步骤：",

        "ag_guide_1": "点击上面的链接进行谷歌 OAuth 授权认证；",

        "ag_guide_2": "跳转失败报错提示无法连接 localhost:11451 时，返回此控制面板；",

        "ag_guide_3": "点击下方按钮直接获取并自动保存凭证文件；",

        "ag_guide_4": "若无法回源，可复制跳转后的完整 URL 展开下方快捷通道进行解析。",

        "ag_save_btn": "获取并保存 Omni 凭证",

        "ag_success_title": "获取的凭证文件内容：",

        "ag_download_btn": "下载凭证文件到本地",

        "upload_title": "批量上传本地凭证",

        "upload_desc": "将您现有的 Code Assist 或 Omni 认证 JSON/ZIP 文件拖拽或选择上传到服务器中。",

        "upload_code_assist_title": "Code Assist 凭证批量上传",

        "upload_code_assist_area_title": "点击选择文件，或直接拖拽文件到这里",

        "upload_code_assist_area_subtitle": "支持 .json 文件或 .zip 压缩包",

        "upload_code_assist_area_note": "ZIP 文件会自动提取解压所有的 JSON 凭证文件。",

        "upload_pending_code_assist": "待上传 of Code Assist 文件列表：",

        "upload_start_btn": "开始批量上传",

        "upload_clear_btn": "清空选择列表",

        "upload_progress": "上传进度",

        "upload_ag_title": "Omni 凭证批量上传",

        "upload_ag_area_title": "点击选择文件，或直接拖拽文件到这里",

        "upload_ag_area_subtitle": "支持 .json 凭证或 .zip 压缩包",

        "upload_ag_area_note": "ZIP 文件会自动解压并过滤提取其中的 JSON 凭证。",

        "upload_pending_ag": "待上传 of Omni 文件列表：",

        "code_assist_manage_title": "Code Assist凭证文件管理",

        "code_assist_manage_desc": "展示并维护您的 Code Assist 代理通道，支持单个或批量检验、下载、状态切换及删除操作。",

        "ag_manage_title": "Omni凭证文件管理",

        "ag_manage_desc": "展示并维护您的 Omni 代理账户及相关的请求配额。",

        "endpoint_banner_title": "API 集成端点地址",

        "endpoint_openai": "OpenAI 兼容:",

        "endpoint_claude": "Claude 兼容:",

        "endpoint_gemini": "Gemini 原生:",

        "stat_total": "总计凭证",

        "stat_active": "正常运行",

        "stat_disabled": "当前禁用",

        "btn_refresh": "刷新凭证列表",

        "btn_download_all": "打包下载所有凭证",

        "batch_panel_title": "批量任务控制",

        "batch_select_all": "全选",

        "batch_selected_count": "已选择 {count} 项",

        "batch_enable": "批量启用",

        "batch_disable": "批量禁用",

        "batch_delete": "批量删除",

        "batch_verify_id": "批量检验 Project ID",

        "batch_preview_toggle": "批量配置 Preview 通道",

        "batch_refresh_emails": "刷新所有账号邮箱",

        "batch_deduplicate": "凭证一键去重",

        "batch_enable_credit": "批量开启积分",

        "batch_disable_credit": "批量关闭积分",

        "filter_status": "状态：",

        "filter_all": "全部",

        "filter_status_enabled": "仅启用",

        "filter_status_disabled": "仅禁用",

        "filter_error": "错误码：",

        "filter_error_none": "正常无错误",

        "filter_cooldown": "冷却中：",

        "filter_cooldown_active": "CD限制中",

        "filter_cooldown_none": "无限制",

        "filter_preview": "Preview：",

        "filter_preview_on": "仅支持 Preview",

        "filter_preview_off": "不支持 Preview",

        "filter_tier": "等级：",

        "filter_per_page": "每页：",

        "card_enabled": "已启用",

        "card_disabled": "已禁用",

        "card_no_error": "正常无错",

        "card_error_code": "错误码: {code}",

        "card_no_email": "未获取邮箱",

        "card_loading_details": "点击\"查看内容\"按钮加载文件详情...",

        "card_loading_errors": "点击\"查看报错\"按钮加载报错信息...",

        "card_loading_quota": "点击\"查看额度\"按钮加载额度信息...",

        "btn_card_enable": "启用",

        "btn_card_disable": "禁用",

        "btn_card_view": "查看内容",

        "btn_card_download": "下载",

        "btn_card_email": "查看账号邮箱",

        "btn_card_quota": "查看额度",

        "btn_card_close_credit": "关闭 Credit",

        "btn_card_open_credit": "开启 Credit",

        "btn_card_set_preview": "设置预览",

        "btn_card_verify": "检验",

        "btn_card_test": "消息测试",

        "btn_card_error_details": "查看报错",

        "btn_card_delete": "删除",

        "config_title": "全局系统配置",

        "config_desc": "调整系统代理、端点地址、安全策略及高频重试参数，修改完并保存后，绝大多数项均可热生效。",

        "btn_save_config": "保存全局配置",

        "btn_reload_config": "重载配置数据",

        "config_loading": "正在向服务器同步当前系统配置...",

        "group_network": "⚙️ 服务网络监听配置",

        "config_host_label": "服务器绑定 Host IP Address:",

        "config_host_note": "监听绑定的IP地址。0.0.0.0 代表对公网所有访问开发，修改后需要重启。",

        "config_port_label": "监听端口号 Port:",

        "config_port_note": "绑定监听的 TCP 端口，改动需重启生效。",

        "config_api_pwd_label": "接口 API 访问鉴权密码 (API Key):",

        "config_api_pwd_note": "用于代理端点请求时的 HTTP Authorization Bearer Token 验证。",

        "config_panel_pwd_label": "控制面板访问登录密码:",

        "config_panel_pwd_note": "保护此控制台页面不被恶意篡改的访问口令。",

        "config_pwd_label": "通用快捷覆盖密码 (可选):",

        "config_pwd_note": "如果配置此字段，将直接强制覆盖 API 和面板密码，建议直接留空。",

        "group_storage": "📂 存储与代理设置",

        "config_storage_label": "本地凭证存储绝对路径:",

        "config_storage_note": "保存上传和授权获取的 JSON 文件的本地存储目录。",

        "config_proxy_label": "全局连接前置代理 Proxy URL:",

        "config_proxy_note": "本地访问谷歌接口时所需的中转网络代理，为空表示直连。",

        "group_endpoints": "🔗 API 端点代理反代设置",

        "config_mirror_btn": "🚀 一键切换至镜像反代地址",

        "config_official_btn": "🔄 还原至谷歌官方官方地址",

        "config_endpoint_code": "Code Assist API 端点:",

        "config_endpoint_oauth": "OAuth 鉴权服务端点:",

        "config_endpoint_apis": "Google APIs 核心端点:",

        "config_endpoint_resource": "Resource Manager API 端点:",

        "config_endpoint_service": "Service Usage API 状态管理端点:",

        "config_endpoint_ag": "Omni API 端点:",

        "group_ban": "🛡️ 账户风控与熔断策略",

        "config_ban_checkbox": "启用特定错误代码凭证自动封禁熔断 (Auto-Ban)",

        "config_ban_codes_label": "触发熔断封禁的 HTTP 错误代码 (逗号分隔):",

        "config_ban_codes_note": "当调用谷歌接口返回此处的错误码时，系统会自动禁用此账户。通常 403 建议熔断。",

        "group_retry": "🔁 自动重试重连机制",

        "config_retry_checkbox": "启用失败请求自动在其他轮换凭证上重试",

        "config_retry_count": "失败最大重试次数:",

        "config_retry_interval": "重试频率间隔 (秒):",

        "group_compat": "🧩 模型协议兼容性覆盖",

        "config_compat_checkbox": "强行启用兼容模式 (将 System 协议消息平铺合并入 User)",

        "config_compat_note": "该设置可能导致复杂的 Prompt 理解力有微弱下降，但能完美解决极个别三方客户端因 system_instructions 缺失引发的空返回或流式熔断报错。",

        "config_thinking_checkbox": "透传模型的思维链 (Thinking Process) 到前端响应",

        "config_thinking_note": "适用于具备推理过程的最新 Gemini 2.0 系列模型。如果关闭，思维链内容会被过滤以提供更洁净的直接回复。",

        "config_ag_stream_checkbox": "Omni模式启用流式响应转换 (Stream to Non-stream Collection)",

        "config_ag_retry_checkbox": "Omni 错误时主动切换其他轮换凭证",

        "group_trunc": "⏱️ 抗输出截断长文本控制 (Truncation Recovery)",

        "config_trunc_count": "最大防截断断点续传次数:",

        "config_trunc_note": "调用携带 -流式抗截断 后缀的代理模型时，如果遇到长上下文输出被强行腰斩，系统将最多尝试断点重新续传的上限次数。",

        "group_keepalive": "☕ 应用在线保活防沉睡设置 (Keep-Alive)",

        "config_keepalive_label": "服务保活心跳检测请求 URL:",

        "config_keepalive_btn": "智能捕获并自动写入当前保活心跳 URL",

        "config_keepalive_interval": "保活请求频率间隔 (秒):",

        "logs_title": "系统运行日志流",

        "logs_desc": "实时监控后台发往 Google Cloud API 的请求细节与轮换逻辑，快速排查网络代理或限流问题。",

        "btn_log_connect": "手动接入日志通道",

        "btn_log_disconnect": "切断日志通道",

        "btn_log_save": "另存日志文件到本地",

        "btn_log_clear": "清空缓冲区日志",

        "log_filter_level": "过滤等级：",

        "log_scroll_lock": "自动锁定滚动条到底部",

        "log_status_label": "实时链接状态：",

        "log_status_text": "未连接",

        "log_waiting_text": "等待拉取最新系统控制台日志输出...",

        "about_title": "关于 Omni Gateway",

        "tab_dashboard": "仪表盘",
        "regenerate_keys_btn": "重新生成密钥",
        "copy_btn": "复制",
        "confirm_regenerate_key": "确定要重新生成此 API 密钥吗？原有的密钥将立即失效。",
        "regenerate_success": "API 密钥重新生成成功",
        "tooltip_total_calls": "Total number of API requests sent to the Gateway in the past 24 hours.",
        "tooltip_total_files": "Total number of active Code Assist and Omni credential files in the system.",
        "tooltip_avg_calls": "Average number of API requests processed per credential in the past 24 hours.",
        "tooltip_total_calls": "Total number of API requests routed through this gateway in the last 24 hours.",
        "tooltip_total_files": "The number of active Google/Omni credentials currently configured and monitored.",
        "api_keys_title": "API 密钥",
        "api_integration_title": "API 集成",
        "tooltip_total_calls": "过去 24 小时内发送到网关的 API 请求总数。",
        "tooltip_total_files": "系统里正在运行的 Code Assist 和 Omni 账号文件总数。",
        "tooltip_avg_calls": "过去 24 小时内每个账号平均处理的的 API 请求数。",
        "tooltip_total_calls": "过去 24 小时内通过此网关路由的 API 请求总数。",
        "tooltip_total_files": "当前已配置并处于监控状态的活跃 Google/Omni 凭据数量。",
        "quick_info_title": "快速集成信息",
        "info_openai_header": "OpenAI 头部:",
        "info_anthropic_header": "Anthropic 头部:",
        "info_status": "服务状态:",
        "status_running": "运行中",
        "api_key_label": "API 密钥:",
        "api_connection_title": "API 连接信息",
        "quick_guide_title": "快速集成指南",
        "guide_openai_header": "OpenAI 兼容性:",
        "guide_anthropic_header": "Anthropic 兼容性:",
        "guide_tip_header": "提示:",
        "guide_tip_content": "点击连接信息卡片中的任意字段即可复制。单个统一密钥可与 OpenAI 和 Anthropic 格式的客户端无缝协作。",
        "openai_key_label": "OpenAI API 密钥:",
        "anthropic_key_label": "Anthropic API 密钥:",
        "unified_endpoint_title": "API 集成端点",
        "api_integration_card_title": "API 集成",
        "quick_integration_title": "快速集成",
        "integration_openai_title": "兼容 OpenAI 客户端:",
        "integration_anthropic_title": "兼容 Anthropic 客户端:",
        "integration_url_prefix": "接口地址:",
        "integration_key_prefix": "API 密钥:",
        "endpoint_base_label": "接口地址:",
        "dashboard_total_calls": "24h 累计请求数",
        "dashboard_total_files": "已监视证书数",
        "dashboard_avg_calls": "平均每凭证请求数",
        "dashboard_welcome": "欢迎使用全新设计的 Omni Gateway 控制台！您可以在侧边栏中快速切换管理任务。系统会自动轮换活动凭证进行负载均衡，并在遇到频率限制 (429) 或禁用 (403) 错误时进行故障转移和重试，以确保高可用性。",
        "dashboard_breakdown": "24小时内请求细分",
        "oauth_desc": "生成 Google Cloud 授权凭证。支持标准 Code Assist OAuth 和 Omni 凭证导出。",

        "about_desc": "Omni Gateway 是一款面向编程工具的通用 AI 路由。支持智能自动容灾、Token 压缩以及无缝格式转换，最大化利用免费和付费大语言模型。",

        "about_github": "GitHub 开源协议库:",

        "about_notice": "开源性质免责声明: 禁止任何形式 Hippy 商业倒卖和分发销售。仅供测试、个人研究与学术交流。",

        "about_features_title": "主要技术亮点",

        "feat_1_title": "自动配额避让轮换",

        "feat_1_desc": "无感切取空闲账号，有效避让 429 访问限制。",

        "feat_2_title": "原生格式双向转换",

        "feat_2_desc": "极简解析映射 System / Thinking 等前沿协议。",

        "feat_3_title": "Auto-Ban 熔断守护",

        "feat_3_desc": "根据 API 报错秒级做出账户降级与禁用判定。",

        "feat_4_title": "防截断抗输出抗截断",

        "feat_4_desc": "全网独家实现流式断点续传功能。",

        "feat_5_title": "轻量单文件部署",

        "feat_5_desc": "资源开销微乎其微，完美适配各大 PAAS 和 Docker。",

        "feat_6_title": "完美响应式支持",

        "feat_6_desc": "极具质感的面板布局，支持所有现代浏览器。",

        "about_support_title": "GitHub 官方技术交流群",

        "about_support_desc": "欢迎加入我们一起交流玩法与提交功能迭代请求：",

        "about_support_cta": "微信/GitHub 扫码一键加群",

        "about_feedback_title": "联系与反馈渠道",

        "about_feedback_desc": "如果您在使用中发现了任何 Bug 或有好的设计建议，请随时前往开源 GitHub 仓库提交 Issues，也欢迎随时提交 PR 一起丰富生态。",

        "auth_fail_relogin": "认证失败，请重新登录",

        "check_update_info": "正在检查更新...",

        "update_success": "检查成功！已是最新版本。",

        "load_cred_stats": "已加载 {count} 个文件的使用统计",

        "net_error": "网络错误: {msg}",

        "confirm_delete_cred": "确定要删除凭证文件吗？\\n{filename}",

        "save_config_success": "保存全局配置成功！",

        "load_config_success": "载入配置数据成功！",

        "log_connected": "已成功建立日志连接通道。",

        "log_disconnected": "已切断日志连接通道。",

        "select_at_least_one": "请至少选择一个凭证进行操作！",

        "confirm_batch_action": "确认对已选中的 {count} 项凭证执行 {action} 批量操作吗？",

        "batch_action_success": "批量 {action} 操作执行成功！",

        "input_password_prompt": "请输入访问密码！",

        "login_success": "登录成功！",

        "login_failed": "登录失败！密码错误。",

        "net_error_prefix": "网络错误: ",

        "action_success_prefix": "操作成功: ",

        "action_fail_prefix": "操作失败: ",

        "upload_fail_prefix": "上传失败: ",

        "check_update_fail_prefix": "检查更新失败: ",

        "pagination_prev": "上一页",

        "pagination_next": "下一页",

        "pagination_info": "第 {page} 页，共 {total} 页 (显示 {start}-{end}，共 {count} 项)",

        "code_assist_oauth_auth_title": "Code Assist OAuth 认证",

        "oauth_guide_2_fail_suffix": "，此为正常现象；",

        "oauth_paste_url": "完整 URL 粘贴在下方：",

        "ag_auth_title": "Omni 权证认证",

        "ag_guide_2_fail_suffix": "时，返回此控制面板；",

        "upload_file_or_zip": "文件或压缩包",

        "click_to_copy": "点击复制",

        "support_link_label": "GitHub群二维码",

        "enable_only": "仅启用",

        "disable_only": "仅禁用",

        "click_to_open_link": "点击打开链接",

        "right_click_to_copy_link": "右键复制链接",

        "status_disabled": "已禁用",

        "status_enabled": "已启用",

        "preview_supported_title": "该凭证支持Preview模型",

        "preview_not_supported_title": "该凭证不支持Preview模型",

        "tier_badge_title": "凭证等级",

        "credit_enabled_title": "当前已开启Credit模式",

        "credit_disabled_title": "当前已关闭Credit模式",

        "other_models_title": "其他模型",

        "btn_view_content": "查看内容",

        "btn_view_email": "查看账号邮箱",

        "btn_view_quota": "查看额度",

        "btn_view_quota_title": "查看该凭证的额度信息",

        "btn_disable_credit": "关闭 Credit",

        "btn_disable_credit_title": "关闭该凭证的Credit模式",

        "btn_enable_credit": "开启 Credit",

        "btn_enable_credit_title": "开启该凭证的Credit模式",

        "btn_setup_preview": "设置预览",

        "btn_setup_preview_title": "配置Preview通道，启用实验性功能",

        "btn_verify_id": "检验",

        "btn_verify_id_title": "重新获取Project ID，可恢复403错误",

        "btn_message_test": "消息测试",

        "btn_message_test_title": "测试凭证是否可用",

        "btn_view_errors": "查看报错",

        "btn_view_errors_title": "查看该凭证的详细报错信息",

        "email_not_fetched": "未获取邮箱",

        "click_view_content_to_load": "点击\"查看内容\"按钮加载文件详情...",

        "click_view_errors_to_load": "点击\"查看报错\"按钮加载报错信息...",

        "click_view_quota_to_load": "点击\"查看额度\"按钮加载额度信息...",

        "status_loading_file_content": "正在加载文件内容...",

        "status_test_failed": "Test Failed - {error}",

        "remaining_label": "剩余",

        "credits_label": "积分",

        "all": "全部",

        "omni_mode_enabled_streamtono": "Omni模式启用流式响应转换 (Stream to Non-stream Collection)",

        "test_successful": "Test Successful!",

        "oauth_interaction_guide": "OAuth 交互指南：",

        "error_code": "错误码：",

        "no_logs_at_appstatecurrentlogfilter": "暂无{AppState_currentLogFilter}级别的日志...",

        "credential_file_name": "凭证文件名称",

        "nfailed_step_step": "\\n失败步骤: {step}",

        "batch_verification_completed_succes": "⚠️ 批量检验完成：成功 {successCount}/{selectedFiles_length} 个，失败 {failCount} 个",

        "currently_disabled": "当前禁用",

        "omni_authentication_successf": "✅ Omni 认证成功！文件已保存到: {path}",

        "loaded_usage_statistics_for_aggdata": "已加载 {aggData_total_files____Object_keys_AppState_usageStatsData__length} 个文件的使用统计",

        "upload_failed_connection_interrupte": "上传失败：连接中断 - 可能原因：文件过多({this_selectedFiles_length}个)或网络不稳定。建议分批上传。",

        "please_select_the_omni_crede": "请先选择要检验的Omni凭证",

        "downloaded_file_filename": "已下载文件: {filename}",

        "oneclick_credential_deduplication": "凭证一键去重",

        "message_test": "消息测试",

        "div_styletextalign_center_padding_2": "<div style=\"text-align: center; padding: 20px; color: #999;\">\n\n                                <div style=\"font-size: 48px; margin-bottom: 10px;\">📊</div>\n\n                                <div>暂无额度信息</div>\n\n                            </div>",

        "omni_authentication_link": "Omni 认证链接：",

        "authentication_steps": "认证步骤：",

        "fetching_authentication_link": "正在获取认证链接...",

        "upload_failed_request_timeout_proce": "上传失败：请求超时 - 文件处理时间过长，请减少文件数量或检查网络连接",

        "manual_project_id_specification_req": "需要手动指定项目ID，请在高级选项中填入Google Cloud项目ID后重试",

        "resource_manager_api_endpoint": "Resource Manager API 端点:",

        "intelligently_capture_and_automatic": "智能捕获并自动写入当前保活心跳 URL",

        "a_hrefhref_target_blank_relnoopener": "<a href=\"{href}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"message-link\" onclick=\"event.stopPropagation()\" title=\"点击打开链接\\n右键复制链接\">{url}</a>",

        "this_is_not_a_valid_callback_url_pl": "❌ 这不是有效的回调URL！请确保：\\n1. 已完成Google OAuth授权\\n2. 复制的是浏览器地址栏的完整URL\\n3. URL包含code和state参数",

        "file_filename_format_is_not_support": "文件 {file_name} 格式不支持，只支持JSON和ZIP文件",

        "the_following_configurations_have_t": "，以下配置已立即生效: {list}",

        "click_the_link_above_to_proceed_wit": "点击上面的链接进行谷歌 OAuth 授权认证；",

        "unable_to_determine_if_updates_are": "无法确定是否有更新",

        "please_select_the_credentials_to_ve": "❌ 请先选择要检验的凭证",

        "downloaded_file_name": "已下载文件: {name}",

        "please_obtain_the_omni_authe": "请先获取 Omni 认证链接并完成授权",

        "refresh_credential_list": "刷新凭证列表",

        "all_credential_files_have_been_down": "已下载所有凭证文件",

        "preview_channel_configuration_succe": "Preview Channel Configuration Successful!\\n\\n文件: {filename}\\n\\n{data_message}\\n\\nSetting ID: {data_setting_id_____N_A}\\nBinding ID: {data_binding_id_____N_A}",

        "all_verifications_successful_verifi": "✅ 全部检验成功！成功检验 {successCount}/{selectedFiles_length} 个Omni凭证",

        "are_you_sure_you_want_to_batch_veri": "确定要批量检验 {selectedFiles_length} 个Omni凭证的Project ID吗？\\n\\n将并行检验以加快速度。",

        "failed_to_load_usage_statistics": "加载使用统计失败",

        "failed_to_download_logs_datadetail": "下载日志失败: {data_detail____data_error}",

        "generating_authentication_link_usin": "使用指定的项目ID生成认证链接...",

        "not_enabled": "❌ 未启用",

        "download_credential_files_locally": "下载凭证文件到本地",

        "average_calls_per_volume": "平均每凭证请求数",

        "failed_to_get_authentication_link_e": "获取认证链接失败: {error}",

        "successfully_retrieved_email_dataus": "成功获取邮箱: {data_user_email}",

        "code_assist_oauth_authentication": "Code Assist OAuth 认证",

        "failed_to_create_websocket_connecti": "创建WebSocket连接失败:",

        "omni_batch_verification_comp": "Omni批量检验完成",

        "healthy_no_errors": "正常无错",

        "no_data_under_current_filter_condit": "当前筛选条件下暂无数据",

        "successfully_retrieved_email_email": "成功获取邮箱: {email}",

        "get_google_oauth_authentication_lin": "获取 Google OAuth 认证链接",

        "failed_to_fetch_version_information": "版本信息获取失败",

        "switch_to_mirror_proxy_address_with": "🚀 一键切换至镜像反代地址",

        "enable_automatic_retry_of_failed_re": "启用失败请求自动在其他轮换凭证上重试",

        "level": "等级：",

        "please_enter_password_to_login": "请输入密码登录",

        "failed_to_retrieve_credentials_from": "从回调URL获取凭证失败: {error}",

        "please_select_the_credentials_to_ve_dup": "请先选择要检验的凭证",

        "retrieved_authentication_link": "获取到的认证链接：",

        "upload_failed_errordetail_errorerro": "上传失败: {error_detail____error_error}",

        "are_you_sure_you_want_to_perform_on": "确定要对凭证进行凭证一键去重吗？\\n\\n相同邮箱的凭证只保留一个，其他将被删除。\\n此操作不可撤销！",

        "omni_file_list_pending_uploa": "待上传 of Omni 文件列表：",

        "successfully_imported_loadedtotal_c": "✅ 成功导入 {loaded}/{total} 个凭证文件",

        "keepalive_request_interval_seconds": "保活请求频率间隔 (秒):",

        "healthy_no_errors_dup": "正常无错误",

        "clear_failed_datadetail_dataerror_u": "清除失败: {data_detail____data_error}",

        "network_error_while_clearing_logs_e": "清空日志时网络错误: {error_message}",

        "save_log_file_as": "另存日志文件到本地",

        "upload_failed_connection_interrupte_dup": "上传失败：连接中断 - 可能原因：文件过多({count}个)或网络不稳定。建议分批上传。",

        "resultfilename_resultmessage_config": "✅ {result_filename}: {result_message}",

        "disable_credits": "关闭积分",

        "please_select_the_files_to_operate": "请先选择要操作的文件",

        "batch_operation_failed_error": "批量操作失败: {error}",

        "account_risk_control_and_circuit_br": "🛡️ 账户风控与熔断策略",

        "determine_account_downgrade_or_disa": "根据 API 报错秒级做出账户降级与禁用判定。",

        "reset_statistics": "重置统计",

        "google_omni_authentication": "Google Omni 认证",

        "failed_to_download_package_error": "打包下载失败: {error}",

        "div_stylecolor_dc3545reason_escapeh": "<div style=\"color: #dc3545;\">原因: {escapeHtml_detail_reason}</div>",

        "test_successful_dup": "测试成功",

        "are_you_sure_you_want_to_refresh_us": "确定要刷新所有凭证的用户邮箱吗？这可能需要一些时间。",

        "filter_filter": "(筛选: {filter})",

        "view_content": "查看内容",

        "open_source_disclaimer_commercial_r": "开源性质免责声明: 禁止任何形式 Hippy 商业倒卖和分发销售。仅供测试、个人研究与学术交流。",

        "failed_to_save_configuration_error": "保存配置失败: {error}",

        "total_credentials": "总计凭证",

        "contact_and_feedback_channels": "联系与反馈渠道",

        "supports_json_credentials_or_zip_ar": "支持 .json 凭证或 .zip 压缩包",

        "revert_to_google_official_address": "🔄 还原至谷歌官方官方地址",

        "failed_to_retrieve_omni_cred": "从回调URL获取 Omni 凭证失败",

        "import_failed_datadetail_dataerror": "导入失败: {data_detail____data_error}",

        "new_version_foundncurrent_vversionn": "发现新版本！\\n当前: v{version}\\n最新: v{latest}\\n\\n更新内容: {log}",

        "network_error_msg": "网络错误: {msg}",

        "unable_to_retrieve_user_email_error": "无法获取用户邮箱: {error}",

        "batch_action_operation_completed_su": "批量 {action} 操作执行成功！",

        "api_integration_endpoint_addresses": "API 集成端点地址",

        "system_runtime_log_stream": "系统运行日志流",

        "import_failed_error": "导入失败: {error}",

        "google_apis_core_endpoints": "Google APIs 核心端点:",

        "authentication_successful_saved_fil": "认证成功！保存的文件内容：",

        "click_the_view_quota_button_to_load": "点击\\\"查看额度\\\"按钮加载额度信息...",

        "waiting_to_fetch_the_latest_system": "等待拉取最新系统控制台日志输出...",

        "control_panel_login_password": "控制面板访问登录密码:",

        "unable_to_autodetect_project_id_ple": "无法自动检测项目ID，请手动输入您的Google Cloud项目ID:",

        "click_this_link_to_authorize_your_g": "点击此链接授权 Google 账号",

        "email_groupemailnkeep_groupkept_fil": "邮箱: {group_email}\\n保留: {group_kept_file}\\n删除: {group_deleted_files_join}\\n\\n",

        "omni_authentication_link_gen": "✅ Omni 认证链接已生成！请点击链接完成授权",

        "check_successful_already_running_th": "检查成功！已是最新版本。",

        "switched_to_official_endpoint_confi": "✅ 已切换到官方端点配置，记得点击\"保存配置\"按钮保存设置",

        "nplease_enter_index_1dataavailable": "\\n请输入序号 (1-{data_available_projects_length}):",

        "fetch_and_save_authentication_file": "获取并保存认证文件",

        "failed_to_generate_authentication_l": "❌ 生成认证链接失败: {error}",

        "action": "操作",

        "save_config": "保存配置",

        "fetch_omni_credentials": "获取 Omni 凭证",

        "failed_to_generate_authentication_l_dup": "生成认证链接失败",

        "retry_using_the_selected_project": "使用选择的项目重新尝试...",

        "div_styletextalign_center_padding_2_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                        <div style=\"font-weight: bold; margin-bottom: 5px;\">网络错误</div>\n\n                        <div style=\"font-size: 13px; color: #666;\">{error_message}</div>\n\n                    </div>",

        "credential_available": "凭证可用",

        "google_omni_authentication_m": "Google Omni 认证模式",

        "zip_archive": "(ZIP压缩包)",

        "are_you_sure_you_want_to_delete_fil": "确定要删除 {filename} 吗？",

        "page_thiscurrentpage_of_totalpages": "第 {this_currentPage} 页，共 {totalPages} 页 (显示 {startItem}-{endItem}，共 {this_totalCount} 项)",

        "failed_to_clear_logs_datadetail_dat": "清空日志失败: {data_detail____data_error}",

        "please_select_the_credentials_to_co": "请先选择要配置Preview的凭证",

        "websocket_connected": "WebSocket已经连接",

        "enable_autoban_for_credentials_on_s": "启用特定错误代码凭证自动封禁熔断 (Auto-Ban)",

        "preview_channel_configuration_faile": "Preview Channel Configuration Failed\\n\\n文件: {filename}\\n\\n{errorMsg}",

        "autobacksource_failed_use_the_quick": "无法自动回源？使用快捷回调通道",

        "operation_failed_error": "操作失败: {error}",

        "please_fetch_the_authentication_lin": "请先获取认证链接并完成授权",

        "bidirectional_native_format_convers": "原生格式双向转换",

        "oneclick_deduplication_failed_error": "一键去重失败: {error}",

        "disable": "禁用",

        "click_this_link_to_authorize_antigr": "点击此链接授权 Omni 模式",

        "deduplication_network_error_errorme": "去重网络错误: {error_message}",

        "after_successful_authorization_the": "授权成功后浏览器会自动跳转并报错提示无法连接 localhost:11451，这是正常现象；",

        "failed_to_get_environment_variable": "获取环境变量状态失败: {error}",

        "max_antitruncation_resume_attempts": "最大防截断断点续传次数:",

        "log_connection_channel_established": "已成功建立日志连接通道。",

        "test_failednfile_filenamen": "Test Failed\\n文件: {filename}\\n",

        "global_configuration_saved_successf": "保存全局配置成功！",

        "executing_batch_actionlabel_operati": "正在执行批量{actionLabel}操作...",

        "monitor_credential_count": "监控凭证数量",

        "switched_to_official_endpoint_confi_dup": "已切换到官方端点配置，记得点击 '保存配置' 按钮保存设置",

        "local_credential_storage_absolute_p": "本地凭证存储绝对路径:",

        "click_to_open_linknrightclick_to_co": "点击打开链接\\n右键复制链接",

        "upload_failed_http_xhrstatus": "上传失败: HTTP {xhr_status}",

        "verification_successful": "检验成功",

        "force_enable_compatibility_mode_mer": "强行启用兼容模式 (将 System 协议消息平铺合并入 User)",

        "clear_buffer_logs": "清空缓冲区日志",

        "div_stylefontsize_12px_color_666_ma": "<div style=\"font-size: 12px; color: #666; margin-bottom: 5px;\">详细信息:</div>",

        "error_dataerror_failed_to_get_authe": "❌ 错误: {data_error}",

        "select_all": "全选",

        "if_this_field_is_configured_it_will": "如果配置此字段，将直接强制覆盖 API 和面板密码，建议直接留空。",

        "autologin_successful": "自动登录成功",

        "failed_to_save_config_datadetail_da": "保存配置失败: {data_detail____data_error}",

        "batch_operation_completed_processed": "批量操作完成：成功处理 {success}/{total} 个文件",

        "tip_leave_blank_for_firsttime_use_t": "提示：首次使用请留空，系统将自动分配与检测。",

        "configuration_failed": "配置失败",

        "successfully_imported_dataloaded_co": "✅ 成功导入 {data_loaded_count}/{data_total_count} 个凭证文件",

        "switched_to_mirror_url_configuratio": "✅ 已切换到镜像网址配置，记得点击\"保存配置\"按钮保存设置",

        "zip_files_will_automatically_extrac": "ZIP 文件会自动提取解压所有的 JSON 凭证文件。",

        "adjust_system_proxy_endpoint_addres": "调整系统代理、端点地址、安全策略及高频重试参数，修改完并保存后，绝大多数项均可热生效。",

        "loaded_count_type_credential_files": "已加载 {count} 个 {type} 凭证文件",

        "log_stream_connection_error": "日志流连接错误:",

        "quota_information_loaded_successful": "✅ 成功加载额度信息",

        "failed_to_fetch_authentication_link": "获取认证链接失败",

        "return_directly_to_the_current_cont": "直接返回当前控制面板页面，点击下方的 \\\"获取并保存认证文件\\\" 按钮完成接入；",

        "retry_interval_seconds": "重试频率间隔 (秒):",

        "autoban_circuit_breaker": "Auto-Ban 熔断守护",

        "usage_statistics_loaded_for_count_f": "已加载 {count} 个文件的使用统计",

        "operation_successful": "操作成功:",

        "download": "下载",

        "new_version_available": "有新版本",

        "openai_compatibility": "OpenAI 兼容:",

        "verification_successfulnfile_filena": "Verification Successful!\\n文件: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "div_styletextalign_center_padding_2_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                            <div style=\"font-weight: bold; margin-bottom: 5px;\">获取额度信息失败</div>\n\n                            <div style=\"font-size: 13px; color: #666;\">{errorMsg}</div>\n\n                        </div>",

        "delete": "删除",

        "div_styletextalign_center_padding_2_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                            <div style=\"font-weight: bold;\">加载失败</div>\n\n                            <div style=\"font-size: 12px; margin-top: 8px;\">{errorMsg}</div>\n\n                        </div>",

        "file_format_of_name_not_supported_o": "文件 {name} 格式不支持，只支持JSON和ZIP文件",

        "project_info": "项目信息",

        "the_following_configurations_have_t_dup": "，以下配置已立即生效: {data_hot_updated_join}",

        "unable_to_fetch_user_email": "无法获取用户邮箱",

        "failed_to_fetch_credentials_from_ca": "从回调URL获取凭证失败",

        "advanced_settings_specify_google_cl": "高级设置：指定 Google Cloud Project ID (可选)",

        "starting_batch_project_id_verificat": "正在启动批量验证项目ID任务...",

        "open_github_issues": "微信/GitHub 扫码一键加群",

        "when_google_apis_return_these_error": "当调用谷歌接口返回此处的错误码时，系统会自动禁用此账户。通常 403 建议熔断。",

        "failed_to_fetch_error_message": "获取报错信息失败",

        "error_dataerror_failed_to_generate": "❌ 错误: {data_error}",

        "service_network_listening_configura": "⚙️ 服务网络监听配置",

        "connecting": "连接中...",

        "credentials_fetched_successfully_fr": "从回调URL获取凭证成功！",

        "click_the_link_above_sign_in_to_you": "点击上面的链接，在新浏览器标签页中登录您的 Google 账号并同意授权；",

        "omni_credential_file_managem": "Omni凭证文件管理",

        "failed_to_configure_preview_channel": "配置Preview通道失败: {error_message}",

        "authentication_successful_project_i": "✅ 认证成功！项目ID已自动检测为: {id}，文件已保存到: {path}",

        "please_enter_a_valid_url_starting_w": "请输入有效的URL（以http://或https://开头）",

        "successfully_updated_preview_channe": "已成功更新 {count} 个凭证文件的 Preview 通道状态",

        "pending_code_assist_file_upload_list": "待上传 of Code Assist 文件列表：",

        "exclusive_industrywide_support_for": "全网独家实现流式断点续传功能。",

        "configuration_failed_for_all_failed": "❌ 全部配置失败！失败 {failCount}/{selectedFiles_length} 个凭证",

        "omni_batch_verification_comp_dup": "Omni批量检验完成！\\n\\n成功: {successCount} 个\\n失败: {failCount} 个\\n总计: {selectedFiles_length} 个\\n\\n详细结果:\\n{resultMessages_join___n}",

        "enabled": "✅ 已启用",

        "display_and_maintain_your_code_assist_prox": "展示并维护您的 Code Assist 代理通道，支持单个或批量检验、下载、状态切换及删除操作。",

        "batch_operation_network_error_error": "批量操作网络错误: {error}",

        "retrying_with_manually_entered_proj": "使用手动输入的项目ID重新尝试...",

        "get_omni_authentication_link": "获取 Omni 认证链接",

        "json_file": "(JSON文件)",

        "are_you_sure_you_want_to_deduplicat": "确定要对Omni凭证进行凭证一键去重吗？\\n\\n相同邮箱的凭证只保留一个，其他将被删除。\\n此操作不可撤销！",

        "display_and_maintain_your_antigravi": "展示并维护您的 Omni 代理账户及相关的调用配额。",

        "supports_json_files_or_zip_archives": "支持 .json 文件或 .zip 压缩包",

        "code_assist_api_endpoint": "Code Assist API 端点:",

        "failed_to_fetch_error_message_error": "❌ 获取报错信息失败: {errorMsg}",

        "failed_to_load_file_content": "加载文件内容失败:",

        "div_stylebackground_white_borderlef": "<div style=\"background: var(--bg); border: 1px solid var(--border); border-left: 4px solid {percentageColor}; border-radius: var(--radius); padding: 8px 10px;\">\n\n                                    <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;\">\n\n                                        <div style=\"font-weight: bold; color: #333; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; margin-right: 8px;\" title=\"{modelName} - 剩余{remainingPercentage}% - {resetTime}\">\n\n                                            {modelName}\n\n                                        </div>\n\n                                        <div style=\"font-size: 13px; font-weight: bold; color: {percentageColor}; white-space: nowrap;\">\n\n                                            {remainingPercentage}%\n\n                                        </div>\n\n                                    </div>\n\n                                    <div style=\"width: 100%; height: 8px; background-color: var(--bg-subtle); border-radius: var(--radius); overflow: hidden; margin-bottom: 4px;\">\n\n                                        <div style=\"width: {usedPercentage}%; height: 100%; background-color: {percentageColor}; transition: none;\"></div>\n\n                                    </div>\n\n                                    <div style=\"font-size: 10px; color: #666; text-align: right;\">\n\n                                        {resetTime______N_A___________resetTime}\n\n                                    </div>\n\n                                </div>",

        "failed_to_check_for_updates_error": "检查更新失败: {error}",

        "preview_channel_configuration_succe_dup": "Preview通道配置成功",

        "clear_selection_list": "清空选择列表",

        "logs_cleared_waiting_for_new_logs": "日志已清空，等待新日志...",

        "running_normally": "正常运行",

        "lightweight_singlefile_deployment": "轻量单文件部署",

        "button_to_save_settings_success_fun": "按钮保存设置', 'success');\n\n    }\n\n}\n\n\n\nfunction restoreOfficialUrls() {\n\n    if (confirm('确定要将所有端点配置为官方地址吗？')) {\n\n        for (const [fieldId, url] of Object.entries(officialUrls)) {\n\n            const field = document.getElementById(fieldId);\n\n            if (field && !field.disabled) field.value = url;\n\n        }\n\n        showStatus('✅ 已切换到官方端点配置，记得点击",

        "test_successfulnfile_filenamenstatu": "Test Successful!\\n文件: {filename}\\n状态: {data_message_____Omni} ({data_status_code____200})",

        "full_version_datafull_hashncommit_m": "完整版本: {data_full_hash}\\n提交信息: {data_message}\\n提交时间: {data_date}",

        "importing_credentials_from_environm": "正在从环境变量导入凭证...",

        "server_bound_host_ip_address": "服务器绑定 Host IP Address:",

        "verification_failed_for_all_failed": "❌ 全部检验失败！失败 {failCount}/{selectedFiles_length} 个Omni凭证",

        "github_issues_support": "GitHub 官方技术交流群",

        "download_failed_name": "下载失败: {name}",

        "login_successful": "登录成功！",

        "network_error_error": "网络错误: {error}",

        "batch_verification_completennsucces": "批量检验完成！\\n\\n成功: {successCount} 个\\n失败: {failCount} 个\\n总计: {selectedFiles_length} 个\\n\\n详细结果:\\n{resultMessages_join___n}",

        "http_error_codes_that_trigger_circu": "触发熔断封禁的 HTTP 错误代码 (逗号分隔):",

        "upload_failed_error": "上传失败: {error}",

        "batch_verification_complete": "批量检验完成",

        "storage_and_proxy_settings": "📂 存储与代理设置",

        "performing_batch_action_operation": "正在执行批量{action}操作...",

        "this_setting_may_slightly_reduce_co": "该设置可能导致复杂的 Prompt 理解力有微弱下降，但能完美解决极个别三方客户端因 system_instructions 缺失引发的空返回或流式熔断报错。",

        "fetching_environment_variable_statu": "正在获取环境变量状态...",

        "nnerror_details_errordetail": "\\n\\n错误详情: {errorDetail}",

        "highquality_aesthetic_panel_layout": "极具质感的面板布局，支持所有现代浏览器。",

        "load_failed_datadetail_dataerror_un": "加载失败: {data_detail____data_error}",

        "access_password_to_protect_this_con": "保护此控制台页面不被恶意篡改的访问口令。",

        "if_running_on_a_remote_vps_or_a_hea": "如果是在远程VPS或无浏览器桌面环境运行：请展开下方“无法回源快捷通道”进行处理。",

        "log_file_download_successful_filena": "日志文件下载成功: {filename}",

        "automatically_switch_to_another_rot": "Omni 错误时主动切换其他轮换凭证",

        "connected": "已连接",

        "brstrongavailable_projectsstrongbr": "<br><strong>可用项目：</strong><br>",

        "div_span_classfilenamefileicon_file": "<div>\n\n                        <span class=\"file-name\">{fileIcon} {file_name}</span>\n\n                        <span class=\"file-size\">({formatFileSize_file_size}{fileType})</span>\n\n                    </div>\n\n                    <button class=\"remove-btn\" onclick=\"{type______omni_____removeOmniFile_____removeFile}({index})\">删除</button>",

        "passthrough_model_thinking_process": "透传模型的思维链 (Thinking Process) 到前端响应",

        "log_connection_channel_disconnected": "已切断日志连接通道。",

        "parallel_verifying_selectedfileslen": "🔍 正在并行检验 {selectedFiles_length} 个凭证，请稍候...",

        "failed_to_retrieve_authentication_f": "❌ 获取认证文件失败: {error}",

        "applicable_to_the_latest_gemini_20": "适用于具备推理过程的最新 Gemini 2.0 系列模型。如果关闭，思维链内容会被过滤以提供更洁净的直接回复。",

        "log_stream_connection_disconnected": "日志流连接断开",

        "environment_variable_status_check_c": "环境变量状态检查完成",

        "project_description": "Omni Gateway 是一款面向编程工具的通用 AI 路由。支持智能自动容灾、Token 压缩以及无缝格式转换，最大化利用免费和付费大语言模型。",

        "click_the_view_error_button_to_load": "点击\\\"查看报错\\\"按钮加载报错信息...",

        "loaded_datatotal_type_omni_a": "已加载 {data_total} 个{type______omni_____Omni}凭证文件",

        "email_not_retrieved": "未获取邮箱",

        "tip": "提示",

        "load_failed_error": "加载失败: {error}",

        "omni_credential_valid": "Omni凭证可用",

        "in_cooldown": "CD限制中",

        "verification_failed": "检验失败",

        "gemini_native": "Gemini 原生:",

        "error_code_code": "错误码: {code}",

        "api_endpoint_proxy_setup": "🔗 API 端点代理反代设置",

        "login_failed_incorrect_password": "登录失败！密码错误。",

        "used_for_http_authorization_bearer": "用于代理端点请求时的 HTTP Authorization Bearer Token 验证。",

        "enable_batch": "批量启用",

        "failed_to_download_package_errormes": "打包下载失败: {error_message}",

        "batch_configuration_complete_succes": "⚠️ 批量配置完成：成功 {successCount}/{selectedFiles_length} 个，失败 {failCount} 个",

        "claude_compatible": "Claude 兼容:",

        "verifying_omni_project_id_pl": "🔍 正在检验Omni Project ID，请稍候...",

        "invalid_selection_please_restart_th": "无效的选择，请重新开始认证",

        "error_code_dup": "错误码:",

        "configuration_data_loaded_successfu": "载入配置数据成功！",

        "leave_blank_to_attempt_automatic_de": "留空将尝试自动检测并创建项目。",

        "no_usage_breakdown_statistics_avail": "暂无使用细分统计数据",

        "all_verifications_successful_succes": "✅ 全部检验成功！成功检验 {successCount}/{selectedFiles_length} 个凭证",

        "successfully_deleted_datadeleted_co": "✅ 成功删除 {data_deleted_count} 个环境变量凭证文件",

        "are_you_sure_you_want_to_delete_fil_dup": "确定要删除 {filename} 吗？",

        "verify": "检验",

        "click_to_select_files_or_drag_and_d": "点击选择文件，或直接拖拽文件到这里",

        "configuration_successful": "配置成功",

        "error": "错误:",

        "retrieving_credentials_from_callbac": "正在从回调URL获取凭证...",

        "preview_channel_configuration_faile_dup": "Preview通道配置失败",

        "n_restart_notice_datarestart_notice": "\\n⚠️ 重启提醒: {data_restart_notice}",

        "service_usage_api_status_management": "Service Usage API 状态管理端点:",

        "failed_to_retrieve_authentication_f_dup": "获取认证文件失败",

        "please_select_a_projectnnplease_ent": "请选择一个项目：\\n\\n请输入序号 (1-{count}):",

        "per_page": "每页：",

        "failed_to_check_for_updates_dataerr": "检查更新失败: {data_error}",

        "network_error_errormessage": "网络错误: {error_message}",

        "minimal_resource_footprint_perfectl": "资源开销微乎其微，完美适配各大 PAAS 和 Docker。",

        "application_keepalive_settings": "☕ 应用在线保活防沉睡设置 (Keep-Alive)",

        "save_global_configuration": "保存全局配置",

        "failed_to_load_configuration_datade": "加载配置失败: {data_detail____data_error}",

        "uploading_and_extracting_zip_file": "正在上传并解压ZIP文件...",

        "are_you_sure_you_want_to_batch_veri_dup": "确定要批量检验 {selectedFiles_length} 个凭证的Project ID吗？\\n\\n将并行检验以加快速度。",

        "refreshing_all_user_emails": "正在刷新所有用户邮箱...",

        "operation_failed_datadetail_dataerr": "操作失败: {data_detail____data_error}",

        "are_you_sure_you_want_to_delete_the": "确定要删除选中的 {selectedFiles_length} 个文件吗？\\n注意：此操作不可恢复！",

        "new_version_foundncurrent_vdatavers": "发现新版本！\\n当前: v{data_version}\\n最新: v{data_latest_version}\\n\\n更新内容: {data_latest_message}",

        "div_stylecolor_007bfftype_highlight": "<div style=\"color: #007bff;\">类型: {highlightedType}</div>",

        "failed_to_check_for_updates_errorme": "检查更新失败: {error_message}",

        "nerror_detailsndataerror": "\\n错误详情:\\n{data_error}",

        "omni_authentication_successf_dup": "✅ Omni 认证成功！文件已保存到: {data_file_path}",

        "batch_verify_project_id": "批量检验 Project ID",

        "filter_thiscurrentstatusfilter_enab": "(筛选: {this_currentStatusFilter______enabled})",

        "are_you_sure_you_want_to_configure": "确定要将所有端点配置为官方地址吗？",

        "perfect_responsive_support": "完美响应式支持",

        "welcome_to_join_us_to_discuss_usage": "欢迎加入我们一起交流玩法与提交功能迭代请求：",

        "successfully_deleted_count_environm": "✅ 成功删除 {count} 个环境变量凭证文件",

        "monitor_realtime_request_details_an": "实时监控后台发往 Google Cloud API 的请求细节与轮换逻辑，快速排查网络代理或限流问题。",

        "error_errormsg": "错误: {errorMsg}",

        "unlimited": "无限制",

        "drag_and_drop_or_select_your_existi": "将您现有的 Code Assist 或 Omni 认证 JSON/ZIP 文件拖拽或选择上传到服务器中。",

        "authentication_successful_file_save": "✅ 认证成功！文件已保存到: {data_file_path}",

        "connection_lost": "连接断开",

        "batch_preview_channel_configuration": "批量配置Preview通道完成！\\n\\n成功: {successCount} 个\\n失败: {failCount} 个\\n总计: {selectedFiles_length} 个\\n\\n详细结果:\\n{resultMessages_join___n}",

        "are_you_sure_you_want_to_actionlabe": "确定要{actionLabel}选中的 {selectedFiles_length} 个文件吗？",

        "page_page_of_total_showing_startend": "第 {page} 页，共 {total} 页 (显示 {start}-{end}，共 {count} 项)",

        "loading_file_content": "正在加载文件内容...",

        "generating_authentication_link": "生成认证链接中...",

        "failed_to_refresh_emails": "邮箱刷新失败",

        "preview_only": "仅支持 Preview",

        "max_retries_on_failure": "失败最大重试次数:",

        "batch_operation_complete_successful": "批量操作完成：成功处理 {successCount}/{selectedFiles_length} 个文件",

        "deduplication_detailsnn": "去重详情：\\n\\n",

        "synchronizing_current_system_config": "正在向服务器同步当前系统配置...",

        "ip_address_to_listen_on_0000_allows": "监听绑定的IP地址。0.0.0.0 代表对公网所有访问开发，修改后需要重启。",

        "are_you_sure_you_want_to_reset_usag": "确定要重置 {filename} 的使用统计吗？",

        "please_select_at_least_one_credenti": "请至少选择一个凭证进行操作！",

        "authentication_successful_file_save_dup": "✅ 认证成功！文件已保存到: {path}",

        "retrieving_omni_credentials": "正在从回调URL获取 Omni 凭证...",

        "configuring_preview_channel_please": "🔧 正在配置Preview通道，请稍候...",

        "verification_failed_error": "验证失败: {error}",

        "please_select_the_omni_crede_dup": "❌ 请先选择要检验的Omni凭证",

        "successfully_uploaded_datauploaded": "成功上传 {data_uploaded_count} 个{type______omni_____Omni}文件",

        "dataexisting_env_files_count_files": "{data_existing_env_files_count} 个文件",

        "waiting_for_omni_oauth_callb": "正在等待 Omni OAuth回调...",

        "model_protocol_compatibility_overri": "🧩 模型协议兼容性覆盖",

        "maximum_retries_for_resuming_stream": "Số lần tối đa hệ thống cố gắng tiếp tục truyền dữ liệu từ điểm bị ngắt khi yêu cầu mô hình có hậu tố '-流式抗截断'.",

        "successfully_uploaded_count_type_fi": "成功上传 {count} 个 {type} 文件",

        "failed_to_retrieve_credentials_from_dup": "从回调URL获取凭证失败: {error_message}",

        "enable_credits": "开启积分",

        "code_assist_creds__environment_variable_no": "未找到CODE_ASSIST_CREDS_*环境变量",

        "autoscroll_to_bottom": "自动锁定滚动条到底部",

        "please_select_the_credential_to_con": "❌ 请先选择要配置Preview的凭证",

        "please_select_the_file_to_upload_fi": "请先选择要上传的文件",

        "failed_to_check_for_updates": "检查更新失败:",

        "enabled_dup": "已启用",

        "retrieve_the_latest_google_cloud_sd": "获取谷歌最新版本的 Cloud SDK Omni原生鉴权凭证。",

        "global_upstream_proxy_url": "全局连接前置代理 Proxy URL:",

        "processing_credential_deduplication": "正在处理凭证去重...",

        "24h_total_calls": "24h 累计请求数",

        "status": "状态：",

        "maximum_retry_limit_for_resuming_st": "调用携带 -流式抗截断 后缀的代理模型时，如果遇到长上下文输出被强行腰斩，系统将最多尝试断点重新续传的上限次数。",

        "omni_verification_successful": "Omni Verification Successful!\\n\\n文件: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "all_configured_successfully_preview": "✅ 全部配置成功！成功配置 {successCount}/{selectedFiles_length} 个凭证的Preview通道",

        "enable_credit": "开启 Credit",

        "24hour_call_breakdown_statistics": "24小时内请求细分统计",

        "are_you_sure_you_want_to_refresh_us_dup": "确定要刷新所有Omni凭证的用户邮箱吗？这可能需要一些时间。",

        "unable_to_retrieve_version_informat": "无法获取版本信息",

        "batch_disable_dup": "批量禁用",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                        <div style=\"font-weight: bold;\">网络错误</div>\n\n                        <div style=\"font-size: 12px; margin-top: 8px;\">{error_message}</div>\n\n                    </div>",

        "upstream_network_proxy_required_for": "本地访问谷歌接口时所需的中转网络代理，为空表示直连。",

        "if_you_find_any_bugs_or_have_design": "如果您在使用中发现了任何 Bug 或有好的设计建议，请随时前往开源 GitHub 仓库提交 Issues，也欢迎随时提交 PR 一起丰富生态。",

        "view_error": "查看报错",

        "verification_failednnerrormsg": "❌ 检验失败\\n\\n{errorMsg}",

        "failed_to_retrieve_omni_cred_dup": "从回调URL获取 Omni 凭证失败: {error_message}",

        "code_assist_credential_batch_upload": "Code Assist 凭证批量上传",

        "checking_for_updates": "正在检查更新...",

        "unknown_version": "未知版本",

        "oneclick_credential_deduplication_i": "正在进行凭证一键去重...",

        "operation_successful_action": "操作成功: {action}",

        "download_failed_filename": "下载失败: {filename}",

        "retrieve_and_save_omni_crede": "获取并保存 Omni 凭证",

        "ag_credentials": "AG凭证",

        "view_quota": "查看额度",

        "logged_out": "已退出登录",

        "are_you_sure_you_want_to_reset_usag_dup": "确定要重置所有文件的使用统计吗？此操作不可恢复！",

        "configuration_successfulnfile_filen": "Configuration Successful!\\n文件: {filename}\\n状态: {data_message}",

        "batch_delete_dup": "批量删除",

        "modelname_remainingpercentage_remai": "{modelName} - 剩余{remainingPercentage}% - {resetTime}",

        "configuration_management": "配置管理",

        "retrieving_user_emails": "正在获取用户邮箱...",

        "set_preview": "设置预览",

        "authentication_successful_project_i_dup": "✅ 认证成功！项目ID已自动检测为: {data_credentials_project_id}，文件已保存到: {data_file_path}",

        "automatic_quota_avoidance_rotation": "自动配额避让轮换",

        "reload_configuration_data": "重载配置数据",

        "key_technical_highlights": "主要技术亮点",

        "clear_failed_error": "清除失败: {error}",

        "generating_omni_authenticati": "正在生成 Omni 认证链接...",

        "upload_failed_errormessage": "上传失败: {error_message}",

        "failed_to_update_preview_status_in": "批量更新 Preview 状态失败: {error}",

        "downloaded_filename": "✅ 已下载: {filename}",

        "bulk_upload_local_credentials": "批量上传本地凭证",

        "div_stylebackground_lineargradient1": "<div style=\"background: var(--bg-subtle); color: var(--text-primary); padding: 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 15px;\">\n\n                                <h4 style=\"margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;\">\n\n                                    <span style=\"font-size: 20px;\">📊</span>\n\n                                    <span>额度信息详情</span>\n\n                                </h4>\n\n                                <div style=\"font-size: 12px; opacity: 0.9; margin-top: 5px;\">文件: {filename}</div>\n\n                            </div>\n\n                            <div style=\"display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;\">",

        "automatic_retry_reconnection_mechan": "🔁 自动重试重连机制",

        "download_all_credentials_as_archive": "打包下载所有凭证",

        "waiting_for_oauth_callback": "等待OAuth回调中...",

        "local_storage_directory_for_uploade": "保存上传和授权获取的 JSON 文件的本地存储目录。",

        "bulk_preview_channel_configuration": "批量配置Preview通道完成",

        "disable_credit": "关闭 Credit",

        "no_logs_yet": "暂无日志...",

        "already_up_to_date": "已是最新版本！",

        "test_successfulnfile_filenamenstatu_dup": "Test Successful!\\n文件: {filename}\\n状态: {data_message} ({data_status_code____200})",

        "deduplication_complete_deleted_data": "去重完成：删除 {data_deleted_count} 个重复凭证，保留 {data_kept_count} 个凭证（{data_unique_emails_count} 个唯一邮箱）",

        "are_you_sure_you_want_to_perform_th": "确认对已选中的 {count} 项凭证执行 {action} 批量操作吗？",

        "bulk_operation_failed_datadetail_da": "批量操作失败: {data_detail____data_error}",

        "ncredit_datacredit_amount": "\\n积分: {data_credit_amount}",

        "authentication_failed_please_log_in": "认证失败，请重新登录",

        "code_assist_credential_file_management": "Code Assist凭证文件管理",

        "failed_to_retrieve_version_informat": "获取版本信息失败:",

        "filter_level": "过滤等级：",

        "failed_to_get_email_errormessage": "获取邮箱失败: {error_message}",

        "suitable_for_cloud_servervps_deploy": "适用于云服务器/VPS部署、Docker容器环境、或者防火墙拦截 11451 端口的场景。",

        "connection_error": "连接错误",

        "omni_credentials_successfull": "从回调URL获取 Omni 凭证成功！",

        "are_you_sure_you_want_to_configure_dup": "确定要将所有端点配置为镜像网址吗？",

        "sever_log_channel": "切断日志通道",

        "configuration_loaded_successfully": "配置加载成功",

        "unable_to_load_file_content": "无法加载文件内容:",

        "bulk_enable_credit": "批量开启积分",

        "live_connection_status": "实时链接状态：",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\">📊 正在加载额度信息...</div>",

        "connection_failed": "连接失败",

        "oneclick_deduplication_complete_del": "一键去重完成！共删除 {deleted} 个重复文件，保留 {kept} 个唯一账户文件。",

        "verifying_project_id_please_wait": "🔍 正在检验Project ID，请稍候...",

        "email_refresh_network_error_errorme": "邮箱刷新网络错误: {error_message}",

        "waiting_for_oauth_callback_this_may": "正在等待OAuth回调，这可能需要一些时间...",

        "project_id_required_to_complete_aut": "需要项目ID才能完成认证，请重新开始并输入正确的项目ID",

        "error_code_datastatus_code_response": "错误码: {data_status_code____response_status}",

        "cooling_down": "冷却中：",

        "start_bulk_upload": "开始批量上传",

        "attempting_to_autodetect_project_id": "将尝试自动检测项目ID，正在生成认证链接...",

        "check_for_updates_failed_dataupdate": "检查更新失败: {data_update_error}",

        "upload_failed": "上传失败:",

        "all_verifications_failed_failed_fai": "❌ 全部检验失败！失败 {failCount}/{selectedFiles_length} 个凭证",

        "upload_failed_server_response_forma": "上传失败: 服务器响应格式错误",

        "deduplication_failed": "去重失败",

        "credit_resultcreditamount": "(积分: {result_creditAmount})",

        "are_you_sure_you_want_to_delete_the_dup": "确定要删除凭证文件吗？\\n{filename}",

        "test_failed": "测试失败",

        "bulk_configure_preview_channels": "批量配置 Preview 通道",

        "github_open_source_repository": "GitHub 开源协议库:",

        "test_failed_errormessage": "测试失败: {error_message}",

        "view_account_email": "查看账号邮箱",

        "longtext_truncation_recovery_contro": "⏱️ 抗输出截断长文本控制 (Truncation Recovery)",

        "automation_enabled": "自动化已启用：",

        "div_stylepadding_12px_marginbottom": "<div style=\"padding: 12px; margin-bottom: 10px; border-left: 3px solid #dc3545; background-color: #f8f9fa;\">\n\n                                    <div style=\"font-weight: bold; color: #dc3545; margin-bottom: 8px;\">错误码: {errorCode}</div>\n\n                                    <div style=\"line-height: 1.6; color: #333; white-space: pre-wrap; word-break: break-word;\">\n\n                                        {highlightedMsg}\n\n                                    </div>\n\n                                    {detailsHtml}\n\n                                </div>",

        "refresh_all_account_emails": "刷新所有账号邮箱",

        "about_omni-gateway": "关于 Omni Gateway",

        "get_authentication_file": "获取认证文件",

        "n_restart_reminder_notice": "\\n⚠️ 重启提醒: {notice}",

        "test_failed_datamessage_error_code": "Test Failed - {data_message_______________data_status_code____response_status}",

        "service_keepalive_heartbeat_request": "服务保活心跳检测请求 URL:",

        "after_the_google_authorization_redi": "在谷歌授权同意跳转后，复制浏览器地址栏里的完整 URL 地址（即便显示连接失败），粘贴到下方输入框中即可。",

        "disabled": "已禁用",

        "upload_failed_http_status": "上传失败: HTTP {status}",

        "disconnected": "未连接",

        "if_the_redirect_fails_and_shows_an": "跳转失败报错提示无法连接 localhost:11451 时，返回此控制面板；",

        "unknown_error": "未知错误",

        "testing_omni_credentials_ple": "🧪 正在测试Omni凭证，请稍候...",

        "if_you_cannot_return_to_the_source": "若无法回源，可复制跳转后的完整 URL 展开下方快捷通道进行解析。",

        "verification_failed_errormessage": "检验失败: {error_message}",

        "nerror_detailsnjsonstringifyerrorob": "\\n错误详情:\\n{JSON_stringify_errorObj__null__2}",

        "log_stream_connected_successfully": "日志流连接成功",

        "clearing_environment_variable_crede": "正在清除环境变量凭证文件...",

        "get_authentication_link": "获取认证链接",

        "resulterror_step_resultstep": "{result_error} (步骤: {result_step})",

        "network_error": "网络错误:",

        "failed_to_retrieve_environment_vari": "获取环境变量状态失败: {data_detail____data_error}",

        "count_items_selected": "已选择 {count} 项",

        "are_you_sure_you_want_to_clear_all": "确定要清除所有从环境变量导入的凭证文件吗？\\n这将删除所有文件名以 \"env-\" 开头的认证文件。",

        "bulk_operation_network_error_errorm": "批量操作网络错误: {error_message}",

        "streaming_truncation_recovery": "-流式抗截断",

        "failed_to_get_quota_information": "获取额度信息失败",

        "click_the_button_below_to_retrieve": "点击下方按钮直接获取并自动保存凭证文件；",

        "seamlessly_switch_to_idle_accounts": "无感切取空闲账号，有效避让 429 访问限制。",

        "bind_the_listening_tcp_port_changes": "绑定监听的 TCP 端口，改动需重启生效。",

        "bulk_disable_credit": "批量关闭积分",

        "failed": "失败",

        "reset_failed_datamessage_datadetail": "重置失败: {data_message____data_detail____data_error}",

        "failed_to_get_quota_information_err": "❌ 获取额度信息失败: {error_message}",

        "realtime_logs": "实时日志",

        "please_enter_the_access_password": "请输入访问密码！",

        "zip_files_will_be_automatically_dec": "ZIP 文件会自动解压并过滤提取其中的 JSON 凭证。",

        "oauth_authentication_server_endpoin": "OAuth 鉴权服务端点:",

        "are_you_sure_you_want_to_batch_set": "确定要为 {selectedFiles_length} 个凭证批量设置Preview通道吗？\\n\\n将并行配置以加快速度。",

        "settings_saved_successfully_success": "设置保存成功",

        "configuration_saved_successfully": "配置保存成功",

        "preview_not_supported": "不支持 Preview",

        "please_select_a_projectnn": "请选择一个项目：\\n\\n",

        "please_select_the_files_to_upload": "请选择要上传的文件",

        "are_you_sure_you_want_to_action_the": "确定要{action}选中的 {count} 个文件吗？",

        "a_hrefurl_target_blank_stylecolor_0": "<a href=\"{url}\" target=\"_blank\" style=\"color: #007bff; text-decoration: underline; word-break: break-all;\" title=\"点击打开: {url}\">{url}</a>",

        "retry_fetching_authentication_file": "重新尝试获取认证文件",

        "manually_connect_log_channel": "手动接入日志通道",

        "error_information_loaded_successful": "✅ 成功加载报错信息",

        "universal_shortcut_override_passwor": "通用快捷覆盖密码 (可选):",

        "login_failed_datadetail_dataerror_u": "登录失败: {data_detail____data_error}",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\">⏳ 正在加载报错信息...</div>",

        "log_stream_connection_disconnected_dup": "日志流连接已断开",

        "system_configuration_saved_successf": "✅ 系统配置保存成功",

        "div_stylefontsize_12px_color_666sta": "<div style=\"font-size: 12px; color: #666;\">状态: {escapeHtml_parsedMsg_error_status}</div>",

        "api_access_authentication_password": "接口 API 访问鉴权密码 (API Key):",

        "parallel_testing_selectedfileslengt": "🔍 正在并行检验 {selectedFiles_length} 个Omni凭证，请稍候...",

        "operation_failed": "操作失败:",

        "all_omni_credentials_packed": "✅ 所有Omni凭证已打包下载",

        "operation_successful_action_dup": "操作成功: {action}",

        "omni_api_endpoint": "Omni API 端点:",

        "authentication_link_generated_proje": "认证链接已生成（项目ID: {data_detected_project_id}），请点击链接完成授权",

        "configuring_preview_channel_status": "正在批量配置 Preview 通道状态...",

        "after_successful_authorization_the_dup": "系统在授权成功后，会自动检测并为您的谷歌云项目激活 Gemini Cloud Assist API 和 Gemini for Google Cloud API 必要的API服务，无需任何手动配置。",

        "batch_upload_omni_credential": "Omni 凭证批量上传",

        "checking": "检查中...",

        "please_enter_the_callback_url": "请输入回调URL",

        "extract_credentials_from_callback_l": "从回调链接解析获取凭证",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #28a745;\">\n\n                                <div style=\"font-size: 48px; margin-bottom: 10px;\">✅</div>\n\n                                <div style=\"font-weight: bold;\">无报错记录</div>\n\n                                <div style=\"font-size: 12px; color: #666; margin-top: 8px;\">该凭证运行正常</div>\n\n                            </div>",

        "no_details_available": "无详细信息",

        "global_system_configuration": "全局系统配置",

        "network_error_while_downloading_log": "下载日志时网络错误: {error_message}",

        "authentication_link_generated_proje_dup": "认证链接已生成（项目ID: {id}），请点击链接完成授权",

        "listening_port": "监听端口号 Port:",

        "email_refresh_complete_successfully": "邮箱刷新完成：成功获取 {data_success_count}/{data_total_count} 个邮箱地址",

        "already_up_to_date_dup": "已是最新",

        "no_credential_files_available": "暂无凭证文件",

        "validation_successfulnnfile_filenam": "Verification Successful!\\n\\n文件: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "selectedcount_items_selected": "已选择 {selectedCount} 项",

        "click_the_view_content_button_to_lo": "点击\\\"查看内容\\\"按钮加载文件详情...",

        "please_enter_the_password": "请输入密码",

        "upload_progress_dup": "上传进度",

        "error_dataerror_failed_to_fetch_aut": "错误: {data_error}",

        "are_you_sure_you_want_to_delete_the_dup_dup": "确定要删除选中的 {count} 个文件吗？\\n注意：此操作不可恢复！",

        "configuring_preview_channel_for_sel": "🔧 正在为 {selectedFiles_length} 个凭证配置Preview通道，请稍候...",

        "none": "无",

        "this_is_not_a_valid_callback_url_pl_dup": "❌ 这不是有效的回调URL！请确保包含code和state参数",

        "retrieved_credential_file_content": "获取的凭证文件内容：",

        "enable": "启用",

        "antitruncation_output_protection": "防截断抗输出抗截断",

        "authentication_link_generated_proje_dup_dup": "认证链接已生成（将在认证完成后自动检测项目ID），请点击链接完成授权",

        "failed_to_configure_preview_channel_dup": "配置Preview通道失败",

        "testing_credentials_please_wait": "🧪 正在测试凭证，请稍候...",

        "validation_complete_processed_activ": "验证完成！共处理：正常有效 {active} 个，更新ID {changed} 个，标记失效 {disabled} 个",

        "login_successful_dup": "登录成功",

        "batch_task_control": "批量任务控制",

        "24h_api_call_volume": "24H 内请求数",

        "minimalist_parsing_mapping_for_cutt": "极简解析映射 System / Thinking 等前沿协议。",

        "multiple_projects_detected_please_s": "检测到多个项目，请在高级选项中指定项目ID：",

        "failed_to_fetch_error_information_e": "❌ 获取报错信息失败: {error_message}",

        "loaded_usage_statistics_for_aggdata": "已加载 {aggData_total_files____Object_keys_AppState_usageStatsData__length} 个文件的使用统计",
        "failed_to_load_usage_statistics": "加载使用统计失败",
        "error_errormsg": "错误: {errorMsg}",
        "status_net_error": "网络错误: {error}",
        "status_no_filter_data": "未找到使用统计数据。",
        "table_calls": "请求数",
        "btn_reset_stats": "重置统计",
        "confirm_reset_stats": "您确定要重置 {filename} 的统计数据吗？",
        "reset_failed_datamessage_datadetail": "重置失败: {data_message____data_detail____data_error}",
        "are_you_sure_you_want_to_reset_usag_dup": "您确定要重置所有的使用统计数据吗？",
        "table_filename": "凭证文件名",
        "table_actions": "操作"

    },

    vi: {

        "app_title": "Omni Gateway",

        "panel_title": "Bảng Điều Khiển Omni Gateway",

        "login_subtitle": "Vui lòng nhập mật khẩu truy cập để quản lý các cổng proxy",

        "login_placeholder": "Nhập mật khẩu bảng điều khiển",

        "login_btn": "Đăng nhập",

        "logout_btn": "Đăng xuất",

        "version_label": "Phiên bản",

        "check_update_btn": "Kiểm tra cập nhật",

        "loading_text": "Đang tải...",

        "mirror_switch_warning": "Cài đặt mirror proxy sẽ thay đổi tên miền API chính thức sang máy chủ proxy trung gian.",

        "copy_success": "Đã sao chép vào bộ nhớ tạm!",

        "copy_fail": "Sao chép thất bại!",

        "btn_close": "Đóng",

        "dialog_tip": "Gợi ý",

        "error_prefix": "Lỗi: ",

        "tab_oauth": "Xác thực OAuth",

        "tab_omni": "Xác thực Omni",

        "tab_upload": "Tải lên hàng loạt",

        "tab_manage_creds": "Quản lý tài khoản",
        "manage_creds_title": "Quản lý tài khoản",
        "manage_creds_desc": "Chọn nhà cung cấp tài khoản để xem và quản lý các kênh API đang hoạt động.",
        "tab_manage_code_assist": "Quản lý Code Assist",

        "tab_manage_code_assist_short": "Chứng chỉ Code Assist",

        "tab_manage_ag": "Quản lý Omni",

        "tab_manage_ag_short": "Chứng chỉ AG",

        "tab_config": "Cài đặt hệ thống",

        "tab_logs": "Nhật ký trực tiếp",

        "tab_about": "Thông tin dự án",

        "oauth_banner_title": "Đã bật tự động hóa:",

        "oauth_banner_text": "Hệ thống sẽ tự động phát hiện và kích hoạt các dịch vụ API cần thiết cho dự án Google Cloud của bạn (Gemini Cloud Assist API, Gemini for Google Cloud API) sau khi xác thực thành công.",

        "oauth_advanced_title": "Nâng cao: Chỉ định Google Cloud Project ID (Tùy chọn)",

        "oauth_advanced_note": "Để trống để tự động phát hiện và tạo dự án.",

        "oauth_link_btn": "Lấy liên kết xác thực Google OAuth",

        "oauth_auth_title": "Liên kết xác thực đã lấy:",

        "oauth_auth_instruction": "Nhấp vào liên kết này để ủy quyền tài khoản Google",

        "oauth_guide_title": "Hướng dẫn tương tác OAuth:",

        "oauth_guide_1": "Nhấp vào liên kết ở trên, đăng nhập tài khoản Google và đồng ý ủy quyền trong tab mới;",

        "oauth_guide_2": "Sau khi ủy quyền xong, trình duyệt sẽ tự chuyển hướng và báo lỗi không thể kết nối localhost:11451, đây là bình thường;",

        "oauth_guide_3": "Quay lại bảng điều khiển này và nhấp vào nút \"Lấy và lưu tệp chứng chỉ\" phía dưới;",

        "oauth_guide_4": "Nếu chạy trên VPS từ xa không có giao diện đồ họa: Vui lòng mở rộng phần \"Kênh phản hồi nhanh\" bên dưới.",

        "oauth_callback_title": "Không thể tự động phản hồi? Sử dụng kênh phản hồi nhanh",

        "oauth_callback_note": "Thích hợp cho VPS, môi trường Docker, hoặc khi cổng 11451 bị tường lửa chặn.",

        "oauth_callback_instructions": "Sau khi đồng ý ủy quyền trên Google, sao chép toàn bộ URL trên thanh địa chỉ trình duyệt (ngay cả khi báo lỗi kết nối) và dán vào ô bên dưới.",

        "oauth_callback_btn": "Phân tích chứng chỉ từ URL phản hồi",

        "oauth_save_btn": "Lấy và lưu tệp chứng chỉ",

        "oauth_success_title": "Xác thực thành công! Nội dung chứng chỉ đã lưu:",

        "ag_banner_title": "Chế độ xác thực Google Omni",

        "ag_banner_text": "Nhận chứng chỉ xác thực Cloud SDK Omni nguyên bản của Google.",

        "ag_link_btn": "Lấy liên kết xác thực Omni",

        "ag_link_title": "Liên kết xác thực Omni:",

        "ag_link_instruction": "Nhấp vào liên kết này để ủy quyền chế độ Omni",

        "ag_guide_title": "Các bước thực hiện:",

        "ag_guide_1": "Nhấp vào liên kết ở trên để thực hiện ủy quyền Google OAuth;",

        "ag_guide_2": "Khi chuyển hướng thất bại báo lỗi kết nối localhost:11451, quay lại bảng điều khiển này;",

        "ag_guide_3": "Nhấp vào nút bên dưới để nhận trực tiếp và tự động lưu tệp chứng chỉ;",

        "ag_guide_4": "Nếu không thể tự động phản hồi, sao chép URL chuyển hướng và phân tích bên dưới.",

        "ag_save_btn": "Lấy và lưu chứng chỉ Omni",

        "ag_success_title": "Nội dung chứng chỉ Omni đã nhận:",

        "ag_download_btn": "Tải xuống tệp chứng chỉ về máy",

        "upload_title": "Tải lên chứng chỉ hàng loạt",

        "upload_desc": "Kéo và thả hoặc chọn các tệp JSON/ZIP chứng chỉ để tải lên máy chủ.",

        "upload_code_assist_title": "Tải lên chứng chỉ Code Assist hàng loạt",

        "upload_code_assist_area_title": "Nhấp để chọn tệp hoặc kéo thả tệp vào đây",

        "upload_code_assist_area_subtitle": "Hỗ trợ tệp .json hoặc nén .zip",

        "upload_code_assist_area_note": "Tệp ZIP sẽ tự động được giải nén để tìm các tệp chứng chỉ JSON bên trong.",

        "upload_pending_code_assist": "Danh sách tệp Code Assist chờ tải lên:",

        "upload_start_btn": "Bắt đầu tải lên hàng loạt",

        "upload_clear_btn": "Xóa danh sách chọn",

        "upload_progress": "Tiến độ tải lên",

        "upload_ag_title": "Tải lên chứng chỉ Omni hàng loạt",

        "upload_ag_area_title": "Nhấp để chọn tệp hoặc kéo thả tệp vào đây",

        "upload_ag_area_subtitle": "Hỗ trợ tệp chứng chỉ .json hoặc nén .zip",

        "upload_ag_area_note": "Tệp ZIP sẽ tự động được giải nén và lọc để lấy các tệp chứng chỉ JSON.",

        "upload_pending_ag": "Danh sách tệp Omni chờ tải lên:",

        "code_assist_manage_title": "Quản lý chứng chỉ Code Assist",

        "code_assist_manage_desc": "Hiển thị và duy trì các cổng proxy Code Assist của bạn. Hỗ trợ kiểm tra đơn lẻ/hàng loạt, tải xuống, chuyển đổi trạng thái và xóa.",

        "ag_manage_title": "Quản lý chứng chỉ Omni",

        "ag_manage_desc": "Hiển thị và quản lý các tài khoản Omni cùng hạn mức (quota) yêu cầu tương ứng.",

        "endpoint_banner_title": "Địa chỉ cổng API tích hợp",

        "endpoint_openai": "Tương thích OpenAI:",

        "endpoint_claude": "Tương thích Claude:",

        "endpoint_gemini": "Gemini nguyên bản:",

        "stat_total": "Tổng chứng chỉ",

        "stat_active": "Hoạt động bình thường",

        "stat_disabled": "Đang bị tắt",

        "btn_refresh": "Làm mới danh sách",

        "btn_download_all": "Tải xuống tất cả (ZIP)",

        "batch_panel_title": "Điều khiển tác vụ hàng loạt",

        "batch_select_all": "Chọn tất cả",

        "batch_selected_count": "Đã chọn {count} mục",

        "batch_enable": "Bật hàng loạt",

        "batch_disable": "Tắt hàng loạt",

        "batch_delete": "Xóa hàng loạt",

        "batch_verify_id": "Kiểm tra Project ID hàng loạt",

        "batch_preview_toggle": "Cài đặt kênh Preview hàng loạt",

        "batch_refresh_emails": "Làm mới email các tài khoản",

        "batch_deduplicate": "Loại bỏ trùng lặp theo Email",

        "batch_enable_credit": "Bật chế độ Credit hàng loạt",

        "batch_disable_credit": "Tắt chế độ Credit hàng loạt",

        "filter_status": "Trạng thái:",

        "filter_all": "Tất cả",

        "filter_status_enabled": "Chỉ bật",

        "filter_status_disabled": "Chỉ tắt",

        "filter_error": "Mã lỗi:",

        "filter_error_none": "Không lỗi",

        "filter_cooldown": "Thời gian chờ (CD):",

        "filter_cooldown_active": "Đang CD hạn chế",

        "filter_cooldown_none": "Không giới hạn",

        "filter_preview": "Preview:",

        "filter_preview_on": "Chỉ hỗ trợ Preview",

        "filter_preview_off": "Không hỗ trợ Preview",

        "filter_tier": "Cấp độ:",

        "filter_per_page": "Mỗi trang:",

        "card_enabled": "Đang bật",

        "card_disabled": "Đang tắt",

        "card_no_error": "Không lỗi",

        "card_error_code": "Mã lỗi: {code}",

        "card_no_email": "Chưa lấy email",

        "card_loading_details": "Nhấp nút \"Xem nội dung\" để tải chi tiết tệp...",

        "card_loading_errors": "Nhấp nút \"Xem lỗi\" để tải thông tin lỗi...",

        "card_loading_quota": "Nhấp nút \"Xem hạn mức\" để tải thông tin quota...",

        "btn_card_enable": "Bật",

        "btn_card_disable": "Tắt",

        "btn_card_view": "Xem nội dung",

        "btn_card_download": "Tải xuống",

        "btn_card_email": "Xem email tài khoản",

        "btn_card_quota": "Xem hạn mức",

        "btn_card_close_credit": "Tắt Credit",

        "btn_card_open_credit": "Bật Credit",

        "btn_card_set_preview": "Đặt Preview",

        "btn_card_verify": "Kiểm tra",

        "btn_card_test": "Kiểm tra tin nhắn",

        "btn_card_error_details": "Xem lỗi",

        "btn_card_delete": "Xóa",

        "config_title": "Cấu hình hệ thống toàn cục",

        "config_desc": "Điều chỉnh proxy mạng, địa chỉ cổng kết nối, chính sách bảo mật và các tham số thử lại. Hầu hết các thay đổi sẽ có hiệu lực ngay sau khi lưu.",

        "btn_save_config": "Lưu cấu hình toàn cục",

        "btn_reload_config": "Tải lại dữ liệu cấu hình",

        "config_loading": "Đang đồng bộ hóa cấu hình hệ thống hiện tại với máy chủ...",

        "group_network": "⚙️ Cấu hình mạng và bảo mật",

        "config_host_label": "IP máy chủ lắng nghe (Host IP Address):",

        "config_host_note": "Địa chỉ IP lắng nghe (0.0.0.0 cho phép truy cập công cộng từ mọi card mạng, cần khởi động lại).",

        "config_port_label": "Cổng lắng nghe (Port):",

        "config_port_note": "Cổng TCP lắng nghe dịch vụ, cần khởi động lại để áp dụng.",

        "config_api_pwd_label": "Mật khẩu truy cập API (API Key):",

        "config_api_pwd_note": "Dùng để xác thực HTTP Authorization Bearer Token khi gửi yêu cầu đến các cổng proxy.",

        "config_panel_pwd_label": "Mật khẩu đăng nhập bảng điều khiển:",

        "config_panel_pwd_note": "Mật khẩu bảo vệ trang quản lý này không bị truy cập trái phép.",

        "config_pwd_label": "Mật khẩu đè chung (Tùy chọn):",

        "config_pwd_note": "Nếu được cung cấp, mật khẩu này sẽ ép buộc ghi đè lên cả mật khẩu API và đăng nhập. Nên để trống.",

        "group_storage": "📂 Cài đặt lưu trữ và proxy",

        "config_storage_label": "Đường dẫn tuyệt đối thư mục lưu chứng chỉ:",

        "config_storage_note": "Thư mục lưu trữ cục bộ lưu các tệp JSON tải lên hoặc nhận từ xác thực.",

        "config_proxy_label": "Địa chỉ Proxy URL toàn cục (Global Proxy):",

        "config_proxy_note": "Proxy trung gian khi máy chủ kết nối tới Google (SOCKS5 hoặc HTTP), để trống nếu kết nối trực tiếp.",

        "group_endpoints": "🔗 Cấu hình cổng kết nối API (Endpoints)",

        "config_mirror_btn": "🚀 Chuyển sang địa chỉ mirror proxy",

        "config_official_btn": "🔄 Khôi phục địa chỉ Google chính thức",

        "config_endpoint_code": "Cổng Code Assist API:",

        "config_endpoint_oauth": "Cổng xác thực OAuth:",

        "config_endpoint_apis": "Cổng lõi Google APIs:",

        "config_endpoint_resource": "Cổng Resource Manager API:",

        "config_endpoint_service": "Cổng Service Usage API:",

        "config_endpoint_ag": "Cổng Omni API:",

        "group_ban": "🛡️ Chính sách quản lý rủi ro và cầu chì",

        "config_ban_checkbox": "Kích hoạt tự động khóa tài khoản (Auto-Ban) khi gặp các mã lỗi chỉ định",

        "config_ban_codes_label": "Các mã lỗi HTTP kích hoạt khóa tự động (cách nhau bởi dấu phẩy):",

        "config_ban_codes_note": "Tài khoản nhận mã lỗi này từ Google sẽ bị tắt ngay lập tức. Khuyên dùng mã lỗi 403.",

        "group_retry": "🔁 Cơ chế tự động thử lại",

        "config_retry_checkbox": "Kích hoạt tự động thử lại yêu cầu thất bại trên các chứng chỉ rảnh khác",

        "config_retry_count": "Số lần thử lại tối đa:",

        "config_retry_interval": "Khoảng thời gian giữa các lần thử lại (giây):",

        "group_compat": "🧩 Tính tương thích giao thức mô hình",

        "config_compat_checkbox": "Ép buộc bật chế độ tương thích (Gộp tin nhắn System vào tin nhắn User)",

        "config_compat_note": "Giúp giải quyết triệt độ lỗi phản hồi trống của một số ít máy khách bên thứ ba do thiếu system_instructions, đổi lại có thể giảm nhẹ độ hiểu prompt phức tạp.",

        "config_thinking_checkbox": "Chuyển tiếp chuỗi tư duy (Thinking Process) của mô hình về phản hồi giao diện",

        "config_thinking_note": "Áp dụng cho dòng mô hình mới Gemini 2.0 có khả năng suy nghĩ. Nếu tắt, phần tư duy sẽ được lọc bỏ để có câu trả lời sạch hơn.",

        "config_ag_stream_checkbox": "Chuyển đổi luồng cho chế độ Omni (Stream to Non-stream Collection)",

        "config_ag_retry_checkbox": "Tự động đổi chứng chỉ khác khi Omni gặp lỗi",

        "group_trunc": "⏱️ Kiểm soát văn bản dài chống cắt ngang (Truncation Recovery)",

        "config_trunc_count": "Số lần tiếp tục truyền tối đa chống cắt ngang:",

        "config_trunc_note": "Số lần tối đa hệ thống cố gắng tiếp tục truyền dữ liệu từ điểm bị ngắt khi yêu cầu mô hình có hậu tố '-流式抗截断'.",

        "group_keepalive": "☕ Cài đặt giữ dịch vụ luôn trực tuyến (Keep-Alive)",

        "config_keepalive_label": "Địa chỉ URL gửi nhịp tim giữ kết nối trực tuyến:",

        "config_keepalive_btn": "Tự động bắt và điền URL giữ kết nối hiện tại",

        "config_keepalive_interval": "Tần suất gửi nhịp tim (giây):",

        "logs_title": "Nhật ký vận hành hệ thống",

        "logs_desc": "Theo dõi thời gian thực chi tiết yêu cầu gửi tới Google Cloud API và logic luân chuyển, giúp nhanh chóng gỡ lỗi proxy mạng hoặc giới hạn tần suất.",

        "btn_log_connect": "Kết nối cổng nhật ký trực tiếp",

        "btn_log_disconnect": "Ngắt kết nối nhật ký",

        "btn_log_save": "Lưu tệp nhật ký về máy",

        "btn_log_clear": "Xóa sạch nhật ký màn hình",

        "log_filter_level": "Lọc cấp độ nhật ký:",

        "log_scroll_lock": "Tự động cuộn xuống dưới cùng",

        "log_status_label": "Trạng thái kết nối trực tiếp:",

        "log_status_text": "Chưa kết nối",

        "log_waiting_text": "Đang chờ tải dữ liệu nhật ký hệ thống...",

        "about_title": "Về dự án Omni Gateway",

        "tab_dashboard": "Bảng điều khiển",
        "regenerate_keys_btn": "Đổi mã API Key",
        "copy_btn": "Sao chép",
        "confirm_regenerate_key": "Bạn có chắc chắn muốn đổi mã API Key này không? Khóa cũ sẽ lập tức mất hiệu lực.",
        "regenerate_success": "Đã đổi mới tất cả các API Key thành công",
        "tooltip_total_calls": "Total number of API requests sent to the Gateway in the past 24 hours.",
        "tooltip_total_files": "Total number of active Code Assist and Omni credential files in the system.",
        "tooltip_avg_calls": "Average number of API requests processed per credential in the past 24 hours.",
        "tooltip_total_calls": "Total number of API requests routed through this gateway in the last 24 hours.",
        "tooltip_total_files": "The number of active Google/Omni credentials currently configured and monitored.",
        "api_keys_title": "Mã khóa API",
        "api_integration_title": "Tích hợp API",
        "tooltip_total_calls": "Tổng số lượt yêu cầu API được gửi tới Gateway trong vòng 24 giờ qua.",
        "tooltip_total_files": "Tổng số lượng file tài khoản Code Assist và Omni đang hoạt động trong hệ thống.",
        "tooltip_avg_calls": "Số lượng yêu cầu API trung bình được thực hiện bởi mỗi tài khoản trong 24 giờ qua.",
        "tooltip_total_calls": "Tổng số yêu cầu API được chuyển tiếp qua cổng gateway này trong vòng 24 giờ qua.",
        "tooltip_total_files": "Số lượng tệp cấu hình tài khoản Google/Omni đang hoạt động và được giám sát.",
        "quick_info_title": "Thông tin tích hợp nhanh",
        "info_openai_header": "Header OpenAI:",
        "info_anthropic_header": "Header Anthropic:",
        "info_status": "Trạng thái dịch vụ:",
        "status_running": "Hoạt động",
        "api_key_label": "Mã khóa API:",
        "api_connection_title": "Thông tin kết nối API",
        "quick_guide_title": "Hướng dẫn kết nối nhanh",
        "guide_openai_header": "Tương thích OpenAI:",
        "guide_anthropic_header": "Tương thích Anthropic:",
        "guide_tip_header": "Gợi ý:",
        "guide_tip_content": "Nhấp vào bất kỳ trường nào trong thẻ thông tin kết nối để sao chép. Mã khóa API duy nhất hoạt động mượt mà với cả các ứng dụng chuẩn OpenAI hoặc Anthropic.",
        "openai_key_label": "OpenAI API Key:",
        "anthropic_key_label": "Anthropic API Key:",
        "unified_endpoint_title": "Cổng API tích hợp",
        "api_integration_card_title": "Tích hợp API",
        "quick_integration_title": "Tích hợp nhanh",
        "integration_openai_title": "Các Client tương thích OpenAI:",
        "integration_anthropic_title": "Các Client tương thích Anthropic:",
        "integration_url_prefix": "Base URL:",
        "integration_key_prefix": "API Key:",
        "endpoint_base_label": "Địa chỉ cổng API:",
        "dashboard_total_calls": "Tổng số yêu cầu (24h)",
        "dashboard_total_calls_desc": "Tổng số yêu cầu API được xử lý qua cổng kết nối trong 24 giờ qua.",
        "dashboard_total_files_desc": "Tổng số tài khoản cấu hình Code Assist và Omni đang hoạt động trong cơ sở dữ liệu.",
        "dashboard_avg_calls_desc": "Số yêu cầu API trung bình được xử lý bởi mỗi tài khoản hoạt động.",
        "dashboard_total_files": "Tài khoản đang giám sát",
        "dashboard_avg_calls": "Trung bình yêu cầu / Tài khoản",
        "dashboard_welcome": "Chào mừng bạn đến với giao diện điều khiển Omni Gateway được thiết kế mới! Bạn có thể nhanh chóng chuyển đổi các tác vụ quản lý ở thanh bên. Hệ thống tự động luân chuyển các chứng chỉ đang hoạt động để cân bằng tải, thực hiện dự phòng và thử lại khi gặp lỗi giới hạn tần suất (429) hoặc bị chặn (403) nhằm đảm bảo tính sẵn sàng cao.",
        "dashboard_breakdown": "Chi tiết yêu cầu trong 24 giờ",
        "oauth_desc": "Tạo thông tin xác thực ủy quyền Google Cloud. Hỗ trợ xuất chứng chỉ Code Assist OAuth tiêu chuẩn và Omni.",

        "about_desc": "Omni Gateway là bộ định tuyến AI phổ quát cho các công cụ lập trình. Hỗ trợ tự động chuyển đổi thông minh, nén token và dịch định dạng liền mạch để tối ưu hóa việc sử dụng các LLM miễn phí và trả phí.",

        "about_github": "Mã nguồn mở trên GitHub:",

        "about_notice": "Tuyên bố miễn trừ trách nhiệm: Nghiêm cấm mọi hành vi mua bán thương mại hoặc phân phối lại dưới mọi hình thức. Chỉ dành cho nghiên cứu cá nhân và học tập học thuật.",

        "about_features_title": "Các điểm kỹ thuật nổi bật",

        "feat_1_title": "Luân chuyển tránh giới hạn",

        "feat_1_desc": "Tự động luân chuyển giữa các tài khoản để tránh lỗi giới hạn yêu cầu (429 Rate Limit) hiệu quả.",

        "feat_2_title": "Chuyển đổi giao thức mượt mà",

        "feat_2_desc": "Chuyển đổi trực tiếp các cấu trúc đặc thù như System hay Thinking hai chiều.",

        "feat_3_title": "Cầu chì bảo vệ Auto-Ban",

        "feat_3_desc": "Tự động hạ cấp và vô hiệu hóa tài khoản khi nhận diện lỗi API như 403 trong tích tắc.",

        "feat_4_title": "Chống cắt luồng truyền dài",

        "feat_4_desc": "Độc quyền hỗ trợ tiếp tục truyền luồng dữ liệu bị ngắt nửa chừng.",

        "feat_5_title": "Triển khai tệp đơn siêu nhẹ",

        "feat_5_desc": "Yêu cầu tài nguyên tối thiểu, thích hợp cho các dịch vụ PaaS và Docker.",

        "feat_6_title": "Hỗ trợ giao diện phản hồi tốt",

        "feat_6_desc": "Giao diện bảng điều khiển đẹp mắt, tương thích hoàn toàn các thiết bị di động.",

        "about_support_title": "Nhóm giao lưu kỹ thuật chính thức",

        "about_support_desc": "Chào mừng tham gia nhóm GitHub của chúng tôi để cùng trao đổi và gửi yêu cầu tính năng:",

        "about_support_cta": "Quét mã QR để vào nhóm",

        "about_feedback_title": "Kênh liên hệ và phản hồi",

        "about_feedback_desc": "Nếu phát hiện bất kỳ lỗi nào hoặc có đề xuất thiết kế, vui lòng gửi Issues trên kho chứa GitHub. Rất hoan nghênh các đóng góp PR!",

        "auth_fail_relogin": "Lỗi xác thực, vui lòng đăng nhập lại",

        "check_update_info": "Đang kiểm tra cập nhật...",

        "update_success": "Kiểm tra thành công! Đã là phiên bản mới nhất.",

        "load_cred_stats": "Đã tải thống kê sử dụng của {count} tệp",

        "net_error": "Lỗi kết nối mạng: {msg}",

        "confirm_delete_cred": "Bạn có chắc chắn muốn xóa tệp chứng chỉ này không?\\n{filename}",

        "save_config_success": "Lưu cấu hình toàn cục thành công!",

        "load_config_success": "Tải dữ liệu cấu hình thành công!",

        "log_connected": "Đã thiết lập thành công kết nối luồng nhật ký.",

        "log_disconnected": "Đã ngắt kết nối luồng nhật ký.",

        "select_at_least_one": "Vui lòng chọn ít nhất một chứng chỉ để thao tác!",

        "confirm_batch_action": "Xác nhận thực hiện thao tác hàng loạt {action} trên {count} chứng chỉ đã chọn?",

        "batch_action_success": "Thực hiện thao tác hàng loạt {action} thành công!",

        "input_password_prompt": "Vui lòng nhập mật khẩu truy cập!",

        "login_success": "Đăng nhập thành công!",

        "login_failed": "Đăng nhập thất bại! Sai mật khẩu.",

        "net_error_prefix": "Lỗi kết nối mạng: ",

        "action_success_prefix": "Thao tác thành công: ",

        "action_fail_prefix": "Thao tác thất bại: ",

        "upload_fail_prefix": "Tải lên thất bại: ",

        "check_update_fail_prefix": "Kiểm tra cập nhật thất bại: ",

        "pagination_prev": "Trang trước",

        "pagination_next": "Trang sau",

        "pagination_info": "Trang {page} / {total} (Hiển thị {start}-{end} trên tổng số {count} mục)",

        "code_assist_oauth_auth_title": "Xác thực Code Assist OAuth",

        "oauth_guide_2_fail_suffix": ", đây là bình thường;",

        "oauth_paste_url": "Dán toàn bộ URL xuống dưới:",

        "ag_auth_title": "Xác thực Omni",

        "ag_guide_2_fail_suffix": ", quay lại bảng điều khiển này;",

        "upload_file_or_zip": "tệp hoặc lưu trữ ZIP",

        "click_to_copy": "Nhấp để sao chép",

        "support_link_label": "Mã QR nhóm GitHub",

        "enable_only": "Chỉ kích hoạt",

        "disable_only": "Chỉ vô hiệu hóa",

        "click_to_open_link": "Nhấp để mở liên kết",

        "right_click_to_copy_link": "Nhấp chuột phải để sao chép liên kết",

        "status_disabled": "Đã vô hiệu hóa",

        "status_enabled": "Đã kích hoạt",

        "preview_supported_title": "Chứng chỉ này hỗ trợ các mô hình Preview",

        "preview_not_supported_title": "Chứng chỉ này không hỗ trợ các mô hình Preview",

        "tier_badge_title": "Cấp độ chứng chỉ",

        "credit_enabled_title": "Chế độ Credit hiện đang được kích hoạt",

        "credit_disabled_title": "Chế độ Credit hiện đang bị vô hiệu hóa",

        "other_models_title": "Các mô hình khác",

        "btn_view_content": "Xem nội dung",

        "btn_view_email": "Xem Email",

        "btn_view_quota": "Xem Hạn mức",

        "btn_view_quota_title": "Xem thông tin hạn mức sử dụng của chứng chỉ này",

        "btn_disable_credit": "Tắt Credit",

        "btn_disable_credit_title": "Tắt chế độ tích điểm cho chứng chỉ này",

        "btn_enable_credit": "Bật Credit",

        "btn_enable_credit_title": "Bật chế độ tích điểm cho chứng chỉ này",

        "btn_setup_preview": "Cài đặt Preview",

        "btn_setup_preview_title": "Cấu hình kênh Preview, kích hoạt tính năng thử nghiệm",

        "btn_verify_id": "Kiểm tra",

        "btn_verify_id_title": "Lấy lại Project ID, có thể khôi phục từ lỗi 403",

        "btn_message_test": "Thử tin nhắn",

        "btn_message_test_title": "Kiểm tra xem chứng chỉ hoạt động bình thường không",

        "btn_view_errors": "Xem lỗi",

        "btn_view_errors_title": "Xem thông tin báo lỗi chi tiết cho chứng chỉ này",

        "email_not_fetched": "Chưa lấy Email",

        "click_view_content_to_load": "Nhấp nút 'Xem nội dung' để tải chi tiết tệp...",

        "click_view_errors_to_load": "Nhấp nút 'Xem lỗi' để tải tin nhắn lỗi...",

        "click_view_quota_to_load": "Nhấp nút 'Xem hạn mức' để tải hạn mức chi tiết...",

        "status_loading_file_content": "Đang tải nội dung tệp...",

        "status_test_failed": "❌ Thử nghiệm thất bại - {error}",

        "remaining_label": "Còn lại",

        "credits_label": "Tín dụng",

        "all": "Tất cả",

        "omni_mode_enabled_streamtono": "Chế độ Omni đã bật chuyển đổi phản hồi từ dạng stream sang non-stream",

        "test_successful": "✅ Kiểm thử thành công!",

        "oauth_interaction_guide": "Hướng dẫn tương tác OAuth:",

        "error_code": "Mã lỗi:",

        "no_logs_at_appstatecurrentlogfilter": "Hiện không có bản ghi nhật ký cấp độ {AppState_currentLogFilter}...",

        "credential_file_name": "Tên tệp chứng thực",

        "nfailed_step_step": "\\nBước thất bại: {step}",

        "batch_verification_completed_succes": "⚠️ Hoàn tất kiểm tra hàng loạt: {successCount}/{selectedFiles_length} thành công, {failCount} thất bại",

        "currently_disabled": "Hiện đang bị vô hiệu hóa",

        "omni_authentication_successf": "✅ Xác thực Omni thành công! Tệp đã lưu tại: {path}",

        "loaded_usage_statistics_for_aggdata": "Đã tải thống kê sử dụng cho {aggData_total_files____Object_keys_AppState_usageStatsData__length} tệp",

        "upload_failed_connection_interrupte": "Tải lên thất bại: Kết nối bị gián đoạn - Nguyên nhân có thể: Quá nhiều tệp ({this_selectedFiles_length}) hoặc mạng không ổn định. Khuyến nghị tải lên theo từng đợt.",

        "please_select_the_omni_crede": "Vui lòng chọn chứng thực Omni cần kiểm tra trước",

        "downloaded_file_filename": "Đã tải xuống tệp: {filename}",

        "oneclick_credential_deduplication": "Khử trùng lặp chứng thực một lần nhấn",

        "message_test": "Kiểm tra tin nhắn",

        "div_styletextalign_center_padding_2": "<div style=\"text-align: center; padding: 20px; color: #999;\">\n\n                                <div style=\"font-size: 48px; margin-bottom: 10px;\">📊</div>\n\n                                <div>Chưa có thông tin hạn mức</div>\n\n                            </div>",

        "omni_authentication_link": "Liên kết xác thực Omni:",

        "authentication_steps": "Các bước xác thực:",

        "fetching_authentication_link": "Đang lấy liên kết xác thực...",

        "upload_failed_request_timeout_proce": "Tải lên thất bại: Yêu cầu hết thời gian - Thời gian xử lý quá lâu, vui lòng giảm số lượng tệp hoặc kiểm tra kết nối mạng.",

        "manual_project_id_specification_req": "Cần chỉ định ID dự án thủ công. Vui lòng nhập ID dự án Google Cloud trong tùy chọn nâng cao và thử lại.",

        "resource_manager_api_endpoint": "Điểm cuối API Trình quản lý tài nguyên:",

        "intelligently_capture_and_automatic": "Tự động bắt và ghi URL nhịp tim duy trì trạng thái hiện tại",

        "a_hrefhref_target_blank_relnoopener": "<a href=\"{href}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"message-link\" onclick=\"event.stopPropagation()\" title=\"Nhấp để mở liên kết\\nChuột phải để sao chép liên kết\">{url}</a>",

        "this_is_not_a_valid_callback_url_pl": "❌ Đây không phải là URL callback hợp lệ! Vui lòng đảm bảo:\\n1. Đã hoàn tất cấp quyền Google OAuth\\n2. Đã sao chép đầy đủ URL từ thanh địa chỉ trình duyệt\\n3. URL chứa tham số code và state",

        "file_filename_format_is_not_support": "Định dạng tệp {file_name} không được hỗ trợ; chỉ chấp nhận tệp JSON và ZIP.",

        "the_following_configurations_have_t": ", các cấu hình sau đã có hiệu lực ngay lập tức: {list}",

        "click_the_link_above_to_proceed_wit": "Nhấp vào liên kết trên để tiến hành cấp quyền Google OAuth;",

        "unable_to_determine_if_updates_are": "Không thể xác định có bản cập nhật mới không",

        "please_select_the_credentials_to_ve": "❌ Vui lòng chọn chứng thực cần kiểm tra trước",

        "downloaded_file_name": "Đã tải xuống tệp: {name}",

        "please_obtain_the_omni_authe": "Vui lòng lấy liên kết xác thực Omni và hoàn tất cấp quyền trước",

        "refresh_credential_list": "Làm mới danh sách chứng thực",

        "all_credential_files_have_been_down": "Đã tải xuống tất cả các tệp chứng thực",

        "preview_channel_configuration_succe": "✅ Cấu hình kênh Preview thành công!\\n\\nTệp: {filename}\\n\\n{data_message}\\n\\nSetting ID: {data_setting_id_____N_A}\\nBinding ID: {data_binding_id_____N_A}",

        "all_verifications_successful_verifi": "✅ Kiểm tra thành công tất cả! Đã kiểm tra {successCount}/{selectedFiles_length} chứng thực Omni",

        "are_you_sure_you_want_to_batch_veri": "Bạn có chắc chắn muốn kiểm tra hàng loạt ID Dự án cho {selectedFiles_length} chứng thực Omni không?\\n\\nCác yêu cầu sẽ chạy song song để tăng tốc độ.",

        "failed_to_load_usage_statistics": "Tải thống kê sử dụng thất bại",

        "failed_to_download_logs_datadetail": "Tải nhật ký thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "generating_authentication_link_usin": "Đang tạo liên kết xác thực bằng ID Dự án đã chỉ định...",

        "not_enabled": "❌ Chưa bật",

        "download_credential_files_locally": "Tải tệp chứng thực về máy",

        "average_calls_per_volume": "Trung bình yêu cầu trên mỗi tài khoản",

        "failed_to_get_authentication_link_e": "Lấy liên kết xác thực thất bại: {error}",

        "successfully_retrieved_email_dataus": "Đã lấy thành công email: {data_user_email}",

        "code_assist_oauth_authentication": "Xác thực Code Assist OAuth",

        "failed_to_create_websocket_connecti": "Tạo kết nối WebSocket thất bại:",

        "omni_batch_verification_comp": "Hoàn tất kiểm tra Omni hàng loạt",

        "healthy_no_errors": "Bình thường, không có lỗi",

        "no_data_under_current_filter_condit": "Không có dữ liệu theo điều kiện lọc hiện tại",

        "successfully_retrieved_email_email": "Đã lấy thành công email: {email}",

        "get_google_oauth_authentication_lin": "Lấy liên kết xác thực Google OAuth",

        "failed_to_fetch_version_information": "Lấy thông tin phiên bản thất bại",

        "switch_to_mirror_proxy_address_with": "🚀 Chuyển sang địa chỉ proxy phản chiếu chỉ với một lần nhấn",

        "enable_automatic_retry_of_failed_re": "Bật tự động thử lại yêu cầu thất bại trên các chứng thực luân phiên khác",

        "level": "Cấp độ:",

        "please_enter_password_to_login": "Vui lòng nhập mật khẩu để đăng nhập",

        "failed_to_retrieve_credentials_from": "Lấy chứng thực từ URL callback thất bại: {error}",

        "please_select_the_credentials_to_ve_dup": "Vui lòng chọn chứng thực cần kiểm tra trước",

        "retrieved_authentication_link": "Liên kết xác thực đã lấy được:",

        "upload_failed_errordetail_errorerro": "Tải lên thất bại: ${error.detail || error.error || 'Lỗi không xác định'}",

        "are_you_sure_you_want_to_perform_on": "Bạn có chắc chắn muốn khử trùng lặp chứng thực không?\\n\\nChỉ giữ lại một chứng thực cho mỗi email, các chứng thực khác sẽ bị xóa.\\nThao tác này không thể hoàn tác!",

        "omni_file_list_pending_uploa": "Danh sách tệp Omni chờ tải lên:",

        "successfully_imported_loadedtotal_c": "✅ Đã nhập thành công {loaded}/{total} tệp chứng thực",

        "keepalive_request_interval_seconds": "Khoảng thời gian yêu cầu duy trì (giây):",

        "healthy_no_errors_dup": "Bình thường, không lỗi",

        "clear_failed_datadetail_dataerror_u": "Xóa thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "network_error_while_clearing_logs_e": "Lỗi mạng khi xóa nhật ký: {error_message}",

        "save_log_file_as": "Lưu tệp nhật ký dưới dạng...",

        "upload_failed_connection_interrupte_dup": "Tải lên thất bại: Kết nối bị gián đoạn - Nguyên nhân có thể: Quá nhiều tệp ({count}) hoặc mạng không ổn định. Khuyến nghị tải lên theo từng đợt.",

        "resultfilename_resultmessage_config": "✅ {result_filename}: ${result.message || 'Cấu hình thành công'}",

        "disable_credits": "Tắt hiển thị hạn mức",

        "please_select_the_files_to_operate": "Vui lòng chọn các tệp cần thao tác trước",

        "batch_operation_failed_error": "Thao tác hàng loạt thất bại: {error}",

        "account_risk_control_and_circuit_br": "🛡️ Chiến lược kiểm soát rủi ro tài khoản và ngắt mạch",

        "determine_account_downgrade_or_disa": "Quyết định hạ cấp hoặc vô hiệu hóa tài khoản trong vài giây dựa trên lỗi API.",

        "reset_statistics": "Đặt lại thống kê",

        "google_omni_authentication": "Xác thực Google Omni",

        "failed_to_download_package_error": "Tải xuống gói thất bại: {error}",

        "div_stylecolor_dc3545reason_escapeh": "<div style=\"color: #dc3545;\">Nguyên nhân: {escapeHtml_detail_reason}</div>",

        "test_successful_dup": "Kiểm thử thành công",

        "are_you_sure_you_want_to_refresh_us": "Bạn có chắc chắn muốn làm mới email người dùng cho tất cả chứng thực không? Việc này có thể mất một chút thời gian.",

        "filter_filter": "(Lọc: {filter})",

        "view_content": "Xem nội dung",

        "open_source_disclaimer_commercial_r": "Tuyên bố miễn trừ trách nhiệm mã nguồn mở: Nghiêm cấm mọi hình thức mua bán, thương mại hóa hoặc phân phối Hippy. Chỉ dành cho mục đích kiểm thử, nghiên cứu cá nhân và trao đổi học thuật.",

        "failed_to_save_configuration_error": "Lưu cấu hình thất bại: {error}",

        "total_credentials": "Tổng số chứng thực",

        "contact_and_feedback_channels": "Kênh liên hệ và phản hồi",

        "supports_json_credentials_or_zip_ar": "Hỗ trợ chứng thực .json hoặc tệp nén .zip",

        "revert_to_google_official_address": "🔄 Khôi phục về địa chỉ Google chính thức",

        "failed_to_retrieve_omni_cred": "Lấy chứng thực Omni từ URL callback thất bại",

        "import_failed_datadetail_dataerror": "Nhập tệp thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "new_version_foundncurrent_vversionn": "Đã tìm thấy phiên bản mới!\\nHiện tại: v{version}\\nMới nhất: v{latest}\\n\\nChi tiết cập nhật: {log}",

        "network_error_msg": "Lỗi mạng: {msg}",

        "unable_to_retrieve_user_email_error": "Không thể lấy email người dùng: {error}",

        "batch_action_operation_completed_su": "Thao tác {action} hàng loạt đã thực hiện thành công!",

        "api_integration_endpoint_addresses": "Địa chỉ điểm cuối tích hợp API",

        "system_runtime_log_stream": "Luồng nhật ký hệ thống",

        "import_failed_error": "Nhập thất bại: {error}",

        "google_apis_core_endpoints": "Điểm cuối cốt lõi của Google APIs:",

        "authentication_successful_saved_fil": "Xác thực thành công! Nội dung tệp đã lưu:",

        "click_the_view_quota_button_to_load": "Nhấp vào nút \"Xem hạn mức\" để tải thông tin hạn mức...",

        "waiting_to_fetch_the_latest_system": "Đang chờ tải dữ liệu đầu ra nhật ký bảng điều khiển hệ thống mới nhất...",

        "control_panel_login_password": "Mật khẩu đăng nhập bảng điều khiển:",

        "unable_to_autodetect_project_id_ple": "Không thể tự động phát hiện Project ID. Vui lòng nhập thủ công Project ID Google Cloud của bạn:",

        "click_this_link_to_authorize_your_g": "Nhấp vào liên kết này để ủy quyền tài khoản Google",

        "email_groupemailnkeep_groupkept_fil": "Email: {group_email}\\nGiữ lại: {group_kept_file}\\nXóa: {group_deleted_files_join}\\n\\n",

        "omni_authentication_link_gen": "✅ Đã tạo liên kết xác thực Omni! Vui lòng nhấp vào liên kết để hoàn tất ủy quyền.",

        "check_successful_already_running_th": "Kiểm tra thành công! Đã là phiên bản mới nhất.",

        "switched_to_official_endpoint_confi": "✅ Đã chuyển sang cấu hình điểm cuối chính thức. Hãy nhớ nhấp vào nút \"Lưu cấu hình\" để lưu cài đặt.",

        "nplease_enter_index_1dataavailable": "\\nVui lòng nhập số thứ tự (1-{data_available_projects_length}):",

        "fetch_and_save_authentication_file": "Lấy và lưu tệp xác thực",

        "failed_to_generate_authentication_l": "❌ Tạo liên kết xác thực thất bại: {error}",

        "action": "Thao tác",

        "save_config": "Lưu cấu hình",

        "fetch_omni_credentials": "Lấy thông tin xác thực Omni",

        "failed_to_generate_authentication_l_dup": "Tạo liên kết xác thực thất bại",

        "retry_using_the_selected_project": "Thử lại bằng dự án đã chọn...",

        "div_styletextalign_center_padding_2_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                        <div style=\"font-weight: bold; margin-bottom: 5px;\">Lỗi mạng</div>\n\n                        <div style=\"font-size: 13px; color: #666;\">{error_message}</div>\n\n                    </div>",

        "credential_available": "Thông tin xác thực hợp lệ",

        "google_omni_authentication_m": "Chế độ xác thực Google Omni",

        "zip_archive": "(Tệp nén ZIP)",

        "are_you_sure_you_want_to_delete_fil": "Bạn có chắc chắn muốn xóa {filename} không?",

        "page_thiscurrentpage_of_totalpages": "Trang {this_currentPage} / {totalPages} (Hiển thị {startItem}-{endItem}, Tổng số {this_totalCount})",

        "failed_to_clear_logs_datadetail_dat": "Xóa nhật ký thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "please_select_the_credentials_to_co": "Vui lòng chọn thông tin xác thực để cấu hình Preview trước",

        "websocket_connected": "WebSocket đã kết nối",

        "enable_autoban_for_credentials_on_s": "Kích hoạt Auto-Ban (tự động chặn) cho thông tin xác thực khi gặp mã lỗi cụ thể",

        "preview_channel_configuration_faile": "❌ Cấu hình kênh Preview thất bại\\n\\nTệp: {filename}\\n\\n{errorMsg}",

        "autobacksource_failed_use_the_quick": "Không thể tự động quay lại nguồn? Sử dụng kênh callback nhanh",

        "operation_failed_error": "Thao tác thất bại: {error}",

        "please_fetch_the_authentication_lin": "Vui lòng lấy liên kết xác thực và hoàn tất ủy quyền trước",

        "bidirectional_native_format_convers": "Chuyển đổi hai chiều định dạng gốc",

        "oneclick_deduplication_failed_error": "Khử trùng lặp thất bại: {error}",

        "disable": "Vô hiệu hóa",

        "click_this_link_to_authorize_antigr": "Nhấp vào liên kết này để ủy quyền chế độ Omni",

        "deduplication_network_error_errorme": "Lỗi mạng khi khử trùng lặp: {error_message}",

        "after_successful_authorization_the": "Sau khi ủy quyền thành công, trình duyệt sẽ tự động chuyển hướng và báo lỗi không thể kết nối tới localhost:11451, đây là hiện tượng bình thường;",

        "failed_to_get_environment_variable": "Lấy trạng thái biến môi trường thất bại: {error}",

        "max_antitruncation_resume_attempts": "Số lần thử lại tối đa để chống ngắt kết nối:",

        "log_connection_channel_established": "Đã thiết lập kênh kết nối nhật ký thành công.",

        "test_failednfile_filenamen": "❌ Kiểm tra thất bại\\nTệp: {filename}\\n",

        "global_configuration_saved_successf": "Lưu cấu hình toàn cục thành công!",

        "executing_batch_actionlabel_operati": "Đang thực hiện thao tác hàng loạt {actionLabel}...",

        "monitor_credential_count": "Giám sát số lượng thông tin xác thực",

        "switched_to_official_endpoint_confi_dup": "Đã chuyển sang cấu hình điểm cuối chính thức. Hãy nhớ nhấp vào nút 'Lưu cấu hình' để lưu cài đặt.",

        "local_credential_storage_absolute_p": "Đường dẫn tuyệt đối của nơi lưu trữ thông tin xác thực cục bộ:",

        "click_to_open_linknrightclick_to_co": "Nhấp để mở liên kết\\nChuột phải để sao chép liên kết",

        "upload_failed_http_xhrstatus": "Tải lên thất bại: HTTP {xhr_status}",

        "verification_successful": "Kiểm tra thành công",

        "force_enable_compatibility_mode_mer": "Buộc kích hoạt chế độ tương thích (hợp nhất tin nhắn giao thức System vào User)",

        "clear_buffer_logs": "Xóa nhật ký đệm",

        "div_stylefontsize_12px_color_666_ma": "<div style=\"font-size: 12px; color: #666; margin-bottom: 5px;\">Chi tiết:</div>",

        "error_dataerror_failed_to_get_authe": "❌ Lỗi: ${data.error || 'Lấy tệp xác thực thất bại'}",

        "select_all": "Chọn tất cả",

        "if_this_field_is_configured_it_will": "Nếu cấu hình trường này, nó sẽ ghi đè mật khẩu API và bảng điều khiển. Khuyến nghị nên để trống.",

        "autologin_successful": "Đăng nhập tự động thành công",

        "failed_to_save_config_datadetail_da": "Lưu cấu hình thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "batch_operation_completed_processed": "Hoàn tất thao tác hàng loạt: Đã xử lý thành công {success}/{total} tệp.",

        "tip_leave_blank_for_firsttime_use_t": "Gợi ý: Để trống trong lần đầu sử dụng, hệ thống sẽ tự động phân bổ và phát hiện.",

        "configuration_failed": "Cấu hình thất bại",

        "successfully_imported_dataloaded_co": "✅ Nhập thành công {data_loaded_count}/{data_total_count} tệp xác thực",

        "switched_to_mirror_url_configuratio": "✅ Đã chuyển sang cấu hình URL gương (mirror). Hãy nhớ nhấp vào nút \"Lưu cấu hình\" để lưu cài đặt.",

        "zip_files_will_automatically_extrac": "Tệp ZIP sẽ tự động giải nén tất cả các tệp xác thực JSON.",

        "adjust_system_proxy_endpoint_addres": "Điều chỉnh proxy hệ thống, địa chỉ điểm cuối, chính sách bảo mật và các tham số thử lại tần suất cao. Hầu hết các mục sẽ có hiệu lực ngay lập tức sau khi lưu.",

        "loaded_count_type_credential_files": "Đã tải {count} tệp xác thực {type}",

        "log_stream_connection_error": "Lỗi kết nối luồng nhật ký:",

        "quota_information_loaded_successful": "✅ Tải thông tin hạn mức thành công",

        "failed_to_fetch_authentication_link": "Lấy liên kết xác thực thất bại",

        "return_directly_to_the_current_cont": "Quay lại trực tiếp trang bảng điều khiển hiện tại, nhấp vào nút \"Lấy và lưu tệp xác thực\" bên dưới để hoàn tất việc kết nối;",

        "retry_interval_seconds": "Khoảng thời gian thử lại (giây):",

        "autoban_circuit_breaker": "Cầu chì bảo vệ Auto-Ban",

        "usage_statistics_loaded_for_count_f": "Đã tải thống kê sử dụng của {count} tệp",

        "operation_successful": "Thao tác thành công:",

        "download": "Tải xuống",

        "new_version_available": "Có phiên bản mới",

        "openai_compatibility": "Tương thích OpenAI:",

        "verification_successfulnfile_filena": "✅ Kiểm tra thành công!\\nTệp: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "div_styletextalign_center_padding_2_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                            <div style=\"font-weight: bold; margin-bottom: 5px;\">Lấy thông tin hạn mức thất bại</div>\n\n                            <div style=\"font-size: 13px; color: #666;\">{errorMsg}</div>\n\n                        </div>",

        "delete": "Xóa",

        "div_styletextalign_center_padding_2_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                            <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                            <div style=\"font-weight: bold;\">Tải thất bại</div>\n\n                            <div style=\"font-size: 12px; margin-top: 8px;\">{errorMsg}</div>\n\n                        </div>",

        "file_format_of_name_not_supported_o": "Định dạng tệp {name} không được hỗ trợ; chỉ hỗ trợ các tệp JSON và ZIP",

        "project_info": "Thông tin dự án",

        "the_following_configurations_have_t_dup": ", các cấu hình sau đã có hiệu lực ngay lập tức: {data_hot_updated_join}",

        "unable_to_fetch_user_email": "Không thể lấy email người dùng",

        "failed_to_fetch_credentials_from_ca": "Lấy thông tin xác thực từ URL callback thất bại",

        "advanced_settings_specify_google_cl": "Cài đặt nâng cao: Chỉ định Google Cloud Project ID (Tùy chọn)",

        "starting_batch_project_id_verificat": "Đang khởi động tác vụ xác minh Project ID hàng loạt...",

        "open_github_issues": "Quét mã QR GitHub để tham gia nhóm",

        "when_google_apis_return_these_error": "Khi các yêu cầu API đến Google trả về các mã lỗi này, hệ thống sẽ tự động vô hiệu hóa tài khoản. Khuyến nghị cấu hình mã 403 cho cơ chế ngắt mạch.",

        "failed_to_fetch_error_message": "Lấy thông tin báo lỗi thất bại",

        "error_dataerror_failed_to_generate": "❌ Lỗi: ${data.error || 'Tạo liên kết xác thực thất bại'}",

        "service_network_listening_configura": "⚙️ Cấu hình lắng nghe mạng dịch vụ",

        "connecting": "Đang kết nối...",

        "credentials_fetched_successfully_fr": "Lấy thông tin xác thực từ URL callback thành công!",

        "click_the_link_above_sign_in_to_you": "Nhấp vào liên kết phía trên, đăng nhập tài khoản Google của bạn trong thẻ trình duyệt mới và cấp quyền truy cập.",

        "omni_credential_file_managem": "Quản lý tệp xác thực Omni",

        "failed_to_configure_preview_channel": "Cấu hình kênh Preview thất bại: {error_message}",

        "authentication_successful_project_i": "✅ Xác thực thành công! ID dự án đã được tự động phát hiện là: {id}, tệp đã lưu tại: {path}",

        "please_enter_a_valid_url_starting_w": "Vui lòng nhập URL hợp lệ (bắt đầu bằng http:// hoặc https://)",

        "successfully_updated_preview_channe": "Đã cập nhật thành công trạng thái kênh Preview cho {count} tệp xác thực",

        "pending_code_assist_file_upload_list": "Danh sách tệp Code Assist chờ tải lên:",

        "exclusive_industrywide_support_for": "Tính năng độc quyền toàn thị trường hỗ trợ truyền tải tiếp nối (resumable) dạng luồng.",

        "configuration_failed_for_all_failed": "❌ Cấu hình thất bại toàn bộ! Thất bại {failCount}/{selectedFiles_length} tệp xác thực",

        "omni_batch_verification_comp_dup": "Hoàn tất kiểm tra hàng loạt Omni!\\n\\nThành công: {successCount}\\nThất bại: {failCount}\\nTổng: {selectedFiles_length}\\n\\nKết quả chi tiết:\\n{resultMessages_join___n}",

        "enabled": "✅ Đã bật",

        "display_and_maintain_your_code_assist_prox": "Hiển thị và duy trì các kênh proxy Code Assist của bạn, hỗ trợ kiểm tra, tải xuống, chuyển đổi trạng thái và xóa đơn lẻ hoặc hàng loạt.",

        "batch_operation_network_error_error": "Lỗi mạng khi thao tác hàng loạt: {error}",

        "retrying_with_manually_entered_proj": "Thử lại với ID dự án đã nhập thủ công...",

        "get_omni_authentication_link": "Lấy liên kết xác thực Omni",

        "json_file": "(Tệp JSON)",

        "are_you_sure_you_want_to_deduplicat": "Bạn có chắc chắn muốn xóa trùng lặp tệp xác thực Omni không?\\n\\nChỉ giữ lại một tệp xác thực cho mỗi email, các tệp còn lại sẽ bị xóa.\\nHành động này không thể hoàn tác!",

        "display_and_maintain_your_antigravi": "Hiển thị và quản lý các tài khoản Omni cùng hạn mức yêu cầu tương ứng của bạn.",

        "supports_json_files_or_zip_archives": "Hỗ trợ tệp .json hoặc gói nén .zip",

        "code_assist_api_endpoint": "Điểm cuối (Endpoint) Code Assist API:",

        "failed_to_fetch_error_message_error": "❌ Lấy thông báo lỗi thất bại: {errorMsg}",

        "failed_to_load_file_content": "Tải nội dung tệp thất bại:",

        "div_stylebackground_white_borderlef": "<div style=\"background: var(--bg); border: 1px solid var(--border); border-left: 4px solid {percentageColor}; border-radius: var(--radius); padding: 8px 10px;\">\n\n                                    <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;\">\n\n                                        <div style=\"font-weight: bold; color: #333; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; margin-right: 8px;\" title=\"{modelName} - còn lại {remainingPercentage}% - {resetTime}\">\n\n                                            {modelName}\n\n                                        </div>\n\n                                        <div style=\"font-size: 13px; font-weight: bold; color: {percentageColor}; white-space: nowrap;\">\n\n                                            {remainingPercentage}%\n\n                                        </div>\n\n                                    </div>\n\n                                    <div style=\"width: 100%; height: 8px; background-color: var(--bg-subtle); border-radius: var(--radius); overflow: hidden; margin-bottom: 4px;\">\n\n                                        <div style=\"width: {usedPercentage}%; height: 100%; background-color: {percentageColor}; transition: none;\"></div>\n\n                                    </div>\n\n                                    <div style=\"font-size: 10px; color: #666; text-align: right;\">\n\n                                        {resetTime______N_A___________resetTime}\n\n                                    </div>\n\n                                </div>",

        "failed_to_check_for_updates_error": "Kiểm tra cập nhật thất bại: {error}",

        "preview_channel_configuration_succe_dup": "Cấu hình kênh Preview thành công",

        "clear_selection_list": "Xóa danh sách lựa chọn",

        "logs_cleared_waiting_for_new_logs": "Nhật ký đã xóa, chờ nhật ký mới...",

        "running_normally": "Đang chạy bình thường",

        "lightweight_singlefile_deployment": "Triển khai tệp đơn nhẹ",

        "button_to_save_settings_success_fun": "nút lưu cài đặt', 'success');\n\n    }\n\n}\n\n\n\nfunction restoreOfficialUrls() {\n\n    if (confirm('Bạn có chắc chắn muốn đặt lại tất cả các endpoint về địa chỉ chính thức không?')) {\n\n        for (const [fieldId, url] of Object.entries(officialUrls)) {\n\n            const field = document.getElementById(fieldId);\n\n            if (field && !field.disabled) field.value = url;\n\n        }\n\n        showStatus('✅ Đã chuyển sang cấu hình endpoint chính thức, nhớ nhấp",

        "test_successfulnfile_filenamenstatu": "✅ Kiểm tra thành công!\\nTệp: {filename}\\nTrạng thái: ${data.message || 'Tệp xác thực Omni hợp lệ'} ({data_status_code____200})",

        "full_version_datafull_hashncommit_m": "Phiên bản đầy đủ: {data_full_hash}\\nThông báo commit: {data_message}\\nThời gian commit: {data_date}",

        "importing_credentials_from_environm": "Đang nhập tệp xác thực từ biến môi trường...",

        "server_bound_host_ip_address": "Địa chỉ IP Host ràng buộc máy chủ:",

        "verification_failed_for_all_failed": "❌ Kiểm tra thất bại toàn bộ! Thất bại {failCount}/{selectedFiles_length} tệp xác thực Omni",

        "github_issues_support": "Nhóm hỗ trợ kỹ thuật GitHub chính thức",

        "download_failed_name": "Tải xuống thất bại: {name}",

        "login_successful": "Đăng nhập thành công!",

        "network_error_error": "Lỗi mạng: {error}",

        "batch_verification_completennsucces": "Hoàn tất kiểm tra hàng loạt!\\n\\nThành công: {successCount}\\nThất bại: {failCount}\\nTổng: {selectedFiles_length}\\n\\nKết quả chi tiết:\\n{resultMessages_join___n}",

        "http_error_codes_that_trigger_circu": "Mã lỗi HTTP kích hoạt ngắt mạch/khóa tạm thời (phân cách bằng dấu phẩy):",

        "upload_failed_error": "Tải lên thất bại: {error}",

        "batch_verification_complete": "Hoàn tất kiểm tra hàng loạt",

        "storage_and_proxy_settings": "📂 Cài đặt Lưu trữ và Proxy",

        "performing_batch_action_operation": "Đang thực hiện thao tác hàng loạt {action}...",

        "this_setting_may_slightly_reduce_co": "Cài đặt này có thể làm giảm nhẹ khả năng hiểu các Prompt phức tạp, nhưng giải quyết hoàn hảo lỗi trả về trống hoặc ngắt mạch luồng ở một vài ứng dụng khách bên thứ ba do thiếu system_instructions.",

        "fetching_environment_variable_statu": "Đang lấy trạng thái biến môi trường...",

        "nnerror_details_errordetail": "\\n\\nChi tiết lỗi: {errorDetail}",

        "highquality_aesthetic_panel_layout": "Bố cục bảng điều khiển tinh tế, hỗ trợ tất cả các trình duyệt hiện đại.",

        "load_failed_datadetail_dataerror_un": "Tải thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "access_password_to_protect_this_con": "Mật khẩu truy cập để bảo vệ trang bảng điều khiển này khỏi sự can thiệp trái phép.",

        "if_running_on_a_remote_vps_or_a_hea": "Nếu chạy trên VPS từ xa hoặc môi trường không có giao diện đồ họa: vui lòng mở rộng mục \"Kênh tắt không thể回源\" bên dưới để xử lý.",

        "log_file_download_successful_filena": "Tải xuống tệp nhật ký thành công: {filename}",

        "automatically_switch_to_another_rot": "Tự động chuyển sang tệp xác thực khác khi có lỗi Omni",

        "connected": "Đã kết nối",

        "brstrongavailable_projectsstrongbr": "<br><strong>Dự án khả dụng:</strong><br>",

        "div_span_classfilenamefileicon_file": "<div>\n\n                        <span class=\"file-name\">{fileIcon} {file_name}</span>\n\n                        <span class=\"file-size\">({formatFileSize_file_size}{fileType})</span>\n\n                    </div>\n\n                    <button class=\"remove-btn\" onclick=\"{type______omni_____removeOmniFile_____removeFile}({index})\">Xóa</button>",

        "passthrough_model_thinking_process": "Chuyển tiếp luồng suy nghĩ (Thinking Process) của mô hình vào phản hồi front-end",

        "log_connection_channel_disconnected": "Kênh kết nối nhật ký đã bị ngắt.",

        "parallel_verifying_selectedfileslen": "🔍 Đang kiểm tra song song {selectedFiles_length} tệp xác thực, vui lòng đợi...",

        "failed_to_retrieve_authentication_f": "❌ Lấy tệp xác thực thất bại: {error}",

        "applicable_to_the_latest_gemini_20": "Áp dụng cho các mô hình Gemini 2.0 mới nhất có khả năng suy luận. Nếu tắt, nội dung luồng suy nghĩ sẽ bị lọc bỏ để cung cấp câu trả lời trực tiếp sạch sẽ hơn.",

        "log_stream_connection_disconnected": "Kết nối luồng nhật ký bị ngắt",

        "environment_variable_status_check_c": "Kiểm tra trạng thái biến môi trường hoàn tất",

        "project_description": "Omni Gateway là bộ định tuyến AI phổ quát cho các công cụ lập trình. Hỗ trợ tự động chuyển đổi thông minh, nén token và dịch định dạng liền mạch để tối ưu hóa việc sử dụng các LLM miễn phí và trả phí.",

        "click_the_view_error_button_to_load": "Nhấp vào nút \"Xem lỗi\" để tải thông tin lỗi...",

        "loaded_datatotal_type_omni_a": "Đã tải {data_total} tệp xác thực {type______omni_____Omni}",

        "email_not_retrieved": "Chưa lấy được email",

        "tip": "Gợi ý",

        "load_failed_error": "Tải thất bại: {error}",

        "omni_credential_valid": "Tệp xác thực Omni hợp lệ",

        "in_cooldown": "Đang trong thời gian chờ (cooldown)",

        "verification_failed": "Kiểm tra thất bại",

        "gemini_native": "Gemini gốc:",

        "error_code_code": "Mã lỗi: {code}",

        "api_endpoint_proxy_setup": "🔗 Cài đặt Proxy cho điểm cuối API",

        "login_failed_incorrect_password": "Đăng nhập thất bại! Sai mật khẩu.",

        "used_for_http_authorization_bearer": "Dùng để xác thực HTTP Authorization Bearer Token khi thực hiện các yêu cầu qua proxy.",

        "enable_batch": "Bật hàng loạt",

        "failed_to_download_package_errormes": "Tải xuống gói thất bại: {error_message}",

        "batch_configuration_complete_succes": "⚠️ Hoàn tất cấu hình hàng loạt: {successCount}/{selectedFiles_length} thành công, {failCount} thất bại",

        "claude_compatible": "Tương thích Claude:",

        "verifying_omni_project_id_pl": "🔍 Đang kiểm tra ID dự án Omni, vui lòng đợi...",

        "invalid_selection_please_restart_th": "Lựa chọn không hợp lệ, vui lòng khởi động lại quá trình xác thực",

        "error_code_dup": "Mã lỗi:",

        "configuration_data_loaded_successfu": "Tải dữ liệu cấu hình thành công!",

        "leave_blank_to_attempt_automatic_de": "Để trống để thử tự động phát hiện và tạo dự án.",

        "no_usage_breakdown_statistics_avail": "Chưa có dữ liệu thống kê chi tiết sử dụng",

        "all_verifications_successful_succes": "✅ Tất cả kiểm tra thành công! Đã xác minh thành công {successCount}/{selectedFiles_length} tệp xác thực",

        "successfully_deleted_datadeleted_co": "✅ Đã xóa thành công {data_deleted_count} tệp xác thực trong biến môi trường",

        "are_you_sure_you_want_to_delete_fil_dup": "Bạn có chắc chắn muốn xóa {filename} không?",

        "verify": "Kiểm tra",

        "click_to_select_files_or_drag_and_d": "Nhấp để chọn tệp hoặc kéo thả tệp vào đây",

        "configuration_successful": "Cấu hình thành công",

        "error": "Lỗi:",

        "retrieving_credentials_from_callbac": "Đang lấy tệp xác thực từ URL phản hồi...",

        "preview_channel_configuration_faile_dup": "Cấu hình kênh Preview thất bại",

        "n_restart_notice_datarestart_notice": "\\n⚠️ Thông báo khởi động lại: {data_restart_notice}",

        "service_usage_api_status_management": "Điểm cuối quản lý trạng thái Service Usage API:",

        "failed_to_retrieve_authentication_f_dup": "Lấy tệp xác thực thất bại",

        "please_select_a_projectnnplease_ent": "Vui lòng chọn một dự án:\\n\\nVui lòng nhập số thứ tự (1-{count}):",

        "per_page": "Mỗi trang:",

        "failed_to_check_for_updates_dataerr": "Kiểm tra cập nhật thất bại: {data_error}",

        "network_error_errormessage": "Lỗi mạng: {error_message}",

        "minimal_resource_footprint_perfectl": "Chi phí tài nguyên cực thấp, tương thích hoàn hảo với các nền tảng PAAS và Docker.",

        "application_keepalive_settings": "☕ Cài đặt duy trì hoạt động ứng dụng (Keep-Alive)",

        "save_global_configuration": "Lưu cấu hình toàn cục",

        "failed_to_load_configuration_datade": "Tải cấu hình thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "uploading_and_extracting_zip_file": "Đang tải lên và giải nén tệp ZIP...",

        "are_you_sure_you_want_to_batch_veri_dup": "Bạn có chắc chắn muốn kiểm tra hàng loạt Project ID của {selectedFiles_length} tệp tin xác thực không?\\n\\nQuá trình sẽ được thực hiện song song để tăng tốc độ.",

        "refreshing_all_user_emails": "Đang làm mới tất cả email người dùng...",

        "operation_failed_datadetail_dataerr": "Thao tác thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "are_you_sure_you_want_to_delete_the": "Bạn có chắc chắn muốn xóa {selectedFiles_length} tệp đã chọn không?\\nLưu ý: Thao tác này không thể hoàn tác!",

        "new_version_foundncurrent_vdatavers": "Đã tìm thấy phiên bản mới!\\nHiện tại: v{data_version}\\nMới nhất: v{data_latest_version}\\n\\nNội dung cập nhật: ${data.latest_message || 'Không có'}",

        "div_stylecolor_007bfftype_highlight": "<div style=\"color: #007bff;\">Loại: {highlightedType}</div>",

        "failed_to_check_for_updates_errorme": "Kiểm tra cập nhật thất bại: {error_message}",

        "nerror_detailsndataerror": "\\nChi tiết lỗi:\\n{data_error}",

        "omni_authentication_successf_dup": "✅ Xác thực Omni thành công! Tệp đã được lưu tại: {data_file_path}",

        "batch_verify_project_id": "Kiểm tra hàng loạt Project ID",

        "filter_thiscurrentstatusfilter_enab": "(Bộ lọc: ${this.currentStatusFilter === 'enabled' ? 'Chỉ đã bật' : 'Chỉ đã tắt'})",

        "are_you_sure_you_want_to_configure": "Bạn có chắc chắn muốn cấu hình tất cả các endpoint thành địa chỉ chính thức không?",

        "perfect_responsive_support": "Hỗ trợ giao diện phản hồi (responsive) hoàn hảo",

        "welcome_to_join_us_to_discuss_usage": "Chào mừng bạn tham gia cùng chúng tôi để trao đổi cách chơi và gửi yêu cầu nâng cấp tính năng:",

        "successfully_deleted_count_environm": "✅ Đã xóa thành công {count} tệp tin xác thực biến môi trường",

        "monitor_realtime_request_details_an": "Giám sát thời gian thực các chi tiết yêu cầu và logic luân chuyển gửi đến Google Cloud API, giúp nhanh chóng khắc phục các sự cố về proxy mạng hoặc giới hạn lưu lượng.",

        "error_errormsg": "Lỗi: {errorMsg}",

        "unlimited": "Không giới hạn",

        "drag_and_drop_or_select_your_existi": "Kéo thả hoặc chọn tệp JSON/ZIP xác thực Code Assist hoặc Omni hiện có của bạn để tải lên máy chủ.",

        "authentication_successful_file_save": "✅ Xác thực thành công! Tệp đã được lưu tại: {data_file_path}",

        "connection_lost": "Kết nối bị ngắt",

        "batch_preview_channel_configuration": "Hoàn tất cấu hình kênh Preview hàng loạt!\\n\\nThành công: {successCount}\\nThất bại: {failCount}\\nTổng: {selectedFiles_length}\\n\\nKết quả chi tiết:\\n{resultMessages_join___n}",

        "are_you_sure_you_want_to_actionlabe": "Bạn có chắc chắn muốn {actionLabel} {selectedFiles_length} tệp tin đã chọn không?",

        "page_page_of_total_showing_startend": "Trang {page}/{total} (Hiển thị {start}-{end}, tổng số {count} mục)",

        "loading_file_content": "Đang tải nội dung tệp...",

        "generating_authentication_link": "Đang tạo liên kết xác thực...",

        "failed_to_refresh_emails": "Làm mới email thất bại",

        "preview_only": "Chỉ hỗ trợ Preview",

        "max_retries_on_failure": "Số lần thử lại tối đa khi thất bại:",

        "batch_operation_complete_successful": "Hoàn tất thao tác hàng loạt: Đã xử lý thành công {successCount}/{selectedFiles_length} tệp",

        "deduplication_detailsnn": "Chi tiết loại bỏ trùng lặp:\\n\\n",

        "synchronizing_current_system_config": "Đang đồng bộ hóa cấu hình hệ thống hiện tại với máy chủ...",

        "ip_address_to_listen_on_0000_allows": "Địa chỉ IP để lắng nghe. 0.0.0.0 cho phép truy cập công cộng. Cần khởi động lại để áp dụng thay đổi.",

        "are_you_sure_you_want_to_reset_usag": "Bạn có chắc chắn muốn đặt lại thống kê sử dụng cho {filename} không?",

        "please_select_at_least_one_credenti": "Vui lòng chọn ít nhất một thông tin xác thực để thực hiện!",

        "authentication_successful_file_save_dup": "✅ Xác thực thành công! Tệp đã được lưu tại: {path}",

        "retrieving_omni_credentials": "Đang lấy thông tin xác thực Omni từ URL phản hồi...",

        "configuring_preview_channel_please": "🔧 Đang cấu hình kênh Preview, vui lòng chờ...",

        "verification_failed_error": "Xác thực thất bại: {error}",

        "please_select_the_omni_crede_dup": "❌ Vui lòng chọn thông tin xác thực Omni cần kiểm tra trước",

        "successfully_uploaded_datauploaded": "Đã tải lên thành công {data_uploaded_count} tệp {type______omni_____Omni}",

        "dataexisting_env_files_count_files": "{data_existing_env_files_count} tệp tin",

        "waiting_for_omni_oauth_callb": "Đang chờ phản hồi (callback) OAuth từ Omni...",

        "model_protocol_compatibility_overri": "🧩 Ghi đè khả năng tương thích giao thức mô hình",

        "maximum_retries_for_resuming_stream": "Số lần tối đa hệ thống cố gắng tiếp tục truyền dữ liệu từ điểm bị ngắt khi yêu cầu mô hình có hậu tố '-流式抗截断'.",

        "successfully_uploaded_count_type_fi": "Đã tải lên thành công {count} tệp {type}",

        "failed_to_retrieve_credentials_from_dup": "Lấy thông tin xác thực từ URL phản hồi thất bại: {error_message}",

        "enable_credits": "Bật tính năng Tín dụng (Credit)",

        "code_assist_creds__environment_variable_no": "Không tìm thấy biến môi trường CODE_ASSIST_CREDS_*",

        "autoscroll_to_bottom": "Tự động cuộn xuống dưới cùng",

        "please_select_the_credential_to_con": "❌ Vui lòng chọn thông tin xác thực cần cấu hình Preview trước",

        "please_select_the_file_to_upload_fi": "Vui lòng chọn tệp để tải lên trước",

        "failed_to_check_for_updates": "Kiểm tra cập nhật thất bại:",

        "enabled_dup": "Đã bật",

        "retrieve_the_latest_google_cloud_sd": "Lấy thông tin xác thực gốc Omni cho phiên bản mới nhất của Google Cloud SDK.",

        "global_upstream_proxy_url": "URL proxy trung chuyển toàn cục:",

        "processing_credential_deduplication": "Đang xử lý loại bỏ trùng lặp thông tin xác thực...",

        "24h_total_calls": "Tổng số yêu cầu trong 24h",

        "status": "Trạng thái:",

        "maximum_retry_limit_for_resuming_st": "Số lần tối đa hệ thống sẽ thử tiếp tục truyền dữ liệu khi phản hồi từ mô hình bị ngắt quãng đột ngột (đối với model có hậu tố '-流式抗截断').",

        "omni_verification_successful": "✅ Kiểm tra Omni thành công!\\n\\nTệp: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "all_configured_successfully_preview": "✅ Cấu hình thành công tất cả! Đã cấu hình kênh Preview cho {successCount}/{selectedFiles_length} tệp tin xác thực",

        "enable_credit": "Bật tính năng Credit",

        "24hour_call_breakdown_statistics": "Thống kê chi tiết yêu cầu trong 24 giờ",

        "are_you_sure_you_want_to_refresh_us_dup": "Bạn có chắc chắn muốn làm mới email người dùng cho tất cả thông tin xác thực Omni không? Việc này có thể mất một chút thời gian.",

        "unable_to_retrieve_version_informat": "Không thể lấy thông tin phiên bản",

        "batch_disable_dup": "Vô hiệu hóa hàng loạt",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #dc3545;\">\n\n                        <div style=\"font-size: 48px; margin-bottom: 10px;\">❌</div>\n\n                        <div style=\"font-weight: bold;\">Lỗi mạng</div>\n\n                        <div style=\"font-size: 12px; margin-top: 8px;\">{error_message}</div>\n\n                    </div>",

        "upstream_network_proxy_required_for": "Proxy trung chuyển mạng cần thiết để truy cập các API của Google từ cục bộ. Để trống nếu muốn kết nối trực tiếp.",

        "if_you_find_any_bugs_or_have_design": "Nếu bạn phát hiện lỗi hoặc có đề xuất thiết kế, vui lòng mở Issues trên kho GitHub của chúng tôi. Chúng tôi cũng rất hoan nghênh các PR để làm phong phú thêm hệ sinh thái.",

        "view_error": "Xem lỗi",

        "verification_failednnerrormsg": "❌ Kiểm tra thất bại\\n\\n{errorMsg}",

        "failed_to_retrieve_omni_cred_dup": "Lấy thông tin xác thực Omni từ URL phản hồi thất bại: {error_message}",

        "code_assist_credential_batch_upload": "Tải lên hàng loạt thông tin xác thực Code Assist",

        "checking_for_updates": "Đang kiểm tra cập nhật...",

        "unknown_version": "Phiên bản không xác định",

        "oneclick_credential_deduplication_i": "Đang thực hiện loại bỏ trùng lặp thông tin xác thực chỉ với một cú nhấp...",

        "operation_successful_action": "Thao tác thành công: {action}",

        "download_failed_filename": "Tải xuống thất bại: {filename}",

        "retrieve_and_save_omni_crede": "Lấy và lưu thông tin xác thực Omni",

        "ag_credentials": "Thông tin xác thực AG",

        "view_quota": "Xem hạn mức",

        "logged_out": "Đã đăng xuất",

        "are_you_sure_you_want_to_reset_usag_dup": "Bạn có chắc chắn muốn đặt lại thống kê sử dụng cho tất cả các tệp không? Thao tác này không thể hoàn tác!",

        "configuration_successfulnfile_filen": "✅ Cấu hình thành công!\\nTệp: {filename}\\nTrạng thái: {data_message}",

        "batch_delete_dup": "Xóa hàng loạt",

        "modelname_remainingpercentage_remai": "{modelName} - Còn lại {remainingPercentage}% - {resetTime}",

        "configuration_management": "Quản lý cấu hình",

        "retrieving_user_emails": "Đang lấy email người dùng...",

        "set_preview": "Cài đặt Preview",

        "authentication_successful_project_i_dup": "✅ Xác thực thành công! ID dự án được tự động phát hiện là: {data_credentials_project_id}, tệp đã lưu tại: {data_file_path}",

        "automatic_quota_avoidance_rotation": "Tự động luân chuyển tránh hạn mức",

        "reload_configuration_data": "Tải lại dữ liệu cấu hình",

        "key_technical_highlights": "Điểm nổi bật về kỹ thuật",

        "clear_failed_error": "Xóa thất bại: {error}",

        "generating_omni_authenticati": "Đang tạo liên kết xác thực Omni...",

        "upload_failed_errormessage": "Tải lên thất bại: {error_message}",

        "failed_to_update_preview_status_in": "Cập nhật hàng loạt trạng thái Preview thất bại: {error}",

        "downloaded_filename": "✅ Đã tải xuống: {filename}",

        "bulk_upload_local_credentials": "Tải lên hàng loạt thông tin xác thực cục bộ",

        "div_stylebackground_lineargradient1": "<div style=\"background: var(--bg-subtle); color: var(--text-primary); padding: 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 15px;\">\n\n                                <h4 style=\"margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;\">\n\n                                    <span style=\"font-size: 20px;\">📊</span>\n\n                                    <span>Chi tiết thông tin hạn mức</span>\n\n                                </h4>\n\n                                <div style=\"font-size: 12px; opacity: 0.9; margin-top: 5px;\">Tệp: {filename}</div>\n\n                            </div>\n\n                            <div style=\"display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;\">",

        "automatic_retry_reconnection_mechan": "🔁 Cơ chế tự động thử lại và kết nối lại",

        "download_all_credentials_as_archive": "Tải xuống tất cả thông tin xác thực (dạng nén)",

        "waiting_for_oauth_callback": "Đang chờ phản hồi OAuth...",

        "local_storage_directory_for_uploade": "Thư mục lưu trữ cục bộ cho các tệp JSON đã tải lên và xác thực.",

        "bulk_preview_channel_configuration": "Hoàn thành cấu hình hàng loạt kênh Preview",

        "disable_credit": "Tắt Credit",

        "no_logs_yet": "Chưa có nhật ký...",

        "already_up_to_date": "Đã là phiên bản mới nhất!",

        "test_successfulnfile_filenamenstatu_dup": "✅ Kiểm tra thành công!\\nTệp: {filename}\\nTrạng thái: ${data.message || 'Thông tin xác thực khả dụng'} ({data_status_code____200})",

        "deduplication_complete_deleted_data": "Hoàn tất khử trùng lặp: Đã xóa {data_deleted_count} thông tin xác thực trùng lặp, giữ lại {data_kept_count} thông tin ({data_unique_emails_count} email duy nhất)",

        "are_you_sure_you_want_to_perform_th": "Bạn có chắc chắn muốn thực hiện thao tác hàng loạt {action} trên {count} thông tin xác thực đã chọn?",

        "bulk_operation_failed_datadetail_da": "Thao tác hàng loạt thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "ncredit_datacredit_amount": "\\nTín dụng: {data_credit_amount}",

        "authentication_failed_please_log_in": "Xác thực thất bại, vui lòng đăng nhập lại",

        "code_assist_credential_file_management": "Quản lý tệp thông tin xác thực Code Assist",

        "failed_to_retrieve_version_informat": "Lấy thông tin phiên bản thất bại:",

        "filter_level": "Cấp độ lọc:",

        "failed_to_get_email_errormessage": "Lấy email thất bại: {error_message}",

        "suitable_for_cloud_servervps_deploy": "Phù hợp cho môi trường triển khai trên Cloud/VPS, Docker hoặc các trường hợp cổng 11451 bị tường lửa chặn.",

        "connection_error": "Lỗi kết nối",

        "omni_credentials_successfull": "Lấy thông tin xác thực Omni từ URL callback thành công!",

        "are_you_sure_you_want_to_configure_dup": "Bạn có chắc chắn muốn cấu hình tất cả các điểm cuối (endpoints) thành URL mirror?",

        "sever_log_channel": "Ngắt kênh nhật ký",

        "configuration_loaded_successfully": "Tải cấu hình thành công",

        "unable_to_load_file_content": "Không thể tải nội dung tệp:",

        "bulk_enable_credit": "Bật Credit hàng loạt",

        "live_connection_status": "Trạng thái kết nối thời gian thực:",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\">📊 Đang tải thông tin hạn mức...</div>",

        "connection_failed": "Kết nối thất bại",

        "oneclick_deduplication_complete_del": "Khử trùng lặp một chạm hoàn tất! Đã xóa {deleted} tệp trùng lặp, giữ lại {kept} tệp tài khoản duy nhất.",

        "verifying_project_id_please_wait": "🔍 Đang kiểm tra Project ID, vui lòng chờ...",

        "email_refresh_network_error_errorme": "Lỗi mạng khi làm mới email: {error_message}",

        "waiting_for_oauth_callback_this_may": "Đang chờ phản hồi OAuth, việc này có thể mất một chút thời gian...",

        "project_id_required_to_complete_aut": "Cần ID dự án để hoàn tất xác thực, vui lòng bắt đầu lại và nhập ID dự án chính xác",

        "error_code_datastatus_code_response": "Mã lỗi: {data_status_code____response_status}",

        "cooling_down": "Đang làm mát (cooldown):",

        "start_bulk_upload": "Bắt đầu tải lên hàng loạt",

        "attempting_to_autodetect_project_id": "Đang cố gắng tự động phát hiện ID dự án, đang tạo liên kết xác thực...",

        "check_for_updates_failed_dataupdate": "Kiểm tra cập nhật thất bại: ${data.update_error || 'Lỗi không xác định'}",

        "upload_failed": "Tải lên thất bại:",

        "all_verifications_failed_failed_fai": "❌ Tất cả kiểm tra đều thất bại! {failCount}/{selectedFiles_length} thông tin xác thực bị lỗi",

        "upload_failed_server_response_forma": "Tải lên thất bại: Định dạng phản hồi của máy chủ bị lỗi",

        "deduplication_failed": "Khử trùng lặp thất bại",

        "credit_resultcreditamount": "(Tín dụng: {result_creditAmount})",

        "are_you_sure_you_want_to_delete_the_dup": "Bạn có chắc chắn muốn xóa tệp thông tin xác thực không?\\n{filename}",

        "test_failed": "Kiểm tra thất bại",

        "bulk_configure_preview_channels": "Cấu hình hàng loạt kênh Preview",

        "github_open_source_repository": "Kho lưu trữ mã nguồn mở GitHub:",

        "test_failed_errormessage": "Kiểm tra thất bại: {error_message}",

        "view_account_email": "Xem email tài khoản",

        "longtext_truncation_recovery_contro": "⏱️ Kiểm soát phục hồi cắt cụt văn bản dài",

        "automation_enabled": "Tự động hóa đã được bật:",

        "div_stylepadding_12px_marginbottom": "<div style=\"padding: 12px; margin-bottom: 10px; border-left: 3px solid #dc3545; background-color: #f8f9fa;\">\n\n                                    <div style=\"font-weight: bold; color: #dc3545; margin-bottom: 8px;\">Mã lỗi: {errorCode}</div>\n\n                                    <div style=\"line-height: 1.6; color: #333; white-space: pre-wrap; word-break: break-word;\">\n\n                                        {highlightedMsg}\n\n                                    </div>\n\n                                    {detailsHtml}\n\n                                </div>",

        "refresh_all_account_emails": "Làm mới tất cả email tài khoản",

        "about_omni-gateway": "Về Omni Gateway",

        "get_authentication_file": "Lấy tệp xác thực",

        "n_restart_reminder_notice": "\\n⚠️ Nhắc nhở khởi động lại: {notice}",

        "test_failed_datamessage_error_code": "❌ Kiểm tra thất bại - ${data.message || 'Mã lỗi: ' + (data.status_code || response.status)}",

        "service_keepalive_heartbeat_request": "URL yêu cầu nhịp tim duy trì dịch vụ:",

        "after_the_google_authorization_redi": "Sau khi chuyển hướng xác nhận ủy quyền Google, hãy sao chép toàn bộ địa chỉ URL trên thanh địa chỉ của trình duyệt (ngay cả khi nó hiển thị lỗi kết nối) và dán vào ô nhập liệu bên dưới.",

        "disabled": "Đã vô hiệu hóa",

        "upload_failed_http_status": "Tải lên thất bại: HTTP {status}",

        "disconnected": "Chưa kết nối",

        "if_the_redirect_fails_and_shows_an": "Nếu lỗi chuyển hướng hiển thị rằng không thể kết nối tới localhost:11451, hãy quay lại bảng điều khiển này;",

        "unknown_error": "Lỗi không xác định",

        "testing_omni_credentials_ple": "🧪 Đang kiểm tra thông tin xác thực Omni, vui lòng chờ...",

        "if_you_cannot_return_to_the_source": "Nếu không thể quay lại nguồn, bạn có thể sao chép toàn bộ URL sau khi chuyển hướng và mở rộng kênh nhanh bên dưới để phân tích.",

        "verification_failed_errormessage": "Kiểm tra thất bại: {error_message}",

        "nerror_detailsnjsonstringifyerrorob": "\\nChi tiết lỗi:\\n{JSON_stringify_errorObj__null__2}",

        "log_stream_connected_successfully": "Kết nối luồng nhật ký thành công",

        "clearing_environment_variable_crede": "Đang xóa các tệp thông tin xác thực từ biến môi trường...",

        "get_authentication_link": "Lấy liên kết xác thực",

        "resulterror_step_resultstep": "{result_error} (Bước: {result_step})",

        "network_error": "Lỗi mạng:",

        "failed_to_retrieve_environment_vari": "Lấy trạng thái biến môi trường thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "count_items_selected": "Đã chọn {count} mục",

        "are_you_sure_you_want_to_clear_all": "Bạn có chắc chắn muốn xóa tất cả các tệp thông tin xác thực được nhập từ biến môi trường không?\\nViệc này sẽ xóa tất cả các tệp xác thực có tên bắt đầu bằng \"env-\".",

        "bulk_operation_network_error_errorm": "Lỗi mạng thao tác hàng loạt: {error_message}",

        "streaming_truncation_recovery": "-Phục hồi cắt cụt luồng",

        "failed_to_get_quota_information": "Lấy thông tin hạn mức thất bại",

        "click_the_button_below_to_retrieve": "Nhấp vào nút bên dưới để lấy trực tiếp và tự động lưu tệp thông tin xác thực;",

        "seamlessly_switch_to_idle_accounts": "Chuyển đổi liền mạch sang các tài khoản nhàn rỗi để tránh hiệu quả giới hạn 429.",

        "bind_the_listening_tcp_port_changes": "Ràng buộc cổng TCP đang lắng nghe, các thay đổi cần khởi động lại để có hiệu lực.",

        "bulk_disable_credit": "Tắt Credit hàng loạt",

        "failed": "Thất bại",

        "reset_failed_datamessage_datadetail": "Đặt lại thất bại: ${data.message || data.detail || data.error || 'Lỗi không xác định'}",

        "failed_to_get_quota_information_err": "❌ Lấy thông tin hạn mức thất bại: {error_message}",

        "realtime_logs": "Nhật ký thời gian thực",

        "please_enter_the_access_password": "Vui lòng nhập mật khẩu truy cập!",

        "zip_files_will_be_automatically_dec": "Các tệp ZIP sẽ được tự động giải nén và lọc để trích xuất các chứng thực JSON.",

        "oauth_authentication_server_endpoin": "Điểm cuối máy chủ xác thực OAuth:",

        "are_you_sure_you_want_to_batch_set": "Bạn có chắc chắn muốn cài đặt hàng loạt kênh Preview cho {selectedFiles_length} chứng thực không?\\n\\nCấu hình sẽ được xử lý song song để tăng tốc độ.",

        "settings_saved_successfully_success": "Đã lưu cài đặt thành công",

        "configuration_saved_successfully": "Đã lưu cấu hình thành công",

        "preview_not_supported": "Không hỗ trợ Preview",

        "please_select_a_projectnn": "Vui lòng chọn một dự án:\\n\\n",

        "please_select_the_files_to_upload": "Vui lòng chọn các tệp cần tải lên",

        "are_you_sure_you_want_to_action_the": "Bạn có chắc chắn muốn {action} {count} tệp đã chọn không?",

        "a_hrefurl_target_blank_stylecolor_0": "<a href=\"{url}\" target=\"_blank\" style=\"color: #007bff; text-decoration: underline; word-break: break-all;\" title=\"Nhấp để mở: {url}\">{url}</a>",

        "retry_fetching_authentication_file": "Thử lại việc lấy tệp xác thực",

        "manually_connect_log_channel": "Kết nối thủ công kênh nhật ký",

        "error_information_loaded_successful": "✅ Đã tải thành công thông tin lỗi",

        "universal_shortcut_override_passwor": "Mật khẩu ghi đè phím tắt chung (tùy chọn):",

        "login_failed_datadetail_dataerror_u": "Đăng nhập thất bại: ${data.detail || data.error || 'Lỗi không xác định'}",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #666;\">⏳ Đang tải thông tin lỗi...</div>",

        "log_stream_connection_disconnected_dup": "Kết nối luồng nhật ký đã bị ngắt",

        "system_configuration_saved_successf": "✅ Đã lưu cấu hình hệ thống thành công",

        "div_stylefontsize_12px_color_666sta": "<div style=\"font-size: 12px; color: #666;\">Trạng thái: {escapeHtml_parsedMsg_error_status}</div>",

        "api_access_authentication_password": "Mật khẩu xác thực truy cập API (API Key):",

        "parallel_testing_selectedfileslengt": "🔍 Đang kiểm tra song song {selectedFiles_length} chứng thực Omni, vui lòng đợi...",

        "operation_failed": "Thao tác thất bại:",

        "all_omni_credentials_packed": "✅ Tất cả chứng thực Omni đã được đóng gói và tải xuống",

        "operation_successful_action_dup": "Thao tác thành công: {action}",

        "omni_api_endpoint": "Điểm cuối API Omni:",

        "authentication_link_generated_proje": "Liên kết xác thực đã được tạo (ID dự án: {data_detected_project_id}), vui lòng nhấp vào liên kết để hoàn tất ủy quyền",

        "configuring_preview_channel_status": "Đang cấu hình hàng loạt trạng thái kênh Preview...",

        "after_successful_authorization_the_dup": "Sau khi ủy quyền thành công, hệ thống sẽ tự động phát hiện và kích hoạt các dịch vụ API cần thiết như Gemini Cloud Assist API và Gemini for Google Cloud API cho dự án Google Cloud của bạn, không cần cấu hình thủ công.",

        "batch_upload_omni_credential": "Tải lên hàng loạt chứng thực Omni",

        "checking": "Đang kiểm tra...",

        "please_enter_the_callback_url": "Vui lòng nhập URL phản hồi",

        "extract_credentials_from_callback_l": "Trích xuất chứng thực từ liên kết phản hồi",

        "div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup_dup": "<div style=\"text-align: center; padding: 20px; color: #28a745;\"><div style=\"font-size: 48px; margin-bottom: 10px;\">✅</div><div style=\"font-weight: bold;\">Không có hồ sơ lỗi</div><div style=\"font-size: 12px; color: #666; margin-top: 8px;\">Chứng thực này đang hoạt động bình thường</div></div>",

        "no_details_available": "Không có thông tin chi tiết",

        "global_system_configuration": "Cấu hình hệ thống toàn cục",

        "network_error_while_downloading_log": "Lỗi mạng khi tải xuống nhật ký: {error_message}",

        "authentication_link_generated_proje_dup": "Liên kết xác thực đã được tạo (ID dự án: {id}), vui lòng nhấp vào liên kết để hoàn tất ủy quyền",

        "listening_port": "Cổng lắng nghe (Port):",

        "email_refresh_complete_successfully": "Hoàn tất làm mới email: Đã truy xuất thành công {data_success_count}/{data_total_count} địa chỉ email",

        "already_up_to_date_dup": "Đã là phiên bản mới nhất",

        "no_credential_files_available": "Chưa có tệp chứng thực nào",

        "validation_successfulnnfile_filenam": "✅ Xác thực thành công!\\n\\nTệp: {filename}\\nID dự án: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",

        "selectedcount_items_selected": "Đã chọn {selectedCount} mục",

        "click_the_view_content_button_to_lo": "Nhấp vào nút \"Xem nội dung\" để tải chi tiết tệp...",

        "please_enter_the_password": "Vui lòng nhập mật khẩu",

        "upload_progress_dup": "Tiến độ tải lên",

        "error_dataerror_failed_to_fetch_aut": "Lỗi: ${data.error || 'Lấy liên kết xác thực thất bại'}",

        "are_you_sure_you_want_to_delete_the_dup_dup": "Bạn có chắc chắn muốn xóa {count} tệp đã chọn không?\\nLưu ý: Thao tác này không thể hoàn tác!",

        "configuring_preview_channel_for_sel": "🔧 Đang cấu hình kênh Preview cho {selectedFiles_length} chứng thực, vui lòng đợi...",

        "none": "Không",

        "this_is_not_a_valid_callback_url_pl_dup": "❌ Đây không phải là URL phản hồi hợp lệ! Vui lòng đảm bảo nó bao gồm các tham số code và state",

        "retrieved_credential_file_content": "Nội dung tệp chứng thực đã lấy được:",

        "enable": "Bật",

        "antitruncation_output_protection": "Bảo vệ đầu ra chống cắt bớt",

        "authentication_link_generated_proje_dup_dup": "Liên kết xác thực đã được tạo (ID dự án sẽ được tự động phát hiện sau khi hoàn tất xác thực), vui lòng nhấp vào liên kết để hoàn tất ủy quyền",

        "failed_to_configure_preview_channel_dup": "Cấu hình kênh Preview thất bại",

        "testing_credentials_please_wait": "🧪 Đang kiểm tra chứng thực, vui lòng đợi...",

        "validation_complete_processed_activ": "Xác thực hoàn tất! Đã xử lý: {active} tệp hợp lệ, {changed} ID được cập nhật, {disabled} tệp được đánh dấu không hợp lệ",

        "login_successful_dup": "Đăng nhập thành công",

        "batch_task_control": "Điều khiển tác vụ hàng loạt",

        "24h_api_call_volume": "Số yêu cầu trong 24 giờ",

        "minimalist_parsing_mapping_for_cutt": "Ánh xạ phân tích tối giản cho các giao thức tiên tiến như System/Thinking.",

        "multiple_projects_detected_please_s": "Phát hiện nhiều dự án, vui lòng chỉ định ID dự án trong tùy chọn nâng cao:",

        "failed_to_fetch_error_information_e": "❌ Lấy thông tin lỗi thất bại: {error_message}",

        "loaded_usage_statistics_for_aggdata": "Đã tải thống kê sử dụng cho {aggData_total_files____Object_keys_AppState_usageStatsData__length} tệp",
        "failed_to_load_usage_statistics": "Tải thống kê sử dụng thất bại",
        "error_errormsg": "Lỗi: {errorMsg}",
        "status_net_error": "Lỗi mạng: {error}",
        "status_no_filter_data": "Không tìm thấy thống kê sử dụng.",
        "table_calls": "Số yêu cầu",
        "btn_reset_stats": "Đặt lại",
        "confirm_reset_stats": "Bạn có chắc chắn muốn đặt lại thống kê cho {filename} không?",
        "reset_failed_datamessage_datadetail": "Đặt lại thất bại: {data_message____data_detail____data_error}",
        "are_you_sure_you_want_to_reset_usag_dup": "Bạn có chắc chắn muốn đặt lại tất cả thống kê sử dụng không?",
        "table_filename": "Tên tệp chứng thực",
        "table_actions": "Hành động"

    }

};

// =====================================================================

// Comment translated/cleaned for compliance

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

    localStorage.setItem('ogw_lang', lang);

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

// Comment translated/cleaned for compliance

document.addEventListener('DOMContentLoaded', initLanguage);

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

const ROUTE_MAP = {

    '/dashboard': 'dashboard',

    '/omni': 'manage',

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

    const savedToken = localStorage.getItem('ogw_auth_token') || AppState.authToken;

    const isAuthenticated = !!savedToken;

    if (!isAuthenticated) {

        targetPath = '/login';

        if (window.location.pathname !== '/login') {

            history.replaceState(null, '', '/login');

        }

        const loginEl = document.getElementById('loginSection');

        const mainEl = document.getElementById('mainSection');

        if (loginEl) loginEl.style.setProperty('display', 'flex', 'important');

        if (mainEl) mainEl.style.setProperty('display', 'none', 'important');

        return;

    } else {

        if (targetPath === '/login') {

            targetPath = '/dashboard';

        }

        const loginEl = document.getElementById('loginSection');

        const mainEl = document.getElementById('mainSection');

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

// Comment translated/cleaned for compliance

// =====================================================================

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

const AppState = {

    // Comment translated/cleaned for compliance

    authToken: '',

    authInProgress: false,

    currentProjectId: '',

    // Comment translated/cleaned for compliance

    omniAuthState: null,

    omniAuthInProgress: false,

    // Comment translated/cleaned for compliance

    creds: createCredsManager('normal'),

    omniCreds: createCredsManager('omni'),

    // Comment translated/cleaned for compliance

    uploadFiles: createUploadManager('normal'),

    omniUploadFiles: createUploadManager('omni'),

    // Comment translated/cleaned for compliance

    currentConfig: {},

    envLockedFields: new Set(),

    // Comment translated/cleaned for compliance

    logWebSocket: null,

    allLogs: [],

    filteredLogs: [],

    currentLogFilter: 'all',

    // Comment translated/cleaned for compliance

    usageStatsData: {},

    // Comment translated/cleaned for compliance

    cooldownTimerInterval: null

};

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

function createCredsManager(type) {

    const modeParam = type === 'omni' ? 'mode=omni' : 'mode=code_assist';

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

        // Comment translated/cleaned for compliance

        getEndpoint: (action) => {

            const endpoints = {

                status: `./ogw/creds/status`,

                action: `./ogw/creds/action`,

                batchAction: `./ogw/creds/batch-action`,

                download: `./ogw/creds/download`,

                downloadAll: `./ogw/creds/download-all`,

                detail: `./ogw/creds/detail`,

                fetchEmail: `./ogw/creds/fetch-email`,

                refreshAllEmails: `./ogw/creds/refresh-all-emails`,

                deduplicate: `./ogw/creds/deduplicate-by-email`,

                verifyProject: `./ogw/creds/verify-project`,

                quota: `./ogw/creds/quota`

            };

            return endpoints[action] || '';

        },

        // Comment translated/cleaned for compliance

        getModeParam: () => modeParam,

        // Comment translated/cleaned for compliance

        getElementId: (suffix) => {

            // Comment translated/cleaned for compliance

            // Comment translated/cleaned for compliance

            if (type === 'omni') {

                return 'omni' + suffix.charAt(0).toUpperCase() + suffix.slice(1);

            }

            return suffix.charAt(0).toLowerCase() + suffix.slice(1);

        },

        // Comment translated/cleaned for compliance

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

                    // Comment translated/cleaned for compliance

                    if (data.stats) {

                        this.statsData = data.stats;

                    } else {

                        // Comment translated/cleaned for compliance

                        this.calculateStats();

                    }

                    this.updateStatsDisplay();

                    this.filteredData = this.data;

                    this.renderList();

                    this.updatePagination();

                    let msg = t('status_loaded_creds', {count: data.total, type: type === 'omni' ? 'Omni' : ''});

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

        // Comment translated/cleaned for compliance

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

        // Comment translated/cleaned for compliance

        updateStatsDisplay() {

            document.getElementById(this.getElementId('StatTotal')).textContent = this.statsData.total;

            document.getElementById(this.getElementId('StatNormal')).textContent = this.statsData.normal;

            document.getElementById(this.getElementId('StatDisabled')).textContent = this.statsData.disabled;

        },

        // Comment translated/cleaned for compliance

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

        // Comment translated/cleaned for compliance

        getTotalPages() {

            return Math.ceil(this.totalCount / this.pageSize);

        },

        // Comment translated/cleaned for compliance

        updatePagination() {

            const totalPages = this.getTotalPages();

            const startItem = (this.currentPage - 1) * this.pageSize + 1;

            const endItem = Math.min(this.currentPage * this.pageSize, this.totalCount);

            document.getElementById(this.getElementId('PaginationInfo')).textContent =

                t('status_page_info', {page: this.currentPage, total: totalPages, start: startItem, end: endItem, count: this.totalCount});

            document.getElementById(this.getElementId('PrevPageBtn')).disabled = this.currentPage <= 1;

            document.getElementById(this.getElementId('NextPageBtn')).disabled = this.currentPage >= totalPages;

        },

        // Comment translated/cleaned for compliance

        changePage(direction) {

            const newPage = this.currentPage + direction;

            if (newPage >= 1 && newPage <= this.getTotalPages()) {

                this.currentPage = newPage;

                this.refresh();

            }

        },

        // Comment translated/cleaned for compliance

        changePageSize() {

            this.pageSize = parseInt(document.getElementById(this.getElementId('PageSizeSelect')).value);

            this.currentPage = 1;

            this.refresh();

        },

        // Comment translated/cleaned for compliance

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

        // Comment translated/cleaned for compliance

        updateBatchControls() {

            const selectedCount = this.selectedFiles.size;

            document.getElementById(this.getElementId('SelectedCount')).textContent = t('status_selected_items', {count: selectedCount});

            const batchBtnNames = ['Enable', 'Disable', 'Delete', 'Verify', 'Preview'];

            if (this.type === 'omni') {

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

        // Comment translated/cleaned for compliance

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

        // Comment translated/cleaned for compliance

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

            if (!confirm(confirmMsg)) return;

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

// Comment translated/cleaned for compliance

// =====================================================================

function createUploadManager(type) {

    const modeParam = type === 'omni' ? 'mode=omni' : 'mode=code_assist';

    const endpoint = `./ogw/creds/upload?${modeParam}`;

    return {

        type: type,

        selectedFiles: [],

        getElementId: (suffix) => {

            // Comment translated/cleaned for compliance

            // Comment translated/cleaned for compliance

            if (type === 'omni') {

                return 'omni' + suffix.charAt(0).toUpperCase() + suffix.slice(1);

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

                const fileIcon = isZip ? '📦' : '📄';

                const fileType = isZip ? t('label_zip_pack') : t('label_json_file');

                const fileItem = document.createElement('div');

                fileItem.className = 'file-item';

                fileItem.innerHTML = `

                    <div>

                        <span class="file-name">${fileIcon} ${file.name}</span>

                        <span class="file-size">(${formatFileSize(file.size)}${fileType})</span>

                    </div>

                    <button class="remove-btn" onclick="${type === 'omni' ? 'removeOmniFile' : 'removeFile'}(${index})">${t('action_delete')}</button>

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

                            showStatus(t('status_upload_success', {count: data.uploaded_count, type: type === 'omni' ? 'Omni' : ''}), 'success');

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

        // Comment translated/cleaned for compliance

        if (window._statusTimeout) {

            clearTimeout(window._statusTimeout);

        }

        // Comment translated/cleaned for compliance

        statusSection.innerHTML = `<div class="status ${type}">${message}</div>`;

        const statusDiv = statusSection.querySelector('.status');

        // Comment translated/cleaned for compliance

        statusDiv.offsetHeight;

        statusDiv.classList.add('show');

        // Comment translated/cleaned for compliance

        window._statusTimeout = setTimeout(() => {

            statusDiv.classList.add('fade-out');

            setTimeout(() => {

                statusSection.innerHTML = '';

            }, 300); // Comment translated/cleaned for compliance

        }, 3000);

    } else {

        showMessageModal(t('dialog_tip'), message, 'info');

    }

}

async function updateEndpointUrls() {
    const origin = window.location.origin;

    const unifiedEl = document.getElementById('unifiedEndpointUrl');
    if (unifiedEl) unifiedEl.textContent = `${origin}/ogw/v1`;

    try {
        const response = await fetch('./ogw/auth/keys', { headers: getAuthHeaders() });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const apiKeyEl = document.getElementById('apiKey');
                if (apiKeyEl) apiKeyEl.value = data.api_key;
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
    navigator.clipboard.writeText(input.value).then(() => {
        showStatus(t('copy_success'), 'success');
    }).catch(err => {
        showStatus(t('copy_fail'), 'error');
    });
}

async function regenerateApiKey() {
    if (!confirm(t('confirm_regenerate_key', 'Are you sure you want to regenerate this API key? Previous key will become invalid immediately.'))) {
        return;
    }
    try {
        const response = await fetch('./ogw/auth/keys/reset', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const el = document.getElementById('apiKey');
                if (el) el.value = data.api_key;
                showStatus(t('regenerate_success', 'API Key regenerated successfully'), 'success');
            } else {
                showStatus(data.error || 'Failed to regenerate key', 'error');
            }
        } else {
            showStatus('Failed to regenerate key', 'error');
        }
    } catch (e) {
        console.error("Failed to regenerate key", e);
        showStatus('Network error occurred', 'error');
    }
}

// Comment translated/cleaned for compliance

function linkifyText(text) {

    if (!text) return text;

    // Comment translated/cleaned for compliance

    const urlPattern = /(https?:\/\/[^\s"'<>()[\]{}]+)|(www\.[^\s"'<>()[\]{}]+)/gi;

    return text.replace(urlPattern, function(url) {

        let href = url;

        // Comment translated/cleaned for compliance

        if (url.startsWith('www.')) {

            href = 'https://' + url;

        }

        return `<a href="${href}" target="_blank" rel="noopener noreferrer" class="message-link" onclick="event.stopPropagation()" title="${t('click_to_open_link')}\n${t('right_click_to_copy_link')}">${url}</a>`;

    });

}

// Comment translated/cleaned for compliance

function showMessageModal(title, message, type = 'info') {

    // Comment translated/cleaned for compliance

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

    // Comment translated/cleaned for compliance

    document.body.appendChild(modal);

    // Comment translated/cleaned for compliance

    modal.addEventListener('click', function(e) {

        if (e.target === modal) {

            modal.remove();

        }

    });

    // Comment translated/cleaned for compliance

    const escHandler = function(e) {

        if (e.key === 'Escape') {

            modal.remove();

            document.removeEventListener('keydown', escHandler);

        }

    };

    document.addEventListener('keydown', escHandler);

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

// Comment translated/cleaned for compliance

// =====================================================================

function createCredCard(credInfo, manager) {

    const div = document.createElement('div');

    const { status, filename } = credInfo;

    const managerType = manager.type;

    // Comment translated/cleaned for compliance

    div.className = status.disabled ? 'cred-card disabled' : 'cred-card';

    // Comment translated/cleaned for compliance

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

    // Comment translated/cleaned for compliance

    if (managerType !== 'omni' && credInfo.preview !== undefined) {

        if (credInfo.preview) {

            statusBadges += `<span class="status-badge success" title="${t('preview_supported_title')}">Preview: ON</span>`;

        } else {

            statusBadges += `<span class="status-badge muted" title="${t('preview_not_supported_title')}">Preview: OFF</span>`;

        }

    }

    // Comment translated/cleaned for compliance

    const tier = (credInfo.tier || 'pro').toString().toLowerCase();

    const tierLabel = tier.toUpperCase();

    const tierClass = tier === 'ultra' ? 'tier-ultra' : (tier === 'free' ? 'tier-free' : 'tier-pro');

    statusBadges += `<span class="status-badge ${tierClass}" title="${t('tier_badge_title')}: ${tierLabel}">Tier: ${tierLabel}</span>`;

    // Comment translated/cleaned for compliance

    if (managerType === 'omni') {

        if (credInfo.enable_credit) {

            statusBadges += `<span class="status-badge credit-on" title="${t('credit_enabled_title')}">Credit: ON</span>`;

        } else {

            statusBadges += `<span class="status-badge credit-off" title="${t('credit_disabled_title')}">Credit: OFF</span>`;

        }

    }

    // Comment translated/cleaned for compliance

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

    // Comment translated/cleaned for compliance

    const pathId = (managerType === 'omni' ? 'omni_' : '') + btoa(encodeURIComponent(filename)).replace(/[+/=]/g, '_');

    // Comment translated/cleaned for compliance

    const actionButtons = `

        ${status.disabled

            ? `<button class="cred-btn enable" data-filename="${filename}" data-action="enable">${t('action_enable')}</button>`

            : `<button class="cred-btn disable" data-filename="${filename}" data-action="disable">${t('action_disable')}</button>`

        }

        <button class="cred-btn view" onclick="toggle${managerType === 'omni' ? 'Omni' : ''}CredDetails('${pathId}')">${t('btn_view_content')}</button>

        <button class="cred-btn download" onclick="download${managerType === 'omni' ? 'Omni' : ''}Cred('${filename}')">${t('btn_download')}</button>

        <button class="cred-btn email" onclick="fetch${managerType === 'omni' ? 'Omni' : ''}UserEmail('${filename}')">${t('btn_view_email')}</button>

        ${managerType === 'omni' ? `<button class="cred-btn" onclick="toggleOmniQuotaDetails('${pathId}')" title="${t('btn_view_quota_title')}">${t('btn_view_quota')}</button>` : ''}

        ${managerType === 'omni' ? (credInfo.enable_credit

            ? `<button class="cred-btn" data-filename="${filename}" data-action="disable_credit" title="${t('btn_disable_credit_title')}">${t('btn_disable_credit')}</button>`

            : `<button class="cred-btn" data-filename="${filename}" data-action="enable_credit" title="${t('btn_enable_credit_title')}">${t('btn_enable_credit')}</button>`

        ) : ''}

        ${managerType !== 'omni' ? `<button class="cred-btn" onclick="configurePreviewChannel('${filename}')" title="${t('btn_setup_preview_title')}">${t('btn_setup_preview')}</button>` : ''}

        <button class="cred-btn" onclick="verify${managerType === 'omni' ? 'Omni' : ''}ProjectId('${filename}')" title="${t('btn_verify_id_title')}">${t('btn_verify_id')}</button>

        <button class="cred-btn" onclick="test${managerType === 'omni' ? 'Omni' : ''}Credential('${filename}')" title="${t('btn_message_test_title')}">${t('btn_message_test')}</button>

        <button class="cred-btn" onclick="toggle${managerType === 'omni' ? 'Omni' : ''}ErrorDetails('${pathId}')" title="${t('btn_view_errors_title')}">${t('btn_view_errors')}</button>

        <button class="cred-btn delete" data-filename="${filename}" data-action="delete">${t('action_delete')}</button>

    `;

    // Comment translated/cleaned for compliance

    const emailInfo = credInfo.user_email

        ? `<div class="cred-email">${credInfo.user_email}</div>`

        : `<div class="cred-email empty">${t('email_not_fetched')}</div>`;

    const checkboxClass = manager.getElementId('file-checkbox');

    div.innerHTML = `

        <div class="cred-header">

            <div class="cred-title-row">

                <input type="checkbox" class="${checkboxClass}" data-filename="${filename}" onchange="toggle${managerType === 'omni' ? 'Omni' : ''}FileSelection('${filename}')">

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

        ${managerType === 'omni' ? `

        <div class="cred-quota-details" id="quota-${pathId}">

            <div class="cred-quota-content" data-filename="${filename}" data-loaded="false">

                ${t('click_view_quota_to_load')}

            </div>

        </div>

        ` : ''}

    `;

    // Comment translated/cleaned for compliance

    div.querySelectorAll('[data-filename][data-action]').forEach(button => {

        button.addEventListener('click', function () {

            const fn = this.getAttribute('data-filename');

            const action = this.getAttribute('data-action');

            if (action === 'delete') {

                if (confirm(t('confirm_delete_cred', {filename: fn}))) {

                    manager.action(fn, action);

                }

            } else {

                manager.action(fn, action);

            }

        });

    });

    return div;

}

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

async function toggleCredDetails(pathId) {

    await toggleCredDetailsCommon(pathId, AppState.creds);

}

async function toggleOmniCredDetails(pathId) {

    await toggleCredDetailsCommon(pathId, AppState.omniCreds);

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

                const modeParam = manager.type === 'omni' ? 'mode=omni' : 'mode=code_assist';

                const endpoint = `./ogw/creds/detail/${encodeURIComponent(filename)}?${modeParam}`;

                const response = await fetch(endpoint, { headers: getAuthHeaders() });

                const data = await response.json();

                if (response.ok && data.content) {

                    contentDiv.textContent = JSON.stringify(data.content, null, 2);

                    contentDiv.setAttribute('data-loaded', 'true');

                } else {

                    contentDiv.textContent = t('status_load_failed_prefix') + (data.error || data.detail || t('unknown_error'));

                }

            } catch (error) {

                contentDiv.textContent = t('status_load_failed_prefix') + error.message;

            }

        }

    }

}

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

async function login() {

    const password = document.getElementById('loginPassword').value;

    if (!password) {

        showStatus(t('please_enter_the_password'), 'error');

        return;

    }

    try {

        const response = await fetch('./ogw/auth/login', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ password })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.authToken = data.token;

            localStorage.setItem('ogw_auth_token', AppState.authToken);

            showStatus(t('login_successful_dup'), 'success');

            navigate('/dashboard');

        } else {

            showStatus(t('login_failed_datadetail_dataerror_u', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function autoLogin() {

    const savedToken = localStorage.getItem('ogw_auth_token');

    if (!savedToken) {

        navigate('/login', false);

        return false;

    }

    AppState.authToken = savedToken;

    try {

        const response = await fetch('./ogw/config/get', {

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

            localStorage.removeItem('ogw_auth_token');

            AppState.authToken = '';

            navigate('/login', false);

            return false;

        }

    } catch (error) {

        localStorage.removeItem('ogw_auth_token');

        AppState.authToken = '';

        navigate('/login', false);

        return false;

    }

}

function logout() {

    localStorage.removeItem('ogw_auth_token');

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

// Comment translated/cleaned for compliance

// =====================================================================

// Comment translated/cleaned for compliance

function updateTabSlider(targetTab, animate = true) {

    const slider = document.querySelector('.tab-slider');

    const tabs = document.querySelector('.tabs');

    if (!slider || !tabs || !targetTab) return;

    // Comment translated/cleaned for compliance

    const tabLeft = targetTab.offsetLeft;

    const tabWidth = targetTab.offsetWidth;

    const tabsWidth = tabs.scrollWidth;

    // Comment translated/cleaned for compliance

    const rightValue = tabsWidth - tabLeft - tabWidth;

    if (animate) {

        slider.style.left = `${tabLeft}px`;

        slider.style.right = `${rightValue}px`;

    } else {

        // Comment translated/cleaned for compliance

        slider.style.transition = 'none';

        slider.style.left = `${tabLeft}px`;

        slider.style.right = `${rightValue}px`;

        // Comment translated/cleaned for compliance

        slider.offsetHeight;

        slider.style.transition = '';

    }

}

// Comment translated/cleaned for compliance

function initTabSlider() {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) {

        updateTabSlider(activeTab, false);

    }

}

// Comment translated/cleaned for compliance

document.addEventListener('DOMContentLoaded', initTabSlider);

window.addEventListener('resize', () => {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) updateTabSlider(activeTab, false);

});

function switchTab(tabName) {

    const route = TAB_MAP[tabName] || '/dashboard';

    navigate(route, true);

}

// Comment translated/cleaned for compliance

function triggerTabDataLoad(tabName) {

    if (tabName === 'dashboard') {

        refreshUsageStats();

        updateEndpointUrls();

    }

    if (tabName === 'manage') {
        AppState.omniCreds.refresh();
    }

    if (tabName === 'config') loadConfig();

    if (tabName === 'logs') connectWebSocket();

}

// =====================================================================

// Comment translated/cleaned for compliance

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

        const response = await fetch('./ogw/auth/start', {

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

        const response = await fetch('./ogw/auth/callback', {

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

            const selection = prompt(projectOptions);

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

            const userProjectId = prompt(t('unable_to_autodetect_project_id_ple'));

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

// Comment translated/cleaned for compliance

// =====================================================================

async function startOmniAuth() {

    const btn = document.getElementById('getOmniAuthBtn');

    btn.disabled = true;

    btn.textContent = t('generating_authentication_link');

    try {

        showStatus(t('generating_omni_authenticati'), 'info');

        const response = await fetch('./ogw/auth/start', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ mode: 'omni' })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.omniAuthState = data.state;

            AppState.omniAuthInProgress = true;

            const authUrlLink = document.getElementById('omniAuthUrl');

            authUrlLink.href = data.auth_url;

            authUrlLink.textContent = data.auth_url;

            document.getElementById('omniAuthUrlSection').classList.remove('hidden');

            showStatus(t('omni_authentication_link_gen'), 'success');

        } else {

            showStatus(t('error_dataerror_failed_to_generate', {data_error: data.error || t('failed_to_generate_authentication_l_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_omni_authentication_link');

    }

}

async function getOmniCredentials() {

    if (!AppState.omniAuthInProgress) {

        showStatus(t('please_obtain_the_omni_authe'), 'error');

        return;

    }

    const btn = document.getElementById('getOmniCredsBtn');

    btn.disabled = true;

    btn.textContent = t('waiting_for_oauth_callback');

    try {

        showStatus(t('waiting_for_omni_oauth_callb'), 'info');

        const response = await fetch('./ogw/auth/callback', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ mode: 'omni' })

        });

        const data = await response.json();

        if (response.ok) {

            document.getElementById('omniCredsContent').textContent = JSON.stringify(data.credentials, null, 2);

            document.getElementById('omniCredsSection').classList.remove('hidden');

            AppState.omniAuthInProgress = false;

            showStatus(t('omni_authentication_successf_dup', {data_file_path: data.file_path}), 'success');

        } else {

            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: data.error || t('failed_to_retrieve_authentication_f_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('fetch_omni_credentials');

    }

}

function downloadOmniCredentials() {

    const content = document.getElementById('omniCredsContent').textContent;

    const blob = new Blob([content], { type: 'application/json' });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = `omni-credential-${Date.now()}.json`;

    a.click();

    window.URL.revokeObjectURL(url);

}

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

function toggleProjectIdSection() {

    const section = document.getElementById('projectIdSection');

    const icon = document.getElementById('projectIdToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(90deg)';

        icon.textContent = '▼';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '▶';

    }

}

function toggleCallbackUrlSection() {

    const section = document.getElementById('callbackUrlSection');

    const icon = document.getElementById('callbackUrlToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(180deg)';

        icon.textContent = '▲';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '▼';

    }

}

function toggleOmniCallbackUrlSection() {

    const section = document.getElementById('omniCallbackUrlSection');

    const icon = document.getElementById('omniCallbackUrlToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(180deg)';

        icon.textContent = '▲';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '▼';

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

        const response = await fetch('./ogw/auth/callback-url', {

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

                msg += `• ${p.name} (ID: ${p.project_id})<br>`;

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

async function processOmniCallbackUrl() {

    const callbackUrl = document.getElementById('omniCallbackUrlInput').value.trim();

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

    showStatus(t('retrieving_omni_credentials'), 'info');

    try {

        const response = await fetch('./ogw/auth/callback-url', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ callback_url: callbackUrl, mode: 'omni' })

        });

        const result = await response.json();

        if (result.credentials) {

            showStatus(result.message || t('omni_credentials_successfull'), 'success');

            document.getElementById('omniCredsContent').textContent = JSON.stringify(result.credentials, null, 2);

            document.getElementById('omniCredsSection').classList.remove('hidden');

        } else {

            showStatus(result.error || t('failed_to_retrieve_omni_cred'), 'error');

        }

        document.getElementById('omniCallbackUrlInput').value = '';

    } catch (error) {

        showStatus(t('failed_to_retrieve_omni_cred_dup', {error_message: error.message}), 'error');

    }

}

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

// Comment translated/cleaned for compliance

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

    fetch(`./ogw/creds/download/${filename}`, { headers: { 'Authorization': `Bearer ${AppState.authToken}` } })

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

        const response = await fetch('./ogw/creds/download-all', {

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

// Comment translated/cleaned for compliance

function refreshOmniCredsList() { AppState.omniCreds.refresh(); }

function applyOmniStatusFilter() { AppState.omniCreds.applyStatusFilter(); }

function changeOmniPage(direction) { AppState.omniCreds.changePage(direction); }

function changeOmniPageSize() { AppState.omniCreds.changePageSize(); }

function toggleOmniFileSelection(filename) {

    if (AppState.omniCreds.selectedFiles.has(filename)) {

        AppState.omniCreds.selectedFiles.delete(filename);

    } else {

        AppState.omniCreds.selectedFiles.add(filename);

    }

    AppState.omniCreds.updateBatchControls();

}

function toggleSelectAllOmni() {

    const checkbox = document.getElementById('selectAllOmniCheckbox');

    const checkboxes = document.querySelectorAll('.omniFile-checkbox');

    if (checkbox.checked) {

        checkboxes.forEach(cb => AppState.omniCreds.selectedFiles.add(cb.getAttribute('data-filename')));

    } else {

        AppState.omniCreds.selectedFiles.clear();

    }

    checkboxes.forEach(cb => cb.checked = checkbox.checked);

    AppState.omniCreds.updateBatchControls();

}

function batchOmniAction(action) { AppState.omniCreds.batchAction(action); }

function downloadOmniCred(filename) {

    fetch(`./ogw/creds/download/${filename}?mode=omni`, { headers: getAuthHeaders() })

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

function deleteOmniCred(filename) {

    if (confirm(t('are_you_sure_you_want_to_delete_fil_dup', {filename: filename}))) {

        AppState.omniCreds.action(filename, 'delete');

    }

}

async function downloadAllOmniCreds() {

    try {

        const response = await fetch('./ogw/creds/download-all?mode=omni', { headers: getAuthHeaders() });

        if (response.ok) {

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = `omni_credentials_${Date.now()}.zip`;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('all_omni_credentials_packed'), 'success');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

// Comment translated/cleaned for compliance

function handleFileSelect(event) { AppState.uploadFiles.handleFileSelect(event); }

function removeFile(index) { AppState.uploadFiles.removeFile(index); }

function clearFiles() { AppState.uploadFiles.clearFiles(); }

function uploadFiles() { AppState.uploadFiles.upload(); }

function handleOmniFileSelect(event) { AppState.omniUploadFiles.handleFileSelect(event); }

function handleOmniFileDrop(event) {

    event.preventDefault();

    event.currentTarget.style.borderColor = '#007bff';

    event.currentTarget.style.backgroundColor = '#f8f9fa';

    AppState.omniUploadFiles.addFiles(Array.from(event.dataTransfer.files));

}

function removeOmniFile(index) { AppState.omniUploadFiles.removeFile(index); }

function clearOmniFiles() { AppState.omniUploadFiles.clearFiles(); }

function uploadOmniFiles() { AppState.omniUploadFiles.upload(); }

// Comment translated/cleaned for compliance

// Comment translated/cleaned for compliance

function updateEmailDisplay(filename, email, managerType = 'normal') {

    // Comment translated/cleaned for compliance

    const containerId = managerType === 'omni' ? 'omniCredsList' : 'credsList';

    const container = document.getElementById(containerId);

    if (!container) return false;

    // Comment translated/cleaned for compliance

    const checkbox = container.querySelector(`input[data-filename="${filename}"]`);

    if (!checkbox) return false;

    // Comment translated/cleaned for compliance

    const card = checkbox.closest('.cred-card');

    if (!card) return false;

    // Comment translated/cleaned for compliance

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

        const response = await fetch(`./ogw/creds/fetch-email/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.user_email) {

            showStatus(t('successfully_retrieved_email_dataus', {data_user_email: data.user_email}), 'success');

            // Comment translated/cleaned for compliance

            updateEmailDisplay(filename, data.user_email, 'normal');

        } else {

            showStatus(data.message || t('unable_to_fetch_user_email'), 'error');

        }

    } catch (error) {

        showStatus(t('failed_to_get_email_errormessage', {error_message: error.message}), 'error');

    }

}

async function fetchOmniUserEmail(filename) {

    try {

        showStatus(t('retrieving_user_emails'), 'info');

        const response = await fetch(`./ogw/creds/fetch-email/${encodeURIComponent(filename)}?mode=omni`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.user_email) {

            showStatus(t('successfully_retrieved_email_dataus', {data_user_email: data.user_email}), 'success');

            // Comment translated/cleaned for compliance

            updateEmailDisplay(filename, data.user_email, 'omni');

        } else {

            showStatus(data.message || t('unable_to_fetch_user_email'), 'error');

        }

    } catch (error) {

        showStatus(t('failed_to_get_email_errormessage', {error_message: error.message}), 'error');

    }

}

async function verifyProjectId(filename) {

    try {

        // Comment translated/cleaned for compliance

        showStatus(t('verifying_project_id_please_wait'), 'info');

        const response = await fetch(`./ogw/creds/verify-project/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            // Comment translated/cleaned for compliance

            const tierLine = data.subscription_tier ? `\nTier: ${data.subscription_tier}` : '';

            const creditLine = data.credit_amount !== undefined && data.credit_amount !== null

                ? t('ncredit_datacredit_amount', {data_credit_amount: data.credit_amount})

                : '';

            const successMsg = t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message});

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            // Comment translated/cleaned for compliance

            showMessageModal(t('verification_successful'), t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message}), 'success');

            await AppState.creds.refresh();

        } else {

            // Comment translated/cleaned for compliance

            const errorMsg = data.message || t('verification_failed');

            showStatus(`❌ ${errorMsg}`, 'error');

            showMessageModal(t('verification_failed'), t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(`❌ ${errorMsg}`, 'error');

        showMessageModal(t('verification_failed'), `❌ ${errorMsg}`, 'error');

    }

}

async function verifyOmniProjectId(filename) {

    try {

        // Comment translated/cleaned for compliance

        showStatus(t('verifying_omni_project_id_pl'), 'info');

        const response = await fetch(`./ogw/creds/verify-project/${encodeURIComponent(filename)}?mode=omni`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            // Comment translated/cleaned for compliance

            const tierLine = data.subscription_tier ? `\nTier: ${data.subscription_tier}` : '';

            const creditLine = data.credit_amount !== undefined && data.credit_amount !== null

                ? t('ncredit_datacredit_amount', {data_credit_amount: data.credit_amount})

                : '';

            const successMsg = t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message});

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            // Comment translated/cleaned for compliance

            showMessageModal(t('verification_successful'), t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message}), 'success');

            await AppState.omniCreds.refresh();

        } else {

            // Comment translated/cleaned for compliance

            const errorMsg = data.message || t('verification_failed');

            showStatus(`❌ ${errorMsg}`, 'error');

            showMessageModal(t('verification_failed'), t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(`❌ ${errorMsg}`, 'error');

        showMessageModal(t('verification_failed'), `❌ ${errorMsg}`, 'error');

    }

}

async function testCredential(filename) {

    try {

        // Comment translated/cleaned for compliance

        showStatus(t('testing_credentials_please_wait'), 'info');

        const response = await fetch(`./ogw/creds/test/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        // Comment translated/cleaned for compliance

        const data = await response.json();

        if (response.status === 200) {

            // Comment translated/cleaned for compliance

            const successMsg = `✅ ${t('status_action_success', {action: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n${t('log_status_label')}: ${data.message || t('credential_available')} (${data.status_code || 200})`;

            showStatus(t('test_successful'), 'success');

            showMessageModal(t('test_successful_dup'), successMsg, 'success');

            await AppState.creds.refresh();

        }

        else {

            // Comment translated/cleaned for compliance

            let errorDetails = `❌ ${t('status_action_failed', {error: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n`;

            // Comment translated/cleaned for compliance

            if (data.error) {

                try {

                    // Comment translated/cleaned for compliance

                    const errorObj = JSON.parse(data.error);

                    errorDetails += t('nerror_detailsnjsonstringifyerrorob', {JSON_stringify_errorObj__null__2: JSON.stringify(errorObj, null, 2)});

                } catch {

                    // Comment translated/cleaned for compliance

                    errorDetails += t('nerror_detailsndataerror', {data_error: data.error});

                }

            } else {

                errorDetails += t('error_code_datastatus_code_response', {data_status_code____response_status: data.status_code || response.status});

            }

            showStatus(`Test Failed - ${data.message || t('error_code_prefix') + (data.status_code || response.status)}`, 'error');

            showMessageModal(t('test_failed'), errorDetails, 'error');

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(`❌ ${errorMsg}`, 'error');

        showMessageModal(t('test_failed'), `❌ ${errorMsg}`, 'error');

    }

}

async function testOmniCredential(filename) {

    try {

        // Comment translated/cleaned for compliance

        showStatus(t('testing_omni_credentials_ple'), 'info');

        const response = await fetch(`./ogw/creds/test/${encodeURIComponent(filename)}?mode=omni`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        // Comment translated/cleaned for compliance

        const data = await response.json();

        if (response.status === 200) {

            // Comment translated/cleaned for compliance

            const successMsg = `✅ ${t('status_action_success', {action: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n${t('log_status_label')}: ${data.message || t('omni_credential_valid')} (${data.status_code || 200})`;

            showStatus(t('test_successful'), 'success');

            showMessageModal(t('test_successful_dup'), successMsg, 'success');

            await AppState.omniCreds.refresh();

        }

        else {

            // Comment translated/cleaned for compliance

            let errorDetails = `❌ ${t('status_action_failed', {error: t('btn_message_test')})}\n${t('table_filename')}: ${filename}\n`;

            // Comment translated/cleaned for compliance

            if (data.error) {

                try {

                    // Comment translated/cleaned for compliance

                    const errorObj = JSON.parse(data.error);

                    errorDetails += t('nerror_detailsnjsonstringifyerrorob', {JSON_stringify_errorObj__null__2: JSON.stringify(errorObj, null, 2)});

                } catch {

                    // Comment translated/cleaned for compliance

                    errorDetails += t('nerror_detailsndataerror', {data_error: data.error});

                }

            } else {

                errorDetails += t('error_code_datastatus_code_response', {data_status_code____response_status: data.status_code || response.status});

            }

            showStatus(`Test Failed - ${data.message || t('error_code_prefix') + (data.status_code || response.status)}`, 'error');

            showMessageModal(t('test_failed'), errorDetails, 'error');

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(`❌ ${errorMsg}`, 'error');

        showMessageModal(t('test_failed'), `❌ ${errorMsg}`, 'error');

    }

}

async function configurePreviewChannel(filename) {

    try {

        // Comment translated/cleaned for compliance

        showStatus(t('configuring_preview_channel_please'), 'info');

        const response = await fetch(`./ogw/creds/configure-preview/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            // Comment translated/cleaned for compliance

            const successMsg = `✅ ${t('status_action_success', {action: t('btn_setup_preview')})}\n${t('table_filename')}: ${filename}\n${t('log_status_label')}: ${data.message}`;

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal(t('preview_channel_configuration_succe_dup'), `✅ ${t('status_action_success', {action: t('btn_setup_preview')})}\n\n${t('table_filename')}: ${filename}\n\n${data.message}\n\nSetting ID: ${data.setting_id || 'N/A'}\nBinding ID: ${data.binding_id || 'N/A'}`, 'success');

            // Comment translated/cleaned for compliance

            await AppState.creds.refresh();

        } else {

            // Comment translated/cleaned for compliance

            const errorMsg = data.message || t('configuration_failed');

            const errorDetail = data.error || '';

            const step = data.step || '';

            let alertMsg = `❌ ${t('status_action_failed', {error: t('btn_setup_preview')})}\n\n${t('table_filename')}: ${filename}\n\n${errorMsg}`;

            if (step) {

                alertMsg += t('nfailed_step_step', {step: step});

            }

            if (errorDetail) {

                alertMsg += t('nnerror_details_errordetail', {errorDetail: errorDetail});

            }

            showStatus(`❌ ${errorMsg}`, 'error');

            showMessageModal(t('preview_channel_configuration_faile_dup'), alertMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_configure_preview_channel', {error_message: error.message});

        showStatus(`❌ ${errorMsg}`, 'error');

        showMessageModal(t('failed_to_configure_preview_channel_dup'), `❌ ${errorMsg}`, 'error');

    }

}

async function toggleOmniQuotaDetails(pathId) {

    const quotaDetails = document.getElementById('quota-' + pathId);

    if (!quotaDetails) return;

    // Comment translated/cleaned for compliance

    const isShowing = quotaDetails.style.display === 'block';

    if (isShowing) {

        // Comment translated/cleaned for compliance

        quotaDetails.style.display = 'none';

    } else {

        // Comment translated/cleaned for compliance

        quotaDetails.style.display = 'block';

        const contentDiv = quotaDetails.querySelector('.cred-quota-content');

        const filename = contentDiv.getAttribute('data-filename');

        // Comment translated/cleaned for compliance

        if (filename) {

            contentDiv.innerHTML = t('div_styletextalign_center_padding_2_dup_dup_dup_dup_dup');

            try {

                const response = await fetch(`./ogw/creds/quota/${encodeURIComponent(filename)}?mode=omni`, {

                    method: 'GET',

                    headers: getAuthHeaders()

                });

                const data = await response.json();

                if (response.ok && data.success) {

                    // Comment translated/cleaned for compliance

                    const models = data.models || {};

                    if (Object.keys(models).length === 0) {

                        contentDiv.innerHTML = `

                            <div style="text-align: center; padding: 20px; color: #999;">

                                <div style="font-size: 48px; margin-bottom: 10px;">📊</div>

                                <div>${t('status_no_quota_info')}</div>

                            </div>

                        `;

                    } else {

                        let quotaHTML = `

                            <div style="background: var(--bg-subtle); color: var(--text-primary); padding: 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 15px;">

                                <h4 style="margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px;">

                                    <span style="font-size: 20px;">📊</span>

                                    <span>${t('quota_details')}</span>

                                </h4>

                                <div style="font-size: 12px; color: var(--text-muted); margin-top: 5px;">${t('table_filename')}: ${filename}</div>

                            </div>

                            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">

                        `;

                        for (const [modelName, quotaData] of Object.entries(models)) {

                            // Comment translated/cleaned for compliance

                            const remainingFraction = quotaData.remaining || 0;

                            const resetTime = quotaData.resetTime || 'N/A';

                            // Comment translated/cleaned for compliance

                            const usedPercentage = Math.round((1 - remainingFraction) * 100);

                            const remainingPercentage = Math.round(remainingFraction * 100);

                            // Comment translated/cleaned for compliance

                            let percentageColor = '#28a745'; // Comment translated/cleaned for compliance

                            if (usedPercentage >= 90) percentageColor = '#dc3545'; // Comment translated/cleaned for compliance

                            else if (usedPercentage >= 70) percentageColor = '#ffc107'; // Comment translated/cleaned for compliance

                            else if (usedPercentage >= 50) percentageColor = '#17a2b8'; // Comment translated/cleaned for compliance

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

                    // Comment translated/cleaned for compliance

                    const errorMsg = data.error || t('failed_to_get_quota_information');

                    contentDiv.innerHTML = `

                        <div style="text-align: center; padding: 20px; color: #dc3545;">

                            <div style="font-size: 48px; margin-bottom: 10px;">❌</div>

                            <div style="font-weight: bold; margin-bottom: 5px;">${t('status_quota_failed')}</div>

                            <div style="font-size: 13px; color: #666;">${errorMsg}</div>

                        </div>

                    `;

                    showStatus(`❌ ${errorMsg}`, 'error');

                }

            } catch (error) {

                contentDiv.innerHTML = `

                    <div style="text-align: center; padding: 20px; color: #dc3545;">

                        <div style="font-size: 48px; margin-bottom: 10px;">❌</div>

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

// Comment translated/cleaned for compliance

// =====================================================================

async function toggleErrorDetails(pathId) {

    await toggleErrorDetailsCommon(pathId, AppState.creds);

}

async function toggleOmniErrorDetails(pathId) {

    await toggleErrorDetailsCommon(pathId, AppState.omniCreds);

}

async function toggleErrorDetailsCommon(pathId, manager) {

    const errorDetails = document.getElementById('errors-' + pathId);

    if (!errorDetails) return;

    // Comment translated/cleaned for compliance

    const isShowing = errorDetails.classList.toggle('show');

    if (isShowing) {

        const contentDiv = errorDetails.querySelector('.cred-content');

        const filename = contentDiv.getAttribute('data-filename');

        // Comment translated/cleaned for compliance

        if (filename) {

            contentDiv.innerHTML = t('div_styletextalign_center_padding_2_dup_dup_dup_dup_dup_dup');

            try {

                const modeParam = manager.type === 'omni' ? 'mode=omni' : 'mode=code_assist';

                const response = await fetch(`./ogw/creds/errors/${encodeURIComponent(filename)}?${modeParam}`, {

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

                                <div style="font-size: 48px; margin-bottom: 10px;">✅</div>

                                <div style="font-weight: bold;">${t('status_no_errors')}</div>

                                <div style="font-size: 12px; color: #666; margin-top: 8px;">${t('status_credential_normal')}</div>

                            </div>

                        `;

                    } else {

                        let errorHTML = '';

                        // Comment translated/cleaned for compliance

                        errorCodes.forEach((errorCode) => {

                            const messageStr = errorMessages[errorCode] || t('no_details_available');

                            // Comment translated/cleaned for compliance

                            let displayMsg = messageStr;

                            let detailsHtml = '';

                            try {

                                // Comment translated/cleaned for compliance

                                const parsedMsg = JSON.parse(messageStr);

                                if (parsedMsg.error) {

                                    // Comment translated/cleaned for compliance

                                    if (parsedMsg.error.message) {

                                        displayMsg = parsedMsg.error.message;

                                    }

                                    // Comment translated/cleaned for compliance

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

                                            // Comment translated/cleaned for compliance

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

                                    // Comment translated/cleaned for compliance

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

                                // Comment translated/cleaned for compliance

                            }

                            // Comment translated/cleaned for compliance

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

                    // Comment translated/cleaned for compliance

                    const errorMsg = data.detail || data.error || t('failed_to_fetch_error_message');

                    contentDiv.innerHTML = `

                        <div style="text-align: center; padding: 20px; color: #dc3545;">

                            <div style="font-size: 48px; margin-bottom: 10px;">❌</div>

                            <div style="font-weight: bold;">${t('status_load_failed')}</div>

                            <div style="font-size: 12px; margin-top: 8px;">${errorMsg}</div>

                        </div>

                    `;

                    showStatus(t('failed_to_fetch_error_message_error', {errorMsg: errorMsg}), 'error');

                }

            } catch (error) {

                contentDiv.innerHTML = `

                    <div style="text-align: center; padding: 20px; color: #dc3545;">

                        <div style="font-size: 48px; margin-bottom: 10px;">❌</div>

                        <div style="font-weight: bold;">${t('net_error')}</div>

                        <div style="font-size: 12px; margin-top: 8px;">${error.message}</div>

                    </div>

                `;

                showStatus(t('failed_to_fetch_error_information_e', {error_message: error.message}), 'error');

            }

        }

    }

}

// Comment translated/cleaned for compliance

function escapeHtml(text) {

    const div = document.createElement('div');

    div.textContent = text;

    return div.innerHTML;

}

// Comment translated/cleaned for compliance

function highlightHttpLinks(text) {

    // Comment translated/cleaned for compliance

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

    if (!confirm(t('are_you_sure_you_want_to_batch_veri_dup', {selectedFiles_length: selectedFiles.length}))) {

        return;

    }

    showStatus(t('parallel_verifying_selectedfileslen', {selectedFiles_length: selectedFiles.length}), 'info');

    // Comment translated/cleaned for compliance

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./ogw/creds/verify-project/${encodeURIComponent(filename)}`, {

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

    // Comment translated/cleaned for compliance

    const results = await Promise.all(promises);

    // Comment translated/cleaned for compliance

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            const creditSuffix = result.creditAmount !== undefined && result.creditAmount !== null

                ? ` (${t('credits_label')}: ${result.creditAmount})`

                : '';

            resultMessages.push(`✅ ${result.filename}: ${result.projectId}${creditSuffix}`);

        } else {

            failCount++;

            resultMessages.push(`❌ ${result.filename}: ${result.error}`);

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

async function batchVerifyOmniProjectIds() {

    const selectedFiles = Array.from(AppState.omniCreds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_omni_crede_dup'), 'error');

        showMessageModal(t('tip'), t('please_select_the_omni_crede'), 'error');

        return;

    }

    if (!confirm(t('are_you_sure_you_want_to_batch_veri', {selectedFiles_length: selectedFiles.length}))) {

        return;

    }

    showStatus(t('parallel_testing_selectedfileslengt', {selectedFiles_length: selectedFiles.length}), 'info');

    // Comment translated/cleaned for compliance

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./ogw/creds/verify-project/${encodeURIComponent(filename)}?mode=omni`, {

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

    // Comment translated/cleaned for compliance

    const results = await Promise.all(promises);

    // Comment translated/cleaned for compliance

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            const creditSuffix = result.creditAmount !== undefined && result.creditAmount !== null

                ? ` (${t('credits_label')}: ${result.creditAmount})`

                : '';

            resultMessages.push(`✅ ${result.filename}: ${result.projectId}${creditSuffix}`);

        } else {

            failCount++;

            resultMessages.push(`❌ ${result.filename}: ${result.error}`);

        }

    });

    await AppState.omniCreds.refresh();

    const summary = t('omni_batch_verification_comp_dup', {successCount: successCount, failCount: failCount, selectedFiles_length: selectedFiles.length, resultMessages_join___n: resultMessages.join('\n')});

    if (failCount === 0) {

        showStatus(t('all_verifications_successful_verifi', {successCount: successCount, selectedFiles_length: selectedFiles.length}), 'success');

        showMessageModal(t('omni_batch_verification_comp'), summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('verification_failed_for_all_failed', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal(t('omni_batch_verification_comp'), summary, 'error');

    } else {

        showStatus(t('batch_verification_completed_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal(t('omni_batch_verification_comp'), summary, 'info');

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

    if (!confirm(t('are_you_sure_you_want_to_batch_set', {selectedFiles_length: selectedFiles.length}))) {

        return;

    }

    showStatus(t('configuring_preview_channel_for_sel', {selectedFiles_length: selectedFiles.length}), 'info');

    // Comment translated/cleaned for compliance

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./ogw/creds/configure-preview/${encodeURIComponent(filename)}`, {

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

    // Comment translated/cleaned for compliance

    const results = await Promise.all(promises);

    // Comment translated/cleaned for compliance

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

            resultMessages.push(`❌ ${result.filename}: ${errorMsg}`);

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

    if (!confirm(t('are_you_sure_you_want_to_refresh_us'))) return;

    try {

        showStatus(t('refreshing_all_user_emails'), 'info');

        const response = await fetch('./ogw/creds/refresh-all-emails', {

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

async function refreshAllOmniEmails() {

    if (!confirm(t('are_you_sure_you_want_to_refresh_us_dup'))) return;

    try {

        showStatus(t('refreshing_all_user_emails'), 'info');

        const response = await fetch('./ogw/creds/refresh-all-emails?mode=omni', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            showStatus(t('email_refresh_complete_successfully', {data_success_count: data.success_count, data_total_count: data.total_count}), 'success');

            await AppState.omniCreds.refresh();

        } else {

            showStatus(data.message || t('failed_to_refresh_emails'), 'error');

        }

    } catch (error) {

        showStatus(t('email_refresh_network_error_errorme', {error_message: error.message}), 'error');

    }

}

async function deduplicateByEmail() {

    if (!confirm(t('are_you_sure_you_want_to_perform_on'))) return;

    try {

        showStatus(t('oneclick_credential_deduplication_i'), 'info');

        const response = await fetch('./ogw/creds/deduplicate-by-email', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            const msg = t('deduplication_complete_deleted_data', {data_deleted_count: data.deleted_count, data_kept_count: data.kept_count, data_unique_emails_count: data.unique_emails_count});

            showStatus(msg, 'success');

            await AppState.creds.refresh();

            // Comment translated/cleaned for compliance

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

async function deduplicateOmniByEmail() {

    if (!confirm(t('are_you_sure_you_want_to_deduplicat'))) return;

    try {

        showStatus(t('oneclick_credential_deduplication_i'), 'info');

        const response = await fetch('./ogw/creds/deduplicate-by-email?mode=omni', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            const msg = t('deduplication_complete_deleted_data', {data_deleted_count: data.deleted_count, data_kept_count: data.kept_count, data_unique_emails_count: data.unique_emails_count});

            showStatus(msg, 'success');

            await AppState.omniCreds.refresh();

            // Comment translated/cleaned for compliance

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

// Comment translated/cleaned for compliance

// =====================================================================

function connectWebSocket() {

    if (AppState.logWebSocket && AppState.logWebSocket.readyState === WebSocket.OPEN) {

        // showStatus(t('websocket_connected'), 'info');

        return;

    }

    try {

        const wsPath = new URL('./ogw/logs/stream', window.location.href).href;

        const wsUrl = wsPath.replace(/^http/, 'ws');

        // Comment translated/cleaned for compliance

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

        const response = await fetch('./ogw/logs/download', { headers: getAuthHeaders() });

        if (response.ok) {

            const contentDisposition = response.headers.get('Content-Disposition');

            let filename = 'ogw_logs.txt';

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

        const response = await fetch('./ogw/logs/clear', {

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

// Comment translated/cleaned for compliance

// =====================================================================

async function checkEnvCredsStatus() {

    const loading = document.getElementById('envStatusLoading');

    const content = document.getElementById('envStatusContent');

    try {

        loading.style.display = 'block';

        content.classList.add('hidden');

        const response = await fetch('./ogw/auth/env-creds-status', { headers: getAuthHeaders() });

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

        const response = await fetch('./ogw/auth/load-env-creds', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            if (data.loaded_count > 0) {

                showStatus(t('successfully_imported_dataloaded_co', {data_loaded_count: data.loaded_count, data_total_count: data.total_count}), 'success');

                setTimeout(() => checkEnvCredsStatus(), 1000);

            } else {

                showStatus(`⚠️ ${data.message}`, 'info');

            }

        } else {

            showStatus(t('import_failed_datadetail_dataerror', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function clearEnvCredentials() {

    if (!confirm(t('are_you_sure_you_want_to_clear_all'))) {

        return;

    }

    try {

        showStatus(t('clearing_environment_variable_crede'), 'info');

        const response = await fetch('./ogw/auth/env-creds', {

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

// Comment translated/cleaned for compliance

// =====================================================================

const CONFIG_FIELD_KEYS = {
    host: 'ogw_host',
    port: 'ogw_port',
    configApiPassword: 'ogw_api_password',
    configPanelPassword: 'ogw_panel_password',
    configPassword: 'ogw_password',
    credentialsDir: 'ogw_credentials_dir',
    proxy: 'ogw_proxy',
    codeAssistEndpoint: 'ogw_code_assist_endpoint',
    oauthProxyUrl: 'ogw_oauth_url',
    googleapisProxyUrl: 'ogw_google_apis_url',
    resourceManagerApiUrl: 'ogw_resource_manager_url',
    serviceUsageApiUrl: 'ogw_service_usage_url',
    omniApiUrl: 'ogw_api_url',
    autoBanEnabled: 'ogw_auto_disable_enabled',
    autoBanErrorCodes: 'ogw_auto_disable_error_codes',
    retry429Enabled: 'ogw_retry_429_enabled',
    retry429MaxRetries: 'ogw_retry_429_max_retries',
    retry429Interval: 'ogw_retry_429_interval',
    compatibilityModeEnabled: 'ogw_compatibility_mode_enabled',
    returnThoughtsToFrontend: 'ogw_return_thoughts_to_frontend',
    omniStreamToNonstream: 'ogw_stream_to_nonstream',
    omniSwitchCredentialEnabled: 'ogw_switch_credential_enabled',
    antiTruncationMaxAttempts: 'ogw_anti_truncation_max_attempts',
    keepaliveUrl: 'ogw_keepalive_url',
    keepaliveInterval: 'ogw_keepalive_interval'
};

async function loadConfig() {

    const loading = document.getElementById('configLoading');

    const form = document.getElementById('configForm');

    try {

        loading.style.display = 'block';

        form.classList.add('hidden');

        const response = await fetch('./ogw/config/get', { headers: getAuthHeaders() });

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

    setConfigField('host', c.ogw_host || '0.0.0.0');

    setConfigField('port', c.ogw_port || 7861);

    setConfigField('configApiPassword', c.ogw_api_password || '');

    setConfigField('configPanelPassword', c.ogw_panel_password || '');

    setConfigField('configPassword', c.ogw_password || 'pwd');

    setConfigField('credentialsDir', c.ogw_credentials_dir || '');

    setConfigField('proxy', c.ogw_proxy || '');

    setConfigField('codeAssistEndpoint', c.ogw_code_assist_endpoint || '');

    setConfigField('oauthProxyUrl', c.ogw_oauth_url || '');

    setConfigField('googleapisProxyUrl', c.ogw_google_apis_url || '');

    setConfigField('resourceManagerApiUrl', c.ogw_resource_manager_url || '');

    setConfigField('serviceUsageApiUrl', c.ogw_service_usage_url || '');

    setConfigField('omniApiUrl', c.ogw_api_url || '');

    setConfigCheckbox('autoBanEnabled', Boolean(c.ogw_auto_disable_enabled));

    setConfigField('autoBanErrorCodes', (c.ogw_auto_disable_error_codes || []).join(','));

    setConfigCheckbox('retry429Enabled', Boolean(c.ogw_retry_429_enabled));

    setConfigField('retry429MaxRetries', c.ogw_retry_429_max_retries || 20);

    setConfigField('retry429Interval', c.ogw_retry_429_interval || 0.1);

    setConfigCheckbox('compatibilityModeEnabled', Boolean(c.ogw_compatibility_mode_enabled));

    setConfigCheckbox('returnThoughtsToFrontend', Boolean(c.ogw_return_thoughts_to_frontend !== false));

    setConfigCheckbox('omniStreamToNonstream', Boolean(c.ogw_stream_to_nonstream !== false));

    setConfigCheckbox('omniSwitchCredentialEnabled', Boolean(c.ogw_switch_credential_enabled));

    setConfigField('antiTruncationMaxAttempts', c.ogw_anti_truncation_max_attempts || 3);

    setConfigField('keepaliveUrl', c.ogw_keepalive_url || '');

    setConfigField('keepaliveInterval', c.ogw_keepalive_interval || 60);

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

            ogw_host: getValue('host', '0.0.0.0'),

            ogw_port: getInt('port', 7861),

            ogw_api_password: getValue('configApiPassword'),

            ogw_panel_password: getValue('configPanelPassword'),

            ogw_password: getValue('configPassword', 'pwd'),

            ogw_code_assist_endpoint: getValue('codeAssistEndpoint'),

            ogw_credentials_dir: getValue('credentialsDir'),

            ogw_proxy: getValue('proxy'),

            ogw_oauth_url: getValue('oauthProxyUrl'),

            ogw_google_apis_url: getValue('googleapisProxyUrl'),

            ogw_resource_manager_url: getValue('resourceManagerApiUrl'),

            ogw_service_usage_url: getValue('serviceUsageApiUrl'),

            ogw_api_url: getValue('omniApiUrl'),

            ogw_auto_disable_enabled: getChecked('autoBanEnabled'),

            ogw_auto_disable_error_codes: getValue('autoBanErrorCodes').split(',')

                .map(c => parseInt(c.trim())).filter(c => !isNaN(c)),

            ogw_retry_429_enabled: getChecked('retry429Enabled'),

            ogw_retry_429_max_retries: getInt('retry429MaxRetries', 20),

            ogw_retry_429_interval: getFloat('retry429Interval', 0.1),

            ogw_compatibility_mode_enabled: getChecked('compatibilityModeEnabled'),

            ogw_return_thoughts_to_frontend: getChecked('returnThoughtsToFrontend'),

            ogw_stream_to_nonstream: getChecked('omniStreamToNonstream'),

            ogw_switch_credential_enabled: getChecked('omniSwitchCredentialEnabled'),

            ogw_anti_truncation_max_attempts: getInt('antiTruncationMaxAttempts', 3),

            ogw_keepalive_url: getValue('keepaliveUrl'),

            ogw_keepalive_interval: getInt('keepaliveInterval', 60)

        };

        const response = await fetch('./ogw/config/save', {

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

// Comment translated/cleaned for compliance

const mirrorUrls = {

    codeAssistEndpoint: 'https://cloudcode-pa.googleapis.com',

    oauthProxyUrl: 'https://oauth2.googleapis.com',

    googleapisProxyUrl: 'https://www.googleapis.com',

    resourceManagerApiUrl: 'https://cloudresourcemanager.googleapis.com',

    serviceUsageApiUrl: 'https://serviceusage.googleapis.com',

    omniApiUrl: 'https://daily-cloudcode-pa.googleapis.com'

};

const officialUrls = {

    codeAssistEndpoint: 'https://cloudcode-pa.googleapis.com',

    oauthProxyUrl: 'https://oauth2.googleapis.com',

    googleapisProxyUrl: 'https://www.googleapis.com',

    resourceManagerApiUrl: 'https://cloudresourcemanager.googleapis.com',

    serviceUsageApiUrl: 'https://serviceusage.googleapis.com',

    omniApiUrl: 'https://daily-cloudcode-pa.googleapis.com'

};

function useMirrorUrls() {

    if (confirm(t('are_you_sure_you_want_to_configure_dup'))) {

        for (const [fieldId, url] of Object.entries(mirrorUrls)) {

            const field = document.getElementById(fieldId);

            if (field && !field.disabled) field.value = url;

        }

        showStatus(t('switched_to_mirror_url_configuratio'), 'success');

    }

}

function restoreOfficialUrls() {

    if (confirm(t('are_you_sure_you_want_to_configure'))) {

        for (const [fieldId, url] of Object.entries(officialUrls)) {

            const field = document.getElementById(fieldId);

            if (field && !field.disabled) field.value = url;

        }

        showStatus(t('switched_to_official_endpoint_confi'), 'success');

    }

}

// =====================================================================

// Comment translated/cleaned for compliance

// =====================================================================

async function refreshUsageStats() {

    const loading = document.getElementById('usageLoading');

    const list = document.getElementById('usageList');

    try {

        loading.style.display = 'block';

        list.innerHTML = '';

        const [statsResponse, aggregatedResponse] = await Promise.all([

            fetch('./ogw/usage/stats', { headers: getAuthHeaders() }),

            fetch('./ogw/usage/aggregated', { headers: getAuthHeaders() })

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

        tr.innerHTML = `<td colspan="3" style="text-align: center; color: var(--color-mute); padding: var(--spacing-lg) 0;">${t('status_no_filter_data')}</td>`;

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

    if (!confirm(t('confirm_reset_stats', {filename: filename}))) return;

    try {

        const response = await fetch('./ogw/usage/reset', {

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

    if (!confirm(t('are_you_sure_you_want_to_reset_usag_dup'))) return;

    try {

        const response = await fetch('./ogw/usage/reset', {

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

// Comment translated/cleaned for compliance

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

    // Comment translated/cleaned for compliance

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

    // Comment translated/cleaned for compliance

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

// Comment translated/cleaned for compliance

// =====================================================================

// Comment translated/cleaned for compliance

async function fetchAndDisplayVersion() {

    try {

        const response = await fetch('./ogw/version/info');

        const data = await response.json();

        const versionText = document.getElementById('versionText');

        if (data.success) {

            // Comment translated/cleaned for compliance

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

// Comment translated/cleaned for compliance

async function checkForUpdates() {

    const checkBtn = document.getElementById('checkUpdateBtn');

    if (!checkBtn) return;

    const originalText = checkBtn.textContent;

    try {

        // Comment translated/cleaned for compliance

        checkBtn.textContent = t('checking');

        checkBtn.disabled = true;

        // Comment translated/cleaned for compliance

        const response = await fetch('./ogw/version/info?check_update=true');

        const data = await response.json();

        if (data.success) {

            if (data.check_update === false) {

                // Comment translated/cleaned for compliance

                showStatus(t('check_for_updates_failed_dataupdate', {data_update_error: data.update_error || t('unknown_error')}), 'error');

            } else if (data.has_update === true) {

                // Comment translated/cleaned for compliance

                const updateMsg = t('new_version_foundncurrent_vdatavers', {data_version: data.version, data_latest_version: data.latest_version, data_latest_message: data.latest_message || t('none')});

                showStatus(updateMsg.replace(/\n/g, ' '), 'warning');

                // Comment translated/cleaned for compliance

                checkBtn.style.backgroundColor = '#ffc107';

                checkBtn.textContent = t('new_version_available');

                setTimeout(() => {

                    checkBtn.style.backgroundColor = '#17a2b8';

                    checkBtn.textContent = originalText;

                }, 5000);

            } else if (data.has_update === false) {

                // Comment translated/cleaned for compliance

                showStatus(t('already_up_to_date'), 'success');

                checkBtn.style.backgroundColor = '#28a745';

                checkBtn.textContent = t('already_up_to_date_dup');

                setTimeout(() => {

                    checkBtn.style.backgroundColor = '#17a2b8';

                    checkBtn.textContent = originalText;

                }, 3000);

            } else {

                // Comment translated/cleaned for compliance

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

// Comment translated/cleaned for compliance

// =====================================================================

window.onload = async function () {

    // popstate listener

    window.addEventListener('popstate', () => {

        navigate(window.location.pathname, false);

    });

    const autoLoginSuccess = await autoLogin();

    if (autoLoginSuccess) {

        await fetchAndDisplayVersion();

    }

    startCooldownTimer();

    const omniAuthBtn = document.getElementById('getOmniAuthBtn');

    if (omniAuthBtn) {

        omniAuthBtn.addEventListener('click', startOmniAuth);

    }

};

// Comment translated/cleaned for compliance

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
