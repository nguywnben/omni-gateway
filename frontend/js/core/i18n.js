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
        "unavailable_credential": "Unavailable credential",
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

const LANGUAGE_STORAGE_KEY = 'omni_gateway_console_locale';

// Legacy actions still use generated keys. Keep their fallback concise and
// intentional until each flow is migrated to a named semantic key.
const LEGACY_UI_FALLBACKS = {
    en: { complete: 'The operation completed successfully.', failed: 'The operation could not be completed.', progress: 'The operation is in progress. Please wait.', confirm: 'Review the details and confirm to continue.', unavailable: 'The requested information is not available.', required: 'Complete the required information to continue.', notice: 'Review the information and try again.' },
    'zh-CN': { complete: '操作已成功完成。', failed: '无法完成此操作。', progress: '正在处理，请稍候。', confirm: '请检查详细信息并确认继续。', unavailable: '请求的信息暂不可用。', required: '请填写必填信息后继续。', notice: '请检查相关信息后重试。' },
    'zh-TW': { complete: '操作已成功完成。', failed: '無法完成此操作。', progress: '正在處理，請稍候。', confirm: '請檢查詳細資訊並確認繼續。', unavailable: '要求的資訊目前無法取得。', required: '請填寫必要資訊後繼續。', notice: '請檢查相關資訊後再試一次。' },
    de: { complete: 'Der Vorgang wurde erfolgreich abgeschlossen.', failed: 'Der Vorgang konnte nicht abgeschlossen werden.', progress: 'Der Vorgang wird ausgeführt. Bitte warten Sie.', confirm: 'Prüfen Sie die Angaben und bestätigen Sie, um fortzufahren.', unavailable: 'Die angeforderten Informationen sind nicht verfügbar.', required: 'Vervollständigen Sie die erforderlichen Angaben, um fortzufahren.', notice: 'Prüfen Sie die Angaben und versuchen Sie es erneut.' },
    es: { complete: 'La operación se completó correctamente.', failed: 'No se pudo completar la operación.', progress: 'La operación está en curso. Espera un momento.', confirm: 'Revisa los detalles y confirma para continuar.', unavailable: 'La información solicitada no está disponible.', required: 'Completa la información obligatoria para continuar.', notice: 'Revisa la información e inténtalo de nuevo.' },
    fr: { complete: 'L’opération s’est terminée correctement.', failed: 'L’opération n’a pas pu être effectuée.', progress: 'L’opération est en cours. Veuillez patienter.', confirm: 'Vérifiez les informations, puis confirmez pour continuer.', unavailable: 'Les informations demandées ne sont pas disponibles.', required: 'Renseignez les informations obligatoires pour continuer.', notice: 'Vérifiez les informations, puis réessayez.' },
    id: { complete: 'Operasi berhasil diselesaikan.', failed: 'Operasi tidak dapat diselesaikan.', progress: 'Operasi sedang diproses. Harap tunggu.', confirm: 'Periksa detailnya, lalu konfirmasikan untuk melanjutkan.', unavailable: 'Informasi yang diminta tidak tersedia.', required: 'Lengkapi informasi wajib untuk melanjutkan.', notice: 'Periksa informasinya, lalu coba lagi.' },
    it: { complete: 'L’operazione è stata completata.', failed: 'Non è stato possibile completare l’operazione.', progress: 'Operazione in corso. Attendi.', confirm: 'Controlla i dettagli e conferma per continuare.', unavailable: 'Le informazioni richieste non sono disponibili.', required: 'Completa le informazioni obbligatorie per continuare.', notice: 'Controlla le informazioni e riprova.' },
    ja: { complete: '操作が完了しました。', failed: '操作を完了できませんでした。', progress: '処理中です。しばらくお待ちください。', confirm: '内容を確認してから、続行してください。', unavailable: '要求された情報は利用できません。', required: '必須項目を入力して続行してください。', notice: '内容を確認して、もう一度お試しください。' },
    ko: { complete: '작업이 완료되었습니다.', failed: '작업을 완료하지 못했습니다.', progress: '작업을 처리하고 있습니다. 잠시 기다려 주세요.', confirm: '세부 정보를 확인한 후 계속 진행하세요.', unavailable: '요청한 정보를 사용할 수 없습니다.', required: '필수 정보를 입력한 후 계속하세요.', notice: '정보를 확인한 후 다시 시도하세요.' },
    pt: { complete: 'A operação foi concluída.', failed: 'Não foi possível concluir a operação.', progress: 'A operação está em andamento. Aguarde.', confirm: 'Revise os detalhes e confirme para continuar.', unavailable: 'As informações solicitadas não estão disponíveis.', required: 'Preencha as informações obrigatórias para continuar.', notice: 'Revise as informações e tente novamente.' },
    ru: { complete: 'Операция успешно завершена.', failed: 'Не удалось завершить операцию.', progress: 'Операция выполняется. Подождите.', confirm: 'Проверьте сведения и подтвердите продолжение.', unavailable: 'Запрошенная информация недоступна.', required: 'Заполните обязательные поля, чтобы продолжить.', notice: 'Проверьте сведения и повторите попытку.' },
    th: { complete: 'ดำเนินการเรียบร้อยแล้ว', failed: 'ไม่สามารถดำเนินการให้เสร็จได้', progress: 'กำลังดำเนินการ โปรดรอสักครู่', confirm: 'ตรวจสอบรายละเอียดและยืนยันเพื่อดำเนินการต่อ', unavailable: 'ไม่มีข้อมูลที่ร้องขอ', required: 'กรอกข้อมูลที่จำเป็นเพื่อดำเนินการต่อ', notice: 'ตรวจสอบข้อมูลแล้วลองอีกครั้ง' },
    tr: { complete: 'İşlem başarıyla tamamlandı.', failed: 'İşlem tamamlanamadı.', progress: 'İşlem devam ediyor. Lütfen bekleyin.', confirm: 'Ayrıntıları inceleyip devam etmek için onaylayın.', unavailable: 'İstenen bilgiler kullanılamıyor.', required: 'Devam etmek için gerekli bilgileri tamamlayın.', notice: 'Bilgileri kontrol edip yeniden deneyin.' },
    vi: { complete: 'Thao tác đã hoàn tất.', failed: 'Không thể hoàn tất thao tác.', progress: 'Đang xử lý. Vui lòng chờ.', confirm: 'Hãy kiểm tra thông tin và xác nhận để tiếp tục.', unavailable: 'Thông tin được yêu cầu hiện không khả dụng.', required: 'Hãy điền đầy đủ thông tin bắt buộc để tiếp tục.', notice: 'Hãy kiểm tra thông tin và thử lại.' }
};

