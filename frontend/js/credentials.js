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
                                        <div class="usage-provider-meta">Credential restore</div>
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
                <div class="message-result-section-title">Restore Summary</div>
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

        showStatus('Pool archive exceeds the 10 MB upload limit.', 'error');
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

            throw new Error(data.detail || data.error || `Pool restore failed with HTTP ${response.status}.`);

        }

        const variant = Number(data.error_count || 0) > 0
            ? (Number(data.uploaded_count || 0) > 0 ? 'warning' : 'error')
            : Number(data.skipped_count || 0) > 0
                ? 'info'
                : 'success';

        showStatus(data.message || 'Pool archive restored.', variant);
        showMessageModal('Pool Import', buildPoolImportResultHtml(data), variant, { html: true });
        await AppState.primaryCreds.refresh();
        refreshUsageStats();

    } catch (error) {

        const message = error.name === 'AbortError'
            ? 'Pool restore timed out while validating provider credentials.'
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

async function verifyProjectId(filename) {

    try {

        showStatus(t('verifying_project_id_please_wait'), 'info');

        const response = await fetch(`./api/credentials/verify-project/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            const tierLine = data.subscription_tier ? `\nTier: ${data.subscription_tier}` : '';

            const creditLine = data.credit_amount !== undefined && data.credit_amount !== null

                ? t('ncredit_datacredit_amount', {data_credit_amount: data.credit_amount})

                : '';

            const successMsg = t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message});

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal('Credential Verification', buildCredentialVerificationHtml(filename, data), 'success', {html: true});

            await AppState.creds.refresh();

        } else {

            const errorMsg = data.message || t('verification_failed');

            showStatus(` ${errorMsg}`, 'error');

            showMessageModal('Credential Verification', t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(` ${errorMsg}`, 'error');

        showMessageModal('Credential Verification', ` ${errorMsg}`, 'error');

    }

}

async function verifyPrimaryProjectId(filename) {

    try {

        showStatus(t('verifying_primary_project_id_pl'), 'info');

        const response = await fetch(`./api/credentials/verify-project/${encodeURIComponent(filename)}?mode=provider`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            const tierLine = data.subscription_tier ? `\nTier: ${data.subscription_tier}` : '';

            const creditLine = data.credit_amount !== undefined && data.credit_amount !== null

                ? t('ncredit_datacredit_amount', {data_credit_amount: data.credit_amount})

                : '';

            const successMsg = t('validation_successfulnnfile_filenam', {filename: filename, data_project_id: data.project_id, tierLine: tierLine, creditLine: creditLine, data_message: data.message});

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal('Credential Verification', buildCredentialVerificationHtml(filename, data), 'success', {html: true});

            await AppState.primaryCreds.refresh();

        } else {

            const errorMsg = data.message || t('verification_failed');

            showStatus(` ${errorMsg}`, 'error');

            showMessageModal('Credential Verification', t('verification_failednnerrormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        const errorMsg = t('verification_failed_errormessage', {error_message: error.message});

        showStatus(` ${errorMsg}`, 'error');

        showMessageModal('Credential Verification', ` ${errorMsg}`, 'error');

    }

}

async function testCredential(filename, model) {

    try {

        showStatus(t('testing_model_please_wait'), 'info');

        const response = await fetch(`./api/credentials/test/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ model })

        });

        const data = await response.json();

        const logicalStatus = data.status_code || response.status;
        const isRateLimited = logicalStatus === 429 && data.success === true;

        if (response.status === 200 || isRateLimited) {

            const resultHtml = buildCredentialTestResultHtml(filename, data, response, { mode: 'Code Assist' });

            showStatus(isRateLimited ? t('credential_rate_limited') : t('test_successful'), isRateLimited ? 'warning' : 'success');

            await AppState.creds.refresh();

            return {
                html: resultHtml,
                type: isRateLimited ? 'info' : 'success'
            };

        }

        else {

            const errorDetails = buildCredentialTestErrorHtml(filename, data, response);

            showStatus(`Test failed: ${data.message || `${t('error_code_prefix')} ${data.status_code || response.status}`}`, 'error');

            return {
                html: errorDetails,
                type: 'error'
            };

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(errorMsg, 'error');

        return {
            type: 'error',
            html: buildApiResultHtml({
                intro: 'The selected model test could not be completed.',
                rows: [
                    ['Result', 'Failed'],
                    [t('table_filename'), filename],
                    ['Model', model],
                ],
                summaryLabel: 'Failure summary',
                note: errorMsg,
            })
        };

    }

}

async function testPrimaryCredential(filename, model) {

    try {

        showStatus(t('testing_model_please_wait'), 'info');

        const response = await fetch(`./api/credentials/test/${encodeURIComponent(filename)}?mode=provider`, {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ model })

        });

        const data = await response.json();

        const logicalStatus = data.status_code || response.status;
        const isRateLimited = logicalStatus === 429 && data.success === true;

        if (response.status === 200 || isRateLimited) {

            const resultHtml = buildCredentialTestResultHtml(filename, data, response, { mode: 'Provider' });

            showStatus(isRateLimited ? t('credential_rate_limited') : t('test_successful'), isRateLimited ? 'warning' : 'success');

            await AppState.primaryCreds.refresh();

            return {
                html: resultHtml,
                type: isRateLimited ? 'info' : 'success'
            };

        }

        else {

            const errorDetails = buildCredentialTestErrorHtml(filename, data, response);

            showStatus(`Test failed: ${data.message || `${t('error_code_prefix')} ${data.status_code || response.status}`}`, 'error');

            return {
                html: errorDetails,
                type: 'error'
            };

        }

    } catch (error) {

        const errorMsg = t('test_failed_errormessage', {error_message: error.message});

        showStatus(errorMsg, 'error');

        return {
            type: 'error',
            html: buildApiResultHtml({
                intro: 'The selected model test could not be completed.',
                rows: [
                    ['Result', 'Failed'],
                    [t('table_filename'), filename],
                    ['Model', model],
                ],
                summaryLabel: 'Failure summary',
                note: errorMsg,
            })
        };

    }

}

