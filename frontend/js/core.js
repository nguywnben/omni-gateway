// Omni Gateway management console: core.

const TRANSLATIONS = {
    en: {
        "a_hrefurl_target_blank_stylecolor_0": "<a href=\"{url}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"message-link\" title=\"Open link: {url}\">{url}</a>",
        "action_delete": "Delete",
        "action_disable": "Disable",
        "action_disable_credit": "Disable credits",
        "action_enable": "Enable",
        "action_enable_credit": "Enable credits",
        "all_configured_successfully_preview": "Preview channel configured for {successCount}/{selectedFiles_length} credentials.",
        "all_credential_files_have_been_down": "Downloaded all credential files.",
        "all_primary_credentials_packed": "Downloaded all provider credentials.",
        "all_verifications_failed_failed_fai": "All verifications failed. Failed {failCount}/{selectedFiles_length} credentials.",
        "all_verifications_successful_succes": "All verifications passed. Verified {successCount}/{selectedFiles_length} credentials.",
        "all_verifications_successful_verifi": "All verifications passed. Verified {successCount}/{selectedFiles_length} provider credentials.",
        "already_up_to_date": "Already up to date.",
        "already_up_to_date_dup": "Already up to date.",
        "are_you_sure_you_want_to_batch_set": "Configure the Preview channel for {selectedFiles_length} credentials?\\n\\nThis operation will run in parallel.",
        "are_you_sure_you_want_to_batch_veri": "Verify Project IDs for {selectedFiles_length} provider credentials?\\n\\nThis operation will run in parallel.",
        "are_you_sure_you_want_to_batch_veri_dup": "Verify Project IDs for {selectedFiles_length} credentials?\\n\\nThis operation will run in parallel.",
        "are_you_sure_you_want_to_clear_all": "Clear all credential files imported from environment variables?\\nThis will delete authentication files that start with \"env-\".",
        "are_you_sure_you_want_to_deduplicat": "Deduplicate provider credentials?\\n\\nOnly one credential per email will be kept, and all others will be deleted.\\nThis action cannot be undone.",
        "are_you_sure_you_want_to_delete_fil_dup": "Are you sure you want to delete {filename}?",
        "are_you_sure_you_want_to_perform_on": "Deduplicate credentials now?\\n\\nOnly one credential per email will be kept, and all others will be deleted.\\nThis action cannot be undone.",
        "are_you_sure_you_want_to_refresh_us": "Refresh user emails for all credentials? This may take some time.",
        "are_you_sure_you_want_to_refresh_us_dup": "Refresh user emails for all provider credentials? This may take some time.",
        "attempting_to_autodetect_project_id": "Attempting to auto-detect the Project ID and generate an authentication link...",
        "authentication_failed_please_log_in": "Authentication failed. Please sign in again.",
        "authentication_link_generated_proje": "Authentication link generated for Project ID {data_detected_project_id}. Click the link to complete authorization.",
        "authentication_link_generated_proje_dup_dup": "Authentication link generated. The Project ID will be detected after authorization. Click the link to complete authorization.",
        "authentication_successful_file_save": "Authentication successful. File saved to: {data_file_path}.",
        "authentication_successful_project_i_dup": "Authentication successful. Project ID automatically detected as {data_credentials_project_id}. File saved to: {data_file_path}.",
        "autologin_successful": "Signed in automatically.",
        "batch_configuration_complete_succes": "Batch configuration complete: {successCount}/{selectedFiles_length} succeeded, {failCount} failed.",
        "batch_preview_channel_configuration": "Batch Preview channel configuration complete.\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",
        "batch_verification_completed_succes": "Batch verification completed: {successCount}/{selectedFiles_length} succeeded, {failCount} failed.",
        "batch_verification_completennsucces": "Batch verification complete.\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",
        "brstrongavailable_projectsstrongbr": "<br><strong>Available projects:</strong><br>",
        "btn_cancel": "Cancel",
        "btn_clear_credentials": "Clear credentials",
        "btn_close": "Close",
        "btn_configure": "Configure",
        "btn_continue": "Continue",
        "btn_deduplicate": "Deduplicate",
        "btn_disable_credit": "Disable credits",
        "btn_disable_credit_title": "Prevent this credential from using available Google One AI credits.",
        "btn_download": "Download",
        "btn_enable_credit": "Enable credits",
        "btn_enable_credit_title": "Allow this credential to use available Google One AI credits.",
        "btn_test_model": "Test model",
        "btn_test_model_title": "Select a model and test it with this credential.",
        "btn_test_another_model": "Test another model",
        "btn_refresh": "Refresh",
        "btn_regenerate": "Regenerate",
        "btn_reset_defaults": "Reset defaults",
        "btn_setup_preview": "Configure Preview",
        "btn_setup_preview_title": "Configure the Preview channel and enable experimental features.",
        "btn_verify_id": "Verify access",
        "btn_verify_credentials": "Verify credentials",
        "btn_verify_id_title": "Verify this credential and refresh its provider metadata.",
        "btn_view_content": "View details",
        "btn_view_content_title": "View the stored details and payload for this credential.",
        "btn_view_errors": "View errors",
        "btn_view_errors_title": "View detailed error messages for this credential.",
        "btn_view_models": "View models",
        "btn_view_models_title": "View models available through this credential.",
        "btn_view_quota": "View quota",
        "btn_view_quota_title": "View quota usage information for this credential.",
        "bulk_preview_channel_configuration": "Bulk Preview channel configuration complete",
        "card_loading_errors": "Loading error details...",
        "card_loading_quota": "Loading quota details...",
        "check_for_updates_failed_dataupdate": "Update check failed: {data_update_error}",
        "checking": "Checking...",
        "checking_provider_authorization": "Checking authorization status...",
        "clear_failed_datadetail_dataerror_u": "Clear failed: {data_detail____data_error}",
        "clearing_environment_variable_crede": "Clearing environment variable credential files...",
        "click_to_open_link": "Click to open link",
        "code_assist_creds__environment_variable_no": "No Code Assist credential environment variables found.",
        "configuration_failed": "Configuration failed",
        "configuration_failed_for_all_failed": "Configuration failed for all credentials. Failed {failCount}/{selectedFiles_length} credentials.",
        "configuration_loaded_successfully": "Configuration loaded.",
        "configuration_saved_successfully": "Configuration saved.",
        "configuration_successful": "Configuration successful.",
        "configuring_preview_channel_for_sel": "Configuring Preview channel for {selectedFiles_length} credentials. Please wait...",
        "configuring_preview_channel_please": "Configuring Preview channel. Please wait...",
        "confirm_batch_enable": "Enable {count} selected credentials?",
        "confirm_batch_disable": "Disable {count} selected credentials?",
        "confirm_batch_delete": "Delete {count} selected credentials? Their secrets and pool state will be removed. Historical usage will be retained anonymously. This action cannot be undone.",
        "confirm_batch_enable_credit": "Allow {count} selected credentials to use available Google One AI credits?",
        "confirm_batch_disable_credit": "Prevent {count} selected credentials from using available Google One AI credits?",
        "confirm_batch_enable_title": "Enable Credentials",
        "confirm_batch_disable_title": "Disable Credentials",
        "confirm_batch_delete_title": "Delete Credentials",
        "confirm_batch_enable_credit_title": "Enable Credit Usage",
        "confirm_batch_disable_credit_title": "Disable Credit Usage",
        "confirm_delete_cred": "Delete this credential? Its secrets and pool state will be removed. Historical usage will be retained anonymously. This action cannot be undone.",
        "confirm_delete_cred_title": "Delete Credential",
        "confirm_clear_logs": "Clear all persisted runtime logs? This action cannot be undone. New log entries will continue to appear as the service runs.",
        "confirm_clear_logs_title": "Clear Runtime Logs",
        "btn_clear_logs": "Clear logs",
        "confirm_regenerate_key": "Regenerate the API key? The current key will become invalid immediately. This action cannot be undone.",
        "confirm_regenerate_key_title": "Regenerate API Key",
        "confirm_verify_credentials_title": "Verify Credentials",
        "confirm_configure_preview_title": "Configure Preview Channel",
        "confirm_refresh_emails_title": "Refresh Credential Emails",
        "confirm_deduplicate_title": "Deduplicate Credentials",
        "confirm_clear_imported_credentials_title": "Clear Imported Credentials",
        "confirm_reset_google_ai_studio_title": "Reset Google AI Studio Settings",
        "confirm_reset_antigravity_title": "Reset Google Antigravity Settings",
        "confirm_reset_system_config_title": "Reset System Configuration",
        "confirm_manage_credentials_title": "Manage Credentials",
        "connected": "Connected",
        "connecting": "Connecting...",
        "connection_error": "Connection error",
        "connection_failed": "Connection failed",
        "connection_lost": "Connection lost",
        "copy_fail": "Copy failed.",
        "copy_success": "Copied to clipboard.",
        "credential_available": "Credential available",
        "credential_rate_limited": "Credential is valid, but the upstream provider is currently rate limited.",
        "credential_status_label": "Status:",
        "credentials_fetched_successfully_fr": "Credentials retrieved from the callback URL.",
        "credit_disabled_title": "Google One AI credit usage is disabled for this credential.",
        "credit_enabled_title": "Google One AI credit usage is enabled for this credential.",
        "credits_label": "Credits",
        "dataexisting_env_files_count_files": "{data_existing_env_files_count} files",
        "deduplication_complete_deleted_data": "Deduplication complete. Deleted {data_deleted_count} duplicate credentials and kept {data_kept_count} credentials ({data_unique_emails_count} unique emails).",
        "deduplication_details_title": "Deduplication Details",
        "deduplication_detailsnn": "Deduplication details:\\n\\n",
        "deduplication_failed": "Deduplication failed.",
        "deduplication_network_error_errorme": "Deduplication network error: {error_message}",
        "deleted_credential": "Deleted credential",
        "dialog_tip": "Tip",
        "disable_only": "Disabled only",
        "disconnected": "Disconnected",
        "download_failed_filename": "Download failed: {filename}",
        "downloaded_filename": "Downloaded: {filename}",
        "email_groupemailnkeep_groupkept_fil": "Email: {group_email}\\nKeep: {group_kept_file}\\nDelete: {group_deleted_files_join}\\n\\n",
        "email_not_fetched": "Email unavailable",
        "email_refresh_complete_successfully": "Email refresh complete. Retrieved {data_success_count}/{data_total_count} email addresses.",
        "email_refresh_network_error_errorme": "Email refresh network error: {error_message}",
        "enable_only": "Enabled only",
        "enabled": "Enabled",
        "environment_variable_status_check_c": "Environment variable status check complete.",
        "error_code_prefix": "Error",
        "error_dataerror_failed_to_fetch_aut": "Failed to fetch the authentication link: {data_error}",
        "error_dataerror_failed_to_generate": "Failed to generate the authentication link: {data_error}",
        "error_dataerror_failed_to_get_authe": "Failed to retrieve the authentication file: {data_error}",
        "error_details": "Error details",
        "error_errormsg": "Error: {errorMsg}",
        "failed": "Failed",
        "failed_to_check_for_updates": "Failed to check for updates:",
        "failed_to_check_for_updates_dataerr": "Failed to check for updates: {data_error}",
        "failed_to_check_for_updates_errorme": "Failed to check for updates: {error_message}",
        "failed_to_clear_logs_datadetail_dat": "Failed to clear logs: {data_detail____data_error}",
        "failed_to_configure_preview_channel": "Failed to configure Preview channel: {error_message}",
        "failed_to_download_logs_datadetail": "Failed to download logs: {data_detail____data_error}",
        "failed_to_download_package_errormes": "Failed to download package: {error_message}",
        "failed_to_fetch_authentication_link": "Failed to fetch authentication link",
        "failed_to_fetch_credentials_from_ca": "Failed to fetch credentials from callback URL",
        "failed_to_fetch_error_information_e": "Failed to fetch error information: {error_message}",
        "failed_to_fetch_error_message": "Failed to fetch error message",
        "failed_to_fetch_error_message_error": "Failed to fetch error message: {errorMsg}",
        "failed_to_fetch_version_information": "Failed to fetch version information",
        "failed_to_generate_authentication_l_dup": "Failed to generate authentication link",
        "failed_to_get_quota_information": "Failed to get quota information.",
        "failed_to_get_quota_information_err": "Failed to get quota information: {error_message}",
        "failed_to_load_configuration_datade": "Failed to load configuration: {data_detail____data_error}",
        "failed_to_load_usage_statistics": "Failed to load usage statistics",
        "failed_to_refresh_emails": "Failed to refresh emails.",
        "failed_to_retrieve_authentication_f_dup": "Failed to retrieve authentication file",
        "failed_to_retrieve_credentials_from_dup": "Failed to retrieve credentials from callback URL: {error_message}",
        "failed_to_retrieve_environment_vari": "Failed to retrieve environment variable status: {data_detail____data_error}",
        "failed_to_retrieve_version_informat": "Failed to retrieve version information:",
        "failed_to_save_config_datadetail_da": "Failed to save configuration: {data_detail____data_error}",
        "fetch_primary_credentials": "Save credentials",
        "fetching_authentication_link": "Fetching authentication link...",
        "full_version_datafull_hashncommit_m": "Full version: {data_full_hash}\\nCommit message: {data_message}\\nCommit time: {data_date}",
        "generating_authentication_link": "Generating authentication link...",
        "generating_authentication_link_usin": "Generating authentication link using the specified Project ID...",
        "generating_primary_authenticati": "Generating provider authentication link...",
        "get_authentication_file": "Get authentication file",
        "get_authentication_link": "Get authentication link",
        "get_primary_authentication_link": "Get provider authentication link",
        "import_failed_datadetail_dataerror": "Import failed: {data_detail____data_error}",
        "importing_credentials_from_environm": "Importing credentials from environment variables...",
        "input_required_title": "Input required",
        "invalid_selection_please_restart_th": "Invalid selection. Please restart the authentication process.",
        "label_json_file": "JSON file",
        "label_zip_pack": "ZIP archive",
        "loaded_usage_statistics_for_aggdata": "Loaded usage statistics for {aggData_total_files____Object_keys_AppState_usageStatsData__length} files",
        "log_file_download_successful_filena": "Log file downloaded: {filename}.",
        "log_stream_connected_successfully": "Log stream connected.",
        "log_stream_connection_disconnected": "Log stream disconnected.",
        "log_stream_connection_disconnected_dup": "Log stream disconnected.",
        "logged_out": "Signed out.",
        "login_failed": "Login failed. Please check your password.",
        "login_failed_incorrect_password": "Incorrect password. Please try again.",
        "login_successful_dup": "Signed in.",
        "logs_cleared_waiting_for_new_logs": "Logs cleared. Waiting for new logs...",
        "manual_project_id_specification_req": "A Google Cloud Project ID is required. Enter it in advanced options and try again.",
        "model_title": "Model",
        "multiple_projects_detected_please_s": "Multiple projects were detected. Specify a Project ID in advanced options:",
        "n_restart_notice_datarestart_notice": "\\nRestart notice: {data_restart_notice}",
        "ncredit_datacredit_amount": "\\nCredit: {data_credit_amount}",
        "network_error_while_clearing_logs_e": "Network error while clearing logs: {error_message}",
        "network_error_while_downloading_log": "Network error while downloading logs: {error_message}",
        "new_version_available": "New version available",
        "new_version_foundncurrent_vdatavers": "New version available.\\nCurrent: v{data_version}\\nLatest: v{data_latest_version}\\n\\nRelease notes: {data_latest_message}",
        "nfailed_step_step": "\\nFailed Step: {step}",
        "nnerror_details_errordetail": "\\n\\nError details: {errorDetail}",
        "no_details_available": "No details available",
        "no_logs_at_appstatecurrentlogfilter": "No logs are currently available at the {AppState_currentLogFilter} level.",
        "no_logs_yet": "No logs yet.",
        "none": "None",
        "not_enabled": "Not enabled",
        "nplease_enter_index_1dataavailable": "\\nPlease enter an index (1-{data_available_projects_length}):",
        "oneclick_credential_deduplication_i": "One-click credential deduplication in progress...",
        "open_troubleshooter": "Open troubleshooter",
        "other_models_title": "Other models",
        "parallel_testing_selectedfileslengt": "Testing {selectedFiles_length} provider credentials in parallel. Please wait...",
        "parallel_verifying_selectedfileslen": "Verifying {selectedFiles_length} credentials in parallel. Please wait...",
        "please_enter_a_valid_url_starting_w": "Please enter a valid URL starting with http:// or https://.",
        "please_enter_the_callback_url": "Please enter the callback URL.",
        "please_enter_the_password": "Please enter your password.",
        "please_fetch_the_authentication_lin": "Please fetch the authentication link and complete authorization first.",
        "please_obtain_the_primary_authe": "Please obtain the provider authentication link and complete authorization first.",
        "please_select_a_projectnn": "Please select a project:\\n\\n",
        "please_select_the_credential_to_con": "Please select a credential before configuring Preview.",
        "please_select_the_credentials_to_co": "Please select credentials to configure Preview first.",
        "please_select_the_credentials_to_ve": "Please select credentials to verify first.",
        "please_select_the_credentials_to_ve_dup": "Please select credentials to verify first.",
        "please_select_the_files_to_operate": "Select files before continuing.",
        "please_select_the_primary_crede": "Please select provider credentials to verify first.",
        "please_select_the_primary_crede_dup": "Please select a provider credential to verify first.",
        "preview_not_supported_title": "This credential does not support Preview models",
        "preview_supported_title": "This credential supports Preview models",
        "primary_authentication_link_gen": "Provider authentication link generated. Open it, finish Google authorization, then return here to save credentials. If Google opens a localhost callback page, paste that full URL into Callback URL.",
        "primary_batch_verification_comp_dup": "Provider batch verification complete.\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",
        "primary_credential_valid": "Provider credential is valid.",
        "project_id_required_to_complete_aut": "A Project ID is required to complete authentication. Restart the flow and enter the correct Project ID.",
        "provider_antigravity": "Google Antigravity",
        "provider_google_ai_studio": "Google AI Studio",
        "provider_authorization_expired": "This authorization session was not found or has expired. Generate a new authorization link and try again.",
        "provider_authorization_pending": "Authorization is not complete yet. If Google opened a localhost callback page, copy the full callback URL from that tab and paste it into Callback URL.",
        "provider_callback_url_required": "Paste the localhost callback URL from the Google tab, then click Save credentials.",
        "provider_code_assist": "Code Assist",
        "provider_credential_replaced_title": "Credential renewed",
        "provider_credential_saved_body": "The credential was saved and the provider pool was refreshed. File: {data_file_path}.",
        "provider_credential_saved_title": "Credential saved to pool",
        "provider_credential_skipped_body": "The credential was not added because the pool already has the same email with an equal or later expiry. File: {data_file_path}.",
        "provider_credential_skipped_title": "Credential already exists",
        "quota_details": "Quota details",
        "quota_preview_loading": "Loading",
        "quota_unavailable": "Unavailable",
        "refreshing_all_user_emails": "Refreshing all user emails...",
        "regenerate_success": "API key regenerated.",
        "resulterror_step_resultstep": "{result_error} (Step: {result_step})",
        "resultfilename_resultmessage_config": "{result_filename}: {result_message}",
        "retrieving_credentials_from_callbac": "Retrieving credentials from callback URL...",
        "retry_fetching_authentication_file": "Retry fetching authentication file",
        "retry_using_the_selected_project": "Retrying with the selected project...",
        "retrying_with_manually_entered_proj": "Retrying with manually entered Project ID...",
        "right_click_to_copy_link": "Right-click to copy link",
        "saving_provider_credentials": "Saving credentials to the pool...",
        "saving_provider_credentials_from_callback": "Saving credentials from the callback URL...",
        "status_action_failed": "Action failed: {error}",
        "status_action_success": "Action completed: {action}.",
        "status_batch_complete": "Batch operation complete. Processed {success}/{total} credentials.",
        "status_batch_failed": "Batch operation failed: {error}",
        "status_batch_in_progress": "{action} is running for the selected credential files.",
        "status_batch_net_error": "Batch operation network error: {error}",
        "status_credential_normal": "This credential has no recorded error details.",
        "status_disabled": "Disabled",
        "status_download_success": "Downloaded {filename}.",
        "status_enabled": "Enabled",
        "status_filter_suffix": " Filter: {filter}.",
        "status_invalid_file_format": "The file format for {name} is not supported. Use JSON or ZIP files.",
        "status_load_failed": "Unable to load details: {error}",
        "status_loaded_creds": "Loaded {count} {type} credential files.",
        "status_loading_file_content": "Loading file content...",
        "status_log_stream_connection_failed": "Failed to connect to the log stream: ",
        "status_log_stream_error_prefix": "Log stream error: ",
        "status_net_error": "Network error: {error}",
        "status_no_creds": "No credentials are in this pool yet. Add an account or upload credentials to get started.",
        "status_no_errors": "No errors",
        "status_no_filter_data": "No usage statistics found.",
        "status_no_quota_info": "No quota information is available for this credential.",
        "status_page_info": "Page {page} of {total} (showing {start}-{end} of {count}).",
        "status_select_upload_first": "Select at least one credential file before uploading.",
        "status_selected_items": "Selected {count} item(s)",
        "status_upload_aborted": "Upload failed because the connection was interrupted while sending {count} files.",
        "status_upload_failed_details": "Upload failed: {error}",
        "status_upload_failed_http": "Upload failed with HTTP {status}.",
        "status_upload_invalid_response": "The upload completed, but the server returned an invalid response.",
        "status_upload_success": "Imported {count} {type} credential files.",
        "status_upload_timeout": "Upload timed out. Try again with fewer files.",
        "status_uploading_zip": "Uploading and extracting ZIP archives...",
        "successfully_deleted_datadeleted_co": "Deleted {data_deleted_count} environment variable credential files.",
        "successfully_imported_dataloaded_co": "Imported {data_loaded_count}/{data_total_count} credential files.",
        "table_filename": "Credential file name",
        "test_failed_errormessage": "Test failed: {error_message}",
        "test_successful": "Test completed.",
        "testing_model_please_wait": "Testing the selected model. Please wait...",
        "testing_selected_model": "Testing {model} with a minimal generation request...",
        "testing_short": "Testing...",
        "the_following_configurations_have_t_dup": " Applied immediately: {data_hot_updated_join}",
        "this_is_not_a_valid_callback_url_pl": "This is not a valid callback URL. Please ensure:\\n1. Google OAuth authorization is complete.\\n2. You copied the full URL from the browser address bar.\\n3. The URL contains code and state parameters.",
        "tier_badge_title": "Credential tier",
        "tip": "Tip",
        "unable_to_autodetect_project_id_ple": "Unable to auto-detect Project ID. Please manually enter your Google Cloud Project ID:",
        "unable_to_determine_if_updates_are": "Unable to determine if updates are available.",
        "unable_to_load_file_content": "Unable to load file content:",
        "unable_to_retrieve_version_informat": "Unable to retrieve version information",
        "unknown_error": "Unknown error",
        "unknown_version": "Unknown version",
        "upload_result_error_title": "Import failed",
        "upload_result_mixed_title": "Import complete",
        "upload_result_skipped_title": "Duplicate credentials skipped",
        "upload_result_success_title": "Credentials imported",
        "validation_successfulnnfile_filenam": "Validation successful.\\n\\nFile: {filename}\\nProject ID: {data_project_id}{tierLine}{creditLine}\\n\\n{data_message}",
        "verification_failed": "Verification failed",
        "verification_failed_errormessage": "Verification failed: {error_message}",
        "verification_failed_for_all_failed": "Verification failed for all credentials. Failed {failCount}/{selectedFiles_length} provider credentials.",
        "verification_failednnerrormsg": "Verification failed.\\n\\n{errorMsg}",
        "verifying_primary_project_id_pl": "Verifying provider project ID. Please wait...",
        "verifying_project_id_please_wait": "Verifying Project ID. Please wait...",
        "waiting_for_oauth_callback": "Waiting for OAuth callback...",
        "waiting_for_oauth_callback_this_may": "Waiting for OAuth callback, this may take some time...",
        "websocket_connected": "WebSocket connected"
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

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = String(value ?? '');
    return div.innerHTML;
}

function escapeAttribute(value) {
    return String(value ?? '').replace(/[&<>"']/g, (character) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[character]);
}

function safeHttpUrl(value) {
    try {
        const url = new URL(String(value ?? ''));
        return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
    } catch (_) {
        return '';
    }
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

    '/pool': 'pool',

    '/models': 'models',

    '/provider': 'pool',

    '/providers': 'providers',

    '/oauth': 'providers',

    '/upload': 'providers',

    '/config': 'config',

    '/logs': 'logs',

    '/about': 'about'

};

const TAB_MAP = {
    dashboard: '/dashboard',
    pool: '/pool',
    models: '/models',
    providers: '/providers',
    config: '/config',
    logs: '/logs',
    about: '/about'
};

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

        resetConsoleScroll();

        return;

    }

    const isAuthenticated = AppState.authenticated;

    if (!isAuthenticated) {

        targetPath = '/login';

        if (window.location.pathname !== '/login') {

            history.replaceState(null, '', '/login');

        }

        if (setupEl) setupEl.style.setProperty('display', 'none', 'important');

        if (loginEl) loginEl.style.setProperty('display', 'flex', 'important');

        if (mainEl) mainEl.style.setProperty('display', 'none', 'important');

        resetConsoleScroll();

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

    const tabName = ROUTE_MAP[targetPath] || 'dashboard';
    const canonicalPath = TAB_MAP[tabName] || '/dashboard';

    targetPath = canonicalPath;

    if (window.location.pathname !== targetPath) {

        if (pushState) {

            history.pushState(null, '', targetPath);

        } else {

            history.replaceState(null, '', targetPath);

        }

    }

    setMobileMenuState(false);

    const currentContent = document.querySelector('.tab-content.active');

    const targetContent = document.getElementById(tabName + 'Tab');

    const shouldResetScroll = !currentContent || currentContent !== targetContent;

    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
        tab.removeAttribute('aria-current');
    });

    const targetTabButton = document.querySelector(`.tab[onclick*="'${tabName}'"]`);

    if (targetTabButton) {

        targetTabButton.classList.add('active');
        targetTabButton.setAttribute('aria-current', 'page');

    }

    // Toggle panels instantly

    if (currentContent) {

        currentContent.classList.remove('active');

    }

    if (targetContent) {

        targetContent.classList.add('active');

        triggerTabDataLoad(tabName);

        if (shouldResetScroll) {

            resetConsoleScroll(targetContent);

        }

    }

}

