// Omni Gateway management console: settings.

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

            document.getElementById('envFilesCount').textContent = t(
                'dataexisting_env_files_count_files',
                {files: formatCountLabel(data.existing_env_files_count, 'file')}
            );

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

                showStatus(t('successfully_imported_dataloaded_co', {
                    data_loaded_count: data.loaded_count,
                    data_total_count: data.total_count,
                    credential_noun: Number(data.total_count) === 1 ? 'credential file' : 'credential files'
                }), 'success');

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

            showStatus(t('successfully_deleted_datadeleted_co', {
                files: formatCountLabel(data.deleted_count, 'environment-variable credential file')
            }), 'success');

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

const XAI_CONFIG_FIELDS = {
    xaiClientId: 'xai_client_id',
    xaiOauthIssuer: 'xai_oauth_issuer',
    xaiApiUrl: 'xai_api_url',
    xaiUserAgent: 'xai_user_agent'
};

const XAI_CONFIG_GROUPS = {
    oauth: {
        label: 'Grok',
        resetTitle: 'Reset Grok Settings',
        fieldIds: ['xaiClientId', 'xaiOauthIssuer']
    },
    api: {
        label: 'Grok and xAI Console transport',
        resetTitle: 'Reset Grok and xAI Console Transport Settings',
        fieldIds: ['xaiApiUrl', 'xaiUserAgent']
    }
};

async function loadXaiSettings() {
    if (!Object.keys(XAI_CONFIG_FIELDS).some(fieldId => document.getElementById(fieldId))) return;
    try {
        const response = await fetch('./api/providers/xai/config', { headers: getAuthHeaders() });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        const locked = new Set(data.env_locked || []);
        Object.entries(XAI_CONFIG_FIELDS).forEach(([fieldId, configKey]) => {
            const field = document.getElementById(fieldId);
            if (!field) return;
            field.value = data.config?.[configKey] || '';
            field.disabled = locked.has(configKey);
            field.classList.toggle('env-locked', field.disabled);
        });
    } catch (error) {
        showStatus(`Failed to load Grok and xAI Console settings: ${error.message}`, 'error');
    }
}

async function saveXaiSettings(scope) {
    const group = XAI_CONFIG_GROUPS[scope];
    if (!group) return;
    const config = {};
    group.fieldIds.forEach((fieldId) => {
        const configKey = XAI_CONFIG_FIELDS[fieldId];
        const field = document.getElementById(fieldId);
        if (field && !field.disabled) config[configKey] = field.value.trim();
    });
    try {
        const response = await fetch('./api/providers/xai/config', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ config })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(`${group.label} settings saved.`, 'success');
        await loadXaiSettings();
    } catch (error) {
        showStatus(`Failed to save ${group.label} settings: ${error.message}`, 'error');
    }
}

async function resetXaiSettings(scope) {
    const group = XAI_CONFIG_GROUPS[scope];
    if (!group) return;
    const confirmed = await showConfirmModal(
        `Restore the built-in ${group.label} settings?`,
        { title: group.resetTitle, confirmLabel: 'Reset defaults' }
    );
    if (!confirmed) return;
    try {
        const response = await fetch(`./api/providers/xai/config/reset?scope=${encodeURIComponent(scope)}`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(data.message || `${group.label} settings reset to defaults.`, 'success');
        await loadXaiSettings();
    } catch (error) {
        showStatus(`Failed to reset ${group.label} settings: ${error.message}`, 'error');
    }
}

function showXaiCredentialSaveResult(kind, data) {
    const isOauth = kind === 'oauth';
    const prefix = isOauth ? 'xaiOauth' : 'xaiApiKey';
    const result = document.getElementById(`${prefix}SaveResult`);
    const title = document.getElementById(`${prefix}SaveResultTitle`);
    const text = document.getElementById(`${prefix}SaveResultText`);
    const credentialName = isOauth ? 'Grok OAuth credential' : 'xAI Console API key';
    if (title) {
        title.textContent = data.credential_action === 'updated'
            ? `${credentialName} updated`
            : `${credentialName} added to pool`;
    }
    if (text) {
        const modelCount = Number(data.model_count) || 0;
        text.textContent = `${data.message} ${modelCount} model${modelCount === 1 ? '' : 's'} available.`;
    }
    result?.classList.remove('hidden');
}

async function addXaiApiKeyCredential(event) {
    event?.preventDefault();
    const field = document.getElementById('xaiApiKey');
    const button = document.getElementById('addXaiKeyBtn');
    const apiKey = field?.value.trim() || '';
    if (!apiKey) {
        showStatus('Enter an xAI Console API key.', 'error');
        field?.focus();
        return;
    }
    button.disabled = true;
    button.textContent = 'Validating...';
    document.getElementById('xaiApiKeySaveResult')?.classList.add('hidden');
    try {
        const response = await fetch('./api/providers/xai/credentials', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ api_key: apiKey })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        field.value = '';
        showXaiCredentialSaveResult('api-key', data);
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await loadModelCatalog(true);
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to add xAI Console API key: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Validate and add';
    }
}

async function startXaiOauth() {
    const button = document.getElementById('startXaiOauthBtn');
    button.disabled = true;
    button.textContent = 'Generating...';
    document.getElementById('xaiOauthSaveResult')?.classList.add('hidden');
    try {
        const response = await fetch('./api/providers/xai/oauth/start', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        const authorizationLink = document.getElementById('xaiAuthorizationUrl');
        authorizationLink.href = data.auth_url || '#';
        authorizationLink.textContent = data.auth_url || 'Authorization unavailable';
        document.getElementById('xaiAuthorizationCode').value = '';
        const oauthFields = document.getElementById('xaiOauthFields');
        if (oauthFields) {
            oauthFields.dataset.state = data.state || '';
            oauthFields.classList.remove('hidden');
        }
        showStatus('Grok authorization link generated.', 'success');
    } catch (error) {
        showStatus(`Failed to start Grok OAuth: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Get provider authentication link';
    }
}

async function saveXaiOauth() {
    const field = document.getElementById('xaiAuthorizationCode');
    const button = document.getElementById('saveXaiOauthBtn');
    const code = field?.value.trim() || '';
    const oauthFields = document.getElementById('xaiOauthFields');
    const state = oauthFields?.dataset.state || '';
    if (!code) {
        showStatus('Enter the code shown on the Grok authorization page.', 'error');
        field?.focus();
        return;
    }
    if (!state) {
        showStatus('Generate a new Grok authorization link before saving the credential.', 'error');
        return;
    }
    button.disabled = true;
    button.textContent = 'Saving...';
    try {
        const response = await fetch('./api/providers/xai/oauth/complete', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ code, state })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        field.value = '';
        delete oauthFields.dataset.state;
        showXaiCredentialSaveResult('oauth', data);
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await loadModelCatalog(true);
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to save Grok OAuth credential: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Save credential';
    }
}

const ANTIGRAVITY_CONFIG_FIELD_KEYS = {
    antigravityOauthClientId: 'antigravity_client_id',
    antigravityOauthClientSecret: 'antigravity_client_secret',
    antigravityApiUrl: 'antigravity_api_url',
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

    setAntigravityConfigField('antigravityApiUrl', c.antigravity_api_url || '');

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
            antigravity_api_url: getValue('antigravityApiUrl'),
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
