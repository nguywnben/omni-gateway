async function loadAntigravitySettings() {

    const loading = document.getElementById('antigravitySettingsLoading');

    const form = document.getElementById('antigravitySettingsForm');

    if (!loading || !form) return;

    try {

        loading.hidden = false;

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

        loading.hidden = true;

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
