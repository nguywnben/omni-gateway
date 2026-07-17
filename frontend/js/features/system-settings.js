async function loadConfig(options = {}) {

    const loading = document.getElementById('configLoading');

    const form = document.getElementById('configForm');

    const preserveContent = options.preserveContent ?? AppState.configLoaded;

    try {

        if (loading && !preserveContent) loading.hidden = false;

        if (!preserveContent) form.classList.add('hidden');

        const response = await fetch('./api/config/get', { headers: getAuthHeaders() });

        const data = await response.json();

        if (response.ok) {

            AppState.currentConfig = data.config;

            AppState.configLoaded = true;

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

        if (loading) loading.hidden = true;

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
