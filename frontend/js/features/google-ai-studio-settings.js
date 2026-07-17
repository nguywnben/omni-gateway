async function loadGoogleAIStudioSettings() {
    const field = document.getElementById('googleAiStudioApiUrl');
    if (!field) return;

    setProviderSettingsLoading(
        ['googleAiStudioSettingsLoading'],
        ['googleAiStudioSettingsForm'],
        true
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
        const isLocked = (data.env_locked || []).includes('google_ai_studio_api_url');
        field.disabled = isLocked;
        field.classList.toggle('env-locked', isLocked);
    } catch (error) {
        showStatus(`Failed to load Google AI Studio settings: ${error.message}`, 'error');
    } finally {
        setProviderSettingsLoading(
            ['googleAiStudioSettingsLoading'],
            ['googleAiStudioSettingsForm'],
            false
        );
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
