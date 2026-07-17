// Omni Gateway management console: credentials.

function refreshCredsStatus() { AppState.creds.refresh(); }

function applyStatusFilter() { AppState.creds.applyStatusFilter(); }

function changePage(direction) { AppState.creds.changePage(direction); }

function changePageSize() { AppState.creds.changePageSize(); }

function toggleFileSelection(filename) {

    if (AppState.creds.selectedFiles.has(filename)) {

        AppState.creds.selectedFiles.delete(filename);

    } else {

        AppState.creds.selectedFiles.add(filename);

    }

    AppState.creds.updateBatchControls();

}

function toggleSelectAll() {

    const checkbox = document.getElementById('selectAllCheckbox');

    const checkboxes = document.querySelectorAll('.file-checkbox');

    if (checkbox.checked) {

        checkboxes.forEach(cb => AppState.creds.selectedFiles.add(cb.getAttribute('data-filename')));

    } else {

        AppState.creds.selectedFiles.clear();

    }

    checkboxes.forEach(cb => cb.checked = checkbox.checked);

    AppState.creds.updateBatchControls();

}

function batchAction(action) { AppState.creds.batchAction(action); }

function downloadCred(filename) {

    fetch(`./api/credentials/download/${encodeURIComponent(filename)}`)

        .then(r => r.ok ? r.blob() : Promise.reject())

        .then(blob => {

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = filename;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('status_download_success', {filename}), 'success');

        })

        .catch(() => showStatus(t('download_failed_filename', {filename: filename}), 'error'));

}

async function downloadAllCreds() {

    try {

        const response = await fetch('./api/credentials/download-all');

        if (response.ok) {

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = 'credentials.zip';

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('all_credential_files_have_been_down'), 'success');

        }

    } catch (error) {

        showStatus(t('failed_to_download_package_errormes', {error_message: error.message}), 'error');

    }

}

function refreshPrimaryCredsList() { AppState.primaryCreds.refresh(); }

function applyPrimaryStatusFilter() { AppState.primaryCreds.applyStatusFilter(); }

function changePrimaryPage(direction) { AppState.primaryCreds.changePage(direction); }

function changePrimaryPageSize() { AppState.primaryCreds.changePageSize(); }

function togglePrimaryFileSelection(filename) {

    if (AppState.primaryCreds.selectedFiles.has(filename)) {

        AppState.primaryCreds.selectedFiles.delete(filename);

    } else {

        AppState.primaryCreds.selectedFiles.add(filename);

    }

    AppState.primaryCreds.updateBatchControls();

}

function toggleSelectAllPrimary() {

    const checkbox = document.getElementById('selectAllPrimaryCheckbox');

    const checkboxes = document.querySelectorAll('.primaryFile-checkbox');

    if (checkbox.checked) {

        checkboxes.forEach(cb => AppState.primaryCreds.selectedFiles.add(cb.getAttribute('data-filename')));

    } else {

        AppState.primaryCreds.selectedFiles.clear();

    }

    checkboxes.forEach(cb => cb.checked = checkbox.checked);

    AppState.primaryCreds.updateBatchControls();

}

function batchPrimaryAction(action) { AppState.primaryCreds.batchAction(action); }

function downloadPrimaryCred(filename) {

    fetch(`./api/credentials/download/${encodeURIComponent(filename)}?mode=provider`, { headers: getAuthHeaders() })

        .then(r => r.ok ? r.blob() : Promise.reject())

        .then(blob => {

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = filename;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('downloaded_filename', {filename: filename}), 'success');

        })

        .catch(() => showStatus(t('download_failed_filename', {filename: filename}), 'error'));

}

async function deletePrimaryCred(filename) {

    if (await showConfirmModal(t('confirm_delete_cred'), {

        title: t('confirm_delete_cred_title'),

        confirmLabel: t('action_delete')

    })) {

        AppState.primaryCreds.action(filename, 'delete');

    }

}