const PROVIDER_COPY_FALLBACKS = {
    en: { configure: 'Configure this provider and add credentials to the shared routing pool.', import: 'Import provider credentials from JSON files or ZIP archives.', instruction: 'Complete the provider authorization, then return here to continue.', files: 'Supports JSON files and ZIP archives.', drop: 'Drop credential files here.', loading: 'Loading provider settings.', unavailable: 'Authorization information is not available.' },
    'zh-CN': { configure: '配置此提供商，并将凭据添加到共享路由池。', import: '从 JSON 文件或 ZIP 压缩包导入提供商凭据。', instruction: '完成提供商授权后，返回此处继续。', files: '支持 JSON 文件和 ZIP 压缩包。', drop: '将凭据文件拖放到此处。', loading: '正在加载提供商设置。', unavailable: '授权信息暂不可用。' },
    'zh-TW': { configure: '設定此供應商，並將憑證新增至共用路由集區。', import: '從 JSON 檔案或 ZIP 壓縮檔匯入供應商憑證。', instruction: '完成供應商授權後，返回此處繼續。', files: '支援 JSON 檔案與 ZIP 壓縮檔。', drop: '將憑證檔案拖放到此處。', loading: '正在載入供應商設定。', unavailable: '授權資訊目前無法取得。' },
    de: { configure: 'Konfigurieren Sie diesen Anbieter und fügen Sie Zugangsdaten zum gemeinsamen Routing-Pool hinzu.', import: 'Importieren Sie Anbieter-Zugangsdaten aus JSON-Dateien oder ZIP-Archiven.', instruction: 'Schließen Sie die Autorisierung beim Anbieter ab und kehren Sie anschließend hierher zurück.', files: 'Unterstützt JSON-Dateien und ZIP-Archive.', drop: 'Zugangsdaten-Dateien hier ablegen.', loading: 'Anbietereinstellungen werden geladen.', unavailable: 'Autorisierungsinformationen sind nicht verfügbar.' },
    es: { configure: 'Configura este proveedor y añade credenciales al grupo de enrutamiento compartido.', import: 'Importa credenciales del proveedor desde archivos JSON o ZIP.', instruction: 'Completa la autorización con el proveedor y vuelve aquí para continuar.', files: 'Admite archivos JSON y ZIP.', drop: 'Suelta aquí los archivos de credenciales.', loading: 'Cargando la configuración del proveedor.', unavailable: 'La información de autorización no está disponible.' },
    fr: { configure: 'Configurez ce fournisseur et ajoutez des identifiants au pool de routage partagé.', import: 'Importez des identifiants fournisseur depuis des fichiers JSON ou des archives ZIP.', instruction: 'Terminez l’autorisation auprès du fournisseur, puis revenez ici pour continuer.', files: 'Accepte les fichiers JSON et les archives ZIP.', drop: 'Déposez les fichiers d’identifiants ici.', loading: 'Chargement des paramètres du fournisseur.', unavailable: 'Les informations d’autorisation ne sont pas disponibles.' },
    id: { configure: 'Konfigurasikan penyedia ini dan tambahkan kredensial ke pool perutean bersama.', import: 'Impor kredensial penyedia dari file JSON atau arsip ZIP.', instruction: 'Selesaikan otorisasi penyedia, lalu kembali ke sini untuk melanjutkan.', files: 'Mendukung file JSON dan arsip ZIP.', drop: 'Letakkan file kredensial di sini.', loading: 'Memuat pengaturan penyedia.', unavailable: 'Informasi otorisasi tidak tersedia.' },
    it: { configure: 'Configura questo provider e aggiungi le credenziali al pool di routing condiviso.', import: 'Importa le credenziali del provider da file JSON o archivi ZIP.', instruction: 'Completa l’autorizzazione del provider, quindi torna qui per continuare.', files: 'Supporta file JSON e archivi ZIP.', drop: 'Trascina qui i file delle credenziali.', loading: 'Caricamento delle impostazioni del provider.', unavailable: 'Le informazioni di autorizzazione non sono disponibili.' },
    ja: { configure: 'このプロバイダーを設定し、認証情報を共有ルーティングプールに追加します。', import: 'JSON ファイルまたは ZIP アーカイブからプロバイダーの認証情報をインポートします。', instruction: 'プロバイダーでの認証を完了してから、ここに戻って続行してください。', files: 'JSON ファイルと ZIP アーカイブに対応しています。', drop: '認証情報ファイルをここにドロップします。', loading: 'プロバイダー設定を読み込んでいます。', unavailable: '認証情報を利用できません。' },
    ko: { configure: '이 공급자를 설정하고 자격 증명을 공유 라우팅 풀에 추가하세요.', import: 'JSON 파일 또는 ZIP 압축 파일에서 공급자 자격 증명을 가져오세요.', instruction: '공급자 인증을 완료한 후 여기로 돌아와 계속하세요.', files: 'JSON 파일과 ZIP 압축 파일을 지원합니다.', drop: '자격 증명 파일을 여기에 놓으세요.', loading: '공급자 설정을 불러오고 있습니다.', unavailable: '인증 정보를 사용할 수 없습니다.' },
    pt: { configure: 'Configure este provedor e adicione credenciais ao pool de roteamento compartilhado.', import: 'Importe credenciais do provedor de arquivos JSON ou ZIP.', instruction: 'Conclua a autorização no provedor e volte aqui para continuar.', files: 'Compatível com arquivos JSON e ZIP.', drop: 'Solte os arquivos de credenciais aqui.', loading: 'Carregando as configurações do provedor.', unavailable: 'As informações de autorização não estão disponíveis.' },
    ru: { configure: 'Настройте этого провайдера и добавьте учётные данные в общий пул маршрутизации.', import: 'Импортируйте учётные данные провайдера из файлов JSON или архивов ZIP.', instruction: 'Завершите авторизацию у провайдера и вернитесь сюда, чтобы продолжить.', files: 'Поддерживаются файлы JSON и архивы ZIP.', drop: 'Перетащите сюда файлы учётных данных.', loading: 'Загрузка настроек провайдера.', unavailable: 'Сведения для авторизации недоступны.' },
    th: { configure: 'กำหนดค่าผู้ให้บริการนี้และเพิ่มข้อมูลรับรองลงในพูลการกำหนดเส้นทางร่วม', import: 'นำเข้าข้อมูลรับรองของผู้ให้บริการจากไฟล์ JSON หรือไฟล์ ZIP', instruction: 'ดำเนินการอนุญาตกับผู้ให้บริการให้เสร็จ แล้วกลับมาที่นี่เพื่อดำเนินการต่อ', files: 'รองรับไฟล์ JSON และไฟล์ ZIP', drop: 'วางไฟล์ข้อมูลรับรองที่นี่', loading: 'กำลังโหลดการตั้งค่าผู้ให้บริการ', unavailable: 'ไม่มีข้อมูลการอนุญาต' },
    tr: { configure: 'Bu sağlayıcıyı yapılandırın ve kimlik bilgilerini paylaşılan yönlendirme havuzuna ekleyin.', import: 'Sağlayıcı kimlik bilgilerini JSON dosyalarından veya ZIP arşivlerinden içe aktarın.', instruction: 'Sağlayıcı yetkilendirmesini tamamlayıp devam etmek için buraya dönün.', files: 'JSON dosyalarını ve ZIP arşivlerini destekler.', drop: 'Kimlik bilgisi dosyalarını buraya bırakın.', loading: 'Sağlayıcı ayarları yükleniyor.', unavailable: 'Yetkilendirme bilgileri kullanılamıyor.' },
    vi: { configure: 'Cấu hình nhà cung cấp này và thêm thông tin xác thực vào kho định tuyến dùng chung.', import: 'Nhập thông tin xác thực của nhà cung cấp từ tệp JSON hoặc kho lưu trữ ZIP.', instruction: 'Hoàn tất cấp quyền với nhà cung cấp, sau đó quay lại đây để tiếp tục.', files: 'Hỗ trợ tệp JSON và kho lưu trữ ZIP.', drop: 'Thả tệp thông tin xác thực vào đây.', loading: 'Đang tải cài đặt nhà cung cấp.', unavailable: 'Thông tin cấp quyền hiện không khả dụng.' }
};

