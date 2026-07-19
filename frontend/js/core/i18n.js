// Omni Gateway management console: core.

const TRANSLATIONS = {
    en: {
        "a_hrefurl_target_blank_stylecolor_0": "<a href=\"{url}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"message-link\" title=\"Open link: {url}\">{url}</a>",
        "action_delete": "Delete",
        "action_disable": "Disable",
        "action_disable_credit": "Disable credits",
        "action_enable": "Enable",
        "action_enable_credit": "Enable credits",
        "all_configured_successfully_preview": "Preview channel configured for {successCount}/{selectedFiles_length} {credential_noun}.",
        "all_credential_files_have_been_down": "Downloaded all credential files.",
        "all_primary_credentials_packed": "Downloaded all provider credentials.",
        "all_verifications_failed_failed_fai": "Verification failed for all {credentials}.",
        "all_verifications_successful_succes": "All verifications passed. Verified {credentials}.",
        "all_verifications_successful_verifi": "All verifications passed. Verified {credentials}.",
        "already_up_to_date": "Already up to date.",
        "already_up_to_date_dup": "Already up to date.",
        "are_you_sure_you_want_to_batch_set": "Configure the Preview channel for {credentials}?\\n\\nThis operation will run in parallel.",
        "are_you_sure_you_want_to_batch_veri": "Verify access and refresh metadata for {credentials}?\\n\\nThis operation will run in parallel.",
        "are_you_sure_you_want_to_batch_veri_dup": "Verify access and refresh metadata for {credentials}?\\n\\nThis operation will run in parallel.",
        "are_you_sure_you_want_to_clear_all": "Clear all credential files imported from environment variables?\\nThis will delete authentication files that start with \"env-\".",
        "are_you_sure_you_want_to_delete_fil_dup": "Are you sure you want to delete {filename}?",
        "are_you_sure_you_want_to_perform_on": "Deduplicate credentials now?\\n\\nOnly one credential per email will be kept, and all others will be deleted.\\nThis action cannot be undone.",
        "are_you_sure_you_want_to_refresh_us": "Refresh user emails for all credentials? This may take some time.",
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
        "configuration_failed_for_all_failed": "Configuration failed for all credentials. Failed {failCount}/{selectedFiles_length} {credential_noun}.",
        "configuration_loaded_successfully": "Configuration loaded.",
        "configuration_saved_successfully": "Configuration saved.",
        "configuration_successful": "Configuration successful.",
        "configuring_preview_channel_for_sel": "Configuring the Preview channel for {credentials}. Please wait...",
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
        "credentials_fetched_successfully_fr": "Credential retrieved from the callback URL.",
        "credit_disabled_title": "Google One AI credit usage is disabled for this credential.",
        "credit_enabled_title": "Google One AI credit usage is enabled for this credential.",
        "credits_label": "Credits",
        "dataexisting_env_files_count_files": "{files}",
        "deduplication_complete_deleted_data": "Deduplication completed. Deleted {deleted}, kept {kept}, and retained {emails}.",
        "deduplication_details_title": "Deduplication Details",
        "deduplication_detailsnn": "Deduplication details:\\n\\n",
        "deduplication_failed": "Deduplication failed.",
        "deduplication_network_error_errorme": "Deduplication network error: {error_message}",
        "deleted_credential": "Deleted credential",
        "dialog_tip": "Tip",
        "disable_only": "Disabled only",
        "disconnected": "Disconnected",
        "download_failed_filename": "Download failed: {filename}",
        "downloaded_filename": "Downloaded {filename}.",
        "email_groupemailnkeep_groupkept_fil": "Email: {group_email}\\nKeep: {group_kept_file}\\nDelete: {group_deleted_files_join}\\n\\n",
        "email_not_fetched": "Email unavailable",
        "email_refresh_complete_successfully": "Email refresh completed. Retrieved {data_success_count}/{data_total_count} {address_noun}.",
        "email_refresh_network_error_errorme": "Email refresh network error: {error_message}",
        "enable_only": "Enabled only",
        "enabled": "Enabled",
        "environment_variable_status_check_c": "Environment variable status check complete.",
        "error_code_prefix": "Error",
        "http_code_prefix": "HTTP",
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
        "fetch_primary_credentials": "Save credential",
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
        "parallel_testing_selectedfileslengt": "Verifying {credentials} in parallel. Please wait...",
        "parallel_verifying_selectedfileslen": "Verifying {credentials} in parallel. Please wait...",
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
        "primary_authentication_link_gen": "Provider authentication link generated. Open it, finish Google authorization, then return here to save the credential. If Google opens a localhost callback page, paste that full URL into the Callback URL field.",
        "primary_batch_verification_comp_dup": "Provider batch verification complete.\\n\\nSuccess: {successCount}\\nFailed: {failCount}\\nTotal: {selectedFiles_length}\\n\\nDetailed results:\\n{resultMessages_join___n}",
        "primary_credential_valid": "Provider credential is valid.",
        "project_id_required_to_complete_aut": "A Project ID is required to complete authentication. Restart the flow and enter the correct Project ID.",
        "provider_antigravity": "Google Antigravity",
        "provider_google_ai_studio": "Google AI Studio",
        "provider_grok": "Grok Build",
        "provider_authorization_expired": "This authorization session was not found or has expired. Generate a new authorization link and try again.",
        "provider_authorization_pending": "Authorization is not complete yet. If Google opened a localhost callback page, copy the full callback URL from that tab and paste it into the Callback URL field.",
        "provider_callback_url_required": "Paste the localhost callback URL from the Google tab into the Callback URL field, then select Save credential.",
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
        "saving_provider_credentials": "Saving the credential to the pool...",
        "saving_provider_credentials_from_callback": "Saving the credential from the callback URL...",
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
        "status_loaded_creds": "Loaded {credentials}.",
        "status_loading_file_content": "Loading file content...",
        "status_log_stream_connection_failed": "Failed to connect to the log stream: ",
        "status_log_stream_error_prefix": "Log stream error: ",
        "status_net_error": "Network error: {error}",
        "status_no_creds": "No credentials are in this pool yet. Add an account or API key, or import credentials to get started.",
        "status_no_errors": "No errors",
        "status_no_filter_data": "No usage statistics found.",
        "status_no_quota_info": "No quota information is available for this credential.",
        "status_page_info": "Page {page} of {total} (showing {start}-{end} of {count}).",
        "status_select_upload_first": "Select at least one credential file before importing.",
        "status_selected_items": "{count} selected",
        "status_upload_aborted": "Import failed because the connection was interrupted while sending {files}.",
        "status_upload_failed_details": "Import failed: {error}",
        "status_upload_failed_http": "Import failed with HTTP {status}.",
        "status_upload_invalid_response": "The import completed, but the server returned an invalid response.",
        "status_upload_success": "Imported {credentials}.",
        "status_upload_timeout": "Import timed out. Try again with fewer files.",
        "status_uploading_zip": "Importing and extracting ZIP archives...",
        "successfully_deleted_datadeleted_co": "Deleted {files}.",
        "successfully_imported_dataloaded_co": "Imported {data_loaded_count}/{data_total_count} {credential_noun}.",
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
        "verification_failed_for_all_failed": "Verification failed for all {credentials}.",
        "verification_failednnerrormsg": "Verification failed.\\n\\n{errorMsg}",
        "verifying_primary_project_id_pl": "Verifying provider access and refreshing metadata. Please wait...",
        "verifying_project_id_please_wait": "Verifying credential access and refreshing metadata. Please wait...",
        "waiting_for_oauth_callback": "Waiting for OAuth callback...",
        "waiting_for_oauth_callback_this_may": "Waiting for the OAuth callback. This may take some time...",
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

function formatCountLabel(count, singular, plural = `${singular}s`) {
    const numericCount = Number(count || 0);
    return `${numericCount} ${numericCount === 1 ? singular : plural}`;
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