async function configurePreviewChannel(filename) {

    try {

        showStatus(t('configuring_preview_channel_please'), 'info');

        const response = await fetch(`./api/credentials/configure-preview/${encodeURIComponent(filename)}`, {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok && data.success) {

            const successMsg = `${t('status_action_success', {action: t('btn_setup_preview')})}\n${t('table_filename')}: ${filename}\n${t('credential_status_label')} ${data.message}`;

            showStatus(successMsg.replace(/\n/g, '<br>'), 'success');

            showMessageModal('Preview Channel Configuration', `${t('status_action_success', {action: t('btn_setup_preview')})}\n\n${t('table_filename')}: ${filename}\n\n${data.message}\n\nSetting ID: ${data.setting_id || 'N/A'}\nBinding ID: ${data.binding_id || 'N/A'}`, 'success');

            await AppState.creds.refresh();

        } else {

            const errorMsg = data.message || t('configuration_failed');

            const errorDetail = data.error || '';

            const step = data.step || '';

            let alertMsg = `${t('status_action_failed', {error: t('btn_setup_preview')})}\n\n${t('table_filename')}: ${filename}\n\n${errorMsg}`;

            if (step) {

                alertMsg += t('nfailed_step_step', {step: step});

            }

            if (errorDetail) {

                alertMsg += t('nnerror_details_errordetail', {errorDetail: errorDetail});

            }

            showStatus(errorMsg, 'error');

            showMessageModal('Preview Channel Configuration', alertMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_configure_preview_channel', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal('Preview Channel Configuration', errorMsg, 'error');

    }

}

async function togglePrimaryQuotaDetails(pathId) {

    const context = getCredentialModalContext(pathId, AppState.primaryCreds);
    const { filename } = context;

    if (!filename) return;

    showStatus(t('card_loading_quota'), 'info');

    try {

        const { response, data } = await fetchPrimaryQuota(filename);

        if (response.ok && data.success) {

            AppState.quotaPreviewCache[filename] = {
                summary: summarizeCredentialQuota(data),
                data,
            };

            updateCredentialQuotaPreview(pathId, filename);

            showMessageModal(t('quota_details'), buildCredentialQuotaHtml(filename, data, context), 'info', {html: true});

        } else {

            const errorMsg = data.error || t('failed_to_get_quota_information');

            AppState.quotaPreviewCache[filename] = { error: errorMsg };

            updateCredentialQuotaPreview(pathId, filename);

            showStatus(errorMsg, 'error');

            showMessageModal(t('quota_details'), errorMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_get_quota_information_err', {error_message: error.message});

        AppState.quotaPreviewCache[filename] = { error: errorMsg };

        updateCredentialQuotaPreview(pathId, filename);

        showStatus(errorMsg, 'error');

        showMessageModal(t('quota_details'), errorMsg, 'error');

    }

}

async function fetchPrimaryQuota(filename) {

    const response = await fetch(`./api/credentials/quota/${encodeURIComponent(filename)}?mode=provider`, {

        method: 'GET',

        headers: getAuthHeaders()

    });

    const data = await response.json();

    return { response, data };

}

async function loadPrimaryQuotaPreview(pathId) {

    const { filename } = getCredentialModalContext(pathId, AppState.primaryCreds);

    if (!filename) return;

    AppState.quotaPreviewCache[filename] = { loading: true };

    updateCredentialQuotaPreview(pathId, filename);

    try {

        const { response, data } = await fetchPrimaryQuota(filename);

        if (response.ok && data.success) {

            AppState.quotaPreviewCache[filename] = {
                summary: summarizeCredentialQuota(data),
                data,
            };

        } else {

            AppState.quotaPreviewCache[filename] = {
                error: data.error || t('failed_to_get_quota_information'),
            };

        }

    } catch (error) {

        AppState.quotaPreviewCache[filename] = {
            error: t('failed_to_get_quota_information_err', {error_message: error.message}),
        };

    } finally {

        updateCredentialQuotaPreview(pathId, filename);

    }

}

// =====================================================================

// =====================================================================

async function toggleErrorDetails(pathId) {

    await toggleErrorDetailsCommon(pathId, AppState.creds);

}

async function togglePrimaryErrorDetails(pathId) {

    await toggleErrorDetailsCommon(pathId, AppState.primaryCreds);

}

async function toggleErrorDetailsCommon(pathId, manager) {

    const { filename, manager: resolvedManager } = getCredentialModalContext(pathId, manager);

    if (!filename) return;

    showStatus(t('card_loading_errors'), 'info');

    try {

        const modeParam = resolvedManager.type === 'primary' ? 'mode=provider' : 'mode=code_assist';

        const response = await fetch(`./api/credentials/errors/${encodeURIComponent(filename)}?${modeParam}`, {

            method: 'GET',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            showMessageModal(t('btn_view_errors'), buildCredentialErrorsHtml(filename, data), 'info', {html: true});

        } else {

            const errorMsg = data.detail || data.error || t('failed_to_fetch_error_message');

            showStatus(t('failed_to_fetch_error_message_error', {errorMsg: errorMsg}), 'error');

            showMessageModal(t('btn_view_errors'), errorMsg, 'error');

        }

    } catch (error) {

        const errorMsg = t('failed_to_fetch_error_information_e', {error_message: error.message});

        showStatus(errorMsg, 'error');

        showMessageModal(t('btn_view_errors'), errorMsg, 'error');

    }

}

function highlightHttpLinks(text) {

    const urlRegex = /(https?:\/\/[^\s<>"]+)/gi;

    return text.replace(urlRegex, function(url) {

        return t('a_hrefurl_target_blank_stylecolor_0', {url: url, url: url, url: url});

    });

}

async function batchVerifyProjectIds() {

    const selectedFiles = Array.from(AppState.creds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_credentials_to_ve'), 'error');

        showMessageModal(t('tip'), t('please_select_the_credentials_to_ve_dup'), 'error');

        return;

    }

    if (!(await showConfirmModal(

        t('are_you_sure_you_want_to_batch_veri_dup', {selectedFiles_length: selectedFiles.length}),

        {title: t('confirm_verify_credentials_title'), confirmLabel: t('btn_verify_credentials')}

    ))) {

        return;

    }

    showStatus(t('parallel_verifying_selectedfileslen', {selectedFiles_length: selectedFiles.length}), 'info');

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./api/credentials/verify-project/${encodeURIComponent(filename)}`, {

                method: 'POST',

                headers: getAuthHeaders()

            });

            const data = await response.json();

            if (response.ok && data.success) {

                return {

                    success: true,

                    filename,

                    projectId: data.project_id,

                    creditAmount: data.credit_amount,

                    message: data.message

                };

            } else {

                return { success: false, filename, error: data.message || t('failed') };

            }

        } catch (error) {

            return { success: false, filename, error: error.message };

        }

    });

    const results = await Promise.all(promises);

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            const creditSuffix = result.creditAmount !== undefined && result.creditAmount !== null

                ? ` (${t('credits_label')}: ${result.creditAmount})`

                : '';

            resultMessages.push(` ${result.filename}: ${result.projectId}${creditSuffix}`);

        } else {

            failCount++;

            resultMessages.push(` ${result.filename}: ${result.error}`);

        }

    });

    await AppState.creds.refresh();

    const summary = t('batch_verification_completennsucces', {successCount: successCount, failCount: failCount, selectedFiles_length: selectedFiles.length, resultMessages_join___n: resultMessages.join('\n')});

    if (failCount === 0) {

        showStatus(t('all_verifications_successful_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length}), 'success');

        showMessageModal('Batch Verification', summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('all_verifications_failed_failed_fai', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal('Batch Verification', summary, 'error');

    } else {

        showStatus(t('batch_verification_completed_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal('Batch Verification', summary, 'info');

    }

}

async function batchVerifyPrimaryProjectIds() {

    const selectedFiles = Array.from(AppState.primaryCreds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_primary_crede_dup'), 'error');

        showMessageModal(t('tip'), t('please_select_the_primary_crede'), 'error');

        return;

    }

    if (!(await showConfirmModal(

        t('are_you_sure_you_want_to_batch_veri', {selectedFiles_length: selectedFiles.length}),

        {title: t('confirm_verify_credentials_title'), confirmLabel: t('btn_verify_credentials')}

    ))) {

        return;

    }

    showStatus(t('parallel_testing_selectedfileslengt', {selectedFiles_length: selectedFiles.length}), 'info');

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./api/credentials/verify-project/${encodeURIComponent(filename)}?mode=provider`, {

                method: 'POST',

                headers: getAuthHeaders()

            });

            const data = await response.json();

            if (response.ok && data.success) {

                return {

                    success: true,

                    filename,

                    projectId: data.project_id,

                    creditAmount: data.credit_amount,

                    message: data.message

                };

            } else {

                return { success: false, filename, error: data.message || t('failed') };

            }

        } catch (error) {

            return { success: false, filename, error: error.message };

        }

    });

    const results = await Promise.all(promises);

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            const creditSuffix = result.creditAmount !== undefined && result.creditAmount !== null

                ? ` (${t('credits_label')}: ${result.creditAmount})`

                : '';

            resultMessages.push(` ${result.filename}: ${result.projectId}${creditSuffix}`);

        } else {

            failCount++;

            resultMessages.push(` ${result.filename}: ${result.error}`);

        }

    });

    await AppState.primaryCreds.refresh();

    const summary = t('primary_batch_verification_comp_dup', {successCount: successCount, failCount: failCount, selectedFiles_length: selectedFiles.length, resultMessages_join___n: resultMessages.join('\n')});

    if (failCount === 0) {

        showStatus(t('all_verifications_successful_verifi', {successCount: successCount, selectedFiles_length: selectedFiles.length}), 'success');

        showMessageModal('Provider Batch Verification', summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('verification_failed_for_all_failed', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal('Provider Batch Verification', summary, 'error');

    } else {

        showStatus(t('batch_verification_completed_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal('Provider Batch Verification', summary, 'info');

    }

}

async function batchConfigurePreview() {

    const selectedFiles = Array.from(AppState.creds.selectedFiles);

    if (selectedFiles.length === 0) {

        showStatus(t('please_select_the_credential_to_con'), 'error');

        showMessageModal(t('tip'), t('please_select_the_credentials_to_co'), 'error');

        return;

    }

    if (!(await showConfirmModal(

        t('are_you_sure_you_want_to_batch_set', {selectedFiles_length: selectedFiles.length}),

        {title: t('confirm_configure_preview_title'), confirmLabel: t('btn_configure')}

    ))) {

        return;

    }

    showStatus(t('configuring_preview_channel_for_sel', {selectedFiles_length: selectedFiles.length}), 'info');

    const promises = selectedFiles.map(async (filename) => {

        try {

            const response = await fetch(`./api/credentials/configure-preview/${encodeURIComponent(filename)}`, {

                method: 'POST',

                headers: getAuthHeaders()

            });

            const data = await response.json();

            if (response.ok && data.success) {

                return {

                    success: true,

                    filename,

                    message: data.message,

                    setting_id: data.setting_id,

                    binding_id: data.binding_id

                };

            } else {

                return {

                    success: false,

                    filename,

                    error: data.message || t('configuration_failed'),

                    step: data.step,

                    errorDetail: data.error

                };

            }

        } catch (error) {

            return { success: false, filename, error: error.message };

        }

    });

    const results = await Promise.all(promises);

    let successCount = 0;

    let failCount = 0;

    const resultMessages = [];

    results.forEach(result => {

        if (result.success) {

            successCount++;

            resultMessages.push(t('resultfilename_resultmessage_config', {result_filename: result.filename, result_message: result.message || t('configuration_successful')}));

        } else {

            failCount++;

            const errorMsg = result.step ? t('resulterror_step_resultstep', {result_error: result.error, result_step: result.step}) : result.error;

            resultMessages.push(` ${result.filename}: ${errorMsg}`);

        }

    });

    await AppState.creds.refresh();

    const summary = t('batch_preview_channel_configuration', {successCount: successCount, failCount: failCount, selectedFiles_length: selectedFiles.length, resultMessages_join___n: resultMessages.join('\n')});

    if (failCount === 0) {

        showStatus(t('all_configured_successfully_preview', {successCount: successCount, selectedFiles_length: selectedFiles.length}), 'success');

        showMessageModal(t('bulk_preview_channel_configuration'), summary, 'success');

    } else if (successCount === 0) {

        showStatus(t('configuration_failed_for_all_failed', {failCount: failCount, selectedFiles_length: selectedFiles.length}), 'error');

        showMessageModal(t('bulk_preview_channel_configuration'), summary, 'error');

    } else {

        showStatus(t('batch_configuration_complete_succes', {successCount: successCount, selectedFiles_length: selectedFiles.length, failCount: failCount}), 'info');

        showMessageModal(t('bulk_preview_channel_configuration'), summary, 'info');

    }

}

async function refreshAllEmails() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_refresh_us'), {

        title: t('confirm_refresh_emails_title'),

        confirmLabel: t('btn_refresh')

    }))) return;

    try {

        showStatus(t('refreshing_all_user_emails'), 'info');

        const response = await fetch('./api/credentials/refresh-all-emails', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            showStatus(t('email_refresh_complete_successfully', {data_success_count: data.success_count, data_total_count: data.total_count}), 'success');

            await AppState.creds.refresh();

        } else {

            showStatus(data.message || t('failed_to_refresh_emails'), 'error');

        }

    } catch (error) {

        showStatus(t('email_refresh_network_error_errorme', {error_message: error.message}), 'error');

    }

}

