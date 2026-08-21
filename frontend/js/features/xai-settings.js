async function loadXaiSettings(options = {}) {
    if (!Object.keys(XAI_CONFIG_FIELDS).some(fieldId => document.getElementById(fieldId))) return;

    const loadingIds = ['grokSettingsLoading', 'xaiConsoleSettingsLoading'];
    const formIds = ['grokSettingsForm', 'xaiConsoleSettingsForm'];
    const preserveContent = options.preserveContent ?? formIds.some(
        id => document.getElementById(id)?.dataset.loaded === 'true'
    );
    setProviderSettingsLoading(loadingIds, formIds, true, preserveContent);

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
        formIds.forEach((id) => {
            const form = document.getElementById(id);
            if (form) form.dataset.loaded = 'true';
        });
    } catch (error) {
        showStatus(t('provider.settings_load_failed', {provider: 'Grok Build / SpaceXAI Console', error: error.message}), 'error');
    } finally {
        setProviderSettingsLoading(loadingIds, formIds, false, preserveContent);
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
        showStatus(t('provider.settings_saved', {provider: group.label}), 'success');
        await loadXaiSettings();
    } catch (error) {
        showStatus(t('provider.settings_save_failed', {provider: group.label, error: error.message}), 'error');
    }
}

async function resetXaiSettings(scope) {
    const group = XAI_CONFIG_GROUPS[scope];
    if (!group) return;
    const confirmed = await showConfirmModal(
        t('provider.reset_confirm', {provider: group.label}),
        {
            title: t('provider.reset_title', {provider: group.label}),
            confirmLabel: t('btn_reset_defaults')
        }
    );
    if (!confirmed) return;
    try {
        const response = await fetch(`./api/providers/xai/config/reset?scope=${encodeURIComponent(scope)}`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(data.message || t('provider.settings_reset', {provider: group.label}), 'success');
        await loadXaiSettings();
    } catch (error) {
        showStatus(t('provider.settings_reset_failed', {provider: group.label, error: error.message}), 'error');
    }
}

function showXaiCredentialSaveResult(kind, data) {
    const isOauth = kind === 'oauth';
    const prefix = isOauth ? 'xaiOauth' : 'xaiApiKey';
    const result = document.getElementById(`${prefix}SaveResult`);
    const title = document.getElementById(`${prefix}SaveResultTitle`);
    const text = document.getElementById(`${prefix}SaveResultText`);
    if (title) {
        title.textContent = t(data.credential_action === 'updated'
            ? 'runtime.credential_updated_title'
            : 'runtime.credential_added_title');
    }
    if (text) {
        const modelCount = Number(data.model_count) || 0;
        text.textContent = `${data.message} ${t('runtime.models_available', {count: modelCount})}`;
    }
    result?.classList.remove('hidden');
}

async function addXaiApiKeyCredential(event) {
    event?.preventDefault();
    const field = document.getElementById('xaiApiKey');
    const button = document.getElementById('addXaiKeyBtn');
    const apiKey = field?.value.trim() || '';
    if (!apiKey) {
        showStatus(t('provider.api_key_required', {provider: 'SpaceXAI Console'}), 'error');
        field?.focus();
        return;
    }
    button.disabled = true;
    button.textContent = t('runtime.validating');
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
        showStatus(t('provider.api_key_add_failed', {provider: 'SpaceXAI Console', error: error.message}), 'error');
    } finally {
        button.disabled = false;
        button.textContent = t('runtime.validate_add');
    }
}

async function startXaiOauth() {
    const button = document.getElementById('startXaiOauthBtn');
    button.disabled = true;
    button.textContent = t('runtime.generating');
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
        authorizationLink.textContent = data.auth_url || t('runtime.authorization_unavailable');
        document.getElementById('xaiAuthorizationCode').value = '';
        const oauthFields = document.getElementById('xaiOauthFields');
        if (oauthFields) {
            oauthFields.dataset.state = data.state || '';
            oauthFields.classList.remove('hidden');
        }
        showStatus(t('provider.auth_ready', {provider: 'Grok Build'}), 'success');
    } catch (error) {
        showStatus(t('provider.auth_start_failed', {provider: 'Grok Build', error: error.message}), 'error');
    } finally {
        button.disabled = false;
        button.textContent = t('runtime.get_provider_auth');
    }
}

async function saveXaiOauth() {
    const field = document.getElementById('xaiAuthorizationCode');
    const button = document.getElementById('saveXaiOauthBtn');
    const code = field?.value.trim() || '';
    const oauthFields = document.getElementById('xaiOauthFields');
    const state = oauthFields?.dataset.state || '';
    if (!code) {
        showStatus(t('provider.auth_code_required', {provider: 'Grok Build'}), 'error');
        field?.focus();
        return;
    }
    if (!state) {
        showStatus(t('provider.auth_session_required', {provider: 'Grok Build'}), 'error');
        return;
    }
    button.disabled = true;
    button.textContent = t('runtime.saving');
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
        showStatus(t('provider.credential_save_failed', {provider: 'Grok Build', error: error.message}), 'error');
    } finally {
        button.disabled = false;
        button.textContent = t('runtime.save_credential');
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
