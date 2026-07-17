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
        showStatus(`Failed to load Grok and xAI Console settings: ${error.message}`, 'error');
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
