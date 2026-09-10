// Omni Gateway management console: dashboard.

const DASHBOARD_RECENT_ACTIVITY_PAGE_SIZE = 5;

function formatUsageCost(value) {
    const amount = Number(value || 0);
    if (!Number.isFinite(amount) || amount < 0) return '$0.00';
    return amount.toLocaleString(getActiveLocale(), {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: amount > 0 && amount < 0.01 ? 4 : 2,
    });
}

function deriveDashboardState(aggregate = {}, health = null) {
    const totalCredentials = Number(aggregate.total_files || 0);
    const activeCredentials = Number(aggregate.active_files || 0);
    const totalCalls = Number(aggregate.total_calls ?? aggregate.total_calls_24h ?? 0);
    const failedCalls = Number(aggregate.failed_calls ?? aggregate.failed_calls_24h ?? 0);
    const healthStatus = String(health?.status || 'no_data');

    if (totalCredentials === 0 && totalCalls === 0) {
        return {
            state: 'first_time',
            titleKey: 'dashboard.state_first_time_title',
            descriptionKey: 'dashboard.state_first_time_description',
            actionKey: 'dashboard.action_add_provider',
            actionTab: 'providers',
        };
    }
    if (activeCredentials === 0) {
        return {
            state: 'no_provider',
            titleKey: 'dashboard.state_no_provider_title',
            descriptionKey: 'dashboard.state_no_provider_description',
            actionKey: 'dashboard.action_review_credentials',
            actionTab: totalCredentials > 0 ? 'pool' : 'providers',
        };
    }
    const errorRate = totalCalls > 0 ? failedCalls / totalCalls : 0;
    const currentHealthNeedsAttention = ['warning', 'critical'].includes(healthStatus);
    const historyIsOnlySignal = (!healthStatus || healthStatus === 'no_data') && errorRate >= 0.05;
    if (currentHealthNeedsAttention || historyIsOnlySignal) {
        return {
            state: 'degraded',
            titleKey: 'dashboard.state_degraded_title',
            descriptionKey: 'dashboard.state_degraded_description',
            actionKey: 'dashboard.action_investigate',
            actionTab: 'activity',
        };
    }
    return {
        state: 'healthy',
        titleKey: totalCalls > 0 ? 'dashboard.state_healthy_title' : 'dashboard.state_ready_title',
        descriptionKey: totalCalls > 0 ? 'dashboard.state_healthy_description' : 'dashboard.state_ready_description',
        actionKey: 'dashboard.action_activity',
        actionTab: 'activity',
    };
}

function renderDashboardReadiness() {
    const container = document.getElementById('dashboardReadiness');
    if (!container || !AppState.dashboardAggregate) return;
    const guidance = deriveDashboardState(AppState.dashboardAggregate, AppState.operationalHealth);
    container.dataset.state = guidance.state;
    container.setAttribute('aria-busy', 'false');
    document.getElementById('dashboardReadinessStatus').textContent = t(`dashboard.state_${guidance.state}`);
    document.getElementById('dashboardReadinessTitle').textContent = t(guidance.titleKey);
    document.getElementById('dashboardReadinessDescription').textContent = t(guidance.descriptionKey);
    const action = document.getElementById('dashboardReadinessAction');
    action.textContent = t(guidance.actionKey);
    action.dataset.tab = guidance.actionTab;
}

function formatUsageNumber(value, options = {}) {

    const number = Number(value || 0);

    if (!Number.isFinite(number)) return '0';

    return number.toLocaleString(getActiveLocale(), {
        maximumFractionDigits: options.decimals ?? 0,
        minimumFractionDigits: options.decimals ?? 0,
    });

}

function getUsagePeriodConfig(period = AppState.usagePeriod) {

    const periods = {
        '1d': {
            value: '1d',
            optionLabel: t('one_day'),
            metricLabel: t('dashboard.period_1d'),
            title: t('dashboard.breakdown_1d'),
        },
        '7d': {
            value: '7d',
            optionLabel: t('seven_days'),
            metricLabel: t('dashboard.period_7d'),
            title: t('dashboard.breakdown_7d'),
        },
        '30d': {
            value: '30d',
            optionLabel: t('thirty_days'),
            metricLabel: t('dashboard.period_30d'),
            title: t('dashboard.breakdown_30d'),
        },
        all: {
            value: 'all',
            optionLabel: t('all'),
            metricLabel: t('dashboard.period_all'),
            title: t('dashboard.breakdown_all'),
        },
    };

    return periods[period] || periods['1d'];

}

