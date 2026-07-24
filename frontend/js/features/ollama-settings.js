async function addOllamaCredential(event) {
    event?.preventDefault();
    const endpointField = document.getElementById('ollamaBaseUrl');
    const apiKeyField = document.getElementById('ollamaApiKey');
    const button = document.getElementById('addOllamaBtn');
    const baseUrl = endpointField?.value.trim() || '';
    const apiKey = apiKeyField?.value.trim() || '';

    if (!baseUrl) {
        showStatus('Enter an Ollama endpoint.', 'error');
        endpointField?.focus();
        return;
    }

    button.disabled = true;
    button.textContent = 'Connecting...';
    document.getElementById('ollamaSaveResult')?.classList.add('hidden');

    try {
        const response = await fetch('./api/providers/ollama/credentials', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ base_url: baseUrl, api_key: apiKey })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || t('unknown_error'));

        const title = document.getElementById('ollamaSaveResultTitle');
        const text = document.getElementById('ollamaSaveResultText');
        if (title) {
            title.textContent = data.credential_action === 'updated'
                ? 'Ollama connection updated'
                : 'Ollama connection added to pool';
        }
        if (text) {
            const count = Number(data.model_count) || 0;
            text.textContent = `${data.message} ${count} model${count === 1 ? '' : 's'} available.`;
        }
        document.getElementById('ollamaSaveResult')?.classList.remove('hidden');
        if (apiKeyField) apiKeyField.value = '';
        showStatus(data.message, 'success');
        await AppState.primaryCreds.refresh();
        await loadModelCatalog(true);
        await refreshUsageStats();
    } catch (error) {
        showStatus(`Failed to add Ollama connection: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Validate and add';
    }
}

function handleOllamaFileSelect(event) {
    AppState.ollamaUploadFiles.handleFileSelect(event);
}

function handleOllamaFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    AppState.ollamaUploadFiles.addFiles(Array.from(event.dataTransfer.files));
}

function clearOllamaFiles() {
    AppState.ollamaUploadFiles.clearFiles();
}

function uploadOllamaFiles() {
    AppState.ollamaUploadFiles.upload();
}