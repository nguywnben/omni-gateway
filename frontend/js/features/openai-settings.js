const OPENAI_CONFIG_FIELDS = {
    openaiApiUrl: 'openai_api_url',
    codexApiUrl: 'codex_api_url',
    codexAuthBase: 'codex_auth_base',
    codexClientId: 'codex_client_id',
    codexUserAgent: 'codex_user_agent'
};

const OPENAI_CONFIG_GROUPS = {
    platform: {
        label: 'OpenAI Platform',
        resetTitle: 'Reset OpenAI Platform Settings',
        fieldIds: ['openaiApiUrl']
    },
    codex: {
        label: 'OpenAI Codex',
        resetTitle: 'Reset OpenAI Codex Settings',
        fieldIds: ['codexApiUrl', 'codexAuthBase', 'codexClientId', 'codexUserAgent']
    }
};

async function loadOpenAISettings(options = {}) {
    if (!Object.keys(OPENAI_CONFIG_FIELDS).some((fieldId) => document.getElementById(fieldId))) {
        return;
    }

    const loadingIds = ['codexSettingsLoading', 'openaiPlatformSettingsLoading'];
    const formIds = ['codexSettingsForm', 'openaiPlatformSettingsForm'];
    const preserveContent = options.preserveContent ?? formIds.some(
        (id) => document.getElementById(id)?.dataset.loaded === 'true'
    );
    setProviderSettingsLoading(loadingIds, formIds, true, preserveContent);

    try {
        const response = await fetch('./api/providers/openai/config', {
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));

        const locked = new Set(data.env_locked || []);
        Object.entries(OPENAI_CONFIG_FIELDS).forEach(([fieldId, configKey]) => {
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
        showStatus(`Failed to load OpenAI provider settings: ${error.message}`, 'error');
    } finally {
        setProviderSettingsLoading(loadingIds, formIds, false, preserveContent);
    }
}

async function saveOpenAISettings(scope) {
    const group = OPENAI_CONFIG_GROUPS[scope];
    if (!group) return;
    const config = {};
    group.fieldIds.forEach((fieldId) => {
        const configKey = OPENAI_CONFIG_FIELDS[fieldId];
        const field = document.getElementById(fieldId);
        if (field && !field.disabled) config[configKey] = field.value.trim();
    });

    try {
        const response = await fetch('./api/providers/openai/config', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ config })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(`${group.label} settings saved.`, 'success');
        await loadOpenAISettings();
    } catch (error) {
        showStatus(`Failed to save ${group.label} settings: ${error.message}`, 'error');
    }
}

async function resetOpenAISettings(scope) {
    const group = OPENAI_CONFIG_GROUPS[scope];
    if (!group) return;
    const confirmed = await showConfirmModal(
        `Restore the built-in ${group.label} settings? Environment-managed values will be preserved.`,
        { title: group.resetTitle, confirmLabel: 'Reset defaults' }
    );
    if (!confirmed) return;

    try {
        const response = await fetch(
            `./api/providers/openai/config/reset?scope=${encodeURIComponent(scope)}`,
            { method: 'POST', headers: getAuthHeaders() }
        );
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(data.message || `${group.label} settings reset to defaults.`, 'success');
        await loadOpenAISettings();
    } catch (error) {
        showStatus(`Failed to reset ${group.label} settings: ${error.message}`, 'error');
    }
}

function showOpenAICredentialSaveResult(kind, data) {
    const isCodex = kind === 'codex';
    const prefix = isCodex ? 'codexOauth' : 'openaiPlatform';
    const result = document.getElementById(`${prefix}SaveResult`);
    const title = document.getElementById(`${prefix}SaveResultTitle`);
    const text = document.getElementById(`${prefix}SaveResultText`);
    const credentialName = isCodex ? 'OpenAI Codex credential' : 'OpenAI Platform API key';
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

async function addOpenAIPlatformCredential(event) {
    event?.preventDefault();
    const field = document.getElementById('openaiPlatformApiKey');
    const button = document.getElementById('addOpenaiPlatformKeyBtn');
    const apiKey = field?.value.trim() || '';
    if (!apiKey) {
        showStatus('Enter an OpenAI Platform API key.', 'error');
        field?.focus();
        return;
    }

    button.disabled = true;
    button.textContent = 'Validating...';
    document.getElementById('openaiPlatformSaveResult')?.classList.add('hidden');
    try {
        const response = await fetch('./api/providers/openai/platform/credentials', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ api_key: apiKey })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        field.value = '';
        showOpenAICredentialSaveResult('platform', data);
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await loadModelCatalog(true);
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to add OpenAI Platform API key: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Validate and add';
    }
}

async function startCodexOauth() {
    const button = document.getElementById('startCodexOauthBtn');
    button.disabled = true;
    button.textContent = 'Generating...';
    document.getElementById('codexOauthSaveResult')?.classList.add('hidden');
    try {
        const response = await fetch('./api/providers/openai/codex/oauth/start', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));

        const fields = document.getElementById('codexOauthFields');
        const code = document.getElementById('codexUserCode');
        const verification = document.getElementById('codexVerificationUrl');
        if (fields) {
            fields.dataset.flowId = data.flow_id || '';
            fields.dataset.pollInterval = String(data.interval || 5);
            fields.classList.remove('hidden');
        }
        if (code) code.value = data.user_code || '';
        if (verification) {
            verification.href = data.verification_uri || '#';
            verification.textContent = data.verification_uri || 'Verification page unavailable';
        }
        showStatus('OpenAI Codex device code generated.', 'success');
    } catch (error) {
        showStatus(`Failed to start OpenAI Codex authorization: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Get authorization code';
    }
}

async function completeCodexOauth() {
    const fields = document.getElementById('codexOauthFields');
    const flowId = fields?.dataset.flowId || '';
    const button = document.getElementById('completeCodexOauthBtn');
    if (!flowId) {
        showStatus('Generate a new OpenAI Codex device code before checking authorization.', 'error');
        return;
    }

    button.disabled = true;
    button.textContent = 'Checking...';
    try {
        const response = await fetch('./api/providers/openai/codex/oauth/complete', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ flow_id: flowId })
        });
        const data = await response.json().catch(() => ({}));
        if (response.status === 202 && data.pending) {
            showStatus(data.message || 'OpenAI Codex authorization is still pending.', 'info');
            return;
        }
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));

        delete fields.dataset.flowId;
        showOpenAICredentialSaveResult('codex', data);
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await loadModelCatalog(true);
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to save OpenAI Codex credential: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Check authorization';
    }
}

function handleCodexFileSelect(event) {
    AppState.codexUploadFiles.handleFileSelect(event);
}

function handleCodexFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    AppState.codexUploadFiles.addFiles(Array.from(event.dataTransfer.files));
}

function clearCodexFiles() {
    AppState.codexUploadFiles.clearFiles();
}

function uploadCodexFiles() {
    AppState.codexUploadFiles.upload();
}

function handleOpenAIPlatformFileSelect(event) {
    AppState.openaiPlatformUploadFiles.handleFileSelect(event);
}

function handleOpenAIPlatformFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    AppState.openaiPlatformUploadFiles.addFiles(Array.from(event.dataTransfer.files));
}

function clearOpenAIPlatformFiles() {
    AppState.openaiPlatformUploadFiles.clearFiles();
}

function uploadOpenAIPlatformFiles() {
    AppState.openaiPlatformUploadFiles.upload();
}