function updateUsagePeriodLabels() {

    const periodConfig = getUsagePeriodConfig();

    const periodSelect = document.getElementById('usagePeriodSelect');

    if (periodSelect) periodSelect.value = periodConfig.value;

    const totalCallsLabel = document.getElementById('totalApiCallsLabel');

    if (totalCallsLabel) totalCallsLabel.textContent = t('dashboard.requests_period', {period: periodConfig.metricLabel});

    const totalTokensLabel = document.getElementById('totalTokensLabel');

    if (totalTokensLabel) totalTokensLabel.textContent = t('dashboard.tokens_period', {period: periodConfig.metricLabel});

    const totalCostLabel = document.getElementById('totalCostLabel');

    if (totalCostLabel) totalCostLabel.textContent = t('dashboard.cost_period', {period: periodConfig.metricLabel});

    const breakdownTitle = document.getElementById('usageBreakdownTitle');

    if (breakdownTitle) breakdownTitle.textContent = periodConfig.title;

    const breakdownDescription = document.getElementById('usageBreakdownDescription');

    if (breakdownDescription) breakdownDescription.textContent = t('dashboard.breakdown_description', {period: periodConfig.metricLabel});

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

    void refreshOperationalHealth();

    void refreshRecentActivity();

    const loading = document.getElementById('usageLoading');

    const list = document.getElementById('usageList');

    const providerSummary = document.getElementById('usageProviderSummary');

    const historicalSection = document.getElementById('historicalUsageSection');

    const historicalList = document.getElementById('historicalUsageList');

    const statsContainer = document.getElementById('dashboardStats');

    const tableWrapper = document.querySelector('#dashboardTab .usage-table-wrapper');

    const preserveContent = options.preserveContent ?? AppState.usageStatsLoaded;

    clearPageState('dashboardUsageState');

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

        if (!preserveContent) {

            if (historicalList) historicalList.innerHTML = '';
            if (historicalSection) historicalSection.hidden = true;

        }

        const usagePeriod = getUsagePeriodConfig().value;

        const usagePeriodQuery = `period=${encodeURIComponent(usagePeriod)}`;

        const [statsResponse, aggregatedResponse] = await Promise.all([

            fetch(`./api/usage/stats/page?${usagePeriodQuery}&page_size=100`, { headers: getAuthHeaders() }),

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

            clearPageState('dashboardUsageState');

            AppState.usageStatsData = statsData.success ? statsData.data : statsData;

            AppState.usageStatsLoaded = true;

            const aggData = aggregatedData.success ? aggregatedData.data : aggregatedData;

            AppState.dashboardAggregate = aggData;

            const totalCalls = Number(aggData.total_calls ?? aggData.total_calls_24h ?? 0);

            const successfulCalls = Number(aggData.successful_calls ?? aggData.successful_calls_24h ?? 0);

            const failedCalls = Number(aggData.failed_calls ?? aggData.failed_calls_24h ?? 0);

            const successRate = totalCalls > 0 ? Math.round((successfulCalls / totalCalls) * 100) : 0;

            document.getElementById('totalApiCalls').textContent = formatUsageNumber(totalCalls);

            document.getElementById('successRate24h').textContent = `${successRate}%`;

            document.getElementById('requestOutcomeDetail').textContent = t('dashboard.successful_failed', {
                successful: formatUsageNumber(successfulCalls),
                failed: formatUsageNumber(failedCalls)
            });

            document.getElementById('successRateDetail').textContent = totalCalls > 0
                ? t('dashboard.requests_succeeded', {successful: formatUsageNumber(successfulCalls), total: formatUsageNumber(totalCalls)})
                : t('dashboard.no_traffic_yet');

            document.getElementById('totalFiles').textContent = formatUsageNumber(aggData.total_files);

            document.getElementById('activeFiles').textContent = formatUsageNumber(aggData.active_files);

            document.getElementById('disabledCredentialsDetail').textContent = t('dashboard.disabled_count', {count: formatUsageNumber(aggData.disabled_files)});

            document.getElementById('totalCostUsd').textContent = formatUsageCost(aggData.total_cost_usd);

            document.getElementById('totalTokens24h').textContent = formatUsageNumber(aggData.total_tokens ?? aggData.total_tokens_24h);

            document.getElementById('inputOutputDetail').textContent = t('dashboard.input_output', {
                input: formatUsageNumber(aggData.input_tokens ?? aggData.input_tokens_24h),
                output: formatUsageNumber(aggData.output_tokens ?? aggData.output_tokens_24h)
            });

            renderTokenDistribution(aggData);
            renderProviderHealthMatrix();
            renderUsageList();
            renderDashboardReadiness();

            // showStatus(t('loaded_usage_statistics_for_aggdata', {aggData_total_files____Object_keys_AppState_usageStatsData__length: aggData.total_files || Object.keys(AppState.usageStatsData).length}), 'success');

        } else {

            const errorMsg = statsData.detail || aggregatedData.detail || t('failed_to_load_usage_statistics');

            throw new Error(errorMsg);

        }

    } catch (error) {

        const message = t('status_net_error', {error: error.message});
        showPageState('dashboardUsageState', {
            kind: preserveContent ? 'stale' : 'error',
            title: t(preserveContent ? 'warning' : 'error'),
            message,
            actionLabel: t('refresh'),
            onAction: () => refreshUsageStats({preserveContent: AppState.usageStatsLoaded})
        });
        showStatus(message, 'error');

    } finally {

        if (loading) loading.hidden = true;

        if (statsContainer && !preserveContent) statsContainer.setAttribute('aria-busy', 'false');

        if (tableWrapper && !preserveContent) tableWrapper.hidden = false;

    }

}

