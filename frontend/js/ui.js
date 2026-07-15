// Omni Gateway management console: ui.

function ensureTerminalPunctuation(message) {

    const value = String(message ?? '');
    const trimmedEnd = value.trimEnd();

    if (!trimmedEnd) return value;

    const visibleText = trimmedEnd
        .replace(/<br\s*\/?>/gi, ' ')
        .replace(/<[^>]+>/g, '')
        .trim();

    if (!visibleText || /[.!?;:…]$/.test(visibleText)) return value;

    return value.slice(0, trimmedEnd.length) + '.' + value.slice(trimmedEnd.length);

}

function showStatus(message, type = 'info') {

    const displayMessage = ensureTerminalPunctuation(message);

    const statusSection = document.getElementById('statusSection');

    if (statusSection) {

        if (window._statusTimeout) {

            clearTimeout(window._statusTimeout);

        }

        const statusDiv = document.createElement('div');
        const statusType = ['success', 'error', 'warning', 'info'].includes(type)
            ? type
            : 'info';
        statusDiv.className = `status ${statusType}`;
        statusDiv.textContent = displayMessage;
        statusSection.replaceChildren(statusDiv);

        statusDiv.offsetHeight;

        statusDiv.classList.add('show');

        window._statusTimeout = setTimeout(() => {

            statusDiv.classList.add('fade-out');

            setTimeout(() => {

                statusSection.replaceChildren();

            }, 300);

        }, 3000);

    } else {

        showMessageModal(t('dialog_tip'), displayMessage, 'info');

    }

}

async function updateEndpointUrls() {
    const origin = window.location.origin;

    const openaiEl = document.getElementById('openaiEndpointUrl');
    if (openaiEl) openaiEl.textContent = `${origin}/v1`;

    const anthropicEl = document.getElementById('anthropicEndpointUrl');
    if (anthropicEl) anthropicEl.textContent = origin;

    const googleGenaiEl = document.getElementById('googleGenaiEndpointUrl');
    if (googleGenaiEl) googleGenaiEl.textContent = origin;

    try {
        const response = await fetch('./api/auth/keys', { headers: getAuthHeaders() });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const apiKeyEl = document.getElementById('apiKey');
                const apiKey = data.api_key || '';
                if (apiKeyEl) {
                    apiKeyEl.value = apiKey;
                    if (!apiKeyEl.dataset.visibilityInitialized) {
                        setApiKeyVisibility(false);
                    }
                }
                const regenerateBtn = document.getElementById('regenerateApiKeyBtn');
                if (regenerateBtn) {
                    const managedByEnv = Boolean(data.managed_by_env);
                    regenerateBtn.disabled = managedByEnv;
                    regenerateBtn.title = managedByEnv
                        ? 'API key is managed by the API_KEY environment variable'
                        : 'Regenerate API key';
                }
            }
        }
    } catch (e) {
        console.error("Failed to fetch API key", e);
    }
}

function setApiKeyVisibility(visible) {
    const input = document.getElementById('apiKey');
    const button = document.getElementById('toggleApiKeyVisibilityBtn');
    if (!input) return;

    input.type = visible ? 'text' : 'password';
    input.dataset.visibilityInitialized = 'true';
    input.dataset.visible = visible ? 'true' : 'false';

    if (button) {
        const label = visible ? 'Hide API key' : 'Show API key';
        button.title = label;
        button.setAttribute('aria-label', label);
        button.innerHTML = visible
            ? '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18"></path><path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"></path><path d="M9.9 5.2A9.6 9.6 0 0 1 12 5c6.5 0 10 7 10 7a18.3 18.3 0 0 1-3.1 4.3"></path><path d="M6.5 6.8C3.7 8.6 2 12 2 12s3.5 7 10 7a9.8 9.8 0 0 0 4.1-.9"></path></svg>'
            : '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
    }
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('apiKey');
    if (!input) return;
    setApiKeyVisibility(input.type === 'password');
}

async function copyTextToClipboard(text) {
    const value = String(text || '');
    if (!value) return false;

    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(value);
            return true;
        } catch (error) {
            // Fall through to the legacy path below. Public HTTP deployments do
            // not always expose the modern clipboard API.
        }
    }

    const textarea = document.createElement('textarea');
    textarea.value = value;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.inset = '0 auto auto 0';
    textarea.style.width = '1px';
    textarea.style.height = '1px';
    textarea.style.opacity = '0';
    textarea.style.pointerEvents = 'none';

    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);

    let copied = false;
    try {
        copied = document.execCommand('copy');
    } catch (error) {
        copied = false;
    } finally {
        document.body.removeChild(textarea);
    }

    return copied;
}

async function copyTextWithStatus(text) {
    const copied = await copyTextToClipboard(text);
    showStatus(t(copied ? 'copy_success' : 'copy_fail'), copied ? 'success' : 'error');
    return copied;
}

function cpUrl(element) {
    const text = element.textContent || element.innerText;
    if (!text) return;
    copyTextWithStatus(text.trim());
}

function copyInputValue(inputId) {
    const input = document.getElementById(inputId);
    if (!input || !input.value || input.value === '...') return;
    if (document.activeElement === input) {
        input.blur();
    }
    copyTextWithStatus(input.value);
}

