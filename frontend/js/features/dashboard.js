// Omni Gateway management console: dashboard.

function formatUsageNumber(value, options = {}) {

    const number = Number(value || 0);

    if (!Number.isFinite(number)) return '0';

    return number.toLocaleString('en-US', {
        maximumFractionDigits: options.decimals ?? 0,
        minimumFractionDigits: options.decimals ?? 0,
    });

}

function getUsagePeriodConfig(period = AppState.usagePeriod) {

    const periods = {
        '1d': {
            value: '1d',
            optionLabel: '1 day',
            metricLabel: 'in the last 24 hours',
            title: '24-Hour Request Breakdown',
            description: 'Review provider and credential traffic for the last 24 hours.',
        },
        '7d': {
            value: '7d',
            optionLabel: '7 days',
            metricLabel: 'in the last 7 days',
            title: '7-Day Request Breakdown',
            description: 'Review provider and credential traffic for the last 7 days.',
        },
        '30d': {
            value: '30d',
            optionLabel: '30 days',
            metricLabel: 'in the last 30 days',
            title: '30-Day Request Breakdown',
            description: 'Review provider and credential traffic for the last 30 days.',
        },
        all: {
            value: 'all',
            optionLabel: 'All',
            metricLabel: 'across all recorded time',
            title: 'All-Time Request Breakdown',
            description: 'Review all recorded provider and credential traffic.',
        },
    };

    return periods[period] || periods['1d'];

}

function updateUsagePeriodLabels() {

    const periodConfig = getUsagePeriodConfig();

    const periodSelect = document.getElementById('usagePeriodSelect');

    if (periodSelect) periodSelect.value = periodConfig.value;

    const totalCallsLabel = document.getElementById('totalApiCallsLabel');

    if (totalCallsLabel) totalCallsLabel.textContent = `Requests ${periodConfig.metricLabel}`;

    const totalTokensLabel = document.getElementById('totalTokensLabel');

    if (totalTokensLabel) totalTokensLabel.textContent = `Tokens ${periodConfig.metricLabel}`;

    const breakdownTitle = document.getElementById('usageBreakdownTitle');

    if (breakdownTitle) breakdownTitle.textContent = periodConfig.title;

    const breakdownDescription = document.getElementById('usageBreakdownDescription');

    if (breakdownDescription) breakdownDescription.textContent = periodConfig.description;

}

function setUsagePeriod(period) {

    const nextPeriod = getUsagePeriodConfig(period).value;

    if (AppState.usagePeriod === nextPeriod) {

        updateUsagePeriodLabels();

        return;

    }

    AppState.usagePeriod = nextPeriod;

    updateUsagePeriodLabels();

    refreshUsageStats();

}