function setOperationalHealthStatus(status) {
    const pill = document.getElementById('sloOverallStatus');
    if (!pill) return;
    const normalized = ['healthy', 'warning', 'critical', 'no_data'].includes(status) ? status : 'critical';
    pill.className = `health-pill ${normalized === 'healthy' ? 'healthy' : normalized === 'critical' ? 'error' : 'warning'}`;
    const label = pill.querySelector('span:last-child');
    if (label) label.textContent = t(`slo.status_${normalized}`);
}

async function refreshOperationalHealth() {
    const card = document.getElementById('operationalHealthCard');
    if (!card) return;
    card.setAttribute('aria-busy', 'true');
    try {
        const response = await fetch('./api/observability/health?window_seconds=900', {headers: getAuthHeaders()});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const snapshot = await response.json();
        AppState.operationalHealth = snapshot;
        const red = snapshot.red || {};
        document.getElementById('sloRequestRate').textContent = formatUsageNumber(red.requests_per_minute, {decimals: 1});
        document.getElementById('sloErrorRate').textContent = `${(Number(red.error_rate || 0) * 100).toFixed(1)}%`;
        document.getElementById('sloErrorCount').textContent = t('slo.errors_of_requests', {errors: formatUsageNumber(red.errors), requests: formatUsageNumber(red.requests)});
        document.getElementById('sloP95').textContent = `${formatUsageNumber(red.p95_duration_ms)} ms`;
        document.getElementById('dashboardP95Latency').textContent = `${formatUsageNumber(red.p95_duration_ms)} ms`;
        const exhaustion = Object.values(snapshot.exhaustion || {}).reduce((total, value) => total + Number(value || 0), 0);
        document.getElementById('sloExhaustion').textContent = formatUsageNumber(exhaustion);
        setOperationalHealthStatus(snapshot.status);
        renderOperationalRoutes(snapshot.routes || []);
        const telemetry = snapshot.telemetry || {};
        document.getElementById('sloPrometheusStatus').textContent = t(telemetry.prometheus?.enabled ? 'slo.enabled' : 'slo.disabled_default');
        document.getElementById('sloOtelStatus').textContent = t(telemetry.opentelemetry?.enabled ? 'slo.enabled' : 'slo.disabled_default');
        const notice = document.getElementById('sloSampleNotice');
        notice.hidden = !snapshot.sample_truncated;
        notice.textContent = snapshot.sample_truncated ? t('slo.sample_truncated', {count: formatUsageNumber(snapshot.sample_size)}) : '';
        renderDashboardReadiness();
    } catch (error) {
        AppState.operationalHealth = {status: 'critical', unavailable: true};
        setOperationalHealthStatus('critical');
        const rows = document.getElementById('sloRouteRows');
        if (rows) {
            rows.replaceChildren();
            const row = rows.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 4;
            cell.textContent = t('slo.load_failed');
        }
        renderDashboardReadiness();
    } finally {
        card.setAttribute('aria-busy', 'false');
    }
}

