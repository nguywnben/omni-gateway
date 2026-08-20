const GEMINI_CLI_CONFIG_FIELDS = {
    geminiCliApiUrl: 'gemini_cli_api_url',
    geminiCliAuthorizeUrl: 'gemini_cli_oauth_authorize_url',
    geminiCliTokenUrl: 'gemini_cli_oauth_token_url',
    geminiCliClientId: 'gemini_cli_client_id',
    geminiCliClientSecret: 'gemini_cli_client_secret'
};

let pendingGeminiCliFiles = [];

async function loadGeminiCliSettings(options = {}) {
    if (!Object.keys(GEMINI_CLI_CONFIG_FIELDS).some((fieldId) => document.getElementById(fieldId))) return;
    const loadingIds = ['geminiCliSettingsLoading'];
    const formIds = ['geminiCliSettingsForm'];
    const preserveContent = options.preserveContent ?? formIds.some(
        (id) => document.getElementById(id)?.dataset.loaded === 'true'
    );
    setProviderSettingsLoading(loadingIds, formIds, true, preserveContent);
    try {
        const response = await fetch('./api/providers/gemini_cli/config', { headers: getAuthHeaders() });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        const locked = new Set(data.env_locked || []);
        Object.entries(GEMINI_CLI_CONFIG_FIELDS).forEach(([fieldId, configKey]) => {
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
        showStatus(`Failed to load Gemini CLI provider settings: ${error.message}`, 'error');
    } finally {
        setProviderSettingsLoading(loadingIds, formIds, false, preserveContent);
    }
}

async function saveGeminiCliSettings() {
    const config = {};
    Object.entries(GEMINI_CLI_CONFIG_FIELDS).forEach(([fieldId, configKey]) => {
        const field = document.getElementById(fieldId);
        if (field && !field.disabled) config[configKey] = field.value.trim();
    });
    try {
        const response = await fetch('./api/providers/gemini_cli/config', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ config })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus('Gemini CLI settings saved.', 'success');
        await loadGeminiCliSettings();
    } catch (error) {
        showStatus(`Failed to save Gemini CLI settings: ${error.message}`, 'error');
    }
}

async function resetGeminiCliSettings() {
    const confirmed = await showConfirmModal(
        'Restore the built-in Gemini CLI settings? Environment-managed values will be preserved.',
        { title: 'Reset Gemini CLI Settings', confirmLabel: 'Reset defaults' }
    );
    if (!confirmed) return;
    try {
        const response = await fetch('./api/providers/gemini_cli/config/reset', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        showStatus(data.message || 'Gemini CLI settings reset to defaults.', 'success');
        await loadGeminiCliSettings();
    } catch (error) {
        showStatus(`Failed to reset Gemini CLI settings: ${error.message}`, 'error');
    }
}

async function startGeminiCliOauth() {
    const fields = document.getElementById('geminiCliOauthFields');
    const authLink = document.getElementById('geminiCliAuthorizationUrl');
    const saveResult = document.getElementById('geminiCliOauthSaveResult');
    if (saveResult) saveResult.classList.add('hidden');
    try {
        const response = await fetch('./api/providers/gemini_cli/oauth/start', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));
        if (authLink) {
            authLink.href = data.authorization_url;
            authLink.textContent = data.authorization_url;
        }
        if (fields) {
            fields.classList.remove('hidden');
            fields.dataset.oauthState = data.state || '';
        }
        showStatus('Gemini CLI authorization link generated. Sign in to complete.', 'info');
    } catch (error) {
        showStatus(`Failed to start Gemini CLI OAuth: ${error.message}`, 'error');
    }
}

async function saveGeminiCliOauth() {
    const codeInput = document.getElementById('geminiCliAuthorizationCode');
    const fields = document.getElementById('geminiCliOauthFields');
    const code = codeInput?.value?.trim() || '';
    if (!code) {
        showStatus('Please paste the authorization code.', 'error');
        codeInput?.focus();
        return;
    }
    const state = fields?.dataset?.oauthState || '';
    try {
        const response = await fetch('./api/providers/gemini_cli/oauth/save', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ code, state })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));

        const saveResult = document.getElementById('geminiCliOauthSaveResult');
        const saveResultText = document.getElementById('geminiCliOauthSaveResultText');
        if (saveResult && saveResultText) {
            saveResultText.textContent = `Credential saved (${data.credential?.user_email || 'Google Account'})`;
            saveResult.classList.remove('hidden');
        }
        if (codeInput) codeInput.value = '';
        showStatus('Gemini CLI credential added to pool.', 'success');
        if (typeof loadCredentials === 'function') loadCredentials();
        if (typeof loadModelCatalog === 'function') loadModelCatalog(true);
    } catch (error) {
        showStatus(`Failed to save Gemini CLI credential: ${error.message}`, 'error');
    }
}

function handleGeminiCliFileSelect(event) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;
    pendingGeminiCliFiles = files;
    renderGeminiCliFileList();
}

function renderGeminiCliFileList() {
    const section = document.getElementById('geminiCliFileListSection');
    const list = document.getElementById('geminiCliFileList');
    if (!section || !list) return;
    if (!pendingGeminiCliFiles.length) {
        section.classList.add('hidden');
        list.innerHTML = '';
        return;
    }
    list.innerHTML = pendingGeminiCliFiles.map(f => `<div>📄 ${escapeHtml(f.name)} (${formatFileSize(f.size)})</div>`).join('');
    section.classList.remove('hidden');
}

function clearGeminiCliFiles() {
    pendingGeminiCliFiles = [];
    const input = document.getElementById('geminiCliFileInput');
    if (input) input.value = '';
    renderGeminiCliFileList();
}

async function uploadGeminiCliFiles() {
    if (!pendingGeminiCliFiles.length) return;
    const progressSection = document.getElementById('geminiCliUploadProgressSection');
    const progressFill = document.getElementById('geminiCliProgressFill');
    const progressText = document.getElementById('geminiCliProgressText');
    const resultSection = document.getElementById('geminiCliUploadResult');
    const resultText = document.getElementById('geminiCliUploadResultText');
    const resultDetails = document.getElementById('geminiCliUploadResultDetails');

    if (progressSection) progressSection.classList.remove('hidden');
    if (progressFill) progressFill.style.width = '30%';
    if (progressText) progressText.textContent = '30%';
    if (resultSection) resultSection.classList.add('hidden');

    const formData = new FormData();
    pendingGeminiCliFiles.forEach(f => formData.append('files', f));

    try {
        const response = await fetch('./api/providers/gemini_cli/import', {
            method: 'POST',
            headers: getAuthHeaders(false),
            body: formData
        });
        const data = await response.json().catch(() => ({}));
        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = '100%';
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));

        if (resultSection && resultText) {
            resultText.textContent = data.message || `Imported ${data.imported_count} credentials.`;
            if (resultDetails && Array.isArray(data.results)) {
                resultDetails.innerHTML = data.results.map(r => `<div>${r.status === 'success' ? '✅' : '❌'} ${escapeHtml(r.source_filename)}: ${escapeHtml(r.message || r.status)}</div>`).join('');
            }
            resultSection.classList.remove('hidden');
        }
        clearGeminiCliFiles();
        showStatus('Gemini CLI import completed.', 'success');
        if (typeof loadCredentials === 'function') loadCredentials();
        if (typeof loadModelCatalog === 'function') loadModelCatalog(true);
    } catch (error) {
        showStatus(`Gemini CLI import failed: ${error.message}`, 'error');
    } finally {
        if (progressSection) setTimeout(() => progressSection.classList.add('hidden'), 1000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadGeminiCliSettings();
});