const PROVIDER_LABEL_KEYS = [
    'Batch Import', 'Authorization link', 'Authorization code', 'Save credential',
    'View', 'Pending files', 'Import', 'Import complete', 'Validate and add',
    'API key added to pool', 'Previous', 'Next'
];

const PROVIDER_LABEL_ROWS = {
    en: ['Batch Import', 'Authorization link', 'Authorization code', 'Save credential', 'View', 'Pending files', 'Import', 'Import complete', 'Validate and add', 'API key added to pool', 'Previous', 'Next'],
    'zh-CN': ['批量导入', '授权链接', '授权码', '保存凭据', '查看', '待处理文件', '导入', '导入完成', '验证并添加', 'API 密钥已添加到凭据池', '上一页', '下一页'],
    'zh-TW': ['批次匯入', '授權連結', '授權碼', '儲存憑證', '檢視', '待處理檔案', '匯入', '匯入完成', '驗證並新增', 'API 金鑰已新增至憑證集區', '上一頁', '下一頁'],
    de: ['Stapelimport', 'Autorisierungslink', 'Autorisierungscode', 'Zugangsdaten speichern', 'Anzeigen', 'Ausstehende Dateien', 'Importieren', 'Import abgeschlossen', 'Prüfen und hinzufügen', 'API-Schlüssel zum Pool hinzugefügt', 'Zurück', 'Weiter'],
    es: ['Importación por lotes', 'Enlace de autorización', 'Código de autorización', 'Guardar credencial', 'Ver', 'Archivos pendientes', 'Importar', 'Importación completada', 'Validar y añadir', 'Clave API añadida al grupo', 'Anterior', 'Siguiente'],
    fr: ['Importation groupée', 'Lien d’autorisation', 'Code d’autorisation', 'Enregistrer l’identifiant', 'Afficher', 'Fichiers en attente', 'Importer', 'Importation terminée', 'Valider et ajouter', 'Clé API ajoutée au pool', 'Précédent', 'Suivant'],
    id: ['Impor Massal', 'Tautan otorisasi', 'Kode otorisasi', 'Simpan kredensial', 'Lihat', 'File tertunda', 'Impor', 'Impor selesai', 'Validasi dan tambahkan', 'Kunci API ditambahkan ke pool', 'Sebelumnya', 'Berikutnya'],
    it: ['Importazione in blocco', 'Link di autorizzazione', 'Codice di autorizzazione', 'Salva credenziale', 'Visualizza', 'File in attesa', 'Importa', 'Importazione completata', 'Convalida e aggiungi', 'Chiave API aggiunta al pool', 'Precedente', 'Successivo'],
    ja: ['一括インポート', '認証リンク', '認証コード', '認証情報を保存', '表示', '保留中のファイル', 'インポート', 'インポート完了', '検証して追加', 'API キーをプールに追加しました', '前へ', '次へ'],
    ko: ['일괄 가져오기', '인증 링크', '인증 코드', '자격 증명 저장', '보기', '대기 중인 파일', '가져오기', '가져오기 완료', '검증 후 추가', 'API 키를 풀에 추가했습니다', '이전', '다음'],
    pt: ['Importação em lote', 'Link de autorização', 'Código de autorização', 'Salvar credencial', 'Ver', 'Arquivos pendentes', 'Importar', 'Importação concluída', 'Validar e adicionar', 'Chave de API adicionada ao pool', 'Anterior', 'Próximo'],
    ru: ['Пакетный импорт', 'Ссылка для авторизации', 'Код авторизации', 'Сохранить учётные данные', 'Открыть', 'Ожидающие файлы', 'Импортировать', 'Импорт завершён', 'Проверить и добавить', 'Ключ API добавлен в пул', 'Назад', 'Далее'],
    th: ['นำเข้าแบบกลุ่ม', 'ลิงก์การอนุญาต', 'รหัสการอนุญาต', 'บันทึกข้อมูลรับรอง', 'ดู', 'ไฟล์ที่รอดำเนินการ', 'นำเข้า', 'นำเข้าเสร็จแล้ว', 'ตรวจสอบและเพิ่ม', 'เพิ่มคีย์ API ลงในพูลแล้ว', 'ก่อนหน้า', 'ถัดไป'],
    tr: ['Toplu İçe Aktarma', 'Yetkilendirme bağlantısı', 'Yetkilendirme kodu', 'Kimlik bilgisini kaydet', 'Görüntüle', 'Bekleyen dosyalar', 'İçe aktar', 'İçe aktarma tamamlandı', 'Doğrula ve ekle', 'API anahtarı havuza eklendi', 'Önceki', 'Sonraki'],
    vi: ['Nhập hàng loạt', 'Liên kết cấp quyền', 'Mã cấp quyền', 'Lưu thông tin xác thực', 'Xem', 'Tệp đang chờ', 'Nhập', 'Đã nhập xong', 'Xác thực và thêm', 'Đã thêm khóa API vào kho', 'Trang trước', 'Trang sau']
};

