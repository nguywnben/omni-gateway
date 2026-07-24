const ANTHROPIC_CONFIG_FIELDS = {
    anthropicApiUrlCode: 'anthropic_api_url',
    anthropicApiUrlPlatform: 'anthropic_api_url',
    claudeAuthorizeUrl: 'claude_oauth_authorize_url',
    claudeTokenUrl: 'claude_oauth_token_url',
    claudeClientId: 'claude_client_id',
    claudeUserAgent: 'claude_user_agent'
};

const ANTHROPIC_CONFIG_GROUPS = {
    code: {
        label: 'Claude Code',
        resetTitle: 'Reset Claude Code Settings',
        fieldIds: ['anthropicApiUrlCode', 'claudeAuthorizeUrl', 'claudeTokenUrl', 'claudeClientId', 'claudeUserAgent']
    },
    platform: {
        label: 'Claude Platform',
        resetTitle: 'Reset Claude Platform Settings',
        fieldIds: ['anthropicApiUrlPlatform']
    }
};

async function loadAnthropicSettings(options = {}) {
    if (!Object.keys(ANTHROPIC_CONFIG_FIELDS).some((fieldId) => document.getElementById(fieldId))) return;
    const loadingIds = ['claudeCodeSettingsLoading', 'claudePlatformSettingsLoading'];
    const formIds = ['claudeCodeSettingsForm', 'claudePlatformSettingsForm'];
    const preserveContent = options.preserveContent ?? formIds.some(
        (id) => document.getElementById(id)?.dataset.loaded === 'true'
    );
    setProviderSettingsLoading(loadingIds, formIds, true, preserveContent);
    try {
        const response = await fetch('./api/providers/anthropic/config', { headers: getAuthHeaders() });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        const locked = new Set(data.env_locked || []);
        Object.entries(ANTHROPIC_CONFIG_FIELDS).forEach(([fieldId, configKey]) => {
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
        showStatus(`Failed to load Anthropic provider settings: ${error.message}`, 'error');
    } finally {
        setProviderSettingsLoading(loadingIds, formIds, false, preserveContent);
    }
}

async function saveAnthropicSettings(scope) {
    const group = ANTHROPIC_CONFIG_GROUPS[scope];
    if (!group) return;
    const config = {};
    group.fieldIds.forEach((fieldId) => {
        const field = document.getElementById(fieldId);
        if (field && !field.disabled) config[ANTHROPIC_CONFIG_FIELDS[fieldId]] = field.value.trim();
    });
    try {
        const response = await fetch('./api/providers/anthropic/config', {
            method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ config })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(`${group.label} settings saved.`, 'success');
        await loadAnthropicSettings();
    } catch (error) {
        showStatus(`Failed to save ${group.label} settings: ${error.message}`, 'error');
    }
}

async function resetAnthropicSettings(scope) {
    const group = ANTHROPIC_CONFIG_GROUPS[scope];
    if (!group) return;
    const confirmed = await showConfirmModal(
        `Restore the built-in ${group.label} settings? Environment-managed values will be preserved.`,
        { title: group.resetTitle, confirmLabel: 'Reset defaults' }
    );
    if (!confirmed) return;
    try {
        const response = await fetch(
            `./api/providers/anthropic/config/reset?scope=${encodeURIComponent(scope)}`,
            { method: 'POST', headers: getAuthHeaders() }
        );
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(data.message || `${group.label} settings reset to defaults.`, 'success');
        await loadAnthropicSettings();
    } catch (error) {
        showStatus(`Failed to reset ${group.label} settings: ${error.message}`, 'error');
    }
}

function showAnthropicCredentialSaveResult(kind, data) {
    const isCode = kind === 'code';
    const prefix = isCode ? 'claudeOauth' : 'claudePlatform';
    const credentialName = isCode ? 'Claude Code credential' : 'Claude Platform API key';
    const title = document.getElementById(`${prefix}SaveResultTitle`);
    const text = document.getElementById(`${prefix}SaveResultText`);
    if (title) title.textContent = data.credential_action === 'updated'
        ? `${credentialName} updated`
        : `${credentialName} added to pool`;
    if (text) {
        const count = Number(data.model_count) || 0;
        text.textContent = `${data.message} ${count} model${count === 1 ? '' : 's'} available.`;
    }
    document.getElementById(`${prefix}SaveResult`)?.classList.remove('hidden');
}

async function addClaudePlatformCredential(event) {
    event?.preventDefault();
    const field = document.getElementById('claudePlatformApiKey');
    const button = document.getElementById('addClaudePlatformKeyBtn');
    const apiKey = field?.value.trim() || '';
    if (!apiKey) {
        showStatus('Enter a Claude Platform API key.', 'error');
        field?.focus();
        return;
    }
    button.disabled = true;
    button.textContent = 'Validating...';
    document.getElementById('claudePlatformSaveResult')?.classList.add('hidden');
    try {
        const response = await fetch('./api/providers/anthropic/platform/credentials', {
            method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ api_key: apiKey })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        field.value = '';
        showAnthropicCredentialSaveResult('platform', data);
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await loadModelCatalog(true);
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to add Claude Platform API key: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Validate and add';
    }
}

async function startClaudeOauth() {
    const button = document.getElementById('startClaudeOauthBtn');
    button.disabled = true;
    button.textContent = 'Generating...';
    document.getElementById('claudeOauthSaveResult')?.classList.add('hidden');
    try {
        const response = await fetch('./api/providers/anthropic/claude-code/oauth/start', {
            method: 'POST', headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        const fields = document.getElementById('claudeOauthFields');
        const link = document.getElementById('claudeAuthorizationUrl');
        if (fields) {
            fields.dataset.oauthState = data.state || '';
            fields.classList.remove('hidden');
        }
        if (link) {
            link.href = data.auth_url || '#';
            link.textContent = data.auth_url || 'Authorization unavailable';
        }
        document.getElementById('claudeAuthorizationCode').value = '';
        showStatus('Claude Code authorization link generated.', 'success');
    } catch (error) {
        showStatus(`Failed to start Claude Code authorization: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Get provider authentication link';
    }
}

async function saveClaudeOauth() {
    const fields = document.getElementById('claudeOauthFields');
    const field = document.getElementById('claudeAuthorizationCode');
    const button = document.getElementById('saveClaudeOauthBtn');
    const code = field?.value.trim() || '';
    const state = fields?.dataset.oauthState || '';
    if (!code || !state) {
        showStatus('Generate an authorization link, then enter the Claude authorization code.', 'error');
        field?.focus();
        return;
    }
    button.disabled = true;
    button.textContent = 'Saving...';
    try {
        const response = await fetch('./api/providers/anthropic/claude-code/oauth/complete', {
            method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ code, state })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        delete fields.dataset.oauthState;
        showAnthropicCredentialSaveResult('code', data);
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await loadModelCatalog(true);
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to save Claude Code credential: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Save credential';
    }
}

function handleClaudeCodeFileSelect(event) { AppState.claudeCodeUploadFiles.handleFileSelect(event); }
function handleClaudeCodeFileDrop(event) { event.preventDefault(); event.currentTarget.classList.remove('dragover'); AppState.claudeCodeUploadFiles.addFiles(Array.from(event.dataTransfer.files)); }
function clearClaudeCodeFiles() { AppState.claudeCodeUploadFiles.clearFiles(); }
function uploadClaudeCodeFiles() { AppState.claudeCodeUploadFiles.upload(); }
function handleClaudePlatformFileSelect(event) { AppState.claudePlatformUploadFiles.handleFileSelect(event); }
function handleClaudePlatformFileDrop(event) { event.preventDefault(); event.currentTarget.classList.remove('dragover'); AppState.claudePlatformUploadFiles.addFiles(Array.from(event.dataTransfer.files)); }
function clearClaudePlatformFiles() { AppState.claudePlatformUploadFiles.clearFiles(); }
function uploadClaudePlatformFiles() { AppState.claudePlatformUploadFiles.upload(); }