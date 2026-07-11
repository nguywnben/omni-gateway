const TRANSLATIONS = {
    en: {
        "a_hrefurl_target_blank_stylecolor_0": "<a href=\"{url}\" target=\"_blank\" style=\"color: #007bff; text-decoration: underline; word-break: break-all;\" title=\"Click to open: {url}\">{url}</a>",
        "action_delete": "Delete",
        "action_disable": "Disable",
        "action_disable_credit": "Disable credit",
        "action_enable": "Enable",
        "action_enable_credit": "Enable credit",
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
        "btn_disable_credit": "Disable credit",
        "btn_disable_credit_title": "Disable credit mode for this credential",
        "btn_download": "Download",
        "btn_enable_credit": "Enable credit",
        "btn_enable_credit_title": "Enable credit mode for this credential",
        "btn_message_test": "Message test",
        "btn_message_test_title": "Test whether this credential is working.",
        "btn_refresh": "Refresh",
        "btn_regenerate": "Regenerate",
        "btn_reset_defaults": "Reset defaults",
        "btn_setup_preview": "Set up Preview",
        "btn_setup_preview_title": "Configure the Preview channel and enable experimental features.",
        "btn_verify_id": "Verify",
        "btn_verify_id_title": "Retrieve the Project ID and recover from some 403 errors.",
        "btn_view_content": "View content",
        "btn_view_errors": "View errors",
        "btn_view_errors_title": "View detailed error messages for this credential.",
        "btn_view_quota": "View quota",
        "btn_view_quota_title": "View quota usage info for this credential",
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
        "confirm_batch_enable_credit": "Enable credit mode for {count} selected credentials?",
        "confirm_batch_disable_credit": "Disable credit mode for {count} selected credentials?",
        "confirm_batch_enable_title": "Enable Credentials",
        "confirm_batch_disable_title": "Disable Credentials",
        "confirm_batch_delete_title": "Delete Credentials",
        "confirm_batch_enable_credit_title": "Enable Credit Mode",
        "confirm_batch_disable_credit_title": "Disable Credit Mode",
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
        "credit_disabled_title": "Credit mode is currently disabled",
        "credit_enabled_title": "Credit mode is currently enabled",
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
        "testing_credentials_please_wait": "Testing credentials. Please wait...",
        "testing_primary_credentials_ple": "Testing provider credentials. Please wait...",
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

                status: `./api/creds/status`,

                action: `./api/creds/action`,

                batchAction: `./api/creds/batch-action`,

                download: `./api/creds/download`,

                downloadAll: `./api/creds/download-all`,

                detail: `./api/creds/detail`,

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

    const endpoint = options.endpoint || `./api/creds/upload?${modeParam}`;

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

function ensureTerminalPunctuation(message) {

    const value = String(message ?? '');
    const trimmedEnd = value.trimEnd();

    if (!trimmedEnd) return value;

    const visibleText = trimmedEnd
        .replace(/<br\s*\/?>/gi, ' ')
        .replace(/<[^>]+>/g, '')
        .trim();

    if (!visibleText || /[.!?;:…]$/.test(visibleText)) return value;

    return value.slice(0, trimmedEnd.length) + '.' + value.slice(trimmedEnd.length);

}

function showStatus(message, type = 'info') {

    const displayMessage = ensureTerminalPunctuation(message);

    const statusSection = document.getElementById('statusSection');

    if (statusSection) {

        if (window._statusTimeout) {

            clearTimeout(window._statusTimeout);

        }

        const statusDiv = document.createElement('div');
        const statusType = ['success', 'error', 'warning', 'info'].includes(type)
            ? type
            : 'info';
        statusDiv.className = `status ${statusType}`;
        statusDiv.textContent = displayMessage;
        statusSection.replaceChildren(statusDiv);

        statusDiv.offsetHeight;

        statusDiv.classList.add('show');

        window._statusTimeout = setTimeout(() => {

            statusDiv.classList.add('fade-out');

            setTimeout(() => {

                statusSection.replaceChildren();

            }, 300);

        }, 3000);

    } else {

        showMessageModal(t('dialog_tip'), displayMessage, 'info');

    }

}

async function updateEndpointUrls() {
    const origin = window.location.origin;

    const openaiEl = document.getElementById('openaiEndpointUrl');
    if (openaiEl) openaiEl.textContent = `${origin}/v1`;

    const anthropicEl = document.getElementById('anthropicEndpointUrl');
    if (anthropicEl) anthropicEl.textContent = origin;

    const googleGenaiEl = document.getElementById('googleGenaiEndpointUrl');
    if (googleGenaiEl) googleGenaiEl.textContent = origin;

    try {
        const response = await fetch('./api/auth/keys', { headers: getAuthHeaders() });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const apiKeyEl = document.getElementById('apiKey');
                const apiKey = data.api_key || '';
                if (apiKeyEl) {
                    apiKeyEl.value = apiKey;
                    if (!apiKeyEl.dataset.visibilityInitialized) {
                        setApiKeyVisibility(false);
                    }
                }
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

function setApiKeyVisibility(visible) {
    const input = document.getElementById('apiKey');
    const button = document.getElementById('toggleApiKeyVisibilityBtn');
    if (!input) return;

    input.type = visible ? 'text' : 'password';
    input.dataset.visibilityInitialized = 'true';
    input.dataset.visible = visible ? 'true' : 'false';

    if (button) {
        const label = visible ? 'Hide API key' : 'Show API key';
        button.title = label;
        button.setAttribute('aria-label', label);
        button.innerHTML = visible
            ? '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18"></path><path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"></path><path d="M9.9 5.2A9.6 9.6 0 0 1 12 5c6.5 0 10 7 10 7a18.3 18.3 0 0 1-3.1 4.3"></path><path d="M6.5 6.8C3.7 8.6 2 12 2 12s3.5 7 10 7a9.8 9.8 0 0 0 4.1-.9"></path></svg>'
            : '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
    }
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('apiKey');
    if (!input) return;
    setApiKeyVisibility(input.type === 'password');
}

async function copyTextToClipboard(text) {
    const value = String(text || '');
    if (!value) return false;

    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(value);
            return true;
        } catch (error) {
            // Fall through to the legacy path below. Public HTTP deployments do
            // not always expose the modern clipboard API.
        }
    }

    const textarea = document.createElement('textarea');
    textarea.value = value;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.inset = '0 auto auto 0';
    textarea.style.width = '1px';
    textarea.style.height = '1px';
    textarea.style.opacity = '0';
    textarea.style.pointerEvents = 'none';

    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);

    let copied = false;
    try {
        copied = document.execCommand('copy');
    } catch (error) {
        copied = false;
    } finally {
        document.body.removeChild(textarea);
    }

    return copied;
}

async function copyTextWithStatus(text) {
    const copied = await copyTextToClipboard(text);
    showStatus(t(copied ? 'copy_success' : 'copy_fail'), copied ? 'success' : 'error');
    return copied;
}

function cpUrl(element) {
    const text = element.textContent || element.innerText;
    if (!text) return;
    copyTextWithStatus(text.trim());
}

function copyInputValue(inputId) {
    const input = document.getElementById(inputId);
    if (!input || !input.value || input.value === '...') return;
    if (document.activeElement === input) {
        input.blur();
    }
    copyTextWithStatus(input.value);
}

async function regenerateApiKey() {
    if (!(await showConfirmModal(t('confirm_regenerate_key'), {
        title: t('confirm_regenerate_key_title'),
        confirmLabel: t('btn_regenerate')
    }))) {
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
                if (el) {
                    el.value = apiKey;
                    if (!el.dataset.visibilityInitialized) {
                        setApiKeyVisibility(false);
                    }
                }
                showStatus(t('regenerate_success'), 'success');
            } else {
                showStatus(data.error || 'Failed to regenerate the API key.', 'error');
            }
        } else {
            showStatus(data.detail || data.message || 'Failed to regenerate the API key.', 'error');
        }
    } catch (e) {
        console.error("Failed to regenerate the API key.", e);
        showStatus(t('status_net_error', {error: e.message}), 'error');
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

function showMessageModal(title, message, type = 'info', options = {}) {

    const modal = document.createElement('div');

    modal.className = 'message-modal-overlay';
    const safeType = String(type || 'info').replace(/[^\w-]/g, '') || 'info';
    const safeTitle = escapeHtml(title);
    const normalizedMessage = normalizeDialogMessage(message);
    const bodyContent = options.html
        ? String(message || '')
        : `<div class="message-modal-copy">${linkifyText(escapeHtml(normalizedMessage)).replace(/\n/g, '<br>')}</div>`;

    modal.innerHTML = `

        <div class="message-modal informational ${safeType}" role="dialog" aria-modal="true" aria-label="${safeTitle}">

            <div class="message-modal-header">

                <h3>${safeTitle}</h3>

            </div>

            <div class="message-modal-body">

                ${bodyContent}

            </div>

            <div class="message-modal-footer">

                <button type="button" class="message-modal-btn" data-dialog-close>${escapeHtml(t('btn_close'))}</button>

            </div>

        </div>

    `;

    let closed = false;

    const close = () => {

        if (closed) return;

        closed = true;

        document.removeEventListener('keydown', escHandler);

        modal.remove();

    };

    modal.addEventListener('click', function(e) {

        if (e.target === modal || e.target.closest('[data-dialog-close]')) close();

    });

    const escHandler = function(e) {

        if (e.key === 'Escape') close();

    };

    document.addEventListener('keydown', escHandler);

    document.body.appendChild(modal);

}

function normalizeDialogMessage(message) {

    return String(message || '').replace(/\\n/g, '\n');

}

function renderDialogMessage(message, options = {}) {

    const escaped = escapeHtml(normalizeDialogMessage(message));

    if (options.compact) {

        return escaped
            .replace(/\n{2,}/g, '<span class="message-modal-break"></span>')
            .replace(/\n/g, '<br>');

    }

    return escaped.replace(/\n/g, '<br>');

}

function stringifyModalDetail(value) {

    if (value === undefined || value === null || value === '') return '';

    if (typeof value === 'string') return normalizeDialogMessage(value);

    try {

        return JSON.stringify(value, null, 2);

    } catch {

        return String(value);

    }

}

function buildMessageResultDetails(label, value, options = {}) {

    const text = stringifyModalDetail(value);

    if (!text) return '';

    return `
        <details class="message-result-details"${options.open ? ' open' : ''}>
            <summary>${escapeHtml(label || 'Details')}</summary>
            <pre>${escapeHtml(text)}</pre>
        </details>
    `;

}

function buildApiResultHtml(options = {}) {

    const introHtml = options.intro
        ? `<div class="message-result-intro">${renderDialogMessage(ensureTerminalPunctuation(options.intro))}</div>`
        : '';

    const headingHtml = options.heading
        ? `<div class="message-result-heading">${escapeHtml(options.heading)}</div>`
        : '';

    const summaryHtml = options.rows?.length
        ? `
            <div class="message-result-section">
                <div class="message-result-section-title">${escapeHtml(options.summaryLabel || 'Summary')}</div>
                <div class="message-result-summary">${renderMessageResultRows(options.rows)}</div>
            </div>
        `
        : '';

    const noteHtml = options.note
        ? `<div class="message-result-note">${renderDialogMessage(ensureTerminalPunctuation(options.note))}</div>`
        : '';

    const detailsHtml = buildMessageResultDetails(
        options.detailsLabel || 'Details',
        options.details,
        { open: options.detailsOpen }
    );

    return `
        <div class="message-result-panel">
            ${introHtml}
            ${headingHtml}
            ${summaryHtml}
            ${noteHtml}
            ${options.extraHtml || ''}
            ${detailsHtml}
        </div>
    `;

}

function buildCredentialTestErrorHtml(filename, data, response) {

    let parsedError = null;
    const rawErrorValue = data?.error || data?.detail || data?.message || '';
    if (rawErrorValue) {
        try {
            parsedError = typeof rawErrorValue === 'string' ? JSON.parse(rawErrorValue) : rawErrorValue;
        } catch {
            parsedError = null;
        }
    }

    const errorRoot = parsedError?.error || parsedError || {};
    const firstDetail = Array.isArray(errorRoot.details) ? errorRoot.details[0] || {} : {};
    const metadata = firstDetail.metadata || {};
    const httpCode = errorRoot.code || data.status_code || response.status;
    const statusText = errorRoot.status || data.message || data.detail || data.error || t('unknown_error');
    const reason = firstDetail.reason || '';
    const permission = metadata.permission || '';
    const resource = metadata.resource || '';
    const troubleshooterUrl = metadata.troubleshooter_url || '';
    const rawDetails = parsedError
        ? JSON.stringify(parsedError, null, 2)
        : String(data.detail || data.error || data.message || `${t('error_code_prefix')} ${httpCode}`);

    const summaryRows = [
        [t('table_filename'), filename],
        ['Code', httpCode],
        [t('credential_status_label').replace(':', ''), statusText],
        reason ? ['Reason', reason] : null,
        permission ? ['Permission', permission] : null,
        resource ? ['Resource', resource] : null,
    ].filter(Boolean);

    const troubleshooterHtml = troubleshooterUrl
        ? `<div class="message-result-actions"><a class="message-link" href="${escapeHtml(troubleshooterUrl)}" target="_blank" rel="noopener noreferrer">${t('open_troubleshooter')}</a></div>`
        : '';

    return buildApiResultHtml({
        intro: 'The message test did not complete successfully. Review the provider status and raw error response below.',
        rows: summaryRows,
        summaryLabel: 'Failure summary',
        extraHtml: troubleshooterHtml,
        detailsLabel: 'Error details',
        details: rawDetails,
        detailsOpen: true,
    });

}

function buildCredentialTestResultHtml(filename, data, response, options = {}) {

    const logicalStatus = data.status_code || response.status;
    const isRateLimited = logicalStatus === 429 && data.success === true;
    const statusMessage = data.message || (isRateLimited ? t('credential_rate_limited') : t('credential_available'));

    return buildApiResultHtml({
        intro: isRateLimited
            ? 'The credential responded, but the provider reported a temporary rate limit. The router can continue with another available credential.'
            : 'The credential completed a live message test successfully.',
        rows: [
            ['Result', isRateLimited ? 'Rate limited' : 'Successful'],
            [t('table_filename'), filename],
            ['HTTP code', logicalStatus || response.status],
            [t('credential_status_label').replace(':', ''), statusMessage],
            data.provider ? ['Provider', getCredentialProviderMeta({ provider: data.provider }, 'usage').name] : null,
            data.model ? ['Model', data.model] : null,
            options.mode ? ['Mode', options.mode] : null,
        ].filter(Boolean),
        summaryLabel: 'Test summary',
    });

}

function normalizeVerificationMessage(message) {

    return String(message || '')
        .replace(/^verification successful\.?\s*/i, '')
        .replace(/^validation successful\.?\s*/i, '')
        .trim();

}

function buildCredentialVerificationHtml(filename, data) {

    const rows = [
        ['Result', 'Successful'],
        [t('table_filename'), filename],
        data.project_id ? ['Project ID', data.project_id] : null,
        data.subscription_tier ? ['Tier', data.subscription_tier] : null,
        data.credit_amount !== undefined && data.credit_amount !== null ? ['Credit', data.credit_amount] : null,
        data.provider ? ['Provider', getCredentialProviderMeta({ provider: data.provider }, 'usage').name] : null,
        Number.isFinite(Number(data.model_count)) ? ['Available models', Number(data.model_count)] : null,
    ].filter(Boolean);

    const detailMessage = normalizeVerificationMessage(data.message);

    return buildApiResultHtml({
        intro: 'The credential was verified and its provider metadata was refreshed.',
        rows,
        summaryLabel: 'Verification summary',
        note: detailMessage,
    });

}

function renderMessageResultRows(rows) {

    return rows.filter(Boolean).map(([label, value]) => `
        <div class="message-result-row">
            <div class="message-result-label">${escapeHtml(label)}</div>
            <div class="message-result-value">${escapeHtml(String(value))}</div>
        </div>
    `).join('');

}

function getCredentialModalContext(pathId, manager) {

    const context = AppState.credentialCardIndex[pathId] || {};
    const resolvedManager = context.managerType === 'primary' ? AppState.primaryCreds : manager;

    if (context.filename) {

        return { ...context, filename: context.filename, manager: resolvedManager };

    }

    const details = document.getElementById('details-' + pathId)
        || document.getElementById('errors-' + pathId)
        || document.getElementById('quota-' + pathId);

    const filename = details?.querySelector('[data-filename]')?.getAttribute('data-filename') || '';

    return { filename, manager };

}

function buildCredentialContentHtml(filename, content) {

    const rows = renderMessageResultRows([
        [t('table_filename'), filename],
        content?.user_email || content?.email ? ['Email', content.user_email || content.email] : null,
        content?.project_id ? ['Project ID', content.project_id] : null,
        content?.expiry ? ['Expiry', content.expiry] : null,
    ].filter(Boolean));
    const body = JSON.stringify(content, null, 2);

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">This is the stored credential payload for the selected account.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Credential summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Credential payload</div>
                <pre class="message-modal-code">${escapeHtml(body)}</pre>
            </div>
        </div>
    `;

}

function quotaLevelFromUsedPercentage(usedPercentage) {

    if (usedPercentage >= 90) return 'danger';
    if (usedPercentage >= 70) return 'warning';
    if (usedPercentage >= 50) return 'info';
    return 'success';

}

function buildCredentialQuotaHtml(filename, data, context = {}) {

    const models = data.models || {};
    const entries = Object.entries(models);
    const summary = summarizeCredentialQuota(data);
    const resetTimes = entries
        .map(([, quotaData]) => quotaData?.resetTime)
        .filter(Boolean);
    const nextReset = resetTimes.length ? resetTimes.sort()[0] : '';
    const rows = renderMessageResultRows([
        ['Provider', context.providerName || t('provider_antigravity')],
        context.email ? ['Account', context.email] : ['Credential', filename],
        ['Tracked models', entries.length],
        summary.label ? ['Average remaining quota', summary.label] : null,
        nextReset ? ['Next reset', nextReset] : null,
    ].filter(Boolean));

    if (entries.length === 0) {

        return `
            <div class="message-result-panel">
                <div class="message-result-intro">No quota information is available for this credential yet.</div>
                <div class="message-result-section">
                    <div class="message-result-section-title">Quota summary</div>
                    <div class="message-result-summary">${rows}</div>
                </div>
                <div class="modal-empty-state">${escapeHtml(t('status_no_quota_info'))}</div>
            </div>
        `;

    }

    const cards = entries.map(([modelName, quotaData]) => {

        const remainingFraction = Number(quotaData.remaining || 0);
        const resetTime = quotaData.resetTime || 'N/A';
        const usedPercentage = Math.max(0, Math.min(100, Math.round((1 - remainingFraction) * 100)));
        const remainingPercentage = Math.max(0, Math.min(100, Math.round(remainingFraction * 100)));
        const level = quotaLevelFromUsedPercentage(usedPercentage);

        return `
            <div class="modal-quota-card ${level}">
                <div class="modal-quota-head">
                    <div class="modal-quota-model" title="${escapeHtml(modelName)}">${escapeHtml(modelName)}</div>
                    <div class="modal-quota-percent">${remainingPercentage}% left</div>
                </div>
                <div class="modal-quota-bar">
                    <div class="modal-quota-bar-value" style="width: ${remainingPercentage}%;"></div>
                </div>
                <div class="modal-quota-foot">
                    <span>Used ${usedPercentage}%</span>
                    <span>${resetTime !== 'N/A' ? `Reset ${escapeHtml(resetTime)}` : 'Reset time unavailable'}</span>
                </div>
            </div>
        `;

    }).join('');

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">Quota usage is grouped by model for the selected credential.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Quota summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Model quota</div>
                <div class="modal-quota-grid">${cards}</div>
            </div>
        </div>
    `;

}

function summarizeCredentialQuota(data) {

    const models = data?.models || {};
    const entries = Object.entries(models);

    if (!entries.length) {

        return {
            level: 'muted',
            label: 'No quota',
        };

    }

    let remainingTotal = 0;

    entries.forEach(([, quotaData]) => {

        const remainingFraction = Number(quotaData?.remaining || 0);
        const remainingPercentage = Math.max(0, Math.min(100, Math.round(remainingFraction * 100)));

        remainingTotal += remainingPercentage;

    });

    const averageRemaining = Math.round(remainingTotal / entries.length);
    const usedPercentage = 100 - averageRemaining;
    const level = quotaLevelFromUsedPercentage(usedPercentage);

    return {
        level,
        label: `${averageRemaining}% left`,
        modelCount: entries.length,
    };

}

function renderCredentialQuotaPreview(pathId, filename, managerType) {

    if (managerType !== 'primary') return '';

    const cached = AppState.quotaPreviewCache[filename] || {};
    const chipState = cached.loading
        ? { level: 'loading', label: t('quota_preview_loading'), title: t('card_loading_quota') }
        : cached.error
            ? { level: 'danger', label: t('quota_unavailable'), title: cached.error }
            : cached.summary
                ? {
                    level: cached.summary.level,
                    label: cached.summary.label,
                    title: cached.summary.modelCount
                        ? `Average quota: ${cached.summary.label} across ${cached.summary.modelCount} model${cached.summary.modelCount === 1 ? '' : 's'}`
                        : t('btn_view_quota_title'),
                }
                : { level: 'loading', label: t('quota_preview_loading'), title: t('card_loading_quota') };

    return `
        <button type="button" class="cred-quota-preview ${chipState.level}" id="quota-preview-${pathId}" onclick="loadPrimaryQuotaPreview('${pathId}')" title="${escapeHtml(chipState.title)}">
            <span>${escapeHtml(chipState.label)}</span>
        </button>
    `;

}

function updateCredentialQuotaPreview(pathId, filename) {

    const chip = document.getElementById(`quota-preview-${pathId}`);

    if (!chip) return;

    chip.outerHTML = renderCredentialQuotaPreview(pathId, filename, 'primary');

}

function renderCredentialErrorDetails(parsedMsg) {

    const error = parsedMsg?.error;
    if (!error) return '';

    const rows = [];

    if (error.status) rows.push(['Status', error.status]);

    if (Array.isArray(error.details)) {

        error.details.forEach((detail, index) => {

            if (detail['@type']) rows.push([`Type ${index + 1}`, detail['@type']]);
            if (detail.reason) rows.push([`Reason ${index + 1}`, detail.reason]);

            if (detail.metadata && typeof detail.metadata === 'object') {

                Object.entries(detail.metadata).forEach(([key, value]) => {
                    rows.push([key, String(value)]);
                });

            }

        });

    }

    if (!rows.length) return '';

    return `<div class="message-error-meta">${renderMessageResultRows(rows)}</div>`;

}

function buildCredentialErrorsHtml(filename, data) {

    const errorCodes = data.error_codes || [];
    const errorMessages = data.error_messages || {};
    const rows = renderMessageResultRows([
        [t('table_filename'), filename],
        ['Stored errors', errorCodes.length],
    ]);

    if (errorCodes.length === 0) {

        return `
            <div class="message-result-panel">
                <div class="message-result-intro">This credential has no stored provider errors.</div>
                <div class="message-result-section">
                    <div class="message-result-section-title">Error summary</div>
                    <div class="message-result-summary">${rows}</div>
                </div>
                <div class="modal-empty-state success">
                    <strong>${escapeHtml(t('status_no_errors'))}</strong>
                    <span>${escapeHtml(t('status_credential_normal'))}</span>
                </div>
            </div>
        `;

    }

    const errorCards = errorCodes.map((errorCode) => {

        const messageStr = errorMessages[errorCode] || t('no_details_available');
        let displayMsg = messageStr;
        let detailsHtml = '';

        try {

            const parsedMsg = JSON.parse(messageStr);

            if (parsedMsg?.error?.message) displayMsg = parsedMsg.error.message;

            detailsHtml = renderCredentialErrorDetails(parsedMsg);

        } catch {

            detailsHtml = '';

        }

        return `
            <div class="message-error-card">
                <div class="message-error-title">${escapeHtml(t('error_code_prefix'))} ${escapeHtml(String(errorCode))}</div>
                <div class="message-error-copy">${highlightHttpLinks(escapeHtml(displayMsg))}</div>
                ${detailsHtml}
            </div>
        `;

    }).join('');

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">These are the latest provider errors recorded for this credential.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Error summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Error details</div>
                <div class="message-error-list">${errorCards}</div>
            </div>
        </div>
    `;

}

function showConfirmModal(message, options = {}) {

    if (!options.title || !options.confirmLabel) {

        throw new Error('Confirmation modals require a contextual title and confirmation label.');

    }

    return new Promise((resolve) => {

        const modal = document.createElement('div');

        modal.className = 'message-modal-overlay';

        const title = options.title;

        const confirmLabel = options.confirmLabel;

        const cancelLabel = options.cancelLabel || t('btn_cancel');

        modal.innerHTML = `

            <div class="message-modal confirm" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}">

                <div class="message-modal-header">

                    <h3>${escapeHtml(title)}</h3>

                </div>

                <div class="message-modal-body">

                    ${renderDialogMessage(message, { compact: true })}

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

            <div class="message-modal prompt" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}">

                <div class="message-modal-header">

                    <h3>${escapeHtml(title)}</h3>

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

        'Content-Type': 'application/json'

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