const PROVIDER_LABEL_TRANSLATIONS = Object.fromEntries(
    Object.entries(PROVIDER_LABEL_ROWS).map(([locale, values]) => [
        locale,
        Object.fromEntries(PROVIDER_LABEL_KEYS.map((key, index) => [key, values[index]]))
    ])
);

const PRESERVED_TECHNICAL_TRANSLATION_KEYS = new Set([
    'a_hrefurl_target_blank_stylecolor_0',
    'brstrongavailable_projectsstrongbr',
    'error_code_prefix',
    'http_code_prefix'
]);

function resolveLegacyFallback(key, source, locale) {
    if (!source || locale === 'en' || PRESERVED_TECHNICAL_TRANSLATION_KEYS.has(key)) return source;

    const normalized = source.toLowerCase();
    let category = 'notice';
    if (/\b(are you sure|confirm|cannot be undone)\b/.test(normalized)) category = 'confirm';
    else if (/\b(please (enter|select|provide|obtain|fetch)|required|invalid selection|before continuing)\b/.test(normalized)) category = 'required';
    else if (/\b(loading|checking|fetching|generating|configuring|verifying|refreshing|importing|downloading|clearing|connecting|in progress|please wait)\b/.test(normalized)) category = 'progress';
    else if (/\b(failed|failure|error|unable|could not|rejected|disconnected|connection lost)\b/.test(normalized)) category = 'failed';
    else if (/\b(no |not available|unavailable|not found|missing|not configured|not enabled)\b/.test(normalized)) category = 'unavailable';
    else if (/\b(success|successful|completed|complete|downloaded|saved|connected|loaded|retrieved|generated|updated|up to date|enabled|disabled|deleted|cleared|imported|passed|signed in|signed out)\b/.test(normalized)) category = 'complete';

    return (LEGACY_UI_FALLBACKS[locale] || LEGACY_UI_FALLBACKS.en)[category];
}