async function refreshRecentActivity() {
    const card = document.getElementById('recentActivityCard');
    if (!card) return;
    card.setAttribute('aria-busy', 'true');
    try {
        const response = await fetch('./api/traces?page_size=5', {headers: getAuthHeaders()});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        renderRecentActivity(Array.isArray(payload.traces) ? payload.traces : []);
    } catch (_error) {
        const list = document.getElementById('recentActivityList');
        if (list) list.innerHTML = `<li class="dashboard-activity-empty">${escapeHtml(t('dashboard.recent_failed'))}</li>`;
    } finally {
        card.setAttribute('aria-busy', 'false');
    }
}

function renderRecentActivity(traces = []) {
    const list = document.getElementById('recentActivityList');
    if (!list) return;
    const boundedTraces = traces.slice(0, DASHBOARD_RECENT_ACTIVITY_PAGE_SIZE);
    if (!boundedTraces.length) {
        list.innerHTML = `<li class="dashboard-activity-empty">${escapeHtml(t('dashboard.recent_empty'))}</li>`;
        return;
    }
    list.innerHTML = boundedTraces.map((trace) => {
        const outcome = String(trace.outcome || 'unknown');
        const safeOutcome = outcome.replace(/[^a-z0-9_-]/gi, '').toLowerCase() || 'unknown';
        const provider = trace.selected_provider || '—';
        const model = trace.requested_model || '—';
        const startedAt = trace.started_at
            ? new Date(trace.started_at).toLocaleString(getActiveLocale(), {dateStyle: 'short', timeStyle: 'short'})
            : '—';
        return `
            <li class="dashboard-activity-item">
                <div class="dashboard-activity-heading">
                    <span class="trace-outcome trace-outcome-${escapeAttribute(safeOutcome)}">${escapeHtml(outcome)}</span>
                    <time datetime="${escapeAttribute(trace.started_at || '')}">${escapeHtml(startedAt)}</time>
                </div>
                <strong>${escapeHtml(model)}</strong>
                <span>${escapeHtml(provider)} · ${formatUsageNumber(trace.duration_ms)} ms · ${escapeHtml(formatUsageCost(trace.cost_usd))}</span>
                <code>${escapeHtml(trace.request_id || trace.trace_id || '')}</code>
            </li>
        `;
    }).join('');
}

function renderOperationalRoutes(routes) {
    const target = document.getElementById('sloRouteRows');
    if (!target) return;
    target.replaceChildren();
    if (!routes.length) {
        const row = target.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 4;
        cell.textContent = t('slo.no_data');
        return;
    }
    routes.slice(0, 10).forEach((route) => {
        const row = target.insertRow();
        [
            route.route,
            formatUsageNumber(route.requests),
            `${(Number(route.error_rate || 0) * 100).toFixed(1)}%`,
            `${formatUsageNumber(route.p95_duration_ms)} ms`,
        ].forEach((value) => {
            const cell = row.insertCell();
            cell.textContent = String(value);
        });
        row.dataset.status = route.status;
    });
}

function getUsageCallCount(stats = {}) {

    return Number(stats.calls ?? stats.calls_24h ?? 0);

}

function getUsageEntriesWithTraffic() {

    return Object.entries(AppState.usageStatsData || {}).filter(([, stats]) => getUsageCallCount(stats) > 0);

}

function isHistoricalUsageEntry([filename, stats]) {

    return filename !== '__gateway_unassigned__.json'
        && Boolean(stats.is_historical || stats.is_deleted);

}

function getCurrentUsageEntriesWithTraffic() {

    return getUsageEntriesWithTraffic().filter((entry) => !isHistoricalUsageEntry(entry));

}

function getHistoricalUsageEntriesWithTraffic() {

    return getUsageEntriesWithTraffic().filter(isHistoricalUsageEntry);

}

