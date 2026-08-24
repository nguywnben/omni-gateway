function createCredsManager(type) {

    const modeParam = type === 'primary' ? 'mode=provider' : 'mode=code_assist';

    return {

        type: type,

        data: {},

        filteredData: {},

        currentPage: 1,

        pageSize: 20,

        selectedFiles: new Set(),

        totalCount: 0,

        hasLoaded: false,

        currentStatusFilter: 'all',

        currentErrorCodeFilter: 'all',

        currentCooldownFilter: 'all',

        currentPreviewFilter: 'all',

        currentTierFilter: 'all',

        currentProviderFilter: 'all',

        currentCredentialKindFilter: 'all',

        currentHealthFilter: 'all',

        currentQuotaStateFilter: 'all',

        currentSourceFilter: 'all',

        filtersRestored: false,

        selectionScope: 'page',

        allMatchingSelection: null,

        facets: {},

        statsData: { total: 0, normal: 0, disabled: 0 },

        getEndpoint: (action) => {

            const endpoints = {

                status: `./api/credentials/status`,

                action: `./api/credentials/action`,

                batchAction: `./api/credentials/batch-action`,

                download: `./api/credentials/download`,

                downloadAll: `./api/credentials/download-all`,

                detail: `./api/credentials/detail`,

                models: `./api/credentials/models`,

                refreshAllEmails: `./api/credentials/refresh-all-emails`,

                deduplicate: `./api/credentials/deduplicate-by-email`,

                verify: `./api/credentials/verify`,

                quota: `./api/credentials/quota`

            };

            return endpoints[action] || '';

        },

        getModeParam: () => modeParam,

        getFilterDefinitions() {

            return {

                provider: { state: 'currentProviderFilter', suffix: 'ProviderFilter', values: ['all', 'google_antigravity', 'google_ai_studio', 'grok', 'xai_console', 'codex', 'openai_platform', 'claude_code', 'claude_platform', 'ollama'] },

                status: { state: 'currentStatusFilter', suffix: 'StatusFilter', values: ['all', 'enabled', 'disabled'] },

                error: { state: 'currentErrorCodeFilter', suffix: 'ErrorCodeFilter', values: ['all', 'none', '400', '401', '403', '429', '500', '502', '503'] },

                cooldown: { state: 'currentCooldownFilter', suffix: 'CooldownFilter', values: ['all', 'in_cooldown', 'no_cooldown'] },

                tier: { state: 'currentTierFilter', suffix: 'TierFilter', values: ['all', 'free', 'pro', 'ultra'] },

                kind: { state: 'currentCredentialKindFilter', suffix: 'CredentialKindFilter', values: ['all', 'oauth', 'api_key', 'connection'] },

                health: { state: 'currentHealthFilter', suffix: 'HealthFilter', values: ['all', 'healthy', 'degraded', 'unhealthy', 'disabled'] },

                quota: { state: 'currentQuotaStateFilter', suffix: 'QuotaStateFilter', values: ['all', 'available', 'limited', 'exhausted', 'unsupported'] },

                source: { state: 'currentSourceFilter', suffix: 'SourceFilter', values: ['all', 'managed', 'environment'] }

            };

        },

        restoreFilterState() {

            if (this.filtersRestored || this.type !== 'primary') return;

            this.filtersRestored = true;

            let stored = {};

            try {

                const raw = sessionStorage.getItem('omni.pool.filters.v1') || '';

                if (raw.length <= 512) stored = JSON.parse(raw) || {};

            } catch (_error) {

                stored = {};

            }

            const params = new URLSearchParams(window.location.search);

            Object.entries(this.getFilterDefinitions()).forEach(([key, definition]) => {

                const candidate = params.get(`pool_${key}`) || stored[key] || 'all';

                const value = definition.values.includes(candidate) ? candidate : 'all';

                this[definition.state] = value;

                const element = document.getElementById(this.getElementId(definition.suffix));

                if (element) element.value = value;

            });

            const pageSize = Number(params.get('pool_page_size') || stored.pageSize);

            if ([20, 50, 100, 200].includes(pageSize)) this.pageSize = pageSize;

            const pageSizeElement = document.getElementById(this.getElementId('PageSizeSelect'));

            if (pageSizeElement) pageSizeElement.value = String(this.pageSize);

        },

        persistFilterState() {

            if (this.type !== 'primary') return;

            const state = {};

            const url = new URL(window.location.href);

            Object.entries(this.getFilterDefinitions()).forEach(([key, definition]) => {

                const value = definition.values.includes(this[definition.state]) ? this[definition.state] : 'all';

                state[key] = value;

                if (value === 'all') url.searchParams.delete(`pool_${key}`);

                else url.searchParams.set(`pool_${key}`, value);

            });

            state.pageSize = this.pageSize;

            if (this.pageSize === 20) url.searchParams.delete('pool_page_size');

            else url.searchParams.set('pool_page_size', String(this.pageSize));

            try {

                const serialized = JSON.stringify(state);

                if (serialized.length <= 512) sessionStorage.setItem('omni.pool.filters.v1', serialized);

            } catch (_error) {

                // Session persistence is optional in privacy-restricted browsers.

            }

            window.history.replaceState(window.history.state, '', url);

        },

        getElementId: (suffix) => {

            if (type === 'primary') {

                return 'primary' + suffix.charAt(0).toUpperCase() + suffix.slice(1);

            }

            return suffix.charAt(0).toLowerCase() + suffix.slice(1);

        },

        async refresh(options = {}) {

            const loading = document.getElementById(this.getElementId('CredsLoading'));

            const list = document.getElementById(this.getElementId('CredsList'));

            const preserveContent = options.preserveContent ?? this.hasLoaded;

            try {

                this.restoreFilterState();

                if (loading && !preserveContent) loading.hidden = false;

                if (!preserveContent) list.innerHTML = '';

                const offset = (this.currentPage - 1) * this.pageSize;

                const errorCodeFilter = this.currentErrorCodeFilter || 'all';

                const cooldownFilter = this.currentCooldownFilter || 'all';

                const previewFilter = this.currentPreviewFilter || 'all';

                const tierFilter = this.currentTierFilter || 'all';

                const providerFilter = this.currentProviderFilter || 'all';

                const credentialKindFilter = this.currentCredentialKindFilter || 'all';

                const healthFilter = this.currentHealthFilter || 'all';

                const quotaStateFilter = this.currentQuotaStateFilter || 'all';

                const sourceFilter = this.currentSourceFilter || 'all';

                const query = new URLSearchParams({

                    offset: String(offset),

                    limit: String(this.pageSize),

                    status_filter: this.currentStatusFilter,

                    error_code_filter: errorCodeFilter,

                    cooldown_filter: cooldownFilter,

                    preview_filter: previewFilter,

                    tier_filter: tierFilter,

                    provider_filter: providerFilter,

                    credential_kind_filter: credentialKindFilter,

                    health_filter: healthFilter,

                    quota_state_filter: quotaStateFilter,

                    source_filter: sourceFilter

                });

                query.set('mode', this.type === 'primary' ? 'provider' : 'code_assist');

                const response = await fetch(

                    `${this.getEndpoint('status')}?${query.toString()}`,

                    { headers: getAuthHeaders() }

                );

                const data = await response.json();

                if (response.ok) {

                    this.data = {};

                    data.items.forEach(item => {

                        this.data[item.filename] = {

                            filename: item.filename,

                            status: {

                                disabled: item.disabled,

                                error_codes: item.error_codes || [],

                                last_success: item.last_success,

                            },

                            user_email: item.user_email,

                            credential_label: item.credential_label,

                            credential_type: item.credential_type,

                            provider: item.provider,

                            provider_variant: item.provider_variant,

                            model_count: Number.isFinite(Number(item.model_count)) ? Number(item.model_count) : 0,

                            model_cooldowns: item.model_cooldowns || {},

                            preview: item.preview,

                            tier: item.tier || 'pro',

                            enable_credit: !!item.enable_credit,

                            health: item.health || 'healthy',

                            cooldown_state: item.cooldown_state || 'no_cooldown',

                            quota_state: item.quota_state || 'unsupported',

                            source: item.source || 'managed'

                        };

                    });

                    this.totalCount = data.total;

                    this.facets = data.facets || {};

                    this.allMatchingSelection = data.selection || null;

                    this.hasLoaded = true;

                    if (data.stats) {

                        this.statsData = data.stats;

                    } else {

                        this.calculateStats();

                    }

                    this.updateStatsDisplay();

                    this.filteredData = this.data;

                    this.renderList();

                    this.updatePagination();

                    const credentialLabel = `${data.total} ${t('credential')}`;
                    let msg = t('status_loaded_creds', {credentials: credentialLabel});

                    if (this.currentStatusFilter !== 'all') {

                        msg += t('status_filter_suffix', {filter: this.currentStatusFilter === 'enabled' ? t('enable_only') : t('disable_only')});

                    }

                    // showStatus(msg, 'success');

                } else {

                    showStatus(t('status_load_failed', {error: data.detail || data.error || t('unknown_error')}), 'error');

                }

            } catch (error) {

                showStatus(t('status_net_error', {error: error.message}), 'error');

            } finally {

                if (loading) loading.hidden = true;

            }

        },

        calculateStats() {

            this.statsData = { total: this.totalCount, normal: 0, disabled: 0 };

            Object.values(this.data).forEach(credInfo => {

                if (credInfo.status.disabled) {

                    this.statsData.disabled++;

                } else {

                    this.statsData.normal++;

                }

            });

        },

        updateStatsDisplay() {

            document.getElementById(this.getElementId('StatTotal')).textContent = this.statsData.total;

            document.getElementById(this.getElementId('StatNormal')).textContent = this.statsData.normal;

            document.getElementById(this.getElementId('StatDisabled')).textContent = this.statsData.disabled;

        },

        renderList() {

            const list = document.getElementById(this.getElementId('CredsList'));

            list.innerHTML = '';
            list.classList.remove('is-empty');

            const entries = Object.entries(this.filteredData);

            if (entries.length === 0) {

                const msg = this.totalCount === 0 ? t('status_no_creds') : t('status_no_filter_data');

                list.classList.add('is-empty');

                const emptyState = document.createElement('div');
                emptyState.className = 'creds-empty-state';
                emptyState.textContent = msg;
                list.appendChild(emptyState);

                document.getElementById(this.getElementId('PaginationContainer')).style.display = 'none';

                return;

            }

            if (this.type === 'primary') {

                const providerGroups = new Map();

                entries.forEach(([, credInfo]) => {

                    const providerMeta = getCredentialProviderMeta(credInfo, this.type);

                    if (!providerGroups.has(providerMeta.id)) {

                        providerGroups.set(providerMeta.id, { providerMeta, credentials: [] });

                    }

                    providerGroups.get(providerMeta.id).credentials.push(credInfo);

                });

                providerGroups.forEach(({ providerMeta, credentials }) => {

                    list.appendChild(createCredentialProviderGroup(providerMeta, credentials, this));

                });

            } else {

                entries.forEach(([, credInfo]) => {

                    list.appendChild(createCredCard(credInfo, this));

                });

            }

            document.getElementById(this.getElementId('PaginationContainer')).style.display =

                this.getTotalPages() > 1 ? 'flex' : 'none';

            this.updateBatchControls();

        },

        getTotalPages() {

            return Math.ceil(this.totalCount / this.pageSize);

        },

        updatePagination() {

            const totalPages = this.getTotalPages();

            const startItem = (this.currentPage - 1) * this.pageSize + 1;

            const endItem = Math.min(this.currentPage * this.pageSize, this.totalCount);

            document.getElementById(this.getElementId('PaginationInfo')).textContent =

                t('status_page_info', {page: this.currentPage, total: totalPages, start: startItem, end: endItem, count: this.totalCount});

            document.getElementById(this.getElementId('PrevPageBtn')).disabled = this.currentPage <= 1;

            document.getElementById(this.getElementId('NextPageBtn')).disabled = this.currentPage >= totalPages;

        },

        changePage(direction) {

            const newPage = this.currentPage + direction;

            if (newPage >= 1 && newPage <= this.getTotalPages()) {

                if (this.selectionScope === 'page') this.clearSelection();

                this.currentPage = newPage;

                this.refresh();

            }

        },

        changePageSize() {

            this.pageSize = parseInt(document.getElementById(this.getElementId('PageSizeSelect')).value);

            this.currentPage = 1;

            if (this.selectionScope === 'page') this.clearSelection();

            this.persistFilterState();

            this.refresh();

        },

        applyStatusFilter() {

            Object.values(this.getFilterDefinitions()).forEach((definition) => {

                const element = document.getElementById(this.getElementId(definition.suffix));

                if (element && definition.values.includes(element.value)) {

                    this[definition.state] = element.value;

                }

            });

            this.clearSelection();

            this.currentPage = 1;

            this.persistFilterState();

            this.refresh();

        },

        clearSelection() {

            this.selectionScope = 'page';

            this.selectedFiles.clear();

            this.updateBatchControls();

        },

        selectAllMatching() {

            if (!this.allMatchingSelection?.token || this.allMatchingSelection.matching_count < 1) return;

            this.selectionScope = 'all_matching';

            this.selectedFiles.clear();

            this.updateBatchControls();

        },

        toggleFileSelection(filename) {

            if (this.selectionScope === 'all_matching') {

                this.selectionScope = 'page';

                this.selectedFiles = new Set(Object.keys(this.data));

            }

            if (this.selectedFiles.has(filename)) this.selectedFiles.delete(filename);

            else this.selectedFiles.add(filename);

            this.updateBatchControls();

        },

        toggleVisibleSelection(checked) {

            this.selectionScope = 'page';

            this.selectedFiles.clear();

            if (checked) Object.keys(this.data).forEach(filename => this.selectedFiles.add(filename));

            this.updateBatchControls();

        },

        updateBatchControls() {

            const allMatching = this.selectionScope === 'all_matching';

            const selectedCount = allMatching

                ? Number(this.allMatchingSelection?.matching_count || 0)

                : this.selectedFiles.size;

            document.getElementById(this.getElementId('SelectedCount')).textContent = allMatching

                ? t('pool.selection.selected_all', {count: selectedCount})

                : t('pool.selection.selected_page', {count: selectedCount});

            const batchBtnNames = ['Enable', 'Disable', 'Delete', 'Verify', 'Preview'];

            if (this.type === 'primary') {

                batchBtnNames.push('EnableCredit');

                batchBtnNames.push('DisableCredit');

            }

            const batchBtns = batchBtnNames.map(action =>

                document.getElementById(this.getElementId(`Batch${action}Btn`))

            );

            batchBtns.forEach(btn => btn && (btn.disabled = selectedCount === 0));

            if (this.type === 'primary') {

                const selectedCredentials = Array.from(this.selectedFiles)

                    .map(filename => this.data[filename])

                    .filter(Boolean);

                const supportsCreditActions = selectedCredentials.length > 0

                    && selectedCredentials.every((credInfo) => (

                        getCredentialProviderMeta(credInfo, this.type).id === 'google_antigravity'

                    ));

                ['EnableCredit', 'DisableCredit'].forEach((action) => {

                    const button = document.getElementById(this.getElementId(`Batch${action}Btn`));

                    if (button) button.disabled = !supportsCreditActions;

                });

            }

            const selectAllCheckbox = document.getElementById(this.getElementId('SelectAllCheckbox'));

            const selectAllMatchingButton = document.getElementById(this.getElementId('SelectAllMatchingBtn'));

            const clearSelectionButton = document.getElementById(this.getElementId('ClearSelectionBtn'));

            if (clearSelectionButton) clearSelectionButton.hidden = selectedCount === 0;

            if (!selectAllCheckbox) return;

            const checkboxes = document.querySelectorAll(`.${this.getElementId('file-checkbox')}`);

            const currentPageSelectedCount = Array.from(checkboxes)

                .filter(cb => this.selectedFiles.has(cb.getAttribute('data-filename'))).length;

            if (allMatching) {

                selectAllCheckbox.indeterminate = false;

                selectAllCheckbox.checked = true;

            } else if (currentPageSelectedCount === 0) {

                selectAllCheckbox.indeterminate = false;

                selectAllCheckbox.checked = false;

            } else if (currentPageSelectedCount === checkboxes.length) {

                selectAllCheckbox.indeterminate = false;

                selectAllCheckbox.checked = true;

            } else {

                selectAllCheckbox.indeterminate = true;

            }

            checkboxes.forEach(cb => {

                cb.checked = allMatching || this.selectedFiles.has(cb.getAttribute('data-filename'));

            });

            if (selectAllMatchingButton) {

                const pageIsSelected = checkboxes.length > 0 && currentPageSelectedCount === checkboxes.length;

                selectAllMatchingButton.hidden = allMatching

                    || !pageIsSelected

                    || selectedCount >= this.totalCount

                    || !this.allMatchingSelection?.token;

                selectAllMatchingButton.textContent = t('pool.selection.select_all_matching', {count: this.totalCount});

            }

        },

        async action(filename, action) {

            try {

                const response = await fetch(`${this.getEndpoint('action')}?${this.getModeParam()}`, {

                    method: 'POST',

                    headers: getAuthHeaders(),

                    body: JSON.stringify({ filename, action })

                });

                const data = await response.json();

                if (response.ok) {

                    showStatus(data.message || t('status_action_success', {action: action}), 'success');

                    if (action === 'delete') {

                        this.selectedFiles.delete(filename);

                        delete AppState.quotaPreviewCache[filename];

                        Object.entries(AppState.credentialCardIndex).forEach(([pathId, context]) => {

                            if (context.filename === filename) delete AppState.credentialCardIndex[pathId];

                        });

                        this.updateBatchControls();

                    }

                    await this.refresh();

                    if (action === 'delete') await refreshUsageStats();

                } else {

                    showStatus(t('status_action_failed', {error: data.detail || data.error || t('unknown_error')}), 'error');

                }

            } catch (error) {

                showStatus(t('status_net_error', {error: error.message}), 'error');

            }

        },

        async batchAction(action) {

            const selectedFiles = Array.from(this.selectedFiles);

            if (selectedFiles.length === 0) {

                showStatus(t('please_select_the_files_to_operate'), 'error');

                return;

            }

            const actionNames = {

                enable: t('action_enable'),

                disable: t('action_disable'),

                delete: t('action_delete'),

                enable_credit: t('action_enable_credit'),

                disable_credit: t('action_disable_credit')

            };

            const confirmationTitles = {

                enable: t('confirm_batch_enable_title'),

                disable: t('confirm_batch_disable_title'),

                delete: t('confirm_batch_delete_title'),

                enable_credit: t('confirm_batch_enable_credit_title'),

                disable_credit: t('confirm_batch_disable_credit_title')

            };

            const confirmationMessages = {

                enable: t('confirm_batch_enable', {count: selectedFiles.length}),

                disable: t('confirm_batch_disable', {count: selectedFiles.length}),

                delete: t('confirm_batch_delete', {count: selectedFiles.length}),

                enable_credit: t('confirm_batch_enable_credit', {count: selectedFiles.length}),

                disable_credit: t('confirm_batch_disable_credit', {count: selectedFiles.length})

            };

            const actionLabel = actionNames[action] || action;

            const confirmMsg = confirmationMessages[action]

                || `${actionLabel} ${selectedFiles.length} selected credentials?`;

            const confirmOptions = {

                title: confirmationTitles[action] || t('confirm_manage_credentials_title'),

                confirmLabel: actionLabel

            };

            if (!(await showConfirmModal(confirmMsg, confirmOptions))) return;

            try {

                showStatus(t('status_batch_in_progress', {action: actionLabel}), 'info');

                const previewResponse = await fetch(`${this.getEndpoint('batchAction')}?${this.getModeParam()}`, {

                    method: 'POST',

                    headers: getAuthHeaders(),

                    body: JSON.stringify({ action, filenames: selectedFiles, preview: true })

                });

                const previewData = await previewResponse.json();

                if (!previewResponse.ok) {

                    const previewError = previewData.error?.message || previewData.detail || t('unknown_error');

                    showStatus(t('status_batch_failed', {error: previewError}), 'error');

                    return;

                }

                const idempotencyKey = crypto.randomUUID();

                const response = await fetch(`${this.getEndpoint('batchAction')}?${this.getModeParam()}`, {

                    method: 'POST',

                    headers: getAuthHeaders(),

                    body: JSON.stringify({

                        action,

                        filenames: selectedFiles,

                        preview_token: previewData.preview_token,

                        idempotency_key: idempotencyKey

                    })

                });

                const data = await response.json();

                if (response.ok) {

                    const successCount = data.success_count ?? data.succeeded ?? 0;

                    showStatus(t('status_batch_complete', {success: successCount, total: selectedFiles.length}), 'success');

                    if (action === 'delete') {

                        selectedFiles.forEach((filename) => {

                            delete AppState.quotaPreviewCache[filename];

                        });

                        Object.entries(AppState.credentialCardIndex).forEach(([pathId, context]) => {

                            if (selectedFiles.includes(context.filename)) delete AppState.credentialCardIndex[pathId];

                        });

                    }

                    this.selectedFiles.clear();

                    this.updateBatchControls();

                    await this.refresh();

                    if (action === 'delete') await refreshUsageStats();

                } else {

                    const operationError = data.error?.message || data.detail || t('unknown_error');

                    showStatus(t('status_batch_failed', {error: operationError}), 'error');

                }

            } catch (error) {

                showStatus(t('status_batch_net_error', {error: error.message}), 'error');

            }

        }

    };

}

// =====================================================================

// =====================================================================