function resetConsoleScroll(activeContent = null) {

    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });

    document.documentElement.scrollTop = 0;

    document.documentElement.scrollLeft = 0;

    document.body.scrollTop = 0;

    document.body.scrollLeft = 0;

    const scrollTargets = [

        document.getElementById('mainSection'),

        document.querySelector('.dashboard-main'),

        document.querySelector('.dashboard-wrapper'),

        activeContent

    ];

    scrollTargets.forEach(target => {

        if (!target) return;

        target.scrollTop = 0;

        target.scrollLeft = 0;

    });

}

// =====================================================================

// =====================================================================

// =====================================================================

// =====================================================================

const AppState = {

    authenticated: false,

    setupRequired: false,

    authInProgress: false,

    currentProjectId: '',

    primaryAuthState: null,

    primaryAuthInProgress: false,

    primaryCredentialFilename: '',

    creds: createCredsManager('normal'),

    primaryCreds: createCredsManager('primary'),

    credentialCardIndex: {},

    uploadFiles: createUploadManager('normal'),

    primaryUploadFiles: createUploadManager('primary'),

    googleAiStudioUploadFiles: createUploadManager('googleAiStudio', {
        endpoint: './api/providers/google-ai-studio/credentials/import',
        elementPrefix: 'googleAiStudio',
        credentialType: 'Google AI Studio',
        timeoutMs: 900000,
        onComplete: () => AppState.primaryCreds.refresh()
    }),

    currentConfig: {},

    envLockedFields: new Set(),

    antigravityConfig: {},

    antigravityEnvLockedFields: new Set(),

    activeProviderWorkspace: 'google_antigravity',

    modelCatalog: [],

    selectedModels: [],

    modelPoolEnabled: true,

    logWebSocket: null,

    allLogs: [],

    filteredLogs: [],

    currentLogFilter: 'all',

    usageStatsData: {},

    usagePeriod: '1d',

    quotaPreviewCache: {},

    cooldownTimerInterval: null

};