async function deduplicateByEmail() {

    if (!(await showConfirmModal(t('are_you_sure_you_want_to_perform_on'), {

        title: t('confirm_deduplicate_title'),

        confirmLabel: t('btn_deduplicate')

    }))) return;

    try {

        showStatus(t('oneclick_credential_deduplication_i'), 'info');

        const response = await fetch('./api/credentials/deduplicate-by-email', {

            method: 'POST',

            headers: getAuthHeaders()

        });

        const data = await response.json();

        if (response.ok) {

            const msg = t('deduplication_complete_deleted_data', {data_deleted_count: data.deleted_count, data_kept_count: data.kept_count, data_unique_emails_count: data.unique_emails_count});

            showStatus(msg, 'success');

            await AppState.creds.refresh();

            if (data.duplicate_groups && data.duplicate_groups.length > 0) {

                let details = t('deduplication_detailsnn');

                data.duplicate_groups.forEach(group => {

                    details += t('email_groupemailnkeep_groupkept_fil', {group_email: group.email, group_kept_file: group.kept_file, group_deleted_files_join: group.deleted_files.join(', ')});

                });

                showMessageModal(t('deduplication_details_title'), details, 'info');

            }

        } else {

            showStatus(data.message || t('deduplication_failed'), 'error');

        }

    } catch (error) {

        showStatus(t('deduplication_network_error_errorme', {error_message: error.message}), 'error');

    }

}

// =====================================================================

// =====================================================================