async function refreshUsageStats(options = {}) {

    const loading = document.getElementById('usageLoading');

    const list = document.getElementById('usageList');

    const providerSummary = document.getElementById('usageProviderSummary');

    const statsContainer = document.getElementById('dashboardStats');

    const tableWrapper = document.querySelector('#dashboardTab .usage-table-wrapper');

    const preserveContent = options.preserveContent ?? AppState.usageStatsLoaded;

    updateUsagePeriodLabels();

    try {

        if (loading && !preserveContent) loading.hidden = false;

        if (statsContainer && !preserveContent) statsContainer.setAttribute('aria-busy', 'true');

        if (tableWrapper && !preserveContent) tableWrapper.hidden = true;

        if (!preserveContent) list.innerHTML = '';

        if (providerSummary && !preserveContent) {

            providerSummary.innerHTML = '';
            providerSummary.hidden = true;

        }

        const usagePeriod = getUsagePeriodConfig().value;

        const usagePeriodQuery = `period=${encodeURIComponent(usagePeriod)}`;

        const [statsResponse, aggregatedResponse] = await Promise.all([

            fetch(`./api/usage/stats?${usagePeriodQuery}`, { headers: getAuthHeaders() }),

            fetch(`./api/usage/aggregated?${usagePeriodQuery}`, { headers: getAuthHeaders() })

        ]);

        if (statsResponse.status === 401 || aggregatedResponse.status === 401) {

            showStatus(t('authentication_failed_please_log_in'), 'error');

            setTimeout(() => location.reload(), 1500);

            return;

        }

        const statsData = await statsResponse.json();

        const aggregatedData = await aggregatedResponse.json();

        if (statsResponse.ok && aggregatedResponse.ok) {

            AppState.usageStatsData = statsData.success ? statsData.data : statsData;

            AppState.usageStatsLoaded = true;

            const aggData = aggregatedData.success ? aggregatedData.data : aggregatedData;

            const totalCalls = Number(aggData.total_calls ?? aggData.total_calls_24h ?? 0);

            const successfulCalls = Number(aggData.successful_calls ?? aggData.successful_calls_24h ?? 0);

            const failedCalls = Number(aggData.failed_calls ?? aggData.failed_calls_24h ?? 0);

            const successRate = totalCalls > 0 ? Math.round((successfulCalls / totalCalls) * 100) : 0;

            document.getElementById('totalApiCalls').textContent = formatUsageNumber(totalCalls);

            document.getElementById('successRate24h').textContent = `${successRate}%`;

            document.getElementById('successfulApiCalls').textContent = formatUsageNumber(successfulCalls);

            document.getElementById('failedApiCalls').textContent = formatUsageNumber(failedCalls);

            document.getElementById('successRateDetail').textContent = totalCalls > 0
                ? `${formatUsageNumber(successfulCalls)} of ${formatUsageNumber(totalCalls)} requests succeeded.`
                : 'No traffic yet';

            document.getElementById('totalFiles').textContent = formatUsageNumber(aggData.total_files);

            document.getElementById('activeFiles').textContent = formatUsageNumber(aggData.active_files);

            document.getElementById('disabledFiles').textContent = formatUsageNumber(aggData.disabled_files);

            document.getElementById('avgCallsPerFile').textContent = formatUsageNumber(
                aggData.avg_calls_per_file,
                { decimals: 1 }
            );

            document.getElementById('assignedApiCalls').textContent = formatUsageNumber(aggData.assigned_calls ?? aggData.assigned_calls_24h);

            document.getElementById('totalTokens24h').textContent = formatUsageNumber(aggData.total_tokens ?? aggData.total_tokens_24h);

            document.getElementById('inputTokens24h').textContent = formatUsageNumber(aggData.input_tokens ?? aggData.input_tokens_24h);

            document.getElementById('outputTokens24h').textContent = formatUsageNumber(aggData.output_tokens ?? aggData.output_tokens_24h);

            document.getElementById('avgTokensPerRequest').textContent = formatUsageNumber(
                aggData.avg_tokens_per_successful_request,
                { decimals: 1 }
            );

            document.getElementById('cachedTokens24h').textContent = formatUsageNumber(aggData.cached_tokens ?? aggData.cached_tokens_24h);

            document.getElementById('estimatedTokensSaved').textContent = formatUsageNumber(aggData.estimated_tokens_saved ?? aggData.estimated_tokens_saved_24h);

            renderUsageList();

            // showStatus(t('loaded_usage_statistics_for_aggdata', {aggData_total_files____Object_keys_AppState_usageStatsData__length: aggData.total_files || Object.keys(AppState.usageStatsData).length}), 'success');

        } else {

            const errorMsg = statsData.detail || aggregatedData.detail || t('failed_to_load_usage_statistics');

            showStatus(t('error_errormsg', {errorMsg: errorMsg}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        if (loading) loading.hidden = true;

        if (statsContainer && !preserveContent) statsContainer.setAttribute('aria-busy', 'false');

        if (tableWrapper && !preserveContent) tableWrapper.hidden = false;

    }

}

function getUsageCallCount(stats = {}) {

    return Number(stats.calls ?? stats.calls_24h ?? 0);

}

function getUsageEntriesWithTraffic() {

    return Object.entries(AppState.usageStatsData || {}).filter(([, stats]) => getUsageCallCount(stats) > 0);

}

function renderUsageList() {

    const list = document.getElementById('usageList');

    if (!list) return;

    list.innerHTML = '';

    renderUsageProviderSummary();

    const usageEntries = getUsageEntriesWithTraffic();

    if (usageEntries.length === 0) {

        const tr = document.createElement('tr');

        tr.innerHTML = `<td colspan="4" style="text-align: center; color: var(--text-muted); padding: 18px 12px;">${t('status_no_filter_data')}</td>`;

        list.appendChild(tr);

        return;

    }

    for (const [filename, stats] of usageEntries) {

        const tr = document.createElement('tr');

        const calls = getUsageCallCount(stats);
        const successfulCalls = stats.successful_calls ?? stats.successful_calls_24h ?? 0;
        const failedCalls = stats.failed_calls ?? stats.failed_calls_24h ?? 0;
        const inputTokens = stats.input_tokens ?? stats.input_tokens_24h ?? 0;
        const outputTokens = stats.output_tokens ?? stats.output_tokens_24h ?? 0;
        const totalTokens = stats.total_tokens ?? stats.total_tokens_24h ?? 0;
        const estimatedTokensSaved = stats.estimated_tokens_saved ?? stats.estimated_tokens_saved_24h ?? 0;
        const successRate = calls > 0 ? Math.round((successfulCalls / calls) * 100) : 0;
        const isUnassigned = filename === '__gateway_unassigned__.json';
        const providerMeta = isUnassigned
            ? { name: 'Gateway', logo: '/frontend/assets/logo.png' }
            : getCredentialProviderMeta({
                provider: stats.provider || stats.provider_name,
                credential_type: stats.credential_type
            }, 'usage');
        const accountLabel = isUnassigned
            ? 'No credential assigned'
            : (stats.is_deleted
                ? t('deleted_credential')
                : (stats.credential_label || stats.user_email || t('email_not_fetched')));
        const providerLogo = providerMeta.logo
            ? `<img src="${escapeAttribute(providerMeta.logo)}" alt="${escapeAttribute(providerMeta.name)} logo">`
            : `<span>${escapeHtml(providerMeta.name.charAt(0))}</span>`;

        tr.innerHTML = `

            <td>
                <div class="usage-credential-identity">
                    <div class="cred-provider-logo" aria-hidden="true">${providerLogo}</div>
                    <div class="usage-credential-copy">
                        <div class="usage-credential-name">${escapeHtml(accountLabel)}</div>
                        <div class="usage-credential-meta">${escapeHtml(providerMeta.name)}</div>
                    </div>
                </div>
            </td>

            <td>
                <div class="usage-cell-primary">${formatUsageNumber(calls)} requests</div>
                <div class="usage-cell-meta">${formatUsageNumber(successfulCalls)} successful / ${formatUsageNumber(failedCalls)} failed</div>
            </td>

            <td>
                <div class="usage-cell-primary">${successRate}%</div>
                <div class="usage-cell-meta">${calls > 0 ? `${formatUsageNumber(successfulCalls)} of ${formatUsageNumber(calls)} succeeded` : 'No traffic recorded'}</div>
            </td>

            <td>
                <div class="usage-cell-primary">${formatUsageNumber(totalTokens)} total</div>
                <div class="usage-cell-meta">Input ${formatUsageNumber(inputTokens)} / output ${formatUsageNumber(outputTokens)} / estimated savings ${formatUsageNumber(estimatedTokensSaved)}</div>
            </td>

        `;

        list.appendChild(tr);

    }

}

function renderUsageProviderSummary() {

    const container = document.getElementById('usageProviderSummary');

    if (!container) return;

    const providers = new Map();

    for (const [filename, stats] of getUsageEntriesWithTraffic()) {

        if (filename === '__gateway_unassigned__.json') continue;

        const providerMeta = getCredentialProviderMeta(
            {
                provider: stats.provider || stats.provider_name,
                credential_type: stats.credential_type
            },
            'usage'
        );

        const current = providers.get(providerMeta.id) || {
            meta: providerMeta,
            credentials: 0,
            calls: 0,
            successfulCalls: 0,
            totalTokens: 0,
        };

        if (!stats.is_deleted) current.credentials += 1;
        current.calls += getUsageCallCount(stats);
        current.successfulCalls += Number(stats.successful_calls ?? stats.successful_calls_24h ?? 0);
        current.totalTokens += Number(stats.total_tokens ?? stats.total_tokens_24h ?? 0);
        providers.set(providerMeta.id, current);

    }

    if (providers.size === 0) {

        container.innerHTML = '';
        container.hidden = true;
        return;

    }

    container.hidden = false;
    const providerOrder = ['google_antigravity', 'google_ai_studio', 'grok', 'xai_console', 'xai', 'code_assist'];
    const providerItems = Array.from(providers.values()).sort((left, right) => {
        const leftIndex = providerOrder.indexOf(left.meta.id);
        const rightIndex = providerOrder.indexOf(right.meta.id);
        return (leftIndex === -1 ? providerOrder.length : leftIndex)
            - (rightIndex === -1 ? providerOrder.length : rightIndex);
    });

    container.innerHTML = providerItems.map((provider) => {

        const successRate = provider.calls > 0
            ? Math.round((provider.successfulCalls / provider.calls) * 100)
            : 0;
        const logo = provider.meta.logo
            ? `<img src="${escapeAttribute(provider.meta.logo)}" alt="">`
            : `<span>${escapeHtml(provider.meta.name.charAt(0))}</span>`;
        const credentialLabel = provider.credentials > 0
            ? `${provider.credentials} active credential${provider.credentials === 1 ? '' : 's'}`
            : 'No active credentials';

        return `
            <article class="usage-provider-item">
                <div class="usage-provider-identity">
                    <div class="usage-provider-logo" aria-hidden="true">${logo}</div>
                    <div>
                        <div class="usage-provider-name">${escapeHtml(provider.meta.name)}</div>
                        <div class="usage-provider-meta">${credentialLabel}</div>
                    </div>
                </div>
                <dl class="usage-provider-metrics">
                    <div><dt>Requests</dt><dd>${formatUsageNumber(provider.calls)}</dd></div>
                    <div><dt>Success</dt><dd>${provider.calls > 0 ? `${successRate}%` : 'No traffic'}</dd></div>
                    <div><dt>Tokens</dt><dd>${formatUsageNumber(provider.totalTokens)}</dd></div>
                </dl>
            </article>
        `;

    }).join('');

}

// =====================================================================

// =====================================================================

function startCooldownTimer() {

    if (AppState.cooldownTimerInterval) {

        clearInterval(AppState.cooldownTimerInterval);

    }

    AppState.cooldownTimerInterval = setInterval(() => {

        updateCooldownDisplays();

    }, 1000);

}

function stopCooldownTimer() {

    if (AppState.cooldownTimerInterval) {

        clearInterval(AppState.cooldownTimerInterval);

        AppState.cooldownTimerInterval = null;

    }

}

function updateCooldownDisplays() {

    let needsRefresh = false;

    for (const credInfo of Object.values(AppState.creds.data)) {

        if (credInfo.model_cooldowns && Object.keys(credInfo.model_cooldowns).length > 0) {

            const currentTime = Date.now() / 1000;

            const hasExpiredCooldowns = Object.entries(credInfo.model_cooldowns).some(([, until]) => until <= currentTime);

            if (hasExpiredCooldowns) {

                needsRefresh = true;

                break;

            }

        }

    }

    if (needsRefresh) {

        AppState.creds.renderList();

        return;

    }

    document.querySelectorAll('.cooldown-badge').forEach(badge => {

        const card = badge.closest('.cred-card');

        const filenameEl = card?.querySelector('.cred-filename');

        if (!filenameEl) return;

        const filename = filenameEl.textContent;

        const credInfo = Object.values(AppState.creds.data).find(c => c.filename === filename);

        if (credInfo && credInfo.model_cooldowns) {

            const currentTime = Date.now() / 1000;

            const titleMatch = badge.getAttribute('title')?.match(/: (.+)/);

            if (titleMatch) {

                const model = titleMatch[1];

                const cooldownUntil = credInfo.model_cooldowns[model];

                if (cooldownUntil) {

                    const remaining = Math.max(0, Math.floor(cooldownUntil - currentTime));

                    if (remaining > 0) {

                        const shortModel = model.replace('gemini-', '').replace('-exp', '')

                            .replace('2.0-', '2-').replace('1.5-', '1.5-');

                        const timeDisplay = formatCooldownTime(remaining).replace(/s$/, '').replace(/ /g, '');

                        badge.textContent = `Cooldown ${shortModel}: ${timeDisplay}`;

                    }

                }

            }

        }

    });

}

// =====================================================================

// =====================================================================