async function regenerateApiKey() {
    if (!(await showConfirmModal(t('confirm_regenerate_key'), {
        title: t('confirm_regenerate_key_title'),
        confirmLabel: t('btn_regenerate')
    }))) {
        return;
    }
    try {
        const response = await fetch('./api/auth/keys/reset', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (response.ok) {
            if (data.success) {
                const el = document.getElementById('apiKey');
                const apiKey = data.api_key || '';
                if (el) {
                    el.value = apiKey;
                    if (!el.dataset.visibilityInitialized) {
                        setApiKeyVisibility(false);
                    }
                }
                showStatus(t('regenerate_success'), 'success');
            } else {
                showStatus(data.error || 'Failed to regenerate the API key.', 'error');
            }
        } else {
            showStatus(data.detail || data.message || 'Failed to regenerate the API key.', 'error');
        }
    } catch (e) {
        console.error("Failed to regenerate the API key.", e);
        showStatus(t('status_net_error', {error: e.message}), 'error');
    }
}

function linkifyText(text) {

    if (!text) return text;

    const urlPattern = /(https?:\/\/[^\s"'<>()[\]{}]+)|(www\.[^\s"'<>()[\]{}]+)/gi;

    return text.replace(urlPattern, function(url) {

        let href = url;

        if (url.startsWith('www.')) {

            href = 'https://' + url;

        }

        const safeHref = href.replaceAll('&amp;', '&');
        return `<a href="${escapeAttribute(safeHref)}" target="_blank" rel="noopener noreferrer" class="message-link" title="${escapeAttribute(`${t('click_to_open_link')} ${t('right_click_to_copy_link')}`)}">${url}</a>`;

    });

}

function showMessageModal(title, message, type = 'info', options = {}) {

    const modal = document.createElement('div');

    modal.className = 'message-modal-overlay';
    const safeType = String(type || 'info').replace(/[^\w-]/g, '') || 'info';
    const safeTitle = escapeHtml(title);
    const safeTitleAttribute = escapeAttribute(title);
    const normalizedMessage = normalizeDialogMessage(message);
    const bodyContent = options.html
        ? String(message || '')
        : `<div class="message-modal-copy">${linkifyText(escapeHtml(normalizedMessage)).replace(/\n/g, '<br>')}</div>`;

    modal.innerHTML = `

        <div class="message-modal informational ${safeType}" role="dialog" aria-modal="true" aria-label="${safeTitleAttribute}">

            <div class="message-modal-header">

                <h3>${safeTitle}</h3>

            </div>

            <div class="message-modal-body">

                ${bodyContent}

            </div>

            <div class="message-modal-footer">

                <button type="button" class="message-modal-btn" data-dialog-close>${escapeHtml(t('btn_close'))}</button>

            </div>

        </div>

    `;

    let closed = false;

    const close = () => {

        if (closed) return;

        closed = true;

        document.removeEventListener('keydown', escHandler);

        modal.remove();

    };

    modal.addEventListener('click', function(e) {

        if (e.target === modal || e.target.closest('[data-dialog-close]')) close();

    });

    const escHandler = function(e) {

        if (e.key === 'Escape') close();

    };

    document.addEventListener('keydown', escHandler);

    document.body.appendChild(modal);

    return modal;

}

function normalizeDialogMessage(message) {

    return String(message || '').replace(/\\n/g, '\n');

}

function renderDialogMessage(message, options = {}) {

    const escaped = escapeHtml(normalizeDialogMessage(message));

    if (options.compact) {

        return escaped
            .replace(/\n{2,}/g, '<span class="message-modal-break"></span>')
            .replace(/\n/g, '<br>');

    }

    return escaped.replace(/\n/g, '<br>');

}

function stringifyModalDetail(value) {

    if (value === undefined || value === null || value === '') return '';

    if (typeof value === 'string') return normalizeDialogMessage(value);

    try {

        return JSON.stringify(value, null, 2);

    } catch {

        return String(value);

    }

}

function buildMessageResultDetails(label, value, options = {}) {

    const text = stringifyModalDetail(value);

    if (!text) return '';

    return `
        <details class="message-result-details"${options.open ? ' open' : ''}>
            <summary>${escapeHtml(label || 'Details')}</summary>
            <pre>${escapeHtml(text)}</pre>
        </details>
    `;

}

function buildApiResultHtml(options = {}) {

    const introHtml = options.intro
        ? `<div class="message-result-intro">${renderDialogMessage(ensureTerminalPunctuation(options.intro))}</div>`
        : '';

    const headingHtml = options.heading
        ? `<div class="message-result-heading">${escapeHtml(options.heading)}</div>`
        : '';

    const summaryHtml = options.rows?.length
        ? `
            <div class="message-result-section">
                <div class="message-result-section-title">${escapeHtml(options.summaryLabel || 'Summary')}</div>
                <div class="message-result-summary">${renderMessageResultRows(options.rows)}</div>
            </div>
        `
        : '';

    const noteHtml = options.note
        ? `<div class="message-result-note">${renderDialogMessage(ensureTerminalPunctuation(options.note))}</div>`
        : '';

    const detailsHtml = buildMessageResultDetails(
        options.detailsLabel || 'Details',
        options.details,
        { open: options.detailsOpen }
    );

    return `
        <div class="message-result-panel">
            ${introHtml}
            ${headingHtml}
            ${summaryHtml}
            ${noteHtml}
            ${options.extraHtml || ''}
            ${detailsHtml}
        </div>
    `;

}

function buildCredentialTestErrorHtml(filename, data, response) {

    let parsedError = null;
    const rawErrorValue = data?.error || data?.detail || data?.message || '';
    if (rawErrorValue) {
        try {
            parsedError = typeof rawErrorValue === 'string' ? JSON.parse(rawErrorValue) : rawErrorValue;
        } catch {
            parsedError = null;
        }
    }

    const errorRoot = parsedError?.error || parsedError || {};
    const firstDetail = Array.isArray(errorRoot.details) ? errorRoot.details[0] || {} : {};
    const metadata = firstDetail.metadata || {};
    const httpCode = errorRoot.code || data.status_code || response.status;
    const statusText = errorRoot.status || data.message || data.detail || data.error || t('unknown_error');
    const reason = firstDetail.reason || '';
    const permission = metadata.permission || '';
    const resource = metadata.resource || '';
    const troubleshooterUrl = safeHttpUrl(metadata.troubleshooter_url);
    const rawDetails = parsedError
        ? JSON.stringify(parsedError, null, 2)
        : String(data.detail || data.error || data.message || `${t('http_code_prefix')} ${httpCode}`);

    const summaryRows = [
        [t('table_filename'), filename],
        ['HTTP code', httpCode],
        [t('credential_status_label').replace(':', ''), statusText],
        data.provider ? ['Provider', getCredentialProviderMeta(data, 'usage').name] : null,
        data.model ? ['Model', data.model] : null,
        reason ? ['Reason', reason] : null,
        permission ? ['Permission', permission] : null,
        resource ? ['Resource', resource] : null,
    ].filter(Boolean);

    const troubleshooterHtml = troubleshooterUrl
        ? `<div class="message-result-actions"><a class="message-link" href="${escapeAttribute(troubleshooterUrl)}" target="_blank" rel="noopener noreferrer">${t('open_troubleshooter')}</a></div>`
        : '';

    return buildApiResultHtml({
        intro: 'The selected model test did not complete successfully. Review the provider status and error response below.',
        rows: summaryRows,
        summaryLabel: 'Failure summary',
        extraHtml: troubleshooterHtml,
        detailsLabel: 'Error details',
        details: rawDetails,
        detailsOpen: true,
    });

}

function buildCredentialTestResultHtml(filename, data, response, options = {}) {

    const logicalStatus = data.status_code || response.status;
    const isRateLimited = logicalStatus === 429 && data.success === true;
    const statusMessage = isRateLimited
        ? t('credential_rate_limited')
        : (data.message || t('credential_available'));

    return buildApiResultHtml({
        intro: isRateLimited
            ? 'The credential responded, but the provider reported a temporary rate limit. The router can continue with another available credential.'
            : 'The credential completed a live model test successfully.',
        rows: [
            ['Result', isRateLimited ? 'Rate limited' : 'Successful'],
            [t('table_filename'), filename],
            ['HTTP code', logicalStatus || response.status],
            [t('credential_status_label').replace(':', ''), statusMessage],
            data.provider ? ['Provider', getCredentialProviderMeta(data, 'usage').name] : null,
            data.model ? ['Model', data.model] : null,
            options.mode ? ['Mode', options.mode] : null,
        ].filter(Boolean),
        summaryLabel: 'Test summary',
    });

}

function normalizeVerificationMessage(message) {

    return String(message || '')
        .replace(/^verification successful\.?\s*/i, '')
        .replace(/^validation successful\.?\s*/i, '')
        .trim();

}

function buildCredentialVerificationHtml(filename, data) {

    const rows = [
        ['Result', 'Successful'],
        [t('table_filename'), filename],
        data.project_id ? ['Project ID', data.project_id] : null,
        data.subscription_tier ? ['Tier', data.subscription_tier] : null,
        data.credit_amount !== undefined && data.credit_amount !== null ? ['Credit', data.credit_amount] : null,
        data.provider ? ['Provider', getCredentialProviderMeta({ provider: data.provider }, 'usage').name] : null,
        Number.isFinite(Number(data.model_count)) ? ['Available models', Number(data.model_count)] : null,
    ].filter(Boolean);

    const detailMessage = normalizeVerificationMessage(data.message);

    return buildApiResultHtml({
        intro: 'The credential was verified and its provider metadata was refreshed.',
        rows,
        summaryLabel: 'Verification summary',
        note: detailMessage,
    });

}

function renderMessageResultRows(rows) {

    return rows.filter(Boolean).map(([label, value]) => `
        <div class="message-result-row">
            <div class="message-result-label">${escapeHtml(label)}</div>
            <div class="message-result-value">${escapeHtml(String(value))}</div>
        </div>
    `).join('');

}

function getCredentialModalContext(pathId, manager) {

    const context = AppState.credentialCardIndex[pathId] || {};
    const resolvedManager = context.managerType === 'primary' ? AppState.primaryCreds : manager;

    if (context.filename) {

        return { ...context, filename: context.filename, manager: resolvedManager };

    }

    const details = document.getElementById('details-' + pathId)
        || document.getElementById('errors-' + pathId)
        || document.getElementById('quota-' + pathId);

    const filename = details?.querySelector('[data-filename]')?.getAttribute('data-filename') || '';

    return { filename, manager };

}

function buildCredentialContentHtml(filename, content) {

    const rows = renderMessageResultRows([
        [t('table_filename'), filename],
        content?.user_email || content?.email ? ['Email', content.user_email || content.email] : null,
        content?.project_id ? ['Project ID', content.project_id] : null,
        content?.expiry ? ['Expiry', content.expiry] : null,
    ].filter(Boolean));
    const body = JSON.stringify(content, null, 2);

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">This is the stored payload for the selected credential.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Credential Summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Credential Payload</div>
                <pre class="message-modal-code">${escapeHtml(body)}</pre>
            </div>
        </div>
    `;

}

function buildCredentialModelsHtml(context) {

    const modelIds = Array.isArray(context.modelIds) ? context.modelIds : [];
    const rows = renderMessageResultRows([
        ['Provider', context.providerName || t('provider_google_ai_studio')],
        ['Available models', modelIds.length],
    ]);
    const modelButtons = modelIds.map((modelId) => `
        <button type="button" class="credential-model-item" data-credential-model="${escapeAttribute(modelId)}" title="Copy model ID">
            ${escapeHtml(modelId)}
        </button>
    `).join('');

    return `
        <div class="message-result-panel credential-model-panel">
            <div class="message-result-intro">These models are currently reported as available for this credential.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Credential Summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Model IDs</div>
                <input type="search" class="credential-model-search" placeholder="Filter models" aria-label="Filter available models" autocomplete="off">
                <div class="credential-model-list">${modelButtons}</div>
                <div class="modal-empty-state credential-model-empty hidden">No models match this filter.</div>
            </div>
        </div>
    `;

}

async function showCredentialModels(pathId) {

    showStatus('Loading available models...', 'info');

    try {
        const context = await loadCredentialModelOptions(pathId);
        const modelIds = context.modelIds;
        if (modelIds.length === 0) {
            showMessageModal('Available Models', 'No model information is available for this credential.', 'info');
            return;
        }

        const modal = showMessageModal(
            'Available Models',
            buildCredentialModelsHtml({ ...context, modelIds }),
            'info',
            { html: true }
        );
        const search = modal.querySelector('.credential-model-search');
        const items = Array.from(modal.querySelectorAll('[data-credential-model]'));
        const emptyState = modal.querySelector('.credential-model-empty');

        items.forEach((item) => {
            item.addEventListener('click', () => {
                copyTextWithStatus(item.getAttribute('data-credential-model'));
            });
        });

        search?.addEventListener('input', () => {
            const query = search.value.trim().toLowerCase();
            let visibleCount = 0;
            items.forEach((item) => {
                const visible = item.textContent.toLowerCase().includes(query);
                item.hidden = !visible;
                if (visible) visibleCount += 1;
            });
            if (emptyState) emptyState.classList.toggle('hidden', visibleCount > 0);
        });

    } catch (error) {
        const message = error.message || 'Unable to load available models.';
        showStatus(message, 'error');
        showMessageModal('Available Models', message, 'error');
    }

}

async function loadCredentialModelOptions(pathId) {

    const context = getCredentialModalContext(pathId, AppState.primaryCreds);
    const { filename, manager } = context;
    if (!filename || !manager) throw new Error('Credential information is unavailable.');

    const response = await fetch(
        `${manager.getEndpoint('models')}/${encodeURIComponent(filename)}?${manager.getModeParam()}`,
        { headers: getAuthHeaders() }
    );
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.detail || data.error || 'Unable to load available models.');
    }

    return {
        ...context,
        modelIds: Array.isArray(data.model_ids) ? data.model_ids : [],
    };

}

async function showCredentialModelTest(pathId) {

    showStatus('Loading available models...', 'info');

    try {
        const context = await loadCredentialModelOptions(pathId);
        if (context.modelIds.length === 0) {
            showMessageModal(
                'Model Test',
                'No models are currently available for this credential.',
                'info'
            );
            return;
        }

        const account = context.accountLabel ? ` for ${context.accountLabel}` : '';
        await showModelTestModal(
            `Select a model to test with the ${context.providerName} credential${account}. The test sends a minimal generation request to the provider.`,
            {
                title: 'Test Model',
                label: 'Model',
                placeholder: 'Select a model',
                confirmLabel: 'Test',
                options: context.modelIds.map((modelId) => ({ value: modelId, label: modelId })),
                onTest: async (model) => {
                    if (context.manager.type === 'primary') {
                        return testPrimaryCredential(context.filename, model);
                    }
                    return testCredential(context.filename, model);
                },
            }
        );
    } catch (error) {
        const message = error.message || 'Unable to load available models.';
        showStatus(message, 'error');
        showMessageModal('Model Test', message, 'error');
    }

}

function quotaLevelFromUsedPercentage(usedPercentage) {

    if (usedPercentage >= 90) return 'danger';
    if (usedPercentage >= 70) return 'warning';
    if (usedPercentage >= 50) return 'info';
    return 'success';

}

function buildCredentialQuotaHtml(filename, data, context = {}) {

    const models = data.models || {};
    const entries = Object.entries(models);
    const summary = summarizeCredentialQuota(data);
    const resetTimes = entries
        .map(([, quotaData]) => quotaData?.resetTime)
        .filter(Boolean);
    const nextReset = resetTimes.length ? resetTimes.sort()[0] : '';
    const rows = renderMessageResultRows([
        ['Provider', context.providerName || t('provider_antigravity')],
        context.email ? ['Account', context.email] : ['Credential', filename],
        ['Tracked models', entries.length],
        summary.label ? ['Average remaining quota', summary.label] : null,
        nextReset ? ['Next reset', nextReset] : null,
    ].filter(Boolean));

    if (entries.length === 0) {

        return `
            <div class="message-result-panel">
                <div class="message-result-intro">No quota information is available for this credential yet.</div>
                <div class="message-result-section">
                    <div class="message-result-section-title">Quota Summary</div>
                    <div class="message-result-summary">${rows}</div>
                </div>
                <div class="modal-empty-state">${escapeHtml(t('status_no_quota_info'))}</div>
            </div>
        `;

    }

    const cards = entries.map(([modelName, quotaData]) => {

        const remainingFraction = Number(quotaData.remaining || 0);
        const resetTime = quotaData.resetTime || 'N/A';
        const usedPercentage = Math.max(0, Math.min(100, Math.round((1 - remainingFraction) * 100)));
        const remainingPercentage = Math.max(0, Math.min(100, Math.round(remainingFraction * 100)));
        const level = quotaLevelFromUsedPercentage(usedPercentage);

        return `
            <div class="modal-quota-card ${level}">
                <div class="modal-quota-head">
                    <div class="modal-quota-model" title="${escapeAttribute(modelName)}">${escapeHtml(modelName)}</div>
                    <div class="modal-quota-percent">${remainingPercentage}% left</div>
                </div>
                <div class="modal-quota-bar">
                    <div class="modal-quota-bar-value" style="width: ${remainingPercentage}%;"></div>
                </div>
                <div class="modal-quota-foot">
                    <span>Used ${usedPercentage}%</span>
                    <span>${resetTime !== 'N/A' ? `Reset ${escapeHtml(resetTime)}` : 'Reset time unavailable'}</span>
                </div>
            </div>
        `;

    }).join('');

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">Quota usage is grouped by model for the selected credential.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Quota Summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Model Quota</div>
                <div class="modal-quota-grid">${cards}</div>
            </div>
        </div>
    `;

}

function summarizeCredentialQuota(data) {

    const models = data?.models || {};
    const entries = Object.entries(models);

    if (!entries.length) {

        return {
            level: 'muted',
            label: 'No quota',
        };

    }

    let remainingTotal = 0;

    entries.forEach(([, quotaData]) => {

        const remainingFraction = Number(quotaData?.remaining || 0);
        const remainingPercentage = Math.max(0, Math.min(100, Math.round(remainingFraction * 100)));

        remainingTotal += remainingPercentage;

    });

    const averageRemaining = Math.round(remainingTotal / entries.length);
    const usedPercentage = 100 - averageRemaining;
    const level = quotaLevelFromUsedPercentage(usedPercentage);

    return {
        level,
        label: `${averageRemaining}% left`,
        modelCount: entries.length,
    };

}

function renderCredentialQuotaPreview(pathId, filename, managerType) {

    if (managerType !== 'primary') return '';

    const cached = AppState.quotaPreviewCache[filename] || {};
    const chipState = cached.loading
        ? { level: 'loading', label: t('quota_preview_loading'), title: t('card_loading_quota') }
        : cached.error
            ? { level: 'danger', label: t('quota_unavailable'), title: cached.error }
            : cached.summary
                ? {
                    level: cached.summary.level,
                    label: cached.summary.label,
                    title: cached.summary.modelCount
                        ? `Average quota: ${cached.summary.label} across ${cached.summary.modelCount} model${cached.summary.modelCount === 1 ? '' : 's'}`
                        : t('btn_view_quota_title'),
                }
                : { level: 'loading', label: t('quota_preview_loading'), title: t('card_loading_quota') };

    return `
        <button type="button" class="cred-quota-preview ${chipState.level}" id="quota-preview-${pathId}" data-quota-preview title="${escapeAttribute(chipState.title)}">
            <span>${escapeHtml(chipState.label)}</span>
        </button>
    `;

}

function updateCredentialQuotaPreview(pathId, filename) {

    const chip = document.getElementById(`quota-preview-${pathId}`);

    if (!chip) return;

    chip.outerHTML = renderCredentialQuotaPreview(pathId, filename, 'primary');
    const updatedChip = document.getElementById(`quota-preview-${pathId}`);
    if (updatedChip) {
        updatedChip.addEventListener('click', () => loadPrimaryQuotaPreview(pathId));
    }

}

function renderCredentialErrorDetails(parsedMsg) {

    const error = parsedMsg?.error;
    if (!error) return '';

    const rows = [];

    if (error.status) rows.push(['Status', error.status]);

    if (Array.isArray(error.details)) {

        error.details.forEach((detail, index) => {

            if (detail['@type']) rows.push([`Type ${index + 1}`, detail['@type']]);
            if (detail.reason) rows.push([`Reason ${index + 1}`, detail.reason]);

            if (detail.metadata && typeof detail.metadata === 'object') {

                Object.entries(detail.metadata).forEach(([key, value]) => {
                    rows.push([key, String(value)]);
                });

            }

        });

    }

    if (!rows.length) return '';

    return `<div class="message-error-meta">${renderMessageResultRows(rows)}</div>`;

}

function buildCredentialErrorsHtml(filename, data) {

    const errorCodes = data.error_codes || [];
    const errorMessages = data.error_messages || {};
    const rows = renderMessageResultRows([
        [t('table_filename'), filename],
        ['Stored errors', errorCodes.length],
    ]);

    if (errorCodes.length === 0) {

        return `
            <div class="message-result-panel">
                <div class="message-result-intro">This credential has no stored provider errors.</div>
                <div class="message-result-section">
                    <div class="message-result-section-title">Error Summary</div>
                    <div class="message-result-summary">${rows}</div>
                </div>
                <div class="modal-empty-state success">
                    <strong>${escapeHtml(t('status_no_errors'))}</strong>
                    <span>${escapeHtml(t('status_credential_normal'))}</span>
                </div>
            </div>
        `;

    }

    const errorCards = errorCodes.map((errorCode) => {

        const messageStr = errorMessages[errorCode] || t('no_details_available');
        let displayMsg = messageStr;
        let detailsHtml = '';

        try {

            const parsedMsg = JSON.parse(messageStr);

            if (parsedMsg?.error?.message) displayMsg = parsedMsg.error.message;

            detailsHtml = renderCredentialErrorDetails(parsedMsg);

        } catch {

            detailsHtml = '';

        }

        return `
            <div class="message-error-card">
                <div class="message-error-title">${escapeHtml(t('error_code_prefix'))} ${escapeHtml(String(errorCode))}</div>
                <div class="message-error-copy">${highlightHttpLinks(escapeHtml(displayMsg))}</div>
                ${detailsHtml}
            </div>
        `;

    }).join('');

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">These are the latest provider errors recorded for this credential.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Error Summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Error Details</div>
                <div class="message-error-list">${errorCards}</div>
            </div>
        </div>
    `;

}

function showConfirmModal(message, options = {}) {

    if (!options.title || !options.confirmLabel) {

        throw new Error('Confirmation modals require a contextual title and confirmation label.');

    }

    return new Promise((resolve) => {

        const modal = document.createElement('div');

        modal.className = 'message-modal-overlay';

        const title = options.title;

        const confirmLabel = options.confirmLabel;

        const cancelLabel = options.cancelLabel || t('btn_cancel');

        modal.innerHTML = `

            <div class="message-modal confirm" role="dialog" aria-modal="true" aria-label="${escapeAttribute(title)}">

                <div class="message-modal-header">

                    <h3>${escapeHtml(title)}</h3>

                </div>

                <div class="message-modal-body">

                    ${renderDialogMessage(message, { compact: true })}

                </div>

                <div class="message-modal-footer">

                    <button type="button" class="message-modal-btn" data-dialog-cancel>${escapeHtml(cancelLabel)}</button>

                    <button type="button" class="message-modal-btn message-modal-btn-primary" data-dialog-confirm>${escapeHtml(confirmLabel)}</button>

                </div>

            </div>

        `;

        let settled = false;

        const close = (value) => {

            if (settled) return;

            settled = true;

            document.removeEventListener('keydown', escHandler);

            modal.remove();

            resolve(value);

        };

        const escHandler = (event) => {

            if (event.key === 'Escape') close(false);

        };

        modal.addEventListener('click', (event) => {

            if (event.target === modal || event.target.closest('[data-dialog-cancel]')) close(false);

            if (event.target.closest('[data-dialog-confirm]')) close(true);

        });

        document.addEventListener('keydown', escHandler);

        document.body.appendChild(modal);

        modal.querySelector('[data-dialog-confirm]')?.focus();

    });

}

function showPromptModal(message, options = {}) {

    return new Promise((resolve) => {

        const modal = document.createElement('div');

        modal.className = 'message-modal-overlay';

        const title = options.title || t('input_required_title');

        const confirmLabel = options.confirmLabel || t('btn_continue');

        const cancelLabel = options.cancelLabel || t('btn_cancel');

        const initialValue = options.value || '';

        const placeholder = options.placeholder || '';

        modal.innerHTML = `

            <div class="message-modal prompt" role="dialog" aria-modal="true" aria-label="${escapeAttribute(title)}">

                <div class="message-modal-header">

                    <h3>${escapeHtml(title)}</h3>

                </div>

                <div class="message-modal-body">

                    <div class="message-modal-prompt-copy">${renderDialogMessage(message)}</div>

                    <input type="text" class="message-modal-input">

                </div>

                <div class="message-modal-footer">

                    <button type="button" class="message-modal-btn" data-dialog-cancel>${escapeHtml(cancelLabel)}</button>

                    <button type="button" class="message-modal-btn message-modal-btn-primary" data-dialog-confirm>${escapeHtml(confirmLabel)}</button>

                </div>

            </div>

        `;

        let settled = false;

        const input = () => modal.querySelector('.message-modal-input');

        const close = (value) => {

            if (settled) return;

            settled = true;

            document.removeEventListener('keydown', escHandler);

            modal.remove();

            resolve(value);

        };

        const escHandler = (event) => {

            if (event.key === 'Escape') close(null);

        };

        modal.addEventListener('click', (event) => {

            if (event.target === modal || event.target.closest('[data-dialog-cancel]')) close(null);

            if (event.target.closest('[data-dialog-confirm]')) close(input()?.value || '');

        });

        modal.addEventListener('keydown', (event) => {

            if (event.key === 'Enter' && event.target === input()) close(input()?.value || '');

        });

        document.addEventListener('keydown', escHandler);

        document.body.appendChild(modal);

        const inputEl = input();

        if (inputEl) {

            inputEl.value = initialValue;

            inputEl.placeholder = placeholder;

            inputEl.focus();

        }

    });

}

function showModelTestModal(message, options = {}) {

    return new Promise((resolve) => {

        const modal = document.createElement('div');
        modal.className = 'message-modal-overlay';

        const title = options.title || 'Test Model';
        const confirmLabel = options.confirmLabel || 'Test';
        const cancelLabel = options.cancelLabel || t('btn_cancel');
        const label = options.label || 'Model';
        const placeholder = options.placeholder || 'Select a model';
        const choices = Array.isArray(options.options) ? options.options : [];
        const optionHtml = choices.map((choice) => `
            <option value="${escapeAttribute(choice.value)}">${escapeHtml(choice.label)}</option>
        `).join('');
        const selectionHtml = `
            <div class="message-modal-prompt-copy">${renderDialogMessage(message)}</div>
            <label class="message-modal-field">
                <span class="message-modal-field-label">${escapeHtml(label)}</span>
                <select class="message-modal-input" data-dialog-select>
                    <option value="" selected disabled>${escapeHtml(placeholder)}</option>
                    ${optionHtml}
                </select>
            </label>
            <div class="model-test-progress hidden" data-model-test-progress role="status" aria-live="polite"></div>
        `;

        modal.innerHTML = `
            <div class="message-modal prompt model-test-modal" role="dialog" aria-modal="true" aria-label="${escapeAttribute(title)}">
                <div class="message-modal-header">
                    <h3>${escapeHtml(title)}</h3>
                </div>
                <div class="message-modal-body"></div>
                <div class="message-modal-footer"></div>
            </div>
        `;

        const dialog = modal.querySelector('.message-modal');
        const body = modal.querySelector('.message-modal-body');
        const footer = modal.querySelector('.message-modal-footer');
        let settled = false;
        let running = false;

        const close = () => {
            if (settled) return;
            settled = true;
            document.removeEventListener('keydown', escHandler);
            modal.remove();
            resolve();
        };

        const renderSelection = () => {
            running = false;
            dialog.className = 'message-modal prompt model-test-modal';
            body.removeAttribute('aria-busy');
            body.innerHTML = selectionHtml;
            footer.innerHTML = `
                <button type="button" class="message-modal-btn" data-dialog-cancel>${escapeHtml(cancelLabel)}</button>
                <button type="button" class="message-modal-btn message-modal-btn-primary" data-dialog-confirm disabled>${escapeHtml(confirmLabel)}</button>
            `;

            const select = body.querySelector('[data-dialog-select]');
            const confirm = footer.querySelector('[data-dialog-confirm]');
            select?.addEventListener('change', () => {
                if (confirm) confirm.disabled = !select.value;
            });
        };

        const renderResult = (result) => {
            const safeType = String(result?.type || 'info').replace(/[^\w-]/g, '') || 'info';
            running = false;
            dialog.className = `message-modal informational model-test-modal ${safeType}`;
            body.removeAttribute('aria-busy');
            body.innerHTML = String(result?.html || '');
            footer.innerHTML = `
                <button type="button" class="message-modal-btn" data-dialog-close>${escapeHtml(t('btn_close'))}</button>
                <button type="button" class="message-modal-btn message-modal-btn-primary" data-dialog-retry>${escapeHtml(t('btn_test_another_model'))}</button>
            `;
        };

        const runTest = async () => {
            if (running) return;

            const select = body.querySelector('[data-dialog-select]');
            const confirm = footer.querySelector('[data-dialog-confirm]');
            const progress = body.querySelector('[data-model-test-progress]');
            const model = select?.value || '';
            if (!model || typeof options.onTest !== 'function') return;

            running = true;
            body.setAttribute('aria-busy', 'true');
            select.disabled = true;
            if (confirm) {
                confirm.disabled = true;
                confirm.textContent = t('testing_short');
            }
            if (progress) {
                progress.textContent = t('testing_selected_model', {model});
                progress.classList.remove('hidden');
            }

            try {
                const result = await options.onTest(model);
                if (!settled) renderResult(result);
            } catch (error) {
                if (settled) return;
                const errorMessage = error?.message || 'The selected model test could not be completed.';
                renderResult({
                    type: 'error',
                    html: buildApiResultHtml({
                        intro: 'The selected model test could not be completed.',
                        rows: [
                            ['Result', 'Failed'],
                            ['Model', model],
                        ],
                        summaryLabel: 'Failure summary',
                        note: errorMessage,
                    }),
                });
            }
        };

        const escHandler = (event) => {
            if (event.key === 'Escape') close();
        };

        modal.addEventListener('click', (event) => {
            if (event.target === modal || event.target.closest('[data-dialog-cancel], [data-dialog-close]')) {
                close();
                return;
            }
            if (event.target.closest('[data-dialog-retry]')) {
                renderSelection();
                return;
            }
            if (event.target.closest('[data-dialog-confirm]')) runTest();
        });

        document.addEventListener('keydown', escHandler);
        document.body.appendChild(modal);
        renderSelection();

    });

}

function getAuthHeaders() {

    return {

        'Content-Type': 'application/json'

    };

}

function formatFileSize(bytes) {

    if (bytes < 1024) return bytes + ' B';

    if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';

    return Math.round(bytes / (1024 * 1024)) + ' MB';

}

function formatCooldownTime(remainingSeconds) {

    const hours = Math.floor(remainingSeconds / 3600);

    const minutes = Math.floor((remainingSeconds % 3600) / 60);

    const seconds = remainingSeconds % 60;

    if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;

    if (minutes > 0) return `${minutes}m ${seconds}s`;

    return `${seconds}s`;

}

// =====================================================================

// =====================================================================

function getCredentialProviderMeta(credInfo, managerType) {

    const provider = String(credInfo.provider || credInfo.provider_name || '')
        .trim()
        .toLowerCase()
        .replace(/[\s-]+/g, '_');

    if (provider === 'google_ai_studio' || provider === 'ai_studio' || provider === 'aistudio' || provider === 'gemini') {

        return {
            id: 'google_ai_studio',
            name: t('provider_google_ai_studio'),
            logo: '/frontend/assets/providers/google-ai-studio-logo.png'
        };

    }

    if (provider === 'google_antigravity' || provider === 'antigravity' || provider === 'primary' || provider === 'provider' || (!provider && managerType === 'primary')) {

        return {
            id: 'google_antigravity',
            name: t('provider_antigravity'),
            logo: '/frontend/assets/providers/google-antigravity-logo.png'
        };

    }

    if (provider === 'xai' || provider === 'grok' || provider === 'xai_grok' || provider === 'xai_console' || provider === 'xai_oauth' || provider === 'xai_api_key') {

        const credentialType = String(credInfo.credential_type || '').trim().toLowerCase();
        const isGrok = provider === 'grok' || provider === 'xai_oauth' || credentialType === 'oauth';
        const isXaiConsole = provider === 'xai_console' || provider === 'xai_api_key' || credentialType === 'api_key';

        if (isGrok) {
            return {
                id: 'grok',
                name: 'Grok',
                logo: '/frontend/assets/providers/xai-grok-logo.png'
            };
        }

        if (isXaiConsole) {
            return {
                id: 'xai_console',
                name: 'xAI Console',
                logo: '/frontend/assets/providers/xai-console-logo.png'
            };
        }

        return {
            id: 'xai',
            name: 'xAI',
            logo: '/frontend/assets/providers/xai-console-logo.png'
        };

    }

    return {
        id: 'code_assist',
        name: t('provider_code_assist'),
        logo: ''
    };

}

function createCredentialProviderGroup(providerMeta, credentials, manager) {

    const section = document.createElement('section');

    section.className = 'credential-provider-group';

    section.setAttribute('aria-labelledby', `credentialProviderGroup-${providerMeta.id}`);

    const logo = providerMeta.logo

        ? `<img src="${escapeAttribute(providerMeta.logo)}" alt="">`

        : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

    const countLabel = `${credentials.length} credential${credentials.length === 1 ? '' : 's'}`;

    section.innerHTML = `

        <div class="credential-provider-group-header">

            <div class="credential-provider-group-logo" aria-hidden="true">${logo}</div>

            <h2 class="credential-provider-group-title" id="credentialProviderGroup-${escapeAttribute(providerMeta.id)}">${escapeHtml(providerMeta.name)}</h2>

            <span class="credential-provider-group-count">${countLabel}</span>

        </div>

        <div class="credential-provider-grid"></div>

    `;

    const grid = section.querySelector('.credential-provider-grid');

    credentials.forEach((credInfo) => {

        grid.appendChild(createCredCard(credInfo, manager));

    });

    return section;

}

function createCredCard(credInfo, manager) {

    const div = document.createElement('div');

    const { status, filename } = credInfo;

    const managerType = manager.type;
    const providerMeta = getCredentialProviderMeta(credInfo, managerType);
    const isGoogleAIStudio = providerMeta.id === 'google_ai_studio';
    const isXai = ['xai', 'grok', 'xai_console'].includes(providerMeta.id);
    const isAntigravity = providerMeta.id === 'google_antigravity';
    const isStaticProvider = isGoogleAIStudio || isXai;
    const accountLabel = credInfo.credential_label || credInfo.user_email || t('email_not_fetched');
    const accountClass = (credInfo.credential_label || credInfo.user_email) ? 'cred-email' : 'cred-email empty';
    const providerLogo = providerMeta.logo
        ? `<img src="${escapeAttribute(providerMeta.logo)}" alt="${escapeAttribute(providerMeta.name)} logo">`
        : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

    div.className = status.disabled ? 'cred-card disabled' : 'cred-card';

    let statusBadges = '';

    statusBadges += status.disabled

        ? `<span class="status-badge disabled">${t('status_disabled')}</span>`

        : `<span class="status-badge enabled">${t('status_enabled')}</span>`;

    if (status.error_codes && status.error_codes.length > 0) {

        statusBadges += `<span class="error-codes">${t('error_code_prefix')} ${escapeHtml(status.error_codes.join(', '))}</span>`;

        const autoBan = status.error_codes.filter(c => c === 400 || c === 403);

        if (autoBan.length > 0 && status.disabled) {

            statusBadges += '<span class="status-badge danger">Auto-disabled</span>';

        }

    } else {

        statusBadges += `<span class="status-badge success">${t('status_no_errors')}</span>`;

    }

    if (managerType !== 'primary' && credInfo.preview !== undefined) {

        if (credInfo.preview) {

            statusBadges += `<span class="status-badge success" title="${t('preview_supported_title')}">Preview: ON</span>`;

        } else {

            statusBadges += `<span class="status-badge muted" title="${t('preview_not_supported_title')}">Preview: OFF</span>`;

        }

    }

    if (isGoogleAIStudio || isXai) {

        const credentialType = credInfo.credential_type === 'oauth' ? 'OAuth' : 'API key';
        statusBadges += `<span class="status-badge muted" title="${escapeAttribute(`${providerMeta.name} ${credentialType} credential`)}">${credentialType}</span>`;

    } else {

        const tier = (credInfo.tier || 'pro').toString().toLowerCase();

        const tierLabel = tier.toUpperCase();

        const tierClass = tier === 'ultra' ? 'tier-ultra' : (tier === 'free' ? 'tier-free' : 'tier-pro');

        statusBadges += `<span class="status-badge ${tierClass}" title="${escapeAttribute(`${t('tier_badge_title')}: ${tierLabel}`)}">Tier: ${escapeHtml(tierLabel)}</span>`;

    }

    if (managerType === 'primary' && isAntigravity) {

        if (credInfo.enable_credit) {

            statusBadges += `<span class="status-badge credit-on" title="${t('credit_enabled_title')}">Credits: ON</span>`;

        } else {

            statusBadges += `<span class="status-badge credit-off" title="${t('credit_disabled_title')}">Credits: OFF</span>`;

        }

    }

    if (credInfo.model_cooldowns && Object.keys(credInfo.model_cooldowns).length > 0) {

        const currentTime = Date.now() / 1000;

        const activeCooldowns = Object.entries(credInfo.model_cooldowns)

            .filter(([, until]) => until > currentTime)

            .map(([model, until]) => {

                const remaining = Math.max(0, Math.floor(until - currentTime));

                const shortModel = model.replace('gemini-', '').replace('-exp', '')

                    .replace('2.0-', '2-').replace('1.5-', '1.5-');

                return {

                    model: shortModel,

                    time: formatCooldownTime(remaining).replace(/s$/, '').replace(/ /g, ''),

                    fullModel: model

                };

            });

        if (activeCooldowns.length > 0) {

            activeCooldowns.slice(0, 2).forEach(item => {

                statusBadges += `<span class="cooldown-badge" title="${escapeAttribute(`${t('model_title')}: ${item.fullModel}`)}">Cooldown ${escapeHtml(item.model)}: ${escapeHtml(item.time)}</span>`;

            });

            if (activeCooldowns.length > 2) {

                const remaining = activeCooldowns.length - 2;

                const remainingModels = activeCooldowns.slice(2).map(i => `${i.fullModel}: ${i.time}`).join('\n');

                statusBadges += `<span class="cooldown-badge" title="${escapeAttribute(`${t('other_models_title')}: ${remainingModels}`)}">+${remaining}</span>`;

            }

        }

    }

    const pathId = (managerType === 'primary' ? 'primary_' : '') + btoa(encodeURIComponent(filename)).replace(/[+/=]/g, '_');

    AppState.credentialCardIndex[pathId] = {
        filename,
        managerType,
        email: credInfo.user_email || '',
        accountLabel: credInfo.user_email || credInfo.credential_label || '',
        providerName: providerMeta.name,
        modelCount: Number.isFinite(Number(credInfo.model_count)) ? Number(credInfo.model_count) : 0,
    };

    const shouldAutoLoadQuota = managerType === 'primary' && isAntigravity && !AppState.quotaPreviewCache[filename];

    if (shouldAutoLoadQuota) {

        AppState.quotaPreviewCache[filename] = { loading: true };

    }

    const actionButtons = `

        ${status.disabled

            ? `<button type="button" class="cred-btn enable" data-credential-command="enable">${t('action_enable')}</button>`

            : `<button type="button" class="cred-btn disable" data-credential-command="disable">${t('action_disable')}</button>`

        }

        <button type="button" class="cred-btn view" data-credential-command="view" title="${escapeAttribute(t('btn_view_content_title'))}">${t('btn_view_content')}</button>

        <button type="button" class="cred-btn download" data-credential-command="download">${t('btn_download')}</button>

        ${isStaticProvider && Number(credInfo.model_count) > 0 ? `<button type="button" class="cred-btn" data-credential-command="models" title="${escapeAttribute(t('btn_view_models_title'))}">${t('btn_view_models')}</button>` : ''}

        ${managerType === 'primary' && isAntigravity ? `<button type="button" class="cred-btn" data-credential-command="quota" title="${escapeAttribute(t('btn_view_quota_title'))}">${t('btn_view_quota')}</button>` : ''}

        ${managerType === 'primary' && isAntigravity ? (credInfo.enable_credit

            ? `<button type="button" class="cred-btn" data-credential-command="disable_credit" title="${escapeAttribute(t('btn_disable_credit_title'))}">${t('btn_disable_credit')}</button>`

            : `<button type="button" class="cred-btn" data-credential-command="enable_credit" title="${escapeAttribute(t('btn_enable_credit_title'))}">${t('btn_enable_credit')}</button>`

        ) : ''}

        ${managerType !== 'primary' ? `<button type="button" class="cred-btn" data-credential-command="preview" title="${escapeAttribute(t('btn_setup_preview_title'))}">${t('btn_setup_preview')}</button>` : ''}

        <button type="button" class="cred-btn" data-credential-command="verify" title="${escapeAttribute(t('btn_verify_id_title'))}">${t('btn_verify_id')}</button>

        <button type="button" class="cred-btn" data-credential-command="test" title="${escapeAttribute(t('btn_test_model_title'))}">${t('btn_test_model')}</button>

        <button type="button" class="cred-btn" data-credential-command="errors" title="${escapeAttribute(t('btn_view_errors_title'))}">${t('btn_view_errors')}</button>

        <button type="button" class="cred-btn delete" data-credential-command="delete">${t('action_delete')}</button>

    `;

    const checkboxClass = manager.getElementId('file-checkbox');
    const quotaPreview = isAntigravity ? renderCredentialQuotaPreview(pathId, filename, managerType) : '';

    div.innerHTML = `

        <div class="cred-header">

            <div class="cred-title-row">

                <input type="checkbox" class="${escapeAttribute(checkboxClass)}" data-filename="${escapeAttribute(filename)}" data-credential-select aria-label="${escapeAttribute(`Select ${providerMeta.name} credential for ${accountLabel}`)}">

                <div class="cred-identity" title="${escapeAttribute(filename)}">
                    <div class="cred-provider-logo" aria-hidden="true">${providerLogo}</div>
                    <div class="cred-identity-copy">
                        <div class="cred-provider-name">${escapeHtml(providerMeta.name)}</div>
                        <div class="${accountClass}">${escapeHtml(accountLabel)}</div>
                    </div>
                </div>

                ${quotaPreview}

            </div>

            <div class="cred-status">${statusBadges}</div>

        </div>

        <div class="cred-actions">${actionButtons}</div>

    `;

    const selectionCheckbox = div.querySelector('[data-credential-select]');
    if (selectionCheckbox) {
        selectionCheckbox.addEventListener('change', () => {
            if (managerType === 'primary') togglePrimaryFileSelection(filename);
            else toggleFileSelection(filename);
        });
    }

    const quotaPreviewButton = div.querySelector('[data-quota-preview]');
    if (quotaPreviewButton) {
        quotaPreviewButton.addEventListener('click', () => loadPrimaryQuotaPreview(pathId));
    }

    div.querySelectorAll('[data-credential-command]').forEach(button => {

        button.addEventListener('click', async function () {

            const command = this.getAttribute('data-credential-command');

            if (command === 'delete') {

                if (!(await showConfirmModal(t('confirm_delete_cred'), {

                    title: t('confirm_delete_cred_title'),

                    confirmLabel: t('action_delete')

                }))) return;

            }

            if (['enable', 'disable', 'delete', 'enable_credit', 'disable_credit'].includes(command)) {
                await manager.action(filename, command);
                return;
            }

            if (command === 'view') await toggleCredDetailsCommon(pathId, manager);
            if (command === 'download') {
                if (managerType === 'primary') downloadPrimaryCred(filename);
                else downloadCred(filename);
            }
            if (command === 'quota') await togglePrimaryQuotaDetails(pathId);
            if (command === 'models') await showCredentialModels(pathId);
            if (command === 'preview') await configurePreviewChannel(filename);
            if (command === 'verify') {
                if (managerType === 'primary') await verifyProviderCredential(filename);
                else await verifyCredential(filename);
            }
            if (command === 'test') {
                await showCredentialModelTest(pathId);
            }
            if (command === 'errors') await toggleErrorDetailsCommon(pathId, manager);


        });

    });

    if (shouldAutoLoadQuota) {

        setTimeout(() => loadPrimaryQuotaPreview(pathId), 0);

    }

    return div;

}

// =====================================================================

// =====================================================================

async function toggleCredDetails(pathId) {

    await toggleCredDetailsCommon(pathId, AppState.creds);

}

async function togglePrimaryCredDetails(pathId) {

    await toggleCredDetailsCommon(pathId, AppState.primaryCreds);

}

async function toggleCredDetailsCommon(pathId, manager) {

    const { filename, manager: resolvedManager } = getCredentialModalContext(pathId, manager);

    if (!filename) return;

    showStatus(t('status_loading_file_content'), 'info');

    try {

        const modeParam = resolvedManager.type === 'primary' ? 'mode=provider' : 'mode=code_assist';

        const endpoint = `./api/credentials/detail/${encodeURIComponent(filename)}?${modeParam}`;

        const response = await fetch(endpoint, { headers: getAuthHeaders() });

        const data = await response.json();

        if (response.ok && data.content) {

            showMessageModal('Credential Details', buildCredentialContentHtml(filename, data.content), 'info', {html: true});

        } else {

            const errorMsg = data.error || data.detail || t('unknown_error');

            showStatus(`${t('unable_to_load_file_content')} ${errorMsg}`, 'error');

            showMessageModal('Credential Details', `${t('unable_to_load_file_content')} ${errorMsg}`, 'error');

        }

    } catch (error) {

        const errorMsg = `${t('unable_to_load_file_content')} ${error.message}`;

        showStatus(errorMsg, 'error');

        showMessageModal('Credential Details', errorMsg, 'error');

    }

}

// =====================================================================

// =====================================================================