function getMessageCatalog(locale) {
    return {
        ...(COMMON_UI_TRANSLATIONS[locale] || {}),
        ...(SETTINGS_LOCALE_TRANSLATIONS[locale] || {}),
        ...(AUTH_LOCALE_TRANSLATIONS[locale] || {}),
        ...(DIALOG_LOCALE_TRANSLATIONS[locale] || {}),
        ...(PAGE_LOCALE_TRANSLATIONS[locale] || {}),
        ...(SUPPORTED_LOCALES[locale]?.messages || {})
    };
}

function translateEnglishSource(source, locale) {
    const englishMessages = getMessageCatalog('en');
    const localizedMessages = getMessageCatalog(locale);
    const semanticKey = Object.keys(englishMessages).find((key) => englishMessages[key] === source);
    if (semanticKey && localizedMessages[semanticKey]) return localizedMessages[semanticKey];

    const legacyKey = Object.keys(TRANSLATIONS.en || {}).find((key) => TRANSLATIONS.en[key] === source);
    if (legacyKey && TRANSLATIONS[locale]?.[legacyKey]) return TRANSLATIONS[locale][legacyKey];
    return '';
}

function translateProviderCopy(source, locale) {
    const normalizedSource = String(source || '').trim();
    if (!normalizedSource || locale === 'en') return normalizedSource;

    const exact = translateEnglishSource(normalizedSource, locale);
    if (exact) return exact;

    const label = PROVIDER_LABEL_TRANSLATIONS[locale]?.[normalizedSource];
    if (label) return label;

    const normalized = normalizedSource.toLowerCase();
    const messages = PROVIDER_COPY_FALLBACKS[locale] || PROVIDER_COPY_FALLBACKS.en;
    if (/^(add|connect|authorize|validate|generate|configure|manage|tune|set)\b/.test(normalized)) return messages.configure;
    if (/^(import|batch import)\b/.test(normalized)) return messages.import;
    if (/^(after|open|copy|if)\b/.test(normalized)) return messages.instruction;
    if (/^supports\b/.test(normalized)) return messages.files;
    if (/^drop\b/.test(normalized)) return messages.drop;
    if (/^loading\b/.test(normalized)) return messages.loading;
    if (/unavailable$/.test(normalized)) return messages.unavailable;
    return normalizedSource;
}