function createUsageTableRow(filename, stats) {

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
        ? t('dashboard.no_credential')
        : (stats.is_deleted
            ? t('deleted_credential')
            : (stats.is_historical
                ? (stats.credential_label || t('unavailable_credential'))
                : (stats.credential_label || stats.user_email || t('email_not_fetched'))));
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
            <div class="usage-cell-primary">${escapeHtml(t('dashboard.requests_count', {count: formatUsageNumber(calls)}))}</div>
            <div class="usage-cell-meta">${escapeHtml(t('dashboard.success_count', {count: formatUsageNumber(successfulCalls), failed: formatUsageNumber(failedCalls)}))}</div>
        </td>

        <td>
            <div class="usage-cell-primary">${successRate}%</div>
            <div class="usage-cell-meta">${escapeHtml(calls > 0 ? t('dashboard.succeeded_count', {successful: formatUsageNumber(successfulCalls), total: formatUsageNumber(calls)}) : t('dashboard.no_traffic_recorded'))}</div>
        </td>

        <td>
            <div class="usage-cell-primary">${escapeHtml(t('dashboard.tokens_total', {count: formatUsageNumber(totalTokens)}))}</div>
            <div class="usage-cell-meta">${escapeHtml(t('dashboard.token_details', {input: formatUsageNumber(inputTokens), output: formatUsageNumber(outputTokens), savings: formatUsageNumber(estimatedTokensSaved)}))}</div>
        </td>

    `;

    return tr;

}

function renderUsageTableRows(list, entries, emptyMessage = '') {

    list.innerHTML = '';

    if (entries.length === 0) {

        if (!emptyMessage) return;

        const tr = document.createElement('tr');

        tr.innerHTML = `<td colspan="4" style="text-align: center; color: var(--text-muted); padding: 18px 12px;">${escapeHtml(emptyMessage)}</td>`;

        list.appendChild(tr);

        return;

    }

    for (const [filename, stats] of entries) {

        list.appendChild(createUsageTableRow(filename, stats));

    }

}

function updateUsagePagination(paginationId, prevBtnId, nextBtnId, infoId, currentPage, totalPages) {

    const container = document.getElementById(paginationId);
    const prevBtn = document.getElementById(prevBtnId);
    const nextBtn = document.getElementById(nextBtnId);
    const info = document.getElementById(infoId);

    if (!container) return;

    if (totalPages <= 1) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'flex';
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
    if (info) info.textContent = t('pagination.page_of', {page: currentPage, total: totalPages});

}

function changeUsagePage(delta) {

    const entries = getCurrentUsageEntriesWithTraffic();
    const totalPages = Math.max(1, Math.ceil(entries.length / (AppState.usagePageSize || 10)));
    const nextPage = Math.min(Math.max(1, AppState.usagePage + delta), totalPages);

    if (nextPage !== AppState.usagePage) {
        AppState.usagePage = nextPage;
        renderUsageList();
    }

}

function changeHistoricalUsagePage(delta) {

    const entries = getHistoricalUsageEntriesWithTraffic();
    const totalPages = Math.max(1, Math.ceil(entries.length / (AppState.historicalUsagePageSize || 10)));
    const nextPage = Math.min(Math.max(1, AppState.historicalUsagePage + delta), totalPages);

    if (nextPage !== AppState.historicalUsagePage) {
        AppState.historicalUsagePage = nextPage;
        renderHistoricalUsageList();
    }

}

function renderHistoricalUsageList() {

    const section = document.getElementById('historicalUsageSection');
    const list = document.getElementById('historicalUsageList');

    if (!section || !list) return;

    const entries = getHistoricalUsageEntriesWithTraffic();
    section.hidden = entries.length === 0;

    const pageSize = AppState.historicalUsagePageSize || 10;
    const totalPages = Math.max(1, Math.ceil(entries.length / pageSize));
    if (AppState.historicalUsagePage > totalPages) {
        AppState.historicalUsagePage = totalPages;
    }

    const startIndex = (AppState.historicalUsagePage - 1) * pageSize;
    const pagedEntries = entries.slice(startIndex, startIndex + pageSize);

    renderUsageTableRows(list, pagedEntries);
    updateUsagePagination(
        'historicalUsagePaginationContainer',
        'historicalUsagePrevPageBtn',
        'historicalUsageNextPageBtn',
        'historicalUsagePaginationInfo',
        AppState.historicalUsagePage,
        totalPages
    );

}

function renderUsageList() {

    const list = document.getElementById('usageList');

    if (!list) return;

    renderUsageProviderSummary();

    const entries = getCurrentUsageEntriesWithTraffic();
    const pageSize = AppState.usagePageSize || 10;
    const totalPages = Math.max(1, Math.ceil(entries.length / pageSize));
    if (AppState.usagePage > totalPages) {
        AppState.usagePage = totalPages;
    }

    const startIndex = (AppState.usagePage - 1) * pageSize;
    const pagedEntries = entries.slice(startIndex, startIndex + pageSize);

    renderUsageTableRows(
        list,
        pagedEntries,
        t('status_no_filter_data')
    );

    updateUsagePagination(
        'usagePaginationContainer',
        'usagePrevPageBtn',
        'usageNextPageBtn',
        'usagePaginationInfo',
        AppState.usagePage,
        totalPages
    );

    renderHistoricalUsageList();

}

function renderUsageProviderSummary() {

    const container = document.getElementById('usageProviderSummary');

    if (!container) return;

    const providers = new Map();

    for (const [filename, stats] of getCurrentUsageEntriesWithTraffic()) {

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
    const providerOrder = ['google_antigravity', 'google_ai_studio', 'grok', 'xai_console', 'codex', 'openai_platform', 'claude_code', 'claude_platform', 'ollama', 'xai', 'openai', 'anthropic', 'code_assist'];
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
            ? t(provider.credentials === 1 ? 'dashboard.active_credentials_count' : 'dashboard.active_credentials_count_plural', {count: formatUsageNumber(provider.credentials)})
            : t('dashboard.no_active_credentials');

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
                    <div><dt>${escapeHtml(t('requests'))}</dt><dd>${formatUsageNumber(provider.calls)}</dd></div>
                    <div><dt>${escapeHtml(t('success'))}</dt><dd>${provider.calls > 0 ? `${successRate}%` : escapeHtml(t('dashboard.no_traffic'))}</dd></div>
                    <div><dt>${escapeHtml(t('tokens'))}</dt><dd>${formatUsageNumber(provider.totalTokens)}</dd></div>
                </dl>
            </article>
        `;

    }).join('');

}

