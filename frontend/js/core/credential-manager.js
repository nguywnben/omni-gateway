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

        currentStatusFilter: 'all',

        currentErrorCodeFilter: 'all',

        currentCooldownFilter: 'all',

        currentPreviewFilter: 'all',

        currentTierFilter: 'all',

        currentProviderFilter: 'all',

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

        getElementId: (suffix) => {

            if (type === 'primary') {

                return 'primary' + suffix.charAt(0).toUpperCase() + suffix.slice(1);

            }

            return suffix.charAt(0).toLowerCase() + suffix.slice(1);

        },

        async refresh() {

            const loading = document.getElementById(this.getElementId('CredsLoading'));

            const list = document.getElementById(this.getElementId('CredsList'));

            try {

                if (loading) loading.hidden = false;

                list.innerHTML = '';

                const offset = (this.currentPage - 1) * this.pageSize;

                const errorCodeFilter = this.currentErrorCodeFilter || 'all';

                const cooldownFilter = this.currentCooldownFilter || 'all';

                const previewFilter = this.currentPreviewFilter || 'all';

                const tierFilter = this.currentTierFilter || 'all';

                const providerFilter = this.currentProviderFilter || 'all';

                const response = await fetch(

                    `${this.getEndpoint('status')}?offset=${offset}&limit=${this.pageSize}&status_filter=${this.currentStatusFilter}&error_code_filter=${errorCodeFilter}&cooldown_filter=${cooldownFilter}&preview_filter=${previewFilter}&tier_filter=${tierFilter}&provider_filter=${providerFilter}&${this.getModeParam()}`,

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

                            model_count: Number.isFinite(Number(item.model_count)) ? Number(item.model_count) : 0,

                            model_cooldowns: item.model_cooldowns || {},

                            preview: item.preview,

                            tier: item.tier || 'pro',

                            enable_credit: !!item.enable_credit

                        };

                    });

                    this.totalCount = data.total;

                    if (data.stats) {

                        this.statsData = data.stats;

                    } else {

                        this.calculateStats();

                    }

                    this.updateStatsDisplay();

                    this.filteredData = this.data;

                    this.renderList();

                    this.updatePagination();

                    const credentialType = type === 'primary' ? 'provider credential' : 'credential';
                    const credentialLabel = `${data.total} ${credentialType}${data.total === 1 ? '' : 's'}`;
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

                this.currentPage = newPage;

                this.refresh();

            }

        },

        changePageSize() {

            this.pageSize = parseInt(document.getElementById(this.getElementId('PageSizeSelect')).value);

            this.currentPage = 1;

            this.refresh();

        },

        applyStatusFilter() {

            this.currentStatusFilter = document.getElementById(this.getElementId('StatusFilter')).value;

            const errorCodeFilterEl = document.getElementById(this.getElementId('ErrorCodeFilter'));

            const cooldownFilterEl = document.getElementById(this.getElementId('CooldownFilter'));

            const previewFilterEl = document.getElementById(this.getElementId('PreviewFilter'));

            const tierFilterEl = document.getElementById(this.getElementId('TierFilter'));

            const providerFilterEl = document.getElementById(this.getElementId('ProviderFilter'));

            this.currentErrorCodeFilter = errorCodeFilterEl ? errorCodeFilterEl.value : 'all';

            this.currentCooldownFilter = cooldownFilterEl ? cooldownFilterEl.value : 'all';

            this.currentPreviewFilter = previewFilterEl ? previewFilterEl.value : 'all';

            this.currentProviderFilter = providerFilterEl ? providerFilterEl.value : 'all';

            if (tierFilterEl) {

                const tierIsRelevant = !['google_ai_studio', 'grok', 'xai_console', 'xai'].includes(this.currentProviderFilter);

                tierFilterEl.disabled = !tierIsRelevant;

                if (!tierIsRelevant) tierFilterEl.value = 'all';

                this.currentTierFilter = tierIsRelevant ? tierFilterEl.value : 'all';

            } else {

                this.currentTierFilter = 'all';

            }

            this.selectedFiles.clear();

            this.currentPage = 1;

            this.refresh();

        },

        updateBatchControls() {

            const selectedCount = this.selectedFiles.size;

            document.getElementById(this.getElementId('SelectedCount')).textContent = t('status_selected_items', {count: selectedCount});

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

            if (!selectAllCheckbox) return;

            const checkboxes = document.querySelectorAll(`.${this.getElementId('file-checkbox')}`);

            const currentPageSelectedCount = Array.from(checkboxes)

                .filter(cb => this.selectedFiles.has(cb.getAttribute('data-filename'))).length;

            if (currentPageSelectedCount === 0) {

                selectAllCheckbox.indeterminate = false;

                selectAllCheckbox.checked = false;

            } else if (currentPageSelectedCount === checkboxes.length) {

                selectAllCheckbox.indeterminate = false;

                selectAllCheckbox.checked = true;

            } else {

                selectAllCheckbox.indeterminate = true;

            }

            checkboxes.forEach(cb => {

                cb.checked = this.selectedFiles.has(cb.getAttribute('data-filename'));

            });

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

                const response = await fetch(`${this.getEndpoint('batchAction')}?${this.getModeParam()}`, {

                    method: 'POST',

                    headers: getAuthHeaders(),

                    body: JSON.stringify({ action, filenames: selectedFiles })

                });

                const data = await response.json();

                if (response.ok) {

                    const successCount = data.success_count || data.succeeded;

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

                    showStatus(t('status_batch_failed', {error: data.detail || data.error || t('unknown_error')}), 'error');

                }

            } catch (error) {

                showStatus(t('status_batch_net_error', {error: error.message}), 'error');

            }

        }

    };

}

// =====================================================================

// =====================================================================