const STORAGE_KEYS = {
    logAutoScroll: 'omni_gateway_log_auto_scroll',
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

        currentProviderFilter: 'all',

        statsData: { total: 0, normal: 0, disabled: 0 },

        getEndpoint: (action) => {

            const endpoints = {

                status: `./api/credentials/status`,

                action: `./api/credentials/action`,

                batchAction: `./api/credentials/batch-action`,

                download: `./api/credentials/download`,

                downloadAll: `./api/credentials/download-all`,

                detail: `./api/credentials/detail`,

                models: `./api/credentials/models`,

                refreshAllEmails: `./api/credentials/refresh-all-emails`,

                deduplicate: `./api/credentials/deduplicate-by-email`,

                verifyProject: `./api/credentials/verify-project`,

                quota: `./api/credentials/quota`

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

                const providerFilter = this.currentProviderFilter || 'all';

                const response = await fetch(

                    `${this.getEndpoint('status')}?offset=${offset}&limit=${this.pageSize}&status_filter=${this.currentStatusFilter}&error_code_filter=${errorCodeFilter}&cooldown_filter=${cooldownFilter}&preview_filter=${previewFilter}&tier_filter=${tierFilter}&provider_filter=${providerFilter}&${this.getModeParam()}`,

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

                            credential_label: item.credential_label,

                            credential_type: item.credential_type,

                            provider: item.provider,

                            model_count: Number.isFinite(Number(item.model_count)) ? Number(item.model_count) : 0,

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
            list.classList.remove('is-empty');

            const entries = Object.entries(this.filteredData);

            if (entries.length === 0) {

                const msg = this.totalCount === 0 ? t('status_no_creds') : t('status_no_filter_data');

                list.classList.add('is-empty');

                const emptyState = document.createElement('div');
                emptyState.className = 'creds-empty-state';
                emptyState.textContent = msg;
                list.appendChild(emptyState);

                document.getElementById(this.getElementId('PaginationContainer')).style.display = 'none';

                return;

            }

            if (this.type === 'primary') {

                const providerGroups = new Map();

                entries.forEach(([, credInfo]) => {

                    const providerMeta = getCredentialProviderMeta(credInfo, this.type);

                    if (!providerGroups.has(providerMeta.id)) {

                        providerGroups.set(providerMeta.id, { providerMeta, credentials: [] });

                    }

                    providerGroups.get(providerMeta.id).credentials.push(credInfo);

                });

                providerGroups.forEach(({ providerMeta, credentials }) => {

                    list.appendChild(createCredentialProviderGroup(providerMeta, credentials, this));

                });

            } else {

                entries.forEach(([, credInfo]) => {

                    list.appendChild(createCredCard(credInfo, this));

                });

            }

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

            const providerFilterEl = document.getElementById(this.getElementId('ProviderFilter'));

            this.currentErrorCodeFilter = errorCodeFilterEl ? errorCodeFilterEl.value : 'all';

            this.currentCooldownFilter = cooldownFilterEl ? cooldownFilterEl.value : 'all';

            this.currentPreviewFilter = previewFilterEl ? previewFilterEl.value : 'all';

            this.currentProviderFilter = providerFilterEl ? providerFilterEl.value : 'all';

            if (tierFilterEl) {

                const tierIsRelevant = this.currentProviderFilter !== 'google_ai_studio';

                tierFilterEl.disabled = !tierIsRelevant;

                if (!tierIsRelevant) tierFilterEl.value = 'all';

                this.currentTierFilter = tierIsRelevant ? tierFilterEl.value : 'all';

            } else {

                this.currentTierFilter = 'all';

            }

            this.selectedFiles.clear();

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

            if (this.type === 'primary') {

                const selectedCredentials = Array.from(this.selectedFiles)

                    .map(filename => this.data[filename])

                    .filter(Boolean);

                const supportsCreditActions = selectedCredentials.length > 0

                    && selectedCredentials.every((credInfo) => (

                        getCredentialProviderMeta(credInfo, this.type).id === 'google_antigravity'

                    ));

                ['EnableCredit', 'DisableCredit'].forEach((action) => {

                    const button = document.getElementById(this.getElementId(`Batch${action}Btn`));

                    if (button) button.disabled = !supportsCreditActions;

                });

            }

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

                    if (action === 'delete') {

                        this.selectedFiles.delete(filename);

                        delete AppState.quotaPreviewCache[filename];

                        Object.entries(AppState.credentialCardIndex).forEach(([pathId, context]) => {

                            if (context.filename === filename) delete AppState.credentialCardIndex[pathId];

                        });

                        this.updateBatchControls();

                    }

                    await this.refresh();

                    if (action === 'delete') await refreshUsageStats();

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

            const confirmationTitles = {

                enable: t('confirm_batch_enable_title'),

                disable: t('confirm_batch_disable_title'),

                delete: t('confirm_batch_delete_title'),

                enable_credit: t('confirm_batch_enable_credit_title'),

                disable_credit: t('confirm_batch_disable_credit_title')

            };

            const confirmationMessages = {

                enable: t('confirm_batch_enable', {count: selectedFiles.length}),

                disable: t('confirm_batch_disable', {count: selectedFiles.length}),

                delete: t('confirm_batch_delete', {count: selectedFiles.length}),

                enable_credit: t('confirm_batch_enable_credit', {count: selectedFiles.length}),

                disable_credit: t('confirm_batch_disable_credit', {count: selectedFiles.length})

            };

            const actionLabel = actionNames[action] || action;

            const confirmMsg = confirmationMessages[action]

                || `${actionLabel} ${selectedFiles.length} selected credentials?`;

            const confirmOptions = {

                title: confirmationTitles[action] || t('confirm_manage_credentials_title'),

                confirmLabel: actionLabel

            };

            if (!(await showConfirmModal(confirmMsg, confirmOptions))) return;

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

                    if (action === 'delete') {

                        selectedFiles.forEach((filename) => {

                            delete AppState.quotaPreviewCache[filename];

                        });

                        Object.entries(AppState.credentialCardIndex).forEach(([pathId, context]) => {

                            if (selectedFiles.includes(context.filename)) delete AppState.credentialCardIndex[pathId];

                        });

                    }

                    this.selectedFiles.clear();

                    this.updateBatchControls();

                    await this.refresh();

                    if (action === 'delete') await refreshUsageStats();

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

function createUploadManager(type, options = {}) {

    const modeParam = type === 'primary' ? 'mode=provider' : 'mode=code_assist';

    const endpoint = options.endpoint || `./api/credentials/upload?${modeParam}`;

    const elementPrefix = options.elementPrefix || (type === 'primary' ? 'primary' : '');

    const credentialType = options.credentialType || (type === 'primary' ? 'provider' : 'Code Assist');

    return {

        type: type,

        selectedFiles: [],

        getElementId: (suffix) => {

            if (elementPrefix) {

                return elementPrefix + suffix.charAt(0).toUpperCase() + suffix.slice(1);

            }

            return suffix.charAt(0).toLowerCase() + suffix.slice(1);

        },

        hideUploadResult() {

            const panel = document.getElementById(this.getElementId('UploadResult'));

            if (panel) panel.classList.add('hidden');

        },

        renderUploadResult(data, fallbackVariant = 'success') {

            const panel = document.getElementById(this.getElementId('UploadResult'));
            const title = document.getElementById(this.getElementId('UploadResultTitle'));
            const text = document.getElementById(this.getElementId('UploadResultText'));
            const details = document.getElementById(this.getElementId('UploadResultDetails'));

            if (!panel || !title || !text || !details) return;

            const results = Array.isArray(data.results) ? data.results : [];
            const savedCount = Number(data.uploaded_count || data.loaded_count || 0);
            const skippedCount = Number(data.skipped_count || 0);
            const errorCount = results.filter(item => item.status === 'error').length;

            let variant = 'success';
            if (fallbackVariant === 'error' || (errorCount > 0 && savedCount === 0 && skippedCount === 0)) {
                variant = 'error';
            } else if (skippedCount > 0 && savedCount === 0 && errorCount === 0) {
                variant = 'info';
            } else if (skippedCount > 0 || errorCount > 0) {
                variant = 'warning';
            }

            const titleText = variant === 'error'
                ? t('upload_result_error_title')
                : variant === 'info'
                    ? t('upload_result_skipped_title')
                    : variant === 'warning'
                        ? t('upload_result_mixed_title')
                        : t('upload_result_success_title');

            panel.classList.remove('hidden', 'info', 'warning', 'error');
            if (variant !== 'success') panel.classList.add(variant);

            title.textContent = titleText;
            text.textContent = ensureTerminalPunctuation(data.message || t('status_upload_success', {count: savedCount, type: credentialType}));
            details.replaceChildren();

            const visibleResults = results.slice(0, 6);
            visibleResults.forEach(item => {
                const detailItem = document.createElement('div');
                detailItem.className = 'upload-result-item';

                const fileLine = document.createElement('div');
                fileLine.className = 'upload-result-file';

                const actionLabel = item.status === 'skipped'
                    ? 'Skipped'
                    : item.status === 'error'
                        ? 'Error'
                        : item.action === 'replaced'
                            ? 'Renewed'
                            : item.action === 'updated'
                                ? 'Updated'
                                : 'Added';
                fileLine.textContent = `${actionLabel}: ${item.filename || item.source_filename || 'Credential'}`;

                const messageLine = document.createElement('div');
                messageLine.className = 'upload-result-message';
                messageLine.textContent = ensureTerminalPunctuation(item.message || data.message || '');

                detailItem.append(fileLine, messageLine);
                details.appendChild(detailItem);
            });

            if (results.length > visibleResults.length) {
                const moreItem = document.createElement('div');
                moreItem.className = 'upload-result-message';
                const hiddenCount = results.length - visibleResults.length;
                moreItem.textContent = `${hiddenCount} more ${hiddenCount === 1 ? 'result' : 'results'} not shown.`;
                details.appendChild(moreItem);
            }

        },

        handleFileSelect(event) {

            this.addFiles(Array.from(event.target.files));

        },

        addFiles(files) {

            this.hideUploadResult();

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

                const fileDetails = document.createElement('div');
                const fileName = document.createElement('span');
                fileName.className = 'file-name';
                fileName.textContent = `${fileIcon} ${file.name}`.trim();
                const fileSize = document.createElement('span');
                fileSize.className = 'file-size';
                fileSize.textContent = `(${formatFileSize(file.size)} ${fileType})`;
                fileDetails.append(fileName, fileSize);

                const removeButton = document.createElement('button');
                removeButton.type = 'button';
                removeButton.className = 'remove-btn';
                removeButton.textContent = t('action_delete');
                removeButton.addEventListener('click', () => this.removeFile(index));

                fileItem.append(fileDetails, removeButton);

                list.appendChild(fileItem);

            });

        },

        removeFile(index) {

            this.selectedFiles.splice(index, 1);

            this.updateFileList();

        },

        clearFiles(hideResult = true) {

            this.selectedFiles = [];

            const fileInput = document.getElementById(this.getElementId('FileInput'));

            if (fileInput) fileInput.value = '';

            this.updateFileList();

            if (hideResult) this.hideUploadResult();

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

                xhr.timeout = options.timeoutMs || 300000;

                xhr.upload.onprogress = (event) => {

                    if (event.lengthComputable) {

                        const percent = (event.loaded / event.total) * 100;

                        progressFill.style.width = percent + '%';

                        progressText.textContent = Math.round(percent) + '%';

                    }

                };

                xhr.onload = () => {

                    if (xhr.status >= 200 && xhr.status < 300) {

                        try {

                            const data = JSON.parse(xhr.responseText);

                            const message = data.message || t('status_upload_success', {count: data.uploaded_count, type: credentialType});
                            const uploadStatus = data.uploaded_count > 0
                                ? (data.error_count > 0 ? 'warning' : 'success')
                                : (data.error_count > 0 ? 'error' : 'info');
                            showStatus(message, uploadStatus);
                            this.renderUploadResult(data);

                            this.clearFiles(false);

                            if (options.onComplete) Promise.resolve(options.onComplete(data));

                            progressSection.classList.add('hidden');

                        } catch (e) {

                            showStatus(t('status_upload_invalid_response'), 'error');

                        }

                    } else {

                        try {

                            const error = JSON.parse(xhr.responseText);
                            const errorMessage = error.detail || error.error || t('unknown_error');

                            showStatus(t('status_upload_failed_details', {error: errorMessage}), 'error');
                            this.renderUploadResult({message: errorMessage, results: []}, 'error');

                        } catch (e) {

                            showStatus(t('status_upload_failed_http', {status: xhr.status}), 'error');
                            this.renderUploadResult({message: t('status_upload_failed_http', {status: xhr.status}), results: []}, 'error');

                        }

                    }

                };

                xhr.onerror = () => {

                    showStatus(t('status_upload_aborted', {count: this.selectedFiles.length}), 'error');
                    this.renderUploadResult({message: t('status_upload_aborted', {count: this.selectedFiles.length}), results: []}, 'error');

                    progressSection.classList.add('hidden');

                };

                xhr.ontimeout = () => {

                    showStatus(t('status_upload_timeout'), 'error');
                    this.renderUploadResult({message: t('status_upload_timeout'), results: []}, 'error');

                    progressSection.classList.add('hidden');

                };

                xhr.open('POST', endpoint);

                xhr.send(formData);

            } catch (error) {

                showStatus(t('status_upload_failed_details', {error: error.message}), 'error');
                this.renderUploadResult({message: error.message, results: []}, 'error');

            }

        }

    };

}

// =====================================================================

// Shared frontend utility functions

// =====================================================================
