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

function formatQuotaNumber(value) {

    const number = Number(value);
    return Number.isFinite(number) ? number.toLocaleString('en-US') : 'Unavailable';

}

function formatQuotaResetTime(value) {

    const date = new Date(value || '');
    if (!Number.isFinite(date.getTime())) return 'Reset time unavailable';
    return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });

}

function buildAccountBillingQuotaHtml(filename, data, context = {}) {

    const periods = [
        data.monthly ? { id: 'monthly', label: 'Monthly Credits', ...data.monthly } : null,
        data.weekly ? { id: 'weekly', label: 'Weekly Usage', ...data.weekly } : null,
    ].filter(Boolean);
    const remainingPercentages = periods
        .map((period) => Number(period.remaining_percentage))
        .filter(Number.isFinite);
    const lowestRemaining = remainingPercentages.length ? Math.min(...remainingPercentages) : null;
    const rows = renderMessageResultRows([
        ['Provider', context.providerName || t('provider_grok')],
        context.accountLabel ? ['Account', context.accountLabel] : ['Credential', filename],
        ['Quota source', 'Grok Build account billing'],
        ['Billing periods', periods.length],
        lowestRemaining !== null ? ['Lowest remaining quota', `${lowestRemaining}%`] : null,
    ].filter(Boolean));

    const cards = periods.map((period) => {
        const usedPercentage = Math.max(0, Math.min(100, Number(period.used_percentage) || 0));
        const remainingPercentage = Math.max(0, Math.min(100, Number(period.remaining_percentage) || 0));
        const level = quotaLevelFromUsedPercentage(usedPercentage);
        const usageText = period.id === 'monthly'
            ? `${formatQuotaNumber(period.used)} / ${formatQuotaNumber(period.limit)} credits used`
            : `${usedPercentage}% used`;

        return `
            <div class="modal-quota-card ${level}">
                <div class="modal-quota-head">
                    <div class="modal-quota-model">${escapeHtml(period.label)}</div>
                    <div class="modal-quota-percent">${remainingPercentage}% left</div>
                </div>
                <div class="modal-quota-bar">
                    <div class="modal-quota-bar-value" style="width: ${remainingPercentage}%;"></div>
                </div>
                <div class="modal-quota-foot">
                    <span>${escapeHtml(usageText)}</span>
                    <span>Resets ${escapeHtml(formatQuotaResetTime(period.reset_time))}</span>
                </div>
            </div>
        `;
    }).join('');

    return `
        <div class="message-result-panel">
            <div class="message-result-intro">Account quota reported by Grok Build for the selected OAuth credential.</div>
            <div class="message-result-section">
                <div class="message-result-section-title">Quota Summary</div>
                <div class="message-result-summary">${rows}</div>
            </div>
            <div class="message-result-section">
                <div class="message-result-section-title">Billing Periods</div>
                <div class="modal-quota-grid">${cards}</div>
            </div>
        </div>
    `;

}

function buildCredentialQuotaHtml(filename, data, context = {}) {

    if (data?.quota_type === 'account_billing') {
        return buildAccountBillingQuotaHtml(filename, data, context);
    }

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

    if (data?.quota_type === 'account_billing') {
        const periods = [data.monthly, data.weekly].filter(Boolean);
        const remainingValues = periods
            .map((period) => Number(period.remaining_percentage))
            .filter(Number.isFinite);
        if (!remainingValues.length) return { level: 'muted', label: 'No quota' };
        const remainingPercentage = Math.min(...remainingValues);
        return {
            level: quotaLevelFromUsedPercentage(100 - remainingPercentage),
            label: `${remainingPercentage}% left`,
            periodCount: periods.length,
        };
    }

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

function describeCredentialQuotaPreview(summary) {

    if (summary.modelCount) {
        const modelLabel = `model${summary.modelCount === 1 ? '' : 's'}`;
        return `Average quota: ${summary.label} across ${summary.modelCount} ${modelLabel}.`;
    }

    if (summary.periodCount > 1) {
        return `Lowest account quota: ${summary.label} across ${summary.periodCount} active billing periods.`;
    }

    if (summary.periodCount === 1) {
        return `Account quota: ${summary.label} for the active billing period.`;
    }

    return t('btn_view_quota_title');

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
                    title: describeCredentialQuotaPreview(cached.summary),
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