function getCredentialProviderMeta(credInfo, managerType) {

    const provider = String(credInfo.provider || credInfo.provider_name || '')
        .trim()
        .toLowerCase()
        .replace(/[\s-]+/g, '_');

    if (provider === 'google_ai_studio' || provider === 'ai_studio' || provider === 'aistudio' || provider === 'gemini') {

        return {
            id: 'google_ai_studio',
            name: t('provider_google_ai_studio'),
            logo: '/frontend/assets/google-ai-studio-logo.png'
        };

    }

    if (provider === 'google_antigravity' || provider === 'antigravity' || provider === 'primary' || provider === 'provider' || (!provider && managerType === 'primary')) {

        return {
            id: 'google_antigravity',
            name: t('provider_antigravity'),
            logo: '/frontend/assets/antigravity-logo.png'
        };

    }

    return {
        id: 'code_assist',
        name: t('provider_code_assist'),
        logo: ''
    };

}

function createCredentialProviderGroup(providerMeta, credentials, manager) {

    const section = document.createElement('section');

    section.className = 'credential-provider-group';

    section.setAttribute('aria-labelledby', `credentialProviderGroup-${providerMeta.id}`);

    const logo = providerMeta.logo

        ? `<img src="${providerMeta.logo}" alt="">`

        : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

    const countLabel = `${credentials.length} credential${credentials.length === 1 ? '' : 's'}`;

    section.innerHTML = `

        <div class="credential-provider-group-header">

            <div class="credential-provider-group-logo" aria-hidden="true">${logo}</div>

            <h2 class="credential-provider-group-title" id="credentialProviderGroup-${providerMeta.id}">${escapeHtml(providerMeta.name)}</h2>

            <span class="credential-provider-group-count">${countLabel}</span>

        </div>

        <div class="credential-provider-grid"></div>

    `;

    const grid = section.querySelector('.credential-provider-grid');

    credentials.forEach((credInfo) => {

        grid.appendChild(createCredCard(credInfo, manager));

    });

    return section;

}