function getActiveLocale() {

    return typeof AppState !== 'undefined' && AppState.lang
        ? AppState.lang
        : 'en';

}

function normalizeLocale(value) {

    const normalized = String(value || '').replace('_', '-').toLowerCase();

    return Object.keys(SUPPORTED_LOCALES).find((locale) => locale.toLowerCase() === normalized) || '';

}

function detectBrowserLocale() {

    const browserNavigator = typeof navigator === 'object' ? navigator : {};
    const candidates = Array.isArray(browserNavigator.languages) && browserNavigator.languages.length > 0
        ? browserNavigator.languages
        : [browserNavigator.language];

    for (const candidate of candidates.filter(Boolean)) {

        const exact = normalizeLocale(candidate);

        if (exact) return exact;

        const normalized = String(candidate).replace('_', '-').toLowerCase();
        const [language, region] = normalized.split('-');

        if (language === 'zh') {

            if (['tw', 'hk', 'mo', 'hant'].includes(region)) return 'zh-TW';

            return 'zh-CN';

        }

        if (SUPPORTED_LOCALES[language]) return language;

    }

    return 'en';

}

function t(key, vars = {}) {

    const lang = getActiveLocale();
    const localeMessages = {
        ...(COMMON_UI_TRANSLATIONS[lang] || {}),
        ...(SETTINGS_LOCALE_TRANSLATIONS[lang] || {}),
        ...(AUTH_LOCALE_TRANSLATIONS[lang] || {}),
        ...(DIALOG_LOCALE_TRANSLATIONS[lang] || {}),
        ...(PAGE_LOCALE_TRANSLATIONS[lang] || {}),
        ...(SUPPORTED_LOCALES[lang]?.messages || {})
    };
    const englishMessages = {
        ...COMMON_UI_TRANSLATIONS.en,
        ...SETTINGS_LOCALE_TRANSLATIONS.en,
        ...AUTH_LOCALE_TRANSLATIONS.en,
        ...DIALOG_LOCALE_TRANSLATIONS.en,
        ...PAGE_LOCALE_TRANSLATIONS.en,
        ...SUPPORTED_LOCALES.en.messages
    };

    const legacySource = TRANSLATIONS.en && TRANSLATIONS.en[key];
    const semanticAlias = legacySource
        ? Object.keys(englishMessages).find((semanticKey) => englishMessages[semanticKey] === legacySource)
        : '';
    let text = localeMessages[key]
        || (TRANSLATIONS[lang] && TRANSLATIONS[lang][key])
        || (semanticAlias && localeMessages[semanticAlias])
        || englishMessages[key]
        || resolveLegacyFallback(key, legacySource, lang)
        || legacySource
        || key;

    for (const [k, v] of Object.entries(vars)) {

        text = text.replaceAll(`{${k}}`, v);

    }

    return text;

}