function renderTokenDistribution(aggData = {}) {

    const inputTokens = Number(aggData.input_tokens ?? aggData.input_tokens_24h ?? 0);
    const outputTokens = Number(aggData.output_tokens ?? aggData.output_tokens_24h ?? 0);
    const cachedTokens = Number(aggData.cached_tokens ?? aggData.cached_tokens_24h ?? 0);
    const reasoningTokens = Number(aggData.reasoning_tokens ?? aggData.reasoning_tokens_24h ?? 0);

    const totalCalculated = inputTokens + outputTokens + cachedTokens + reasoningTokens;

    const inputPct = totalCalculated > 0 ? ((inputTokens / totalCalculated) * 100).toFixed(1) : '0.0';
    const outputPct = totalCalculated > 0 ? ((outputTokens / totalCalculated) * 100).toFixed(1) : '0.0';
    const cachedPct = totalCalculated > 0 ? ((cachedTokens / totalCalculated) * 100).toFixed(1) : '0.0';
    const reasoningPct = totalCalculated > 0 ? ((reasoningTokens / totalCalculated) * 100).toFixed(1) : '0.0';

    const inputEl = document.getElementById('distInputTokens');
    const outputEl = document.getElementById('distOutputTokens');
    const cachedEl = document.getElementById('distCachedTokens');
    const reasoningEl = document.getElementById('distReasoningTokens');

    if (inputEl) inputEl.textContent = formatUsageNumber(inputTokens);
    if (outputEl) outputEl.textContent = formatUsageNumber(outputTokens);
    if (cachedEl) cachedEl.textContent = formatUsageNumber(cachedTokens);
    if (reasoningEl) reasoningEl.textContent = formatUsageNumber(reasoningTokens);

    const inputPctEl = document.getElementById('distInputPct');
    const outputPctEl = document.getElementById('distOutputPct');
    const cachedPctEl = document.getElementById('distCachedPct');
    const reasoningPctEl = document.getElementById('distReasoningPct');

    if (inputPctEl) inputPctEl.textContent = `${inputPct}%`;
    if (outputPctEl) outputPctEl.textContent = `${outputPct}%`;
    if (cachedPctEl) cachedPctEl.textContent = `${cachedPct}%`;
    if (reasoningPctEl) reasoningPctEl.textContent = `${reasoningPct}%`;

    const barContainer = document.getElementById('tokenDistributionBar');
    if (barContainer) {
        const inputSeg = barContainer.querySelector('.input-segment');
        const outputSeg = barContainer.querySelector('.output-segment');
        const cachedSeg = barContainer.querySelector('.cached-segment');
        const reasoningSeg = barContainer.querySelector('.reasoning-segment');

        if (inputSeg) inputSeg.style.width = `${inputPct}%`;
        if (outputSeg) outputSeg.style.width = `${outputPct}%`;
        if (cachedSeg) cachedSeg.style.width = `${cachedPct}%`;
        if (reasoningSeg) reasoningSeg.style.width = `${reasoningPct}%`;
    }

    renderTimelineChart(aggData.timeline || []);

}