function createCredCard(credInfo, manager) {

    const div = document.createElement('div');

    const { status, filename } = credInfo;

    const managerType = manager.type;
    const providerMeta = getCredentialProviderMeta(credInfo, managerType);
    const isGoogleAIStudio = providerMeta.id === 'google_ai_studio';
    const accountLabel = credInfo.credential_label || credInfo.user_email || t('email_not_fetched');
    const accountClass = (credInfo.credential_label || credInfo.user_email) ? 'cred-email' : 'cred-email empty';
    const providerLogo = providerMeta.logo
        ? `<img src="${providerMeta.logo}" alt="${escapeHtml(providerMeta.name)} logo">`
        : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

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

    if (isGoogleAIStudio) {

        statusBadges += '<span class="status-badge muted" title="Google AI Studio API key credential">API key</span>';

    } else {

        const tier = (credInfo.tier || 'pro').toString().toLowerCase();

        const tierLabel = tier.toUpperCase();

        const tierClass = tier === 'ultra' ? 'tier-ultra' : (tier === 'free' ? 'tier-free' : 'tier-pro');

        statusBadges += `<span class="status-badge ${tierClass}" title="${t('tier_badge_title')}: ${tierLabel}">Tier: ${tierLabel}</span>`;

    }

    if (managerType === 'primary' && !isGoogleAIStudio) {

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

    AppState.credentialCardIndex[pathId] = {
        filename,
        managerType,
        email: credInfo.user_email || '',
        providerName: providerMeta.name,
    };

    const shouldAutoLoadQuota = managerType === 'primary' && !isGoogleAIStudio && !AppState.quotaPreviewCache[filename];

    if (shouldAutoLoadQuota) {

        AppState.quotaPreviewCache[filename] = { loading: true };

    }

    const actionButtons = `

        ${status.disabled

            ? `<button class="cred-btn enable" data-filename="${filename}" data-action="enable">${t('action_enable')}</button>`

            : `<button class="cred-btn disable" data-filename="${filename}" data-action="disable">${t('action_disable')}</button>`

        }

        <button class="cred-btn view" onclick="toggle${managerType === 'primary' ? 'Primary' : ''}CredDetails('${pathId}')">${t('btn_view_content')}</button>

        <button class="cred-btn download" onclick="download${managerType === 'primary' ? 'Primary' : ''}Cred('${filename}')">${t('btn_download')}</button>

        ${managerType === 'primary' && !isGoogleAIStudio ? `<button class="cred-btn" onclick="togglePrimaryQuotaDetails('${pathId}')" title="${t('btn_view_quota_title')}">${t('btn_view_quota')}</button>` : ''}

        ${managerType === 'primary' && !isGoogleAIStudio ? (credInfo.enable_credit

            ? `<button class="cred-btn" data-filename="${filename}" data-action="disable_credit" title="${t('btn_disable_credit_title')}">${t('btn_disable_credit')}</button>`

            : `<button class="cred-btn" data-filename="${filename}" data-action="enable_credit" title="${t('btn_enable_credit_title')}">${t('btn_enable_credit')}</button>`

        ) : ''}

        ${managerType !== 'primary' ? `<button class="cred-btn" onclick="configurePreviewChannel('${filename}')" title="${t('btn_setup_preview_title')}">${t('btn_setup_preview')}</button>` : ''}

        <button class="cred-btn" onclick="verify${managerType === 'primary' ? 'Primary' : ''}ProjectId('${filename}')" title="${t('btn_verify_id_title')}">${t('btn_verify_id')}</button>

        <button class="cred-btn" onclick="test${managerType === 'primary' ? 'Primary' : ''}Credential('${filename}')" title="${t('btn_message_test_title')}">${t('btn_message_test')}</button>

        <button class="cred-btn" onclick="toggle${managerType === 'primary' ? 'Primary' : ''}ErrorDetails('${pathId}')" title="${t('btn_view_errors_title')}">${t('btn_view_errors')}</button>

        <button class="cred-btn delete" data-filename="${filename}" data-action="delete">${t('action_delete')}</button>

    `;

    const checkboxClass = manager.getElementId('file-checkbox');
    const quotaPreview = isGoogleAIStudio ? '' : renderCredentialQuotaPreview(pathId, filename, managerType);

    div.innerHTML = `

        <div class="cred-header">

            <div class="cred-title-row">

                <input type="checkbox" class="${checkboxClass}" data-filename="${filename}" aria-label="Select ${escapeHtml(providerMeta.name)} credential for ${escapeHtml(accountLabel)}" onchange="toggle${managerType === 'primary' ? 'Primary' : ''}FileSelection('${filename}')">

                <div class="cred-identity" title="${escapeHtml(filename)}">
                    <div class="cred-provider-logo" aria-hidden="true">${providerLogo}</div>
                    <div class="cred-identity-copy">
                        <div class="cred-provider-name">${escapeHtml(providerMeta.name)}</div>
                        <div class="${accountClass}">${escapeHtml(accountLabel)}</div>
                    </div>
                </div>

                ${quotaPreview}

            </div>

            <div class="cred-status">${statusBadges}</div>

        </div>

        <div class="cred-actions">${actionButtons}</div>

    `;

    div.querySelectorAll('[data-filename][data-action]').forEach(button => {

        button.addEventListener('click', async function () {

            const fn = this.getAttribute('data-filename');

            const action = this.getAttribute('data-action');

            if (action === 'delete') {

                if (!(await showConfirmModal(t('confirm_delete_cred'), {

                    title: t('confirm_delete_cred_title'),

                    confirmLabel: t('action_delete')

                }))) return;

            }

            manager.action(fn, action);


        });

    });

    if (shouldAutoLoadQuota) {

        setTimeout(() => loadPrimaryQuotaPreview(pathId), 0);

    }

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

    const { filename, manager: resolvedManager } = getCredentialModalContext(pathId, manager);

    if (!filename) return;

    showStatus(t('status_loading_file_content'), 'info');

    try {

        const modeParam = resolvedManager.type === 'primary' ? 'mode=provider' : 'mode=code_assist';

        const endpoint = `./api/creds/detail/${encodeURIComponent(filename)}?${modeParam}`;

        const response = await fetch(endpoint, { headers: getAuthHeaders() });

        const data = await response.json();

        if (response.ok && data.content) {

            showMessageModal('Credential Content', buildCredentialContentHtml(filename, data.content), 'info', {html: true});

        } else {

            const errorMsg = data.error || data.detail || t('unknown_error');

            showStatus(`${t('unable_to_load_file_content')} ${errorMsg}`, 'error');

            showMessageModal('Credential Content', `${t('unable_to_load_file_content')} ${errorMsg}`, 'error');

        }

    } catch (error) {

        const errorMsg = `${t('unable_to_load_file_content')} ${error.message}`;

        showStatus(errorMsg, 'error');

        showMessageModal('Credential Content', errorMsg, 'error');

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

            AppState.authenticated = false;

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

            AppState.authenticated = true;

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

            AppState.authenticated = true;

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

    try {

        const response = await fetch('./api/config/get', {

            headers: getAuthHeaders()

        });

        if (response.ok) {

            AppState.authenticated = true;

            // showStatus(t('autologin_successful'), 'success');

            navigate(window.location.pathname, false);

            return true;

        } else {

            AppState.authenticated = false;

            navigate('/login', false);

            return false;

        }

    } catch (error) {

        AppState.authenticated = false;

        navigate('/login', false);

        return false;

    }

}

async function logout() {

    try {

        await fetch('./api/auth/logout', {method: 'POST'});

    } catch (error) {

        console.warn('Failed to notify the server about sign-out.', error);

    }

    AppState.authenticated = false;

    showStatus(t('logged_out'), 'info');

    const passwordInput = document.getElementById('loginPassword');

    if (passwordInput) passwordInput.value = '';

    navigate('/login', false);

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

function initPoolToolsMenu() {

    document.addEventListener('click', (event) => {

        document.querySelectorAll('.pool-tools[open]').forEach((menu) => {

            if (!menu.contains(event.target)) {

                menu.removeAttribute('open');

            }

        });

    });

    document.addEventListener('keydown', (event) => {

        if (event.key !== 'Escape') return;

        document.querySelectorAll('.pool-tools[open]').forEach((menu) => {

            menu.removeAttribute('open');

        });

    });

}

document.addEventListener('DOMContentLoaded', initPoolToolsMenu);

window.addEventListener('resize', () => {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) updateTabSlider(activeTab, false);

    if (window.innerWidth > 960) setMobileMenuState(false);

});

function switchTab(tabName) {

    const route = TAB_MAP[tabName] || '/dashboard';

    navigate(route, true);

}

const PROVIDER_WORKSPACES = {
    google_antigravity: {
        selectorId: 'providerSelectorGoogleAntigravity',
        panelId: 'providerWorkspaceGoogleAntigravity'
    },
    google_ai_studio: {
        selectorId: 'providerSelectorGoogleAiStudio',
        panelId: 'providerWorkspaceGoogleAiStudio'
    }
};

function selectProviderWorkspace(providerId, focusSelector = false) {
    const selected = PROVIDER_WORKSPACES[providerId];
    if (!selected) return;

    AppState.activeProviderWorkspace = providerId;

    Object.entries(PROVIDER_WORKSPACES).forEach(([id, workspace]) => {
        const selector = document.getElementById(workspace.selectorId);
        const panel = document.getElementById(workspace.panelId);
        const isActive = id === providerId;

        selector?.classList.toggle('active', isActive);
        selector?.setAttribute('aria-selected', String(isActive));
        if (selector) selector.tabIndex = isActive ? 0 : -1;
        panel?.classList.toggle('hidden', !isActive);
    });

    if (focusSelector) {
        document.getElementById(selected.selectorId)?.focus();
    }
}

function initProviderWorkspaceSelector() {
    const providerIds = Object.keys(PROVIDER_WORKSPACES);

    providerIds.forEach((providerId, index) => {
        const selector = document.getElementById(PROVIDER_WORKSPACES[providerId].selectorId);
        selector?.addEventListener('keydown', (event) => {
            if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
            event.preventDefault();

            let nextIndex = index;
            if (event.key === 'ArrowLeft') nextIndex = (index - 1 + providerIds.length) % providerIds.length;
            if (event.key === 'ArrowRight') nextIndex = (index + 1) % providerIds.length;
            if (event.key === 'Home') nextIndex = 0;
            if (event.key === 'End') nextIndex = providerIds.length - 1;

            selectProviderWorkspace(providerIds[nextIndex], true);
        });
    });

    selectProviderWorkspace(AppState.activeProviderWorkspace);
}

document.addEventListener('DOMContentLoaded', initProviderWorkspaceSelector);

function triggerTabDataLoad(tabName) {

    if (tabName === 'dashboard') {

        refreshUsageStats();

        updateEndpointUrls();
    }

    if (tabName === 'pool') {
        AppState.primaryCreds.refresh();
    }

    if (tabName === 'models') loadModelCatalog();

    if (tabName === 'providers') {
        loadAntigravitySettings();
        loadGoogleAIStudioSettings();
    }

    if (tabName === 'config') loadConfig();

    if (tabName === 'logs') connectWebSocket();

}

const MODEL_PROVIDER_META = {
    google_antigravity: {
        name: 'Google Antigravity',
        logo: '/frontend/assets/antigravity-logo.png'
    },
    google_ai_studio: {
        name: 'Google AI Studio',
        logo: '/frontend/assets/google-ai-studio-logo.png'
    }
};

function modelProviderMeta(providerId) {
    if (MODEL_PROVIDER_META[providerId]) return MODEL_PROVIDER_META[providerId];
    const name = String(providerId || 'Provider')
        .split(/[_-]+/)
        .filter(Boolean)
        .map(word => ['ai', 'api'].includes(word.toLowerCase())
            ? word.toUpperCase()
            : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
    return { name, logo: '' };
}

function modelCatalogEntry(modelId) {
    return AppState.modelCatalog.find(entry => entry.model_id === modelId) || {
        model_id: modelId,
        providers: [],
        available: false
    };
}

function appendModelProviderBadges(container, providers) {
    const values = Array.isArray(providers) ? providers : [];
    if (values.length === 0) {
        const unavailable = document.createElement('span');
        unavailable.className = 'model-provider-badge unavailable';
        unavailable.textContent = 'Unavailable';
        container.appendChild(unavailable);
        return;
    }
    values.forEach(providerId => {
        const meta = modelProviderMeta(providerId);
        const badge = document.createElement('span');
        badge.className = 'model-provider-badge';
        if (meta.logo) {
            const logo = document.createElement('img');
            logo.src = meta.logo;
            logo.alt = '';
            badge.appendChild(logo);
        }
        badge.appendChild(document.createTextNode(meta.name));
        container.appendChild(badge);
    });
}

function updateModelPoolSummary() {
    const available = AppState.modelCatalog.filter(entry => entry.available).length;
    const unavailable = AppState.selectedModels.filter(
        modelId => !modelCatalogEntry(modelId).available
    ).length;
    const availableEl = document.getElementById('modelStatAvailable');
    const selectedEl = document.getElementById('modelStatSelected');
    const unavailableEl = document.getElementById('modelStatUnavailable');
    if (availableEl) availableEl.textContent = String(available);
    if (selectedEl) selectedEl.textContent = String(AppState.selectedModels.length);
    if (unavailableEl) unavailableEl.textContent = String(unavailable);

    const status = document.getElementById('modelPoolStatus');
    if (status) {
        const ready = AppState.modelPoolEnabled && AppState.selectedModels.length > 0 && unavailable < AppState.selectedModels.length;
        status.textContent = ready ? 'Ready' : 'Not configured';
        status.className = ready ? 'status-badge success' : 'status-badge muted';
    }
}

function createModelOrderButton(label, symbol, disabled, handler) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'model-order-button';
    button.setAttribute('aria-label', label);
    button.title = label;
    button.textContent = symbol;
    button.disabled = disabled;
    button.addEventListener('click', handler);
    return button;
}

function renderSelectedModels() {
    const list = document.getElementById('selectedModelList');
    if (!list) return;
    list.replaceChildren();

    if (AppState.selectedModels.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'model-empty-state';
        empty.textContent = 'Select at least one provider model to activate omway.';
        list.appendChild(empty);
        updateModelPoolSummary();
        return;
    }

    AppState.selectedModels.forEach((modelId, index) => {
        const entry = modelCatalogEntry(modelId);
        const item = document.createElement('div');
        item.className = 'selected-model-item';

        const order = document.createElement('span');
        order.className = 'selected-model-order';
        order.textContent = String(index + 1);

        const details = document.createElement('div');
        details.className = 'selected-model-details';
        const name = document.createElement('strong');
        name.textContent = modelId;
        const providers = document.createElement('div');
        providers.className = 'model-provider-badges';
        appendModelProviderBadges(providers, entry.providers);
        details.append(name, providers);

        const actions = document.createElement('div');
        actions.className = 'model-order-actions';
        actions.append(
            createModelOrderButton('Move model up', '↑', index === 0, () => moveSelectedModel(index, -1)),
            createModelOrderButton('Move model down', '↓', index === AppState.selectedModels.length - 1, () => moveSelectedModel(index, 1)),
            createModelOrderButton('Remove model', '×', false, () => removeSelectedModel(modelId))
        );

        item.append(order, details, actions);
        list.appendChild(item);
    });
    updateModelPoolSummary();
}

function renderModelCatalog() {
    const list = document.getElementById('modelCatalogList');
    if (!list) return;
    const query = document.getElementById('modelCatalogSearch')?.value.trim().toLowerCase() || '';
    const entries = AppState.modelCatalog.filter(entry => {
        if (!query) return true;
        return entry.model_id.toLowerCase().includes(query)
            || entry.providers.some(provider => modelProviderMeta(provider).name.toLowerCase().includes(query));
    });
    list.replaceChildren();

    if (entries.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'model-empty-state';
        empty.textContent = AppState.modelCatalog.length
            ? 'No models match this search.'
            : 'No models are available. Add or enable a provider credential, then refresh the catalog.';
        list.appendChild(empty);
        return;
    }

    entries.forEach(entry => {
        const label = document.createElement('label');
        label.className = `model-catalog-item${entry.available ? '' : ' unavailable'}`;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = AppState.selectedModels.includes(entry.model_id);
        checkbox.disabled = !entry.available && !checkbox.checked;
        checkbox.addEventListener('change', () => toggleModelSelection(entry.model_id, checkbox.checked));

        const details = document.createElement('div');
        details.className = 'model-catalog-details';
        const name = document.createElement('strong');
        name.textContent = entry.model_id;
        const providers = document.createElement('div');
        providers.className = 'model-provider-badges';
        appendModelProviderBadges(providers, entry.providers);
        details.append(name, providers);
        label.append(checkbox, details);
        list.appendChild(label);
    });
}

function toggleModelSelection(modelId, selected) {
    if (selected && !AppState.selectedModels.includes(modelId)) {
        AppState.selectedModels.push(modelId);
    } else if (!selected) {
        AppState.selectedModels = AppState.selectedModels.filter(value => value !== modelId);
    }
    renderSelectedModels();
    renderModelCatalog();
}

function moveSelectedModel(index, offset) {
    const nextIndex = index + offset;
    if (index < 0 || nextIndex < 0 || nextIndex >= AppState.selectedModels.length) return;
    const values = [...AppState.selectedModels];
    [values[index], values[nextIndex]] = [values[nextIndex], values[index]];
    AppState.selectedModels = values;
    renderSelectedModels();
    renderModelCatalog();
}

function removeSelectedModel(modelId) {
    AppState.selectedModels = AppState.selectedModels.filter(value => value !== modelId);
    renderSelectedModels();
    renderModelCatalog();
}

async function loadModelCatalog(forceRefresh = false) {
    const loading = document.getElementById('modelCatalogLoading');
    const workspace = document.getElementById('modelPoolWorkspace');
    const refreshButton = document.getElementById('refreshModelCatalogBtn');
    if (loading) loading.classList.remove('hidden');
    if (workspace) workspace.classList.add('hidden');
    if (refreshButton) refreshButton.disabled = true;
    try {
        const response = await fetch(`./api/model-catalog${forceRefresh ? '?refresh=true' : ''}`, {
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        AppState.modelCatalog = Array.isArray(data.catalog) ? data.catalog : [];
        AppState.selectedModels = Array.isArray(data.pool?.selected_models)
            ? [...data.pool.selected_models]
            : [];
        AppState.modelPoolEnabled = data.pool?.enabled !== false;
        renderSelectedModels();
        renderModelCatalog();
        if (workspace) workspace.classList.remove('hidden');
        if (forceRefresh) showStatus('Provider model catalog refreshed.', 'success');
    } catch (error) {
        showStatus(`Failed to load the provider model catalog: ${error.message}`, 'error');
    } finally {
        if (loading) loading.classList.add('hidden');
        if (refreshButton) refreshButton.disabled = false;
    }
}

async function saveModelPool() {
    const button = document.getElementById('saveModelPoolBtn');
    if (button) button.disabled = true;
    try {
        const response = await fetch('./api/model-pools/omway', {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                selected_models: AppState.selectedModels,
                enabled: AppState.selectedModels.length > 0
            })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        AppState.selectedModels = [...(data.pool?.selected_models || AppState.selectedModels)];
        AppState.modelPoolEnabled = data.pool?.enabled !== false;
        renderSelectedModels();
        renderModelCatalog();
        showStatus(data.message || 'Virtual model updated.', 'success');
    } catch (error) {
        showStatus(`Failed to save omway: ${error.message}`, 'error');
    } finally {
        if (button) button.disabled = false;
    }
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

            showStatus(t('error_dataerror_failed_to_fetch_aut', {data_error: data.detail || data.error || t('failed_to_fetch_authentication_link')}), 'error');

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

            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: data.detail || data.error || t('failed_to_retrieve_authentication_f_dup')}), 'error');

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

            AppState.primaryCredentialFilename = '';

            const authUrlLink = document.getElementById('primaryAuthUrl');

            authUrlLink.href = data.auth_url;

            authUrlLink.textContent = data.auth_url;

            document.getElementById('primaryAuthUrlSection').classList.remove('hidden');
            document.getElementById('primarySaveResult')?.classList.add('hidden');
            document.getElementById('primaryCredsSection')?.classList.add('hidden');
            const primaryCallbackUrlInput = document.getElementById('primaryCallbackUrlInput');
            if (primaryCallbackUrlInput) primaryCallbackUrlInput.value = '';
            updatePrimaryCallbackUrlPlaceholder(data.callback_url);
            setPrimaryCallbackUrlSectionVisible(true);
            const primaryCredsContent = document.getElementById('primaryCredsContent');
            if (primaryCredsContent) primaryCredsContent.textContent = '';

            showStatus(t('primary_authentication_link_gen'), 'success');

        } else {

            showStatus(t('error_dataerror_failed_to_generate', {data_error: data.detail || data.error || t('failed_to_generate_authentication_l_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_primary_authentication_link');

    }

}

function setPrimaryCallbackUrlSectionVisible(visible, focusInput = false) {
    const section = document.getElementById('primaryCallbackUrlSection');
    const input = document.getElementById('primaryCallbackUrlInput');
    if (!section) return;
    section.classList.toggle('hidden', !visible);
    if (visible && focusInput && input) {
        input.focus();
        input.select();
    }
}

function updatePrimaryCallbackUrlPlaceholder(callbackUrl = '') {
    const input = document.getElementById('primaryCallbackUrlInput');
    if (!input) return;

    const callbackBase = callbackUrl || 'http://localhost:4283/callback';
    input.placeholder = `${callbackBase}?state=...&code=...`;
}

function getPrimaryCallbackUrl() {
    return document.getElementById('primaryCallbackUrlInput')?.value.trim() || '';
}

function validateCallbackUrl(callbackUrl) {
    if (!callbackUrl) {
        showStatus(t('please_enter_the_callback_url'), 'error');
        return false;
    }

    if (!callbackUrl.startsWith('http://') && !callbackUrl.startsWith('https://')) {
        showStatus(t('please_enter_a_valid_url_starting_w'), 'error');
        return false;
    }

    if (!callbackUrl.includes('code=') || !callbackUrl.includes('state=')) {
        showStatus(t('this_is_not_a_valid_callback_url_pl'), 'error');
        return false;
    }

    return true;
}

async function completePrimaryCredentialSave(data) {
    const credentialSaved = data.credential_saved !== false;
    const credentialAction = data.credential_action || 'created';
    const resultTitle = credentialAction === 'skipped'
        ? t('provider_credential_skipped_title')
        : credentialAction === 'replaced'
            ? t('provider_credential_replaced_title')
            : t('provider_credential_saved_title');
    const fileSuffix = data.file_path ? ` File: ${data.file_path}.` : '';
    const resultBody = data.message
        ? `${data.message}${data.message.endsWith('.') ? '' : '.'}${fileSuffix}`
        : credentialSaved
            ? t('provider_credential_saved_body', {data_file_path: data.file_path})
            : t('provider_credential_skipped_body', {data_file_path: data.file_path});

    const primaryCredsSection = document.getElementById('primaryCredsSection');
    const primaryCredsContent = document.getElementById('primaryCredsContent');
    const primaryCredsDownloadBtn = document.getElementById('primaryCredsDownloadBtn');

    if (credentialSaved) {
        primaryCredsContent.textContent = JSON.stringify(data.credentials, null, 2);
        primaryCredsSection.classList.remove('hidden');
        primaryCredsDownloadBtn?.classList.remove('hidden');
        AppState.primaryCredentialFilename = getDownloadFilename(data.file_path, `primary-credential-${Date.now()}.json`);
    } else {
        primaryCredsContent.textContent = '';
        primaryCredsSection.classList.add('hidden');
        primaryCredsDownloadBtn?.classList.add('hidden');
        AppState.primaryCredentialFilename = '';
    }

    AppState.primaryAuthInProgress = false;
    setPrimaryCallbackUrlSectionVisible(false);

    const saveResult = document.getElementById('primarySaveResult');
    const saveResultTitle = document.getElementById('primarySaveResultTitle');
    const saveResultText = document.getElementById('primarySaveResultText');
    if (saveResult && saveResultText) {
        if (saveResultTitle) saveResultTitle.textContent = resultTitle;
        saveResultText.textContent = resultBody;
        saveResult.classList.remove('hidden');
    }

    try {
        await AppState.primaryCreds.refresh();
        await refreshUsageStats();
    } catch (refreshError) {
        console.warn('Credential flow completed, but pool refresh failed:', refreshError);
    }

    showStatus(resultBody, credentialSaved ? 'success' : 'info');
}

async function getPrimaryCredentials() {

    if (!AppState.primaryAuthInProgress) {

        showStatus(t('please_obtain_the_primary_authe'), 'error');

        return;

    }

    const btn = document.getElementById('getPrimaryCredsBtn');

    btn.disabled = true;

    btn.textContent = t('checking_provider_authorization');

    try {

        const callbackUrl = getPrimaryCallbackUrl();
        if (callbackUrl) {
            if (!validateCallbackUrl(callbackUrl)) return;
            await savePrimaryCredentialsFromCallbackUrl(callbackUrl, btn);
            return;
        }

        showStatus(t('checking_provider_authorization'), 'info');

        const state = AppState.primaryAuthState;
        const statusResponse = await fetch(`./api/auth/status?state=${encodeURIComponent(state)}`, {
            headers: getAuthHeaders()
        });
        const statusData = await statusResponse.json().catch(() => ({}));

        if (!statusResponse.ok) {
            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: statusData.detail || statusData.error || t('unknown_error')}), 'error');
            return;
        }

        if (statusData.status === 'not_found') {
            AppState.primaryAuthInProgress = false;
            showStatus(t('provider_authorization_expired'), 'error');
            return;
        }

        if (statusData.status !== 'completed') {
            setPrimaryCallbackUrlSectionVisible(true, true);
            showStatus(t('provider_authorization_pending'), 'info');
            return;
        }

        btn.textContent = t('saving_provider_credentials');

        showStatus(t('saving_provider_credentials'), 'info');

        const response = await fetch('./api/auth/callback', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ mode: 'provider' })

        });

        const data = await response.json();

        if (response.ok) {

            await completePrimaryCredentialSave(data);

        } else {

            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: data.detail || data.error || t('failed_to_retrieve_authentication_f_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('fetch_primary_credentials');

    }

}