async function downloadAllPrimaryCreds() {

    try {

        const response = await fetch('./api/credentials/download-all?mode=provider', { headers: getAuthHeaders() });

        if (response.ok) {

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');

            a.href = url;

            a.download = `primary_credentials_${Date.now()}.zip`;

            a.click();

            window.URL.revokeObjectURL(url);

            showStatus(t('all_primary_credentials_packed'), 'success');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

function selectPoolImportArchive() {

    const input = document.getElementById('poolImportArchiveInput');

    if (!input) return;

    input.value = '';
    input.click();

}

function getPoolImportActionLabel(result) {

    if (result.status === 'error') return 'Failed';
    if (result.status === 'skipped') return 'Skipped';
    if (result.action === 'replaced') return 'Renewed';
    if (result.action === 'updated') return 'Updated';
    return 'Added';

}

function buildPoolImportResultHtml(data) {

    const providerItems = Object.values(data.providers || {}).filter((provider) => {

        return ['created', 'updated', 'replaced', 'skipped', 'failed']
            .some((key) => Number(provider[key] || 0) > 0);

    });

    const providerSummary = providerItems.length
        ? `
            <div class="message-result-section">
                <div class="message-result-section-title">Provider Summary</div>
                <div class="usage-provider-summary pool-import-provider-summary">
                    ${providerItems.map((provider) => {
                        const providerMeta = getCredentialProviderMeta({ provider: provider.provider }, 'usage');
                        const imported = Number(provider.created || 0)
                            + Number(provider.updated || 0)
                            + Number(provider.replaced || 0);
                        const logo = providerMeta.logo
                            ? `<img src="${escapeAttribute(providerMeta.logo)}" alt="">`
                            : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

                        return `
                            <article class="usage-provider-item">
                                <div class="usage-provider-identity">
                                    <div class="usage-provider-logo" aria-hidden="true">${logo}</div>
                                    <div>
                                        <div class="usage-provider-name">${escapeHtml(providerMeta.name)}</div>
                                        <div class="usage-provider-meta">Credential import</div>
                                    </div>
                                </div>
                                <dl class="usage-provider-metrics">
                                    <div><dt>Imported</dt><dd>${formatUsageNumber(imported)}</dd></div>
                                    <div><dt>Skipped</dt><dd>${formatUsageNumber(provider.skipped)}</dd></div>
                                    <div><dt>Failed</dt><dd>${formatUsageNumber(provider.failed)}</dd></div>
                                </dl>
                            </article>
                        `;
                    }).join('')}
                </div>
            </div>
        `
        : '';

    const results = Array.isArray(data.results) ? data.results : [];
    const visibleResults = results.slice(0, 24);
    const fileResults = visibleResults.map((result) => {

        const statusClass = result.status === 'error'
            ? 'danger'
            : result.status === 'skipped'
                ? 'muted'
                : 'success';
        const providerName = result.provider_name
            || (result.provider ? getCredentialProviderMeta({ provider: result.provider }, 'usage').name : 'Unrecognized provider');
        const sourceName = result.source_filename || result.filename || 'Credential file';

        return `
            <div class="upload-result-item">
                <div class="pool-import-result-heading">
                    <span class="status-badge ${statusClass}">${escapeHtml(getPoolImportActionLabel(result))}</span>
                    <span class="upload-result-file">${escapeHtml(sourceName)}</span>
                </div>
                <div class="upload-result-message">${escapeHtml(providerName)} - ${escapeHtml(ensureTerminalPunctuation(result.message || 'Import completed.'))}</div>
            </div>
        `;

    }).join('');
    const hiddenCount = Math.max(0, results.length - visibleResults.length);
    const fileSection = results.length
        ? `
            <div class="message-result-section">
                <div class="message-result-section-title">File Results</div>
                <div class="upload-result-details">
                    ${fileResults}
                    ${hiddenCount ? `<div class="upload-result-message">${hiddenCount} more ${hiddenCount === 1 ? 'result was' : 'results were'} processed.</div>` : ''}
                </div>
            </div>
        `
        : '';

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">The archive was inspected and each credential was routed through its provider-specific validation and duplicate checks.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Import Summary</div>
                <div class="message-result-summary pool-import-summary">${renderMessageResultRows([
                    ['Credential files', Number(data.total_count || 0)],
                    ['Imported', Number(data.uploaded_count || 0)],
                    ['Skipped', Number(data.skipped_count || 0)],
                    ['Failed', Number(data.error_count || 0)],
                ])}</div>
            </div>
            ${providerSummary}
            ${fileSection}
        </div>
    `;

}

async function handlePoolImportArchive(event) {

    const input = event.target;
    const archive = input?.files?.[0];

    if (!archive) return;

    if (!archive.name.toLowerCase().endsWith('.zip')) {

        showStatus('Select a ZIP archive created from the credential pool.', 'error');
        input.value = '';
        return;

    }

    if (archive.size > 10 * 1024 * 1024) {

        showStatus('Pool archive exceeds the 10 MB import limit.', 'error');
        input.value = '';
        return;

    }

    const button = document.getElementById('poolImportArchiveBtn');
    const originalLabel = button?.textContent || 'Import ZIP';
    const formData = new FormData();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15 * 60 * 1000);
    formData.append('archive', archive);

    if (button) {

        button.disabled = true;
        button.textContent = 'Importing...';

    }

    showStatus('Inspecting the pool archive and validating provider credentials.', 'info');

    try {

        const response = await fetch('./api/credentials/import', {
            method: 'POST',
            body: formData,
            signal: controller.signal,
        });
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {

            throw new Error(data.detail || data.error || `Pool import failed with HTTP ${response.status}.`);

        }

        const variant = Number(data.error_count || 0) > 0
            ? (Number(data.uploaded_count || 0) > 0 ? 'warning' : 'error')
            : Number(data.skipped_count || 0) > 0
                ? 'info'
                : 'success';

        showStatus(data.message || 'Pool archive imported.', variant);
        showMessageModal('Pool Import', buildPoolImportResultHtml(data), variant, { html: true });
        await AppState.primaryCreds.refresh();
        refreshUsageStats();

    } catch (error) {

        const message = error.name === 'AbortError'
            ? 'Pool import timed out while validating provider credentials.'
            : error.message;
        showStatus(message, 'error');
        showMessageModal('Pool Import', message, 'error');

    } finally {

        clearTimeout(timeout);
        input.value = '';
        if (button) {

            button.disabled = false;
            button.textContent = originalLabel;

        }

    }

}

function handleFileSelect(event) { AppState.uploadFiles.handleFileSelect(event); }

function clearFiles() { AppState.uploadFiles.clearFiles(); }

function uploadFiles() { AppState.uploadFiles.upload(); }

function handlePrimaryFileSelect(event) { AppState.primaryUploadFiles.handleFileSelect(event); }

function handlePrimaryFileDrop(event) {

    event.preventDefault();

    event.currentTarget.classList.remove('dragover');

    AppState.primaryUploadFiles.addFiles(Array.from(event.dataTransfer.files));

}

function clearPrimaryFiles() { AppState.primaryUploadFiles.clearFiles(); }

function uploadPrimaryFiles() { AppState.primaryUploadFiles.upload(); }

function handleGoogleAiStudioFileSelect(event) {
    AppState.googleAiStudioUploadFiles.handleFileSelect(event);
}

function handleGoogleAiStudioFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    AppState.googleAiStudioUploadFiles.addFiles(Array.from(event.dataTransfer.files));
}

function clearGoogleAiStudioFiles() {
    AppState.googleAiStudioUploadFiles.clearFiles();
}

function uploadGoogleAiStudioFiles() {
    AppState.googleAiStudioUploadFiles.upload();
}

function handleGrokFileSelect(event) {
    AppState.grokUploadFiles.handleFileSelect(event);
}

function handleGrokFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    AppState.grokUploadFiles.addFiles(Array.from(event.dataTransfer.files));
}

function clearGrokFiles() {
    AppState.grokUploadFiles.clearFiles();
}

function uploadGrokFiles() {
    AppState.grokUploadFiles.upload();
}

function handleXaiConsoleFileSelect(event) {
    AppState.xaiConsoleUploadFiles.handleFileSelect(event);
}

function handleXaiConsoleFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    AppState.xaiConsoleUploadFiles.addFiles(Array.from(event.dataTransfer.files));
}

function clearXaiConsoleFiles() {
    AppState.xaiConsoleUploadFiles.clearFiles();
}

function uploadXaiConsoleFiles() {
    AppState.xaiConsoleUploadFiles.upload();
}