function renderTimelineChart(timeline = []) {

    const wrapper = document.getElementById('timelineBarsWrapper');
    const maxInfo = document.getElementById('timelineChartMaxInfo');

    if (!wrapper) return;

    if (!timeline || timeline.length === 0) {
        wrapper.innerHTML = `<div style="display:flex; align-items:center; justify-content:center; width:100%; height:100%; color:var(--text-muted); font-size:12px;">${escapeHtml(t('dashboard.no_traffic_recorded'))}</div>`;
        if (maxInfo) maxInfo.textContent = '';
        return;
    }

    const maxRequests = Math.max(...timeline.map(slot => slot.requests || 0));
    const chartScale = Math.max(maxRequests, 1);
    if (maxInfo) {
        maxInfo.textContent = t('dashboard.peak_requests', {count: formatUsageNumber(maxRequests)});
    }

    wrapper.innerHTML = timeline.map((slot) => {
        const reqs = slot.requests || 0;
        const success = slot.successful_requests || 0;
        const failed = slot.failed_requests || 0;
        const tokens = slot.tokens || 0;
        const heightPct = Math.max(reqs > 0 ? (reqs / chartScale) * 100 : 0, 4);

        const timeStr = slot.timestamp ? new Date(slot.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

        return `
            <div class="timeline-bar-col">
                <div class="timeline-tooltip">
                    <div><strong>${escapeHtml(timeStr)}</strong></div>
                    <div>${escapeHtml(t('requests'))}: ${formatUsageNumber(reqs)} (${escapeHtml(t('success'))}: ${formatUsageNumber(success)}${failed > 0 ? `, ${escapeHtml(t('failed'))}: ${formatUsageNumber(failed)}` : ''})</div>
                    <div>${escapeHtml(t('tokens'))}: ${formatUsageNumber(tokens)}</div>
                </div>
                <div class="timeline-bar-fill" style="height: ${reqs > 0 ? heightPct : 0}%; opacity: ${reqs > 0 ? 1 : 0.2};"></div>
            </div>
        `;
    }).join('');

}

function renderProviderHealthMatrix() {

    const container = document.getElementById('providerHealthGrid');
    if (!container) return;

    const trafficMap = new Map();
    for (const [filename, stats] of getCurrentUsageEntriesWithTraffic()) {
        if (filename === '__gateway_unassigned__.json') continue;
        const meta = getCredentialProviderMeta(
            { provider: stats.provider || stats.provider_name, credential_type: stats.credential_type },
            'usage'
        );
        const cur = trafficMap.get(meta.id) || {
            meta: meta,
            calls: 0,
            successful: 0,
            failed: 0,
            hasCooldown: false
        };
        cur.calls += getUsageCallCount(stats);
        cur.successful += Number(stats.successful_calls ?? stats.successful_calls_24h ?? 0);
        cur.failed += Number(stats.failed_calls ?? stats.failed_calls_24h ?? 0);
        if (stats.cooldown_until || stats.in_cooldown) cur.hasCooldown = true;
        trafficMap.set(meta.id, cur);
    }

    // Lấy các provider đang có credentials trong pool
    const activeProviderIds = new Set();
    const primaryCreds = AppState.primaryCreds?.items || [];
    for (const cred of primaryCreds) {
        const meta = getCredentialProviderMeta(cred, 'pool');
        if (meta && meta.id) activeProviderIds.add(meta.id);
    }

    // Chỉ giữ các provider đang có credentials trong pool HOẶC đã có traffic phát sinh
    const relevantProviders = [];
    const providerOrder = ['google_antigravity', 'google_ai_studio', 'grok', 'xai_console', 'codex', 'openai_platform', 'claude_code', 'claude_platform', 'ollama', 'xai', 'openai', 'anthropic', 'code_assist'];

    const providerCatalog = [
        { id: 'google_antigravity', name: 'Google Antigravity', logo: '/frontend/assets/providers/google-antigravity-logo.png' },
        { id: 'google_ai_studio', name: 'Google AI Studio', logo: '/frontend/assets/providers/google-ai-studio-logo.png' },
        { id: 'claude_code', name: 'Claude Code', logo: '/frontend/assets/providers/claude-code-logo.png' },
        { id: 'claude_platform', name: 'Claude Platform', logo: '/frontend/assets/providers/claude-platform-logo.png' },
        { id: 'openai_platform', name: 'OpenAI Platform', logo: '/frontend/assets/providers/openai-platform-logo.png' },
        { id: 'codex', name: 'Codex / ChatGPT', logo: '/frontend/assets/providers/codex-logo.png' },
        { id: 'grok', name: 'Grok / xAI Build', logo: '/frontend/assets/providers/grok-build-logo.png' },
        { id: 'xai_console', name: 'SpaceXAI Console', logo: '/frontend/assets/providers/grok-build-logo.png' },
        { id: 'ollama', name: 'Ollama', logo: '/frontend/assets/providers/ollama-logo.png' }
    ];

    for (const p of providerCatalog) {
        const hasTraffic = trafficMap.has(p.id) && trafficMap.get(p.id).calls > 0;
        const isInPool = activeProviderIds.has(p.id);
        if (hasTraffic || isInPool) {
            relevantProviders.push(p);
        }
    }

    // Nếu có provider có traffic nhưng không nằm trong catalog cố định ở trên
    for (const [id, data] of trafficMap.entries()) {
        if (!relevantProviders.some(p => p.id === id) && data.calls > 0) {
            relevantProviders.push({
                id: id,
                name: data.meta.name,
                logo: data.meta.logo || '/frontend/assets/logo.png'
            });
        }
    }

    if (relevantProviders.length === 0) {
        container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 18px 12px; grid-column: 1 / -1;">${escapeHtml(t('dashboard.no_traffic_yet'))}</div>`;
        return;
    }

    relevantProviders.sort((a, b) => {
        const aIdx = providerOrder.indexOf(a.id);
        const bIdx = providerOrder.indexOf(b.id);
        return (aIdx === -1 ? 999 : aIdx) - (bIdx === -1 ? 999 : bIdx);
    });

    container.innerHTML = relevantProviders.map(p => {
        const traffic = trafficMap.get(p.id) || { calls: 0, successful: 0, failed: 0, hasCooldown: false };
        let status = 'idle';
        let statusText = t('dashboard.status_idle');
        let badgeClass = 'badge-idle';

        if (traffic.hasCooldown || (traffic.calls > 0 && (traffic.successful / traffic.calls) < 0.6)) {
            status = 'error';
            statusText = traffic.hasCooldown ? t('dashboard.status_cooldown') : t('dashboard.status_degraded');
            badgeClass = 'badge-error';
        } else if (traffic.calls > 0) {
            status = 'healthy';
            statusText = t('dashboard.status_healthy');
            badgeClass = 'badge-healthy';
        }

        return `
            <div class="provider-health-item status-${status}">
                <div class="health-item-top">
                    <div class="health-item-identity">
                        <div class="health-item-logo">
                            <img src="${escapeAttribute(p.logo)}" alt="${escapeAttribute(p.name)}">
                        </div>
                        <span class="health-item-name">${escapeHtml(p.name)}</span>
                    </div>
                    <span class="health-badge ${badgeClass}">${escapeHtml(statusText)}</span>
                </div>
                <div class="health-item-stats">
                    <span>${escapeHtml(t('requests'))}: <strong>${formatUsageNumber(traffic.calls)}</strong></span>
                    <span>${escapeHtml(t('success'))}: <strong>${traffic.calls > 0 ? Math.round((traffic.successful / traffic.calls) * 100) + '%' : '-'}</strong></span>
                </div>
            </div>
        `;
    }).join('');

}

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

                        badge.textContent = t('credential_badge_cooldown', {model: shortModel, time: timeDisplay});

                    }

                }

            }

        }

    });

}

// =====================================================================

// =====================================================================