async function savePrimaryCredentialsFromCallbackUrl(callbackUrl, btn = document.getElementById('getPrimaryCredsBtn')) {
    try {
        if (btn) btn.textContent = t('saving_provider_credentials');
        showStatus(t('saving_provider_credentials_from_callback'), 'info');

        const response = await fetch('./api/auth/callback-url', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ callback_url: callbackUrl, mode: 'provider' })
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            await completePrimaryCredentialSave(data);
            const input = document.getElementById('primaryCallbackUrlInput');
            if (input) input.value = '';
        } else {
            showStatus(data.detail || data.error || t('failed_to_fetch_credentials_from_ca'), 'error');
        }
    } catch (error) {
        showStatus(t('failed_to_retrieve_credentials_from_dup', {error_message: error.message}), 'error');
    }
}

function getDownloadFilename(filePath, fallback) {

    const rawName = String(filePath || '').split(/[\\/]/).pop().trim();

    return rawName || fallback;

}

function downloadPrimaryCredentials() {

    const content = document.getElementById('primaryCredsContent').textContent;

    const blob = new Blob([content], { type: 'application/json' });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = getDownloadFilename(AppState.primaryCredentialFilename, `primary-credential-${Date.now()}.json`);

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

            const credentialsContent = document.getElementById('credentialsContent');
            const pre = document.createElement('pre');
            pre.textContent = JSON.stringify(result.credentials, null, 2);
            credentialsContent.replaceChildren(pre);

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

            showStatus(result.detail || result.error || t('failed_to_fetch_credentials_from_ca'), 'error');

        }

        document.getElementById('callbackUrlInput').value = '';

    } catch (error) {

        showStatus(t('failed_to_retrieve_credentials_from_dup', {error_message: error.message}), 'error');

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

    fetch(`./api/creds/download/${filename}`)

        .then(r => r.ok ? r.blob() : Promise.reject())

        .then(blob => {

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = filename;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('status_download_success', {filename}), 'success');

        })

        .catch(() => showStatus(t('download_failed_filename', {filename: filename}), 'error'));

}

async function downloadAllCreds() {

    try {

        const response = await fetch('./api/creds/download-all');

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

    if (await showConfirmModal(t('confirm_delete_cred'), {

        title: t('confirm_delete_cred_title'),

        confirmLabel: t('action_delete')

    })) {

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

function selectPoolImportArchive() {

    const input = document.getElementById('poolImportArchiveInput');

    if (!input) return;

    input.value = '';
    input.click();

}

function getPoolImportActionLabel(result) {

    if (result.status === 'error') return 'Failed';
    if (result.status === 'skipped') return 'Skipped';
    if (result.action === 'replaced') return 'Renewed';
    if (result.action === 'updated') return 'Updated';
    return 'Added';

}

function buildPoolImportResultHtml(data) {

    const providerItems = Object.values(data.providers || {}).filter((provider) => {

        return ['created', 'updated', 'replaced', 'skipped', 'failed']
            .some((key) => Number(provider[key] || 0) > 0);

    });

    const providerSummary = providerItems.length
        ? `
            <div class="message-result-section">
                <div class="message-result-section-title">Provider Summary</div>
                <div class="usage-provider-summary pool-import-provider-summary">
                    ${providerItems.map((provider) => {
                        const providerMeta = getCredentialProviderMeta({ provider: provider.provider }, 'usage');
                        const imported = Number(provider.created || 0)
                            + Number(provider.updated || 0)
                            + Number(provider.replaced || 0);
                        const logo = providerMeta.logo
                            ? `<img src="${providerMeta.logo}" alt="">`
                            : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

                        return `
                            <article class="usage-provider-item">
                                <div class="usage-provider-identity">
                                    <div class="usage-provider-logo" aria-hidden="true">${logo}</div>
                                    <div>
                                        <div class="usage-provider-name">${escapeHtml(providerMeta.name)}</div>
                                        <div class="usage-provider-meta">Credential restore</div>
                                    </div>
                                </div>
                                <dl class="usage-provider-metrics">
                                    <div><dt>Imported</dt><dd>${formatUsageNumber(imported)}</dd></div>
                                    <div><dt>Skipped</dt><dd>${formatUsageNumber(provider.skipped)}</dd></div>
                                    <div><dt>Failed</dt><dd>${formatUsageNumber(provider.failed)}</dd></div>
                                </dl>
                            </article>
                        `;
                    }).join('')}
                </div>
            </div>
        `
        : '';

    const results = Array.isArray(data.results) ? data.results : [];
    const visibleResults = results.slice(0, 24);
    const fileResults = visibleResults.map((result) => {

        const statusClass = result.status === 'error'
            ? 'danger'
            : result.status === 'skipped'
                ? 'muted'
                : 'success';
        const providerName = result.provider_name
            || (result.provider ? getCredentialProviderMeta({ provider: result.provider }, 'usage').name : 'Unrecognized provider');
        const sourceName = result.source_filename || result.filename || 'Credential file';

        return `
            <div class="upload-result-item">
                <div class="pool-import-result-heading">
                    <span class="status-badge ${statusClass}">${escapeHtml(getPoolImportActionLabel(result))}</span>
                    <span class="upload-result-file">${escapeHtml(sourceName)}</span>
                </div>
                <div class="upload-result-message">${escapeHtml(providerName)} - ${escapeHtml(ensureTerminalPunctuation(result.message || 'Import completed.'))}</div>
            </div>
        `;

    }).join('');
    const hiddenCount = Math.max(0, results.length - visibleResults.length);
    const fileSection = results.length
        ? `
            <div class="message-result-section">
                <div class="message-result-section-title">File Results</div>
                <div class="upload-result-details">
                    ${fileResults}
                    ${hiddenCount ? `<div class="upload-result-message">${hiddenCount} more ${hiddenCount === 1 ? 'result was' : 'results were'} processed.</div>` : ''}
                </div>
            </div>
        `
        : '';

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">The archive was inspected and each credential was routed through its provider-specific validation and duplicate checks.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Restore Summary</div>
                <div class="message-result-summary pool-import-summary">${renderMessageResultRows([
                    ['Credential files', Number(data.total_count || 0)],
                    ['Imported', Number(data.uploaded_count || 0)],
                    ['Skipped', Number(data.skipped_count || 0)],
                    ['Failed', Number(data.error_count || 0)],
                ])}</div>
            </div>
            ${providerSummary}
            ${fileSection}
        </div>
    `;

}

async function handlePoolImportArchive(event) {

    const input = event.target;
    const archive = input?.files?.[0];

    if (!archive) return;

    if (!archive.name.toLowerCase().endsWith('.zip')) {

        showStatus('Select a ZIP archive created from the credential pool.', 'error');
        input.value = '';
        return;

    }

    if (archive.size > 10 * 1024 * 1024) {

        showStatus('Pool archive exceeds the 10 MB upload limit.', 'error');
        input.value = '';
        return;

    }

    const button = document.getElementById('poolImportArchiveBtn');
    const originalLabel = button?.textContent || 'Import ZIP';
    const formData = new FormData();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15 * 60 * 1000);
    formData.append('archive', archive);

    if (button) {

        button.disabled = true;
        button.textContent = 'Importing...';

    }

    showStatus('Inspecting the pool archive and validating provider credentials.', 'info');

    try {

        const response = await fetch('./api/creds/import', {
            method: 'POST',
            body: formData,
            signal: controller.signal,
        });
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {

            throw new Error(data.detail || data.error || `Pool restore failed with HTTP ${response.status}.`);

        }

        const variant = Number(data.error_count || 0) > 0
            ? (Number(data.uploaded_count || 0) > 0 ? 'warning' : 'error')
            : Number(data.skipped_count || 0) > 0
                ? 'info'
                : 'success';

        showStatus(data.message || 'Pool archive restored.', variant);
        showMessageModal('Pool Import', buildPoolImportResultHtml(data), variant, { html: true });
        await AppState.primaryCreds.refresh();
        refreshUsageStats();

    } catch (error) {

        const message = error.name === 'AbortError'
            ? 'Pool restore timed out while validating provider credentials.'
            : error.message;
        showStatus(message, 'error');
        showMessageModal('Pool Import', message, 'error');

    } finally {

        clearTimeout(timeout);
        input.value = '';
        if (button) {

            button.disabled = false;
            button.textContent = originalLabel;

        }

    }

}

function handleFileSelect(event) { AppState.uploadFiles.handleFileSelect(event); }

function clearFiles() { AppState.uploadFiles.clearFiles(); }

function uploadFiles() { AppState.uploadFiles.upload(); }

function handlePrimaryFileSelect(event) { AppState.primaryUploadFiles.handleFileSelect(event); }

function handlePrimaryFileDrop(event) {

    event.preventDefault();

    event.currentTarget.style.borderColor = '#007bff';

    event.currentTarget.style.backgroundColor = '#f8f9fa';

    AppState.primaryUploadFiles.addFiles(Array.from(event.dataTransfer.files));

}

function clearPrimaryFiles() { AppState.primaryUploadFiles.clearFiles(); }

function uploadPrimaryFiles() { AppState.primaryUploadFiles.upload(); }

function handleGoogleAiStudioFileSelect(event) {
    AppState.googleAiStudioUploadFiles.handleFileSelect(event);
}

function handleGoogleAiStudioFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    AppState.googleAiStudioUploadFiles.addFiles(Array.from(event.dataTransfer.files));
}

function clearGoogleAiStudioFiles() {
    AppState.googleAiStudioUploadFiles.clearFiles();
}

function uploadGoogleAiStudioFiles() {
    AppState.googleAiStudioUploadFiles.upload();
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

            showMessageModal('Credential Verification', buildCredentialVerificationHtml(filename, data), 'success', {html: true});

            await AppState.creds.refresh();

        } else {

            const errorMsg = data.message || t('verification_failed');

            showStatus(` ${errorMsg}`, 'error');

            showMessageModal('Credential Verification', t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(` ${errorMsg}`, 'error');

        showMessageModal('Credential Verification', ` ${errorMsg}`, 'error');

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

            showMessageModal('Credential Verification', buildCredentialVerificationHtml(filename, data), 'success', {html: true});

            await AppState.primaryCreds.refresh();

        } else {

            const errorMsg = data.message || t('verification_failed');

            showStatus(` ${errorMsg}`, 'error');

            showMessageModal('Credential Verification', t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(` ${errorMsg}`, 'error');

        showMessageModal('Credential Verification', ` ${errorMsg}`, 'error');

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

        const logicalStatus = data.status_code || response.status;
        const isRateLimited = logicalStatus === 429 && data.success === true;

        if (response.status === 200 || isRateLimited) {

            const resultHtml = buildCredentialTestResultHtml(filename, data, response, { mode: 'Code Assist' });

            showStatus(isRateLimited ? t('credential_rate_limited') : t('test_successful'), isRateLimited ? 'warning' : 'success');

            showMessageModal('Message Test', resultHtml, isRateLimited ? 'info' : 'success', {html: true});

            await AppState.creds.refresh();

        }

        else {

            const errorDetails = buildCredentialTestErrorHtml(filename, data, response);

            showStatus(`Test failed: ${data.message || `${t('error_code_prefix')} ${data.status_code || response.status}`}`, 'error');

            showMessageModal('Message Test', errorDetails, 'error', {html: true});

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal('Message Test', errorMsg, 'error');

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

        const logicalStatus = data.status_code || response.status;
        const isRateLimited = logicalStatus === 429 && data.success === true;

        if (response.status === 200 || isRateLimited) {

            const resultHtml = buildCredentialTestResultHtml(filename, data, response, { mode: 'Provider' });

            showStatus(isRateLimited ? t('credential_rate_limited') : t('test_successful'), isRateLimited ? 'warning' : 'success');

            showMessageModal('Message Test', resultHtml, isRateLimited ? 'info' : 'success', {html: true});

            await AppState.primaryCreds.refresh();

        }

        else {

            const errorDetails = buildCredentialTestErrorHtml(filename, data, response);

            showStatus(`Test failed: ${data.message || `${t('error_code_prefix')} ${data.status_code || response.status}`}`, 'error');

            showMessageModal('Message Test', errorDetails, 'error', {html: true});

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal('Message Test', errorMsg, 'error');

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

            const successMsg = `${t('status_action_success', {action: t('btn_setup_preview')})}\n${t('table_filename')}: ${filename}\n${t('credential_status_label')} ${data.message}`;

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal('Preview Channel Configuration', `${t('status_action_success', {action: t('btn_setup_preview')})}\n\n${t('table_filename')}: ${filename}\n\n${data.message}\n\nSetting ID: ${data.setting_id || 'N/A'}\nBinding ID: ${data.binding_id || 'N/A'}`, 'success');

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

            showMessageModal('Preview Channel Configuration', alertMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_configure_preview_channel', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal('Preview Channel Configuration', errorMsg, 'error');

    }

}

async function togglePrimaryQuotaDetails(pathId) {

    const context = getCredentialModalContext(pathId, AppState.primaryCreds);
    const { filename } = context;

    if (!filename) return;

    showStatus(t('card_loading_quota'), 'info');

    try {

        const { response, data } = await fetchPrimaryQuota(filename);

        if (response.ok && data.success) {

            AppState.quotaPreviewCache[filename] = {
                summary: summarizeCredentialQuota(data),
                data,
            };

            updateCredentialQuotaPreview(pathId, filename);

            showMessageModal(t('quota_details'), buildCredentialQuotaHtml(filename, data, context), 'info', {html: true});

        } else {

            const errorMsg = data.error || t('failed_to_get_quota_information');

            AppState.quotaPreviewCache[filename] = { error: errorMsg };

            updateCredentialQuotaPreview(pathId, filename);

            showStatus(errorMsg, 'error');

            showMessageModal(t('quota_details'), errorMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_get_quota_information_err', {error_message: error.message});

        AppState.quotaPreviewCache[filename] = { error: errorMsg };

        updateCredentialQuotaPreview(pathId, filename);

        showStatus(errorMsg, 'error');

        showMessageModal(t('quota_details'), errorMsg, 'error');

    }

}

async function fetchPrimaryQuota(filename) {

    const response = await fetch(`./api/creds/quota/${encodeURIComponent(filename)}?mode=provider`, {

        method: 'GET',

        headers: getAuthHeaders()

    });

    const data = await response.json();

    return { response, data };

}

async function loadPrimaryQuotaPreview(pathId) {

    const { filename } = getCredentialModalContext(pathId, AppState.primaryCreds);

    if (!filename) return;

    AppState.quotaPreviewCache[filename] = { loading: true };

    updateCredentialQuotaPreview(pathId, filename);

    try {

        const { response, data } = await fetchPrimaryQuota(filename);

        if (response.ok && data.success) {

            AppState.quotaPreviewCache[filename] = {
                summary: summarizeCredentialQuota(data),
                data,
            };

        } else {

            AppState.quotaPreviewCache[filename] = {
                error: data.error || t('failed_to_get_quota_information'),
            };

        }

    } catch (error) {

        AppState.quotaPreviewCache[filename] = {
            error: t('failed_to_get_quota_information_err', {error_message: error.message}),
        };

    } finally {

        updateCredentialQuotaPreview(pathId, filename);

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

    const { filename, manager: resolvedManager } = getCredentialModalContext(pathId, manager);

    if (!filename) return;

    showStatus(t('card_loading_errors'), 'info');

    try {

        const modeParam = resolvedManager.type === 'primary' ? 'mode=provider' : 'mode=code_assist';

        const response = await fetch(`./api/creds/errors/${encodeURIComponent(filename)}?${modeParam}`, {

            method: 'GET',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            showMessageModal(t('btn_view_errors'), buildCredentialErrorsHtml(filename, data), 'info', {html: true});

        } else {

            const errorMsg = data.detail || data.error || t('failed_to_fetch_error_message');

            showStatus(t('failed_to_fetch_error_message_error', {errorMsg: errorMsg}), 'error');

            showMessageModal(t('btn_view_errors'), errorMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_fetch_error_information_e', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal(t('btn_view_errors'), errorMsg, 'error');

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

    if (!(await showConfirmModal(

        t('are_you_sure_you_want_to_batch_veri_dup', {selectedFiles_length: selectedFiles.length}),

        {title: t('confirm_verify_credentials_title'), confirmLabel: t('btn_verify_id')}

    ))) {

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

        showMessageModal('Batch Verification', summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('all_verifications_failed_failed_fai', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal('Batch Verification', summary, 'error');

    } else {

        showStatus(t('batch_verification_completed_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal('Batch Verification', summary, 'info');

    }

}

async function batchVerifyPrimaryProjectIds() {

    const selectedFiles = Array.from(AppState.primaryCreds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_primary_crede_dup'), 'error');

        showMessageModal(t('tip'), t('please_select_the_primary_crede'), 'error');

        return;

    }

    if (!(await showConfirmModal(

        t('are_you_sure_you_want_to_batch_veri', {selectedFiles_length: selectedFiles.length}),

        {title: t('confirm_verify_credentials_title'), confirmLabel: t('btn_verify_id')}

    ))) {

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

        showMessageModal('Provider Batch Verification', summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('verification_failed_for_all_failed', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal('Provider Batch Verification', summary, 'error');

    } else {

        showStatus(t('batch_verification_completed_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal('Provider Batch Verification', summary, 'info');

    }

}

async function batchConfigurePreview() {

    const selectedFiles = Array.from(AppState.creds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_credential_to_con'), 'error');

        showMessageModal(t('tip'), t('please_select_the_credentials_to_co'), 'error');

        return;

    }

    if (!(await showConfirmModal(

        t('are_you_sure_you_want_to_batch_set', {selectedFiles_length: selectedFiles.length}),

        {title: t('confirm_configure_preview_title'), confirmLabel: t('btn_configure')}

    ))) {

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

}

async function refreshAllEmails() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_refresh_us'), {

        title: t('confirm_refresh_emails_title'),

        confirmLabel: t('btn_refresh')

    }))) return;

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

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_refresh_us_dup'), {

        title: t('confirm_refresh_emails_title'),

        confirmLabel: t('btn_refresh')

    }))) return;

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

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_perform_on'), {

        title: t('confirm_deduplicate_title'),

        confirmLabel: t('btn_deduplicate')

    }))) return;

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

                showMessageModal(t('deduplication_details_title'), details, 'info');

            }

        } else {

            showStatus(data.message || t('deduplication_failed'), 'error');

        }

    } catch (error) {

        showStatus(t('deduplication_network_error_errorme', {error_message: error.message}), 'error');

    }

}

async function deduplicatePrimaryByEmail() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_deduplicat'), {

        title: t('confirm_deduplicate_title'),

        confirmLabel: t('btn_deduplicate')

    }))) return;

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

                showMessageModal(t('deduplication_details_title'), details, 'info');

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

function initLogAutoScrollPreference() {

    const autoScroll = document.getElementById('autoScroll');

    if (!autoScroll) return;

    const savedValue = localStorage.getItem(STORAGE_KEYS.logAutoScroll);

    if (savedValue !== null) {

        autoScroll.checked = savedValue === 'true';

    }

    autoScroll.addEventListener('change', () => {

        localStorage.setItem(STORAGE_KEYS.logAutoScroll, String(autoScroll.checked));

    });

}

document.addEventListener('DOMContentLoaded', initLogAutoScrollPreference);

function connectWebSocket() {

    if (AppState.logWebSocket && AppState.logWebSocket.readyState === WebSocket.OPEN) {

        // showStatus(t('websocket_connected'), 'info');

        return;

    }

    try {

        const wsPath = new URL('./api/logs/stream', window.location.href).href;

        const wsUrl = wsPath.replace(/^http/, 'ws');

        document.getElementById('connectionStatusText').textContent = t('connecting');

        document.getElementById('logConnectionStatus').className = 'status info';

        AppState.logWebSocket = new WebSocket(wsUrl);

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

                if (document.getElementById('autoScroll')?.checked) {

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

    const confirmed = await showConfirmModal(t('confirm_clear_logs'), {

        title: t('confirm_clear_logs_title'),

        confirmLabel: t('btn_clear_logs')

    });

    if (!confirmed) return;

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

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_clear_all'), {

        title: t('confirm_clear_imported_credentials_title'),

        confirmLabel: t('btn_clear_credentials')

    }))) {

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

async function loadGoogleAIStudioSettings() {
    const field = document.getElementById('googleAiStudioApiUrl');
    if (!field) return;

    try {
        const response = await fetch('./api/providers/google-ai-studio/config', {
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || data.error || t('unknown_error'));
        }
        field.value = data.config?.google_ai_studio_api_url || '';
        const isLocked = (data.env_locked || []).includes('google_ai_studio_api_url');
        field.disabled = isLocked;
        field.classList.toggle('env-locked', isLocked);
    } catch (error) {
        showStatus(`Failed to load Google AI Studio settings: ${error.message}`, 'error');
    }
}

async function saveGoogleAIStudioSettings() {
    const field = document.getElementById('googleAiStudioApiUrl');
    const apiUrl = field?.value.trim() || '';
    if (!apiUrl) {
        showStatus('Enter the Google AI Studio API endpoint.', 'error');
        return;
    }

    try {
        const response = await fetch('./api/providers/google-ai-studio/config', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                config: { google_ai_studio_api_url: apiUrl }
            })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || data.error || t('unknown_error'));
        }
        showStatus(data.message || 'Google AI Studio settings saved.', 'success');
        await loadGoogleAIStudioSettings();
    } catch (error) {
        showStatus(`Failed to save Google AI Studio settings: ${error.message}`, 'error');
    }
}

async function resetGoogleAIStudioSettings() {
    const confirmed = await showConfirmModal(
        'Reset the Google AI Studio endpoint to its default? Environment-managed values will be preserved.',
        {
            title: t('confirm_reset_google_ai_studio_title'),
            confirmLabel: t('btn_reset_defaults')
        }
    );
    if (!confirmed) return;

    try {
        const response = await fetch('./api/providers/google-ai-studio/config/reset', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || data.error || t('unknown_error'));
        }
        showStatus(data.message || 'Google AI Studio settings reset to defaults.', 'success');
        await loadGoogleAIStudioSettings();
    } catch (error) {
        showStatus(`Failed to reset Google AI Studio settings: ${error.message}`, 'error');
    }
}

async function addGoogleAIStudioCredential(event) {
    event?.preventDefault();
    const keyField = document.getElementById('googleAiStudioApiKey');
    const button = document.getElementById('addGoogleAiStudioKeyBtn');
    const apiKey = keyField?.value.trim() || '';

    if (!apiKey) {
        showStatus('Enter a Google AI Studio API key.', 'error');
        keyField?.focus();
        return;
    }

    button.disabled = true;
    button.textContent = 'Validating...';
    document.getElementById('googleAiStudioSaveResult')?.classList.add('hidden');

    try {
        const response = await fetch('./api/providers/google-ai-studio/credentials', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ api_key: apiKey })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || data.error || t('unknown_error'));
        }

        const result = document.getElementById('googleAiStudioSaveResult');
        const title = document.getElementById('googleAiStudioSaveResultTitle');
        const text = document.getElementById('googleAiStudioSaveResultText');
        if (title) {
            title.textContent = data.credential_action === 'updated'
                ? 'API key updated'
                : 'API key added to pool';
        }
        if (text) {
            text.textContent = `${data.message} ${data.model_count} generate-content model${data.model_count === 1 ? '' : 's'} available.`;
        }
        result?.classList.remove('hidden');
        keyField.value = '';
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to add Google AI Studio API key: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Validate and add';
    }
}

const ANTIGRAVITY_CONFIG_FIELD_KEYS = {
    antigravityOauthClientId: 'antigravity_client_id',
    antigravityOauthClientSecret: 'antigravity_client_secret',
    antigravityApiUrl: 'api_url',
    antigravityOauthUrl: 'oauth_url',
    antigravityGoogleApisUrl: 'google_apis_url',
    antigravityResourceManagerUrl: 'resource_manager_url',
    antigravityServiceUsageUrl: 'service_usage_url',
    antigravityUserAgent: 'antigravity_user_agent',
    antigravityPayloadUserAgent: 'antigravity_payload_user_agent',
    antigravityStreamToNonstream: 'stream_to_nonstream',
    antigravitySwitchCredential: 'switch_credential_enabled'
};

async function loadAntigravitySettings() {

    const loading = document.getElementById('antigravitySettingsLoading');

    const form = document.getElementById('antigravitySettingsForm');

    if (!loading || !form) return;

    try {

        loading.style.display = 'block';

        form.classList.add('hidden');

        const response = await fetch('./api/providers/antigravity/config', { headers: getAuthHeaders() });

        const data = await response.json();

        if (response.ok) {

            AppState.antigravityConfig = data.config || {};

            AppState.antigravityEnvLockedFields = new Set(data.env_locked || []);

            populateAntigravitySettings();

            form.classList.remove('hidden');

        } else {

            showStatus(`Failed to load Google Antigravity settings: ${data.detail || data.error || t('unknown_error')}`, 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        loading.style.display = 'none';

    }

}

function populateAntigravitySettings() {

    const c = AppState.antigravityConfig || {};

    setAntigravityConfigField('antigravityOauthClientId', c.antigravity_client_id || '');

    setAntigravityConfigField('antigravityOauthClientSecret', c.antigravity_client_secret || '');

    setAntigravityConfigField('antigravityApiUrl', c.api_url || '');

    setAntigravityConfigField('antigravityOauthUrl', c.oauth_url || '');

    setAntigravityConfigField('antigravityGoogleApisUrl', c.google_apis_url || '');

    setAntigravityConfigField('antigravityResourceManagerUrl', c.resource_manager_url || '');

    setAntigravityConfigField('antigravityServiceUsageUrl', c.service_usage_url || '');

    setAntigravityConfigField('antigravityUserAgent', c.antigravity_user_agent || '');

    setAntigravityConfigField('antigravityPayloadUserAgent', c.antigravity_payload_user_agent || '');

    setAntigravityConfigCheckbox('antigravityStreamToNonstream', Boolean(c.stream_to_nonstream !== false));

    setAntigravityConfigCheckbox('antigravitySwitchCredential', Boolean(c.switch_credential_enabled));

}

function setAntigravityConfigField(fieldId, value) {

    const field = document.getElementById(fieldId);

    if (!field) return;

    field.value = value;

    const configKey = ANTIGRAVITY_CONFIG_FIELD_KEYS[fieldId];

    const isLocked = AppState.antigravityEnvLockedFields.has(configKey);

    field.disabled = isLocked;

    field.classList.toggle('env-locked', isLocked);

}

function setAntigravityConfigCheckbox(fieldId, checked) {

    const field = document.getElementById(fieldId);

    if (!field) return;

    field.checked = checked;

    const configKey = ANTIGRAVITY_CONFIG_FIELD_KEYS[fieldId];

    const isLocked = AppState.antigravityEnvLockedFields.has(configKey);

    field.disabled = isLocked;

    field.classList.toggle('env-locked', isLocked);

    field.closest('.switch-row')?.classList.toggle('env-locked', isLocked);

}

async function saveAntigravitySettings() {

    try {

        const getValue = (id, def = '') => document.getElementById(id)?.value.trim() || def;

        const getChecked = (id, def = false) => {
            const field = document.getElementById(id);
            return field ? field.checked : def;
        };

        const config = {
            antigravity_client_id: getValue('antigravityOauthClientId'),
            antigravity_client_secret: getValue('antigravityOauthClientSecret'),
            api_url: getValue('antigravityApiUrl'),
            oauth_url: getValue('antigravityOauthUrl'),
            google_apis_url: getValue('antigravityGoogleApisUrl'),
            resource_manager_url: getValue('antigravityResourceManagerUrl'),
            service_usage_url: getValue('antigravityServiceUsageUrl'),
            antigravity_user_agent: getValue('antigravityUserAgent'),
            antigravity_payload_user_agent: getValue('antigravityPayloadUserAgent'),
            stream_to_nonstream: getChecked('antigravityStreamToNonstream', true),
            switch_credential_enabled: getChecked('antigravitySwitchCredential')
        };

        const response = await fetch('./api/providers/antigravity/config', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ config })

        });

        const data = await response.json();

        if (response.ok) {

            showStatus(data.message || 'Google Antigravity settings saved.', 'success');

            setTimeout(() => loadAntigravitySettings(), 600);

        } else {

            showStatus(`Failed to save Google Antigravity settings: ${data.detail || data.error || t('unknown_error')}`, 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function resetAntigravitySettings() {

    const confirmed = await showConfirmModal(
        'Reset Google Antigravity advanced settings to their defaults? Environment-managed values will be preserved.',
        {
            title: t('confirm_reset_antigravity_title'),
            confirmLabel: t('btn_reset_defaults')
        }
    );

    if (!confirmed) return;

    try {

        const response = await fetch('./api/providers/antigravity/config/reset', {
            method: 'POST',
            headers: getAuthHeaders()
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {

            showStatus(data.message || 'Google Antigravity settings reset to defaults.', 'success');

            AppState.antigravityConfig = data.config || {};

            AppState.antigravityEnvLockedFields = new Set(data.env_locked || []);

            populateAntigravitySettings();

            setTimeout(() => loadAntigravitySettings(), 600);

        } else {

            showStatus(`Failed to reset Google Antigravity settings: ${data.detail || data.error || t('unknown_error')}`, 'error');

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
    credentialsDir: 'credentials_dir',
    proxy: 'proxy',
    codeAssistClientId: 'code_assist_client_id',
    codeAssistClientSecret: 'code_assist_client_secret',
    codeAssistEndpoint: 'code_assist_endpoint',
    autoBanEnabled: 'auto_disable_enabled',
    autoBanErrorCodes: 'auto_disable_error_codes',
    retry429Enabled: 'retry_429_enabled',
    retry429MaxRetries: 'retry_429_max_retries',
    retry429Interval: 'retry_429_interval',
    compatibilityModeEnabled: 'compatibility_mode_enabled',
    returnThoughtsToFrontend: 'return_thoughts_to_frontend',
    antiTruncationMaxAttempts: 'anti_truncation_max_attempts',
    tokenCompressionEnabled: 'token_compression_enabled',
    tokenCompressionThreshold: 'token_compression_threshold',
    tokenCompressionTarget: 'token_compression_target',
    tokenCompressionMinRecentTurns: 'token_compression_min_recent_turns',
    routingStrategy: 'routing_strategy',
    preferredProvider: 'preferred_provider',
    upstreamTimeoutSeconds: 'upstream_timeout_seconds',
    runtimeLogLevel: 'log_level',
    runtimeLogMaxMb: 'log_max_mb',
    runtimeLogBackupCount: 'log_backup_count',
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

    setConfigField('port', c.port || 4283);

    populateAccessCredentialStatus(c);

    setConfigField('credentialsDir', c.credentials_dir || '');

    setConfigField('proxy', c.proxy || '');

    setConfigField('codeAssistClientId', c.code_assist_client_id || '');

    setConfigField('codeAssistClientSecret', c.code_assist_client_secret || '');

    setConfigField('codeAssistEndpoint', c.code_assist_endpoint || '');

    setConfigCheckbox('autoBanEnabled', Boolean(c.auto_disable_enabled));

    setConfigField('autoBanErrorCodes', (c.auto_disable_error_codes || []).join(','));

    setConfigCheckbox('retry429Enabled', Boolean(c.retry_429_enabled));

    setConfigField('retry429MaxRetries', c.retry_429_max_retries ?? 5);

    setConfigField('retry429Interval', c.retry_429_interval ?? 1);

    setConfigCheckbox('compatibilityModeEnabled', Boolean(c.compatibility_mode_enabled));

    setConfigCheckbox('returnThoughtsToFrontend', Boolean(c.return_thoughts_to_frontend !== false));

    setConfigField('antiTruncationMaxAttempts', c.anti_truncation_max_attempts || 3);

    setConfigCheckbox('tokenCompressionEnabled', Boolean(c.token_compression_enabled !== false));

    setConfigField('tokenCompressionThreshold', c.token_compression_threshold ?? 32000);

    setConfigField('tokenCompressionTarget', c.token_compression_target ?? 24000);

    setConfigField('tokenCompressionMinRecentTurns', c.token_compression_min_recent_turns ?? 4);

    setConfigField('routingStrategy', c.routing_strategy || 'balanced');

    setConfigField('preferredProvider', c.preferred_provider || '');

    setConfigField('upstreamTimeoutSeconds', c.upstream_timeout_seconds ?? 300);

    setConfigField('runtimeLogLevel', c.log_level || 'info');

    setConfigField('runtimeLogMaxMb', c.log_max_mb ?? 10);

    setConfigField('runtimeLogBackupCount', c.log_backup_count ?? 3);

    syncRoutingPolicyControls();

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

            port: getInt('port', 4283),

            code_assist_endpoint: getValue('codeAssistEndpoint'),

            credentials_dir: getValue('credentialsDir'),

            proxy: getValue('proxy'),

            code_assist_client_id: getValue('codeAssistClientId'),

            code_assist_client_secret: getValue('codeAssistClientSecret'),

            auto_disable_enabled: getChecked('autoBanEnabled'),

            auto_disable_error_codes: getValue('autoBanErrorCodes').split(',')

                .map(c => parseInt(c.trim())).filter(c => !isNaN(c)),

            retry_429_enabled: getChecked('retry429Enabled'),

            retry_429_max_retries: getInt('retry429MaxRetries', 5),

            retry_429_interval: getFloat('retry429Interval', 1),

            compatibility_mode_enabled: getChecked('compatibilityModeEnabled'),

            return_thoughts_to_frontend: getChecked('returnThoughtsToFrontend'),

            anti_truncation_max_attempts: getInt('antiTruncationMaxAttempts', 3),

            token_compression_enabled: getChecked('tokenCompressionEnabled', true),

            token_compression_threshold: getInt('tokenCompressionThreshold', 32000),

            token_compression_target: getInt('tokenCompressionTarget', 24000),

            token_compression_min_recent_turns: getInt('tokenCompressionMinRecentTurns', 4),

            routing_strategy: getValue('routingStrategy', 'balanced'),

            preferred_provider: getValue('preferredProvider'),

            upstream_timeout_seconds: getFloat('upstreamTimeoutSeconds', 300),

            log_level: getValue('runtimeLogLevel', 'info'),

            log_max_mb: getInt('runtimeLogMaxMb', 10),

            log_backup_count: getInt('runtimeLogBackupCount', 3),

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
            if (data.restart_required && data.restart_required.length > 0) {
                showStatus(
                    data.restart_notice || 'Configuration saved. Restart the application to apply listener or storage changes.',
                    'info'
                );
            } else {
                showStatus(data.message || 'Configuration saved.', 'success');
            }

            setTimeout(() => loadConfig(), 1000);

        } else {

            showStatus(t('failed_to_save_config_datadetail_da', {data_detail____data_error: data.detail || data.error || t('unknown_error')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

function syncRoutingPolicyControls() {
    const strategy = document.getElementById('routingStrategy');
    const provider = document.getElementById('preferredProvider');
    if (!strategy || !provider) return;

    const isEnvironmentLocked = AppState.envLockedFields.has('preferred_provider');
    provider.disabled = strategy.value !== 'priority' || isEnvironmentLocked;
    provider.classList.toggle('env-locked', isEnvironmentLocked);
}

function populateAccessCredentialStatus(config) {
    const panelLocked = AppState.envLockedFields.has('panel_password');
    const panelStatus = document.getElementById('panelPasswordStatus');
    if (panelStatus) {
        panelStatus.textContent = panelLocked
            ? 'Managed by environment'
            : (config.panel_password_configured ? 'Configured' : 'Not configured');
    }
    for (const id of ['newPanelPassword', 'confirmPanelPassword']) {
        const field = document.getElementById(id);
        if (field) field.disabled = panelLocked;
    }
    const button = document.getElementById('updateAccessCredentialsBtn');
    if (button) button.disabled = panelLocked;
}

async function saveAccessCredentials() {
    const currentPassword = document.getElementById('currentConsolePassword')?.value || '';
    const panelPassword = document.getElementById('newPanelPassword')?.value || '';
    const panelConfirmation = document.getElementById('confirmPanelPassword')?.value || '';

    if (!currentPassword) {
        showStatus('Enter the current console password.', 'error');
        document.getElementById('currentConsolePassword')?.focus();
        return;
    }
    if (!panelPassword) {
        showStatus('Enter a new console password.', 'error');
        return;
    }
    if (panelPassword !== panelConfirmation) {
        showStatus('Console password confirmation does not match.', 'error');
        return;
    }
    const button = document.getElementById('updateAccessCredentialsBtn');
    if (button) button.disabled = true;
    try {
        const response = await fetch('./api/config/access', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                current_password: currentPassword,
                panel_password: panelPassword || null,
                panel_password_confirm: panelConfirmation || null
            })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || data.error || t('unknown_error'));
        }
        for (const id of [
            'currentConsolePassword',
            'newPanelPassword',
            'confirmPanelPassword'
        ]) {
            const field = document.getElementById(id);
            if (field) field.value = '';
        }
        showStatus(data.message || 'Console password updated.', 'success');
        await loadConfig();
    } catch (error) {
        showStatus(`Failed to update the console password: ${error.message}`, 'error');
    } finally {
        if (button) button.disabled = false;
    }
}

async function resetConfig() {

    const confirmed = await showConfirmModal(
        'Reset system configuration to defaults? Access passwords and the generated API key will be preserved.',
        {
            title: t('confirm_reset_system_config_title'),
            confirmLabel: t('btn_reset_defaults')
        }
    );

    if (!confirmed) return;

    try {

        const response = await fetch('./api/config/reset', {
            method: 'POST',
            headers: getAuthHeaders()
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            const requiresRestart = Array.isArray(data.restart_required) && data.restart_required.length > 0;
            const message = requiresRestart
                ? `${data.message} Restart the application to apply listener or storage changes.`
                : (data.message || 'System configuration reset to defaults.');
            showStatus(message, requiresRestart ? 'info' : 'success');

            setTimeout(() => loadConfig(), 600);

        } else {

            showStatus(`Failed to reset system configuration: ${data.detail || data.error || t('unknown_error')}`, 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

// =====================================================================

// =====================================================================

function formatUsageNumber(value, options = {}) {

    const number = Number(value || 0);

    if (!Number.isFinite(number)) return '0';

    return number.toLocaleString('en-US', {
        maximumFractionDigits: options.decimals ?? 0,
        minimumFractionDigits: options.decimals ?? 0,
    });

}

function getUsagePeriodConfig(period = AppState.usagePeriod) {

    const periods = {
        '1d': {
            value: '1d',
            optionLabel: '1 day',
            metricLabel: 'in the last 24 hours',
            title: '24-Hour Request Breakdown',
            description: 'Review provider and credential traffic for the last 24 hours.',
        },
        '7d': {
            value: '7d',
            optionLabel: '7 days',
            metricLabel: 'in the last 7 days',
            title: '7-Day Request Breakdown',
            description: 'Review provider and credential traffic for the last 7 days.',
        },
        '30d': {
            value: '30d',
            optionLabel: '30 days',
            metricLabel: 'in the last 30 days',
            title: '30-Day Request Breakdown',
            description: 'Review provider and credential traffic for the last 30 days.',
        },
        all: {
            value: 'all',
            optionLabel: 'All',
            metricLabel: 'across all recorded time',
            title: 'All-Time Request Breakdown',
            description: 'Review all recorded provider and credential traffic.',
        },
    };

    return periods[period] || periods['1d'];

}

function updateUsagePeriodLabels() {

    const periodConfig = getUsagePeriodConfig();

    const periodSelect = document.getElementById('usagePeriodSelect');

    if (periodSelect) periodSelect.value = periodConfig.value;

    const totalCallsLabel = document.getElementById('totalApiCallsLabel');

    if (totalCallsLabel) totalCallsLabel.textContent = `Requests ${periodConfig.metricLabel}`;

    const totalTokensLabel = document.getElementById('totalTokensLabel');

    if (totalTokensLabel) totalTokensLabel.textContent = `Tokens ${periodConfig.metricLabel}`;

    const breakdownTitle = document.getElementById('usageBreakdownTitle');

    if (breakdownTitle) breakdownTitle.textContent = periodConfig.title;

    const breakdownDescription = document.getElementById('usageBreakdownDescription');

    if (breakdownDescription) breakdownDescription.textContent = periodConfig.description;

}

function setUsagePeriod(period) {

    const nextPeriod = getUsagePeriodConfig(period).value;

    if (AppState.usagePeriod === nextPeriod) {

        updateUsagePeriodLabels();

        return;

    }

    AppState.usagePeriod = nextPeriod;

    updateUsagePeriodLabels();

    refreshUsageStats();

}

async function refreshUsageStats() {

    const loading = document.getElementById('usageLoading');

    const list = document.getElementById('usageList');

    const providerSummary = document.getElementById('usageProviderSummary');

    updateUsagePeriodLabels();

    try {

        loading.style.display = 'block';

        list.innerHTML = '';

        if (providerSummary) {

            providerSummary.innerHTML = '';
            providerSummary.hidden = true;

        }

        const usagePeriod = getUsagePeriodConfig().value;

        const usagePeriodQuery = `period=${encodeURIComponent(usagePeriod)}`;

        const [statsResponse, aggregatedResponse] = await Promise.all([

            fetch(`./api/usage/stats?${usagePeriodQuery}`, { headers: getAuthHeaders() }),

            fetch(`./api/usage/aggregated?${usagePeriodQuery}`, { headers: getAuthHeaders() })

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

            const totalCalls = Number(aggData.total_calls ?? aggData.total_calls_24h ?? 0);

            const successfulCalls = Number(aggData.successful_calls ?? aggData.successful_calls_24h ?? 0);

            const failedCalls = Number(aggData.failed_calls ?? aggData.failed_calls_24h ?? 0);

            const successRate = totalCalls > 0 ? Math.round((successfulCalls / totalCalls) * 100) : 0;

            document.getElementById('totalApiCalls').textContent = formatUsageNumber(totalCalls);

            document.getElementById('successRate24h').textContent = `${successRate}%`;

            document.getElementById('successfulApiCalls').textContent = formatUsageNumber(successfulCalls);

            document.getElementById('failedApiCalls').textContent = formatUsageNumber(failedCalls);

            document.getElementById('successRateDetail').textContent = totalCalls > 0
                ? `${formatUsageNumber(successfulCalls)} of ${formatUsageNumber(totalCalls)} requests succeeded.`
                : 'No traffic yet';

            document.getElementById('totalFiles').textContent = formatUsageNumber(aggData.total_files);

            document.getElementById('activeFiles').textContent = formatUsageNumber(aggData.active_files);

            document.getElementById('disabledFiles').textContent = formatUsageNumber(aggData.disabled_files);

            document.getElementById('avgCallsPerFile').textContent = formatUsageNumber(
                aggData.avg_calls_per_file,
                { decimals: 1 }
            );

            document.getElementById('assignedApiCalls').textContent = formatUsageNumber(aggData.assigned_calls ?? aggData.assigned_calls_24h);

            document.getElementById('totalTokens24h').textContent = formatUsageNumber(aggData.total_tokens ?? aggData.total_tokens_24h);

            document.getElementById('inputTokens24h').textContent = formatUsageNumber(aggData.input_tokens ?? aggData.input_tokens_24h);

            document.getElementById('outputTokens24h').textContent = formatUsageNumber(aggData.output_tokens ?? aggData.output_tokens_24h);

            document.getElementById('avgTokensPerRequest').textContent = formatUsageNumber(
                aggData.avg_tokens_per_successful_request,
                { decimals: 1 }
            );

            document.getElementById('cachedTokens24h').textContent = formatUsageNumber(aggData.cached_tokens ?? aggData.cached_tokens_24h);

            document.getElementById('estimatedTokensSaved').textContent = formatUsageNumber(aggData.estimated_tokens_saved ?? aggData.estimated_tokens_saved_24h);

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

    renderUsageProviderSummary();

    if (Object.keys(AppState.usageStatsData).length === 0) {

        const tr = document.createElement('tr');

        tr.innerHTML = `<td colspan="4" style="text-align: center; color: var(--text-muted); padding: 18px 12px;">${t('status_no_filter_data')}</td>`;

        list.appendChild(tr);

        return;

    }

    for (const [filename, stats] of Object.entries(AppState.usageStatsData)) {

        const tr = document.createElement('tr');

        const calls = stats.calls ?? stats.calls_24h ?? 0;
        const successfulCalls = stats.successful_calls ?? stats.successful_calls_24h ?? 0;
        const failedCalls = stats.failed_calls ?? stats.failed_calls_24h ?? 0;
        const inputTokens = stats.input_tokens ?? stats.input_tokens_24h ?? 0;
        const outputTokens = stats.output_tokens ?? stats.output_tokens_24h ?? 0;
        const totalTokens = stats.total_tokens ?? stats.total_tokens_24h ?? 0;
        const estimatedTokensSaved = stats.estimated_tokens_saved ?? stats.estimated_tokens_saved_24h ?? 0;
        const successRate = calls > 0 ? Math.round((successfulCalls / calls) * 100) : 0;
        const isUnassigned = filename === '__gateway_unassigned__.json';
        const providerMeta = isUnassigned
            ? { name: 'Gateway', logo: '/frontend/assets/logo.png' }
            : getCredentialProviderMeta({ provider: stats.provider || stats.provider_name }, 'usage');
        const accountLabel = isUnassigned
            ? 'No credential assigned'
            : (stats.is_deleted
                ? t('deleted_credential')
                : (stats.credential_label || stats.user_email || t('email_not_fetched')));
        const providerLogo = providerMeta.logo
            ? `<img src="${providerMeta.logo}" alt="${escapeHtml(providerMeta.name)} logo">`
            : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

        tr.innerHTML = `

            <td>
                <div class="usage-credential-identity">
                    <div class="cred-provider-logo" aria-hidden="true">${providerLogo}</div>
                    <div class="usage-credential-copy">
                        <div class="usage-credential-name">${escapeHtml(accountLabel)}</div>
                        <div class="usage-credential-meta">${escapeHtml(providerMeta.name)}</div>
                    </div>
                </div>
            </td>

            <td>
                <div class="usage-cell-primary">${formatUsageNumber(calls)} requests</div>
                <div class="usage-cell-meta">${formatUsageNumber(successfulCalls)} successful / ${formatUsageNumber(failedCalls)} failed</div>
            </td>

            <td>
                <div class="usage-cell-primary">${successRate}%</div>
                <div class="usage-cell-meta">${calls > 0 ? `${formatUsageNumber(successfulCalls)} of ${formatUsageNumber(calls)} succeeded` : 'No traffic recorded'}</div>
            </td>

            <td>
                <div class="usage-cell-primary">${formatUsageNumber(totalTokens)} total</div>
                <div class="usage-cell-meta">Input ${formatUsageNumber(inputTokens)} / output ${formatUsageNumber(outputTokens)} / estimated savings ${formatUsageNumber(estimatedTokensSaved)}</div>
            </td>

        `;

        list.appendChild(tr);

    }

}

function renderUsageProviderSummary() {

    const container = document.getElementById('usageProviderSummary');

    if (!container) return;

    const providers = new Map();

    for (const [filename, stats] of Object.entries(AppState.usageStatsData || {})) {

        if (filename === '__gateway_unassigned__.json') continue;

        const providerMeta = getCredentialProviderMeta(
            { provider: stats.provider || stats.provider_name },
            'usage'
        );

        const current = providers.get(providerMeta.id) || {
            meta: providerMeta,
            credentials: 0,
            calls: 0,
            successfulCalls: 0,
            totalTokens: 0,
        };

        if (!stats.is_deleted) current.credentials += 1;
        current.calls += Number(stats.calls ?? stats.calls_24h ?? 0);
        current.successfulCalls += Number(stats.successful_calls ?? stats.successful_calls_24h ?? 0);
        current.totalTokens += Number(stats.total_tokens ?? stats.total_tokens_24h ?? 0);
        providers.set(providerMeta.id, current);

    }

    if (providers.size === 0) {

        container.innerHTML = '';
        container.hidden = true;
        return;

    }

    container.hidden = false;
    const providerOrder = ['google_antigravity', 'google_ai_studio', 'code_assist'];
    const providerItems = Array.from(providers.values()).sort((left, right) => {
        const leftIndex = providerOrder.indexOf(left.meta.id);
        const rightIndex = providerOrder.indexOf(right.meta.id);
        return (leftIndex === -1 ? providerOrder.length : leftIndex)
            - (rightIndex === -1 ? providerOrder.length : rightIndex);
    });

    container.innerHTML = providerItems.map((provider) => {

        const successRate = provider.calls > 0
            ? Math.round((provider.successfulCalls / provider.calls) * 100)
            : 0;
        const logo = provider.meta.logo
            ? `<img src="${provider.meta.logo}" alt="">`
            : `<span>${escapeHtml(provider.meta.name.charAt(0))}</span>`;
        const credentialLabel = provider.credentials > 0
            ? `${provider.credentials} active credential${provider.credentials === 1 ? '' : 's'}`
            : 'No active credentials';

        return `
            <article class="usage-provider-item">
                <div class="usage-provider-identity">
                    <div class="usage-provider-logo" aria-hidden="true">${logo}</div>
                    <div>
                        <div class="usage-provider-name">${escapeHtml(provider.meta.name)}</div>
                        <div class="usage-provider-meta">${credentialLabel}</div>
                    </div>
                </div>
                <dl class="usage-provider-metrics">
                    <div><dt>Requests</dt><dd>${formatUsageNumber(provider.calls)}</dd></div>
                    <div><dt>Success</dt><dd>${provider.calls > 0 ? `${successRate}%` : 'No traffic'}</dd></div>
                    <div><dt>Tokens</dt><dd>${formatUsageNumber(provider.totalTokens)}</dd></div>
                </dl>
            </article>
        `;

    }).join('');

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

    if (!checkBtn.dataset.defaultText) {

        checkBtn.dataset.defaultText = checkBtn.textContent.trim() || 'Check for updates';

    }

    const originalText = checkBtn.dataset.defaultText;

    const hadUpdateAvailable = checkBtn.classList.contains('update-available');

    if (checkBtn._resetTimer) {

        clearTimeout(checkBtn._resetTimer);

        checkBtn._resetTimer = null;

    }

    checkBtn.classList.remove('update-available', 'update-current');

    const restoreIdleState = () => {

        if (hadUpdateAvailable) {

            checkBtn.textContent = t('new_version_available');

            checkBtn.classList.add('update-available');

            return;

        }

        checkBtn.textContent = originalText;

    };

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

                checkBtn.textContent = t('new_version_available');

                checkBtn.classList.add('update-available');

            } else if (data.has_update === false) {

                showStatus(t('already_up_to_date'), 'success');

                checkBtn.textContent = t('already_up_to_date_dup');

                checkBtn.classList.add('update-current');

                checkBtn._resetTimer = setTimeout(() => {

                    checkBtn.classList.remove('update-current');

                    checkBtn.textContent = originalText;

                    checkBtn._resetTimer = null;

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

            restoreIdleState();

        }

    }

}

// =====================================================================

// =====================================================================

window.onload = async function () {

    updatePrimaryCallbackUrlPlaceholder();

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



function setMobileMenuState(isOpen) {
    const sidebar = document.querySelector('.dashboard-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const menuButton = document.querySelector('.mobile-menu-btn');
    if (!sidebar || !overlay) return;

    sidebar.classList.toggle('open', isOpen);
    overlay.classList.toggle('open', isOpen);
    document.body.classList.toggle('mobile-menu-open', isOpen);
    overlay.style.display = isOpen ? 'block' : 'none';
    overlay.setAttribute('aria-hidden', String(!isOpen));

    if (menuButton) {
        menuButton.setAttribute('aria-expanded', String(isOpen));
        menuButton.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
    }
}

function toggleMobileMenu() {
    const sidebar = document.querySelector('.dashboard-sidebar');
    setMobileMenuState(!sidebar?.classList.contains('open'));
}

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setMobileMenuState(false);
});