function formatCountLabel(count, singular, plural = `${singular}s`) {
    const numericCount = Number(count || 0);
    const formattedCount = new Intl.NumberFormat(getActiveLocale()).format(numericCount);
    return `${formattedCount} ${numericCount === 1 ? singular : plural}`;
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

function populateLanguageSwitchers() {

    document.querySelectorAll('.lang-switcher').forEach((switcher) => {

        if (switcher.options.length === Object.keys(SUPPORTED_LOCALES).length) return;

        switcher.replaceChildren(...Object.entries(SUPPORTED_LOCALES).map(([locale, definition]) => {

            const option = document.createElement('option');
            option.value = locale;
            option.textContent = definition.label;
            return option;

        }));

    });

}

function changeLanguage(locale) {

    setLanguage(locale, true);
    applyLanguage();

    window.setTimeout(() => window.location.reload(), 0);

}

function initLanguage() {

    let storedLocale = '';

    try {

        storedLocale = normalizeLocale(localStorage.getItem(LANGUAGE_STORAGE_KEY));

    } catch (_) {

        // Storage can be disabled by the browser; locale detection remains available.

    }

    setLanguage(storedLocale || detectBrowserLocale(), false);
    applyLanguage();

}

function setLanguage(locale, persist) {

    const selectedLocale = normalizeLocale(locale) || 'en';

    if (typeof AppState !== 'undefined') AppState.lang = selectedLocale;

    if (persist) {

        try {

            localStorage.setItem(LANGUAGE_STORAGE_KEY, selectedLocale);

        } catch (_) {

            // The interface still works when persistent storage is unavailable.

        }

    }

    populateLanguageSwitchers();

    document.querySelectorAll('.lang-switcher').forEach((switcher) => {

        switcher.value = selectedLocale;

    });

}

function installLocalizedFetch() {

    if (typeof window !== 'object' || typeof window.fetch !== 'function' || window.__localizedFetchInstalled) return;

    const nativeFetch = window.fetch.bind(window);
    window.fetch = (input, init = {}) => {

        const requestUrl = new URL(typeof input === 'string' || input instanceof URL ? input : input.url, window.location.href);

        if (requestUrl.origin !== window.location.origin || !requestUrl.pathname.startsWith('/api/')) {

            return nativeFetch(input, init);

        }

        const headers = new Headers(input instanceof Request ? input.headers : undefined);
        new Headers(init.headers || {}).forEach((value, name) => headers.set(name, value));

        if (!headers.has('Accept-Language')) {

            headers.set('Accept-Language', getActiveLocale() || detectBrowserLocale());

        }

        if (input instanceof Request) {

            return nativeFetch(new Request(input, {...init, headers}));

        }

        return nativeFetch(input, {...init, headers});

    };
    window.__localizedFetchInstalled = true;

}

function applyLanguage() {

    const lang = getActiveLocale();

    document.documentElement.lang = lang;

    document.querySelectorAll('[data-i18n]').forEach(el => {

        const key = el.getAttribute('data-i18n');

        const text = t(key);

        if (text && text !== key) {

            el.textContent = text;

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

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {

        const text = t(el.getAttribute('data-i18n-placeholder'));

        if (text) el.setAttribute('placeholder', text);

    });

    document.querySelectorAll('[data-i18n-aria-label]').forEach(el => {

        const text = t(el.getAttribute('data-i18n-aria-label'));

        if (text) el.setAttribute('aria-label', text);

    });

    document.querySelectorAll('.lang-switcher').forEach((switcher) => {

        switcher.setAttribute('aria-label', t('language'));

    });

    applyProviderWorkspaceTranslations(lang);

    document.dispatchEvent(new CustomEvent('omni:locale-change', { detail: { locale: lang } }));

}

const AUTO_TRANSLATED_TEXT = new WeakMap();
const AUTO_TRANSLATED_ATTRIBUTES = new WeakMap();

function applyProviderWorkspaceTranslations(locale) {
    const ignoredParents = new Set(['CODE', 'PRE', 'SCRIPT', 'STYLE']);
    document.querySelectorAll('.provider-workspace, [data-i18n-auto]').forEach((workspace) => {
        const walker = document.createTreeWalker(workspace, NodeFilter.SHOW_TEXT);
        let node = walker.nextNode();
        while (node) {
            const parent = node.parentElement;
            if (parent && !ignoredParents.has(parent.tagName)) {
                let original = AUTO_TRANSLATED_TEXT.get(node);
                if (!original) {
                    const source = node.textContent.trim();
                    if (source) {
                        original = { raw: node.textContent, source };
                        AUTO_TRANSLATED_TEXT.set(node, original);
                    }
                }
                if (original) {
                    const translated = locale === 'en'
                        ? original.source
                        : translateProviderCopy(original.source, locale);
                    node.textContent = original.raw.replace(original.source, translated || original.source);
                }
            }
            node = walker.nextNode();
        }

        workspace.querySelectorAll('[placeholder], [title], [aria-label]').forEach((element) => {
            let originals = AUTO_TRANSLATED_ATTRIBUTES.get(element);
            if (!originals) {
                originals = {};
                AUTO_TRANSLATED_ATTRIBUTES.set(element, originals);
            }
            for (const attribute of ['placeholder', 'title', 'aria-label']) {
                if (!element.hasAttribute(attribute)) continue;
                if (!(attribute in originals)) originals[attribute] = element.getAttribute(attribute) || '';
                const source = originals[attribute];
                const translated = locale === 'en' ? source : translateProviderCopy(source, locale);
                element.setAttribute(attribute, translated || source);
            }
        });
    });
}

installLocalizedFetch();

document.addEventListener('DOMContentLoaded', initLanguage);

document.addEventListener('change', (event) => {

    if (event.target instanceof HTMLSelectElement && event.target.matches('.lang-switcher')) {

        changeLanguage(event.target.value);

    }

});
