async function loadGoogleAIStudioSettings(options = {}) {
    const field = document.getElementById('googleAiStudioApiUrl');
    if (!field) return;

    const preserveContent = options.preserveContent ?? field.dataset.loaded === 'true';

    setProviderSettingsLoading(
        ['googleAiStudioSettingsLoading'],
        ['googleAiStudioSettingsForm'],
        true,
        preserveContent
    );

    try {
        const response = await fetch('./api/providers/google-ai-studio/config', {
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || data.error || t('unknown_error'));
        }
        field.value = data.config?.google_ai_studio_api_url || '';
        field.dataset.loaded = 'true';
        const isLocked = (data.env_locked || []).includes('google_ai_studio_api_url');
        field.disabled = isLocked;
        field.classList.toggle('env-locked', isLocked);
    } catch (error) {
        showStatus(t('provider.settings_load_failed', {provider: 'Google AI Studio', error: error.message}), 'error');
    } finally {
        setProviderSettingsLoading(
            ['googleAiStudioSettingsLoading'],
            ['googleAiStudioSettingsForm'],
            false,
            preserveContent
        );
    }
}

async function saveGoogleAIStudioSettings() {
    const field = document.getElementById('googleAiStudioApiUrl');
    const apiUrl = field?.value.trim() || '';
    if (!apiUrl) {
        showStatus(t('provider.endpoint_required', {provider: 'Google AI Studio'}), 'error');
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
        showStatus(data.message || t('provider.settings_saved', {provider: 'Google AI Studio'}), 'success');
        await loadGoogleAIStudioSettings();
    } catch (error) {
        showStatus(t('provider.settings_save_failed', {provider: 'Google AI Studio', error: error.message}), 'error');
    }
}

async function resetGoogleAIStudioSettings() {
    const confirmed = await showConfirmModal(
        t('provider.reset_confirm', {provider: 'Google AI Studio'}),
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
        showStatus(data.message || t('provider.settings_reset', {provider: 'Google AI Studio'}), 'success');
        await loadGoogleAIStudioSettings();
    } catch (error) {
        showStatus(t('provider.settings_reset_failed', {provider: 'Google AI Studio', error: error.message}), 'error');
    }
}

async function addGoogleAIStudioCredential(event) {
    event?.preventDefault();
    const keyField = document.getElementById('googleAiStudioApiKey');
    const button = document.getElementById('addGoogleAiStudioKeyBtn');
    const apiKey = keyField?.value.trim() || '';

    if (!apiKey) {
        showStatus(t('provider.api_key_required', {provider: 'Google AI Studio'}), 'error');
        keyField?.focus();
        return;
    }

    button.disabled = true;
    button.textContent = t('runtime.validating');
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
            title.textContent = t(data.credential_action === 'updated'
                ? 'runtime.credential_updated_title'
                : 'runtime.credential_added_title');
        }
        if (text) {
            text.textContent = `${data.message} ${t('runtime.models_available', {count: data.model_count})}`;
        }
        result?.classList.remove('hidden');
        keyField.value = '';
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await refreshUsageStats();
    } catch (error) {
        showStatus(t('provider.api_key_add_failed', {provider: 'Google AI Studio', error: error.message}), 'error');
    } finally {
        button.disabled = false;
        button.textContent = t('runtime.validate_add');
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
        label: 'Grok Build',
        resetTitle: 'Reset Grok Build Settings',
        fieldIds: ['xaiClientId', 'xaiOauthIssuer']
    },
    api: {
        label: 'Grok Build and SpaceXAI Console transport',
        resetTitle: 'Reset Grok Build and SpaceXAI Console Transport Settings',
        fieldIds: ['xaiApiUrl', 'xaiUserAgent']
    }
};
