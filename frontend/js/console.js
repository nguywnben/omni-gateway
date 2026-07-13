// Omni Gateway management console: console.

async function refreshSetupStatus() {

    try {

        const response = await fetch('./api/auth/setup/status');

        const data = await response.json();

        AppState.setupRequired = Boolean(data.setup_required);

        const setupTokenGroup = document.getElementById('setupTokenGroup');

        if (setupTokenGroup) {

            setupTokenGroup.classList.toggle('hidden', !data.setup_token_required);

        }

        if (AppState.setupRequired) {

            AppState.authenticated = false;

        }

        return AppState.setupRequired;

    } catch (error) {

        AppState.setupRequired = false;

        return false;

    }

}

async function completeInitialSetup() {

    const password = document.getElementById('setupPassword')?.value || '';

    const confirmPassword = document.getElementById('setupPasswordConfirm')?.value || '';

    const setupToken = document.getElementById('setupToken')?.value || '';

    if (password.length < 8) {

        showStatus('Password must be at least 8 characters.', 'error');

        return;

    }

    if (password !== confirmPassword) {

        showStatus('Passwords do not match.', 'error');

        return;

    }

    try {

        const response = await fetch('./api/auth/setup', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({

                password,

                confirm_password: confirmPassword,

                setup_token: setupToken || undefined

            })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.setupRequired = false;

            AppState.authenticated = true;

            showStatus('Initial setup completed.', 'success');

            navigate('/dashboard');

            await fetchAndDisplayVersion();

        } else {

            showStatus(data.detail || data.error || 'Initial setup failed.', 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function login() {

    const password = document.getElementById('loginPassword').value;

    if (!password) {

        showStatus(t('please_enter_the_password'), 'error');

        return;

    }

    try {

        const response = await fetch('./api/auth/login', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ password })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.authenticated = true;

            showStatus(t('login_successful_dup'), 'success');

            navigate('/dashboard');

            await fetchAndDisplayVersion();

        } else {

            if (response.status === 428) {

                AppState.setupRequired = true;

                navigate('/setup', false);

                return;

            }

            if (response.status === 401) {

                showStatus(t('login_failed_incorrect_password'), 'error');

                return;

            }

            showStatus(data.detail || data.error || t('login_failed'), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    }

}

async function autoLogin() {

    if (AppState.setupRequired) {

        navigate('/setup', false);

        return false;

    }

    try {

        const response = await fetch('./api/config/get', {

            headers: getAuthHeaders()

        });

        if (response.ok) {

            AppState.authenticated = true;

            // showStatus(t('autologin_successful'), 'success');

            navigate(window.location.pathname, false);

            return true;

        } else {

            AppState.authenticated = false;

            navigate('/login', false);

            return false;

        }

    } catch (error) {

        AppState.authenticated = false;

        navigate('/login', false);

        return false;

    }

}

async function logout() {

    try {

        await fetch('./api/auth/logout', {method: 'POST'});

    } catch (error) {

        console.warn('Failed to notify the server about sign-out.', error);

    }

    AppState.authenticated = false;

    showStatus(t('logged_out'), 'info');

    const passwordInput = document.getElementById('loginPassword');

    if (passwordInput) passwordInput.value = '';

    navigate('/login', false);

}

// =====================================================================

// =====================================================================

function updateTabSlider(targetTab, animate = true) {

    const slider = document.querySelector('.tab-slider');

    const tabs = document.querySelector('.tabs');

    if (!slider || !tabs || !targetTab) return;

    const tabLeft = targetTab.offsetLeft;

    const tabWidth = targetTab.offsetWidth;

    const tabsWidth = tabs.scrollWidth;

    const rightValue = tabsWidth - tabLeft - tabWidth;

    if (animate) {

        slider.style.left = `${tabLeft}px`;

        slider.style.right = `${rightValue}px`;

    } else {

        slider.style.transition = 'none';

        slider.style.left = `${tabLeft}px`;

        slider.style.right = `${rightValue}px`;

        slider.offsetHeight;

        slider.style.transition = '';

    }

}

function initTabSlider() {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) {

        updateTabSlider(activeTab, false);

    }

}

document.addEventListener('DOMContentLoaded', initTabSlider);

window.addEventListener('resize', () => {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) updateTabSlider(activeTab, false);

    if (window.innerWidth > 960) setMobileMenuState(false);

});

function switchTab(tabName) {

    const route = TAB_MAP[tabName] || '/dashboard';

    navigate(route, true);

}

const PROVIDER_WORKSPACES = {
    google_antigravity: {
        selectorId: 'providerSelectorGoogleAntigravity',
        panelId: 'providerWorkspaceGoogleAntigravity'
    },
    google_ai_studio: {
        selectorId: 'providerSelectorGoogleAiStudio',
        panelId: 'providerWorkspaceGoogleAiStudio'
    }
};

function selectProviderWorkspace(providerId, focusSelector = false) {
    const selected = PROVIDER_WORKSPACES[providerId];
    if (!selected) return;

    AppState.activeProviderWorkspace = providerId;

    Object.entries(PROVIDER_WORKSPACES).forEach(([id, workspace]) => {
        const selector = document.getElementById(workspace.selectorId);
        const panel = document.getElementById(workspace.panelId);
        const isActive = id === providerId;

        selector?.classList.toggle('active', isActive);
        selector?.setAttribute('aria-selected', String(isActive));
        if (selector) selector.tabIndex = isActive ? 0 : -1;
        panel?.classList.toggle('hidden', !isActive);
    });

    if (focusSelector) {
        document.getElementById(selected.selectorId)?.focus();
    }
}

function initProviderWorkspaceSelector() {
    const providerIds = Object.keys(PROVIDER_WORKSPACES);

    providerIds.forEach((providerId, index) => {
        const selector = document.getElementById(PROVIDER_WORKSPACES[providerId].selectorId);
        selector?.addEventListener('keydown', (event) => {
            if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
            event.preventDefault();

            let nextIndex = index;
            if (event.key === 'ArrowLeft') nextIndex = (index - 1 + providerIds.length) % providerIds.length;
            if (event.key === 'ArrowRight') nextIndex = (index + 1) % providerIds.length;
            if (event.key === 'Home') nextIndex = 0;
            if (event.key === 'End') nextIndex = providerIds.length - 1;

            selectProviderWorkspace(providerIds[nextIndex], true);
        });
    });

    selectProviderWorkspace(AppState.activeProviderWorkspace);
}

document.addEventListener('DOMContentLoaded', initProviderWorkspaceSelector);

function triggerTabDataLoad(tabName) {

    if (tabName === 'dashboard') {

        refreshUsageStats();

        updateEndpointUrls();
    }

    if (tabName === 'pool') {
        AppState.primaryCreds.refresh();
    }

    if (tabName === 'models') loadModelCatalog();

    if (tabName === 'providers') {
        loadAntigravitySettings();
        loadGoogleAIStudioSettings();
    }

    if (tabName === 'config') loadConfig();

    if (tabName === 'logs') connectWebSocket();

}

const MODEL_PROVIDER_META = {
    google_antigravity: {
        name: 'Google Antigravity',
        logo: '/frontend/assets/providers/google-antigravity-logo.png'
    },
    google_ai_studio: {
        name: 'Google AI Studio',
        logo: '/frontend/assets/providers/google-ai-studio-logo.png'
    }
};

function modelProviderMeta(providerId) {
    if (MODEL_PROVIDER_META[providerId]) return MODEL_PROVIDER_META[providerId];
    const name = String(providerId || 'Provider')
        .split(/[_-]+/)
        .filter(Boolean)
        .map(word => ['ai', 'api'].includes(word.toLowerCase())
            ? word.toUpperCase()
            : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
    return { name, logo: '' };
}

function modelCatalogEntry(modelId) {
    return AppState.modelCatalog.find(entry => entry.model_id === modelId) || {
        model_id: modelId,
        providers: [],
        routable_providers: [],
        blacklisted_providers: [],
        available: false
    };
}

function appendModelProviderBadges(container, providers) {
    const values = Array.isArray(providers) ? providers : [];
    if (values.length === 0) {
        const unavailable = document.createElement('span');
        unavailable.className = 'model-provider-badge unavailable';
        unavailable.textContent = 'Unavailable';
        container.appendChild(unavailable);
        return;
    }
    values.forEach(providerId => {
        const meta = modelProviderMeta(providerId);
        const badge = document.createElement('span');
        badge.className = 'model-provider-badge';
        if (meta.logo) {
            const logo = document.createElement('img');
            logo.src = meta.logo;
            logo.alt = '';
            badge.appendChild(logo);
        }
        badge.appendChild(document.createTextNode(meta.name));
        container.appendChild(badge);
    });
}

function updateModelPoolSummary() {
    const available = AppState.modelCatalog.filter(entry => entry.available).length;
    const unavailable = AppState.selectedModels.filter(
        modelId => !modelCatalogEntry(modelId).available
    ).length;
    const availableEl = document.getElementById('modelStatAvailable');
    const selectedEl = document.getElementById('modelStatSelected');
    const unavailableEl = document.getElementById('modelStatUnavailable');
    if (availableEl) availableEl.textContent = String(available);
    if (selectedEl) selectedEl.textContent = String(AppState.selectedModels.length);
    if (unavailableEl) unavailableEl.textContent = String(unavailable);

    const status = document.getElementById('modelPoolStatus');
    if (status) {
        const ready = AppState.modelPoolEnabled && AppState.selectedModels.length > 0 && unavailable < AppState.selectedModels.length;
        status.textContent = ready ? 'Ready' : 'Not configured';
        status.className = ready ? 'status-badge success' : 'status-badge muted';
    }
}

function formatModelBlacklistTime(timestamp) {
    const date = new Date(Number(timestamp || 0) * 1000);
    if (Number.isNaN(date.getTime())) return 'Unknown time';
    return new Intl.DateTimeFormat('en', {
        dateStyle: 'medium',
        timeStyle: 'short'
    }).format(date);
}

function renderModelBlacklist() {
    const list = document.getElementById('modelBlacklistList');
    const count = document.getElementById('modelBlacklistCount');
    const clearButton = document.getElementById('clearModelBlacklistBtn');
    if (!list) return;

    const entries = Array.isArray(AppState.modelBlacklist) ? AppState.modelBlacklist : [];
    if (count) count.textContent = `${entries.length} ${entries.length === 1 ? 'route' : 'routes'}`;
    if (clearButton) clearButton.classList.toggle('hidden', entries.length === 0);
    list.replaceChildren();

    if (entries.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'model-empty-state';
        empty.textContent = 'No model routes are blacklisted.';
        list.appendChild(empty);
        return;
    }

    entries.forEach(entry => {
        const item = document.createElement('div');
        item.className = 'model-blacklist-item';

        const details = document.createElement('div');
        details.className = 'model-blacklist-details';
        const identity = document.createElement('div');
        identity.className = 'model-blacklist-identity';
        const model = document.createElement('strong');
        model.textContent = entry.model_id;
        const providerBadges = document.createElement('div');
        providerBadges.className = 'model-provider-badges';
        const providerMeta = modelProviderMeta(entry.provider_id);
        const providerBadge = document.createElement('span');
        providerBadge.className = 'model-provider-badge unavailable';
        if (providerMeta.logo) {
            const logo = document.createElement('img');
            logo.src = providerMeta.logo;
            logo.alt = '';
            providerBadge.appendChild(logo);
        }
        providerBadge.appendChild(document.createTextNode(providerMeta.name));
        providerBadges.appendChild(providerBadge);
        identity.append(model, providerBadges);

        const metadata = document.createElement('div');
        metadata.className = 'model-blacklist-meta';
        const status = document.createElement('span');
        status.textContent = 'HTTP 404';
        const occurrences = document.createElement('span');
        const failureCount = Math.max(1, Number(entry.failure_count || 1));
        occurrences.textContent = `${failureCount} ${failureCount === 1 ? 'occurrence' : 'occurrences'}`;
        const lastSeen = document.createElement('span');
        lastSeen.textContent = `Last seen ${formatModelBlacklistTime(entry.last_seen_at)}`;
        metadata.append(status, occurrences, lastSeen);
        details.append(identity, metadata);

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'btn btn-secondary btn-small';
        removeButton.textContent = 'Remove';
        removeButton.title = 'Restore this provider-model route';
        removeButton.addEventListener('click', () => removeModelBlacklistEntry(
            entry.provider_id,
            entry.model_id,
            removeButton
        ));
        item.append(details, removeButton);
        list.appendChild(item);
    });
}

function restoreModelRoutesLocally(restoredEntries) {
    const restoredKeys = new Set(
        restoredEntries.map(entry => `${entry.provider_id}\u0000${entry.model_id}`)
    );
    AppState.modelBlacklist = AppState.modelBlacklist.filter(entry => (
        !restoredKeys.has(`${entry.provider_id}\u0000${entry.model_id}`)
    ));
    AppState.modelCatalog = AppState.modelCatalog.map(entry => {
        const restoredProviders = new Set(
            restoredEntries
                .filter(value => value.model_id === entry.model_id)
                .map(value => value.provider_id)
        );
        if (restoredProviders.size === 0) return entry;
        const blacklistedProviders = (entry.blacklisted_providers || [])
            .filter(value => !restoredProviders.has(value));
        const routableProviders = (entry.providers || [])
            .filter(value => !blacklistedProviders.includes(value));
        return {
            ...entry,
            blacklisted_providers: blacklistedProviders,
            routable_providers: routableProviders,
            available: routableProviders.length > 0
        };
    });
    renderSelectedModels();
    renderModelCatalog();
    renderModelBlacklist();
}

function restoreModelRouteLocally(providerId, modelId) {
    restoreModelRoutesLocally([{ provider_id: providerId, model_id: modelId }]);
}

async function removeModelBlacklistEntry(providerId, modelId, button) {
    if (button) button.disabled = true;
    try {
        const response = await fetch(
            `./api/model-blacklist/${encodeURIComponent(providerId)}/models/${encodeURIComponent(modelId)}`,
            { method: 'DELETE', headers: getAuthHeaders() }
        );
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        restoreModelRouteLocally(providerId, modelId);
        showStatus(data.message || 'Model route removed from blacklist.', 'success');
    } catch (error) {
        showStatus(`Failed to remove the model route: ${error.message}`, 'error');
        if (button) button.disabled = false;
    }
}

async function clearModelBlacklist() {
    const confirmed = await showConfirmModal(
        'Restore every provider-model route currently excluded after an upstream 404 response?',
        {
            title: 'Clear Model Blacklist',
            confirmLabel: 'Clear all'
        }
    );
    if (!confirmed) return;

    const button = document.getElementById('clearModelBlacklistBtn');
    if (button) button.disabled = true;
    try {
        const response = await fetch('./api/model-blacklist', {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        restoreModelRoutesLocally([...AppState.modelBlacklist]);
        showStatus(data.message || 'Model blacklist cleared.', 'success');
    } catch (error) {
        showStatus(`Failed to clear the model blacklist: ${error.message}`, 'error');
    } finally {
        if (button) button.disabled = false;
    }
}

function createModelOrderButton(label, symbol, disabled, handler) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'model-order-button';
    button.setAttribute('aria-label', label);
    button.title = label;
    button.textContent = symbol;
    button.disabled = disabled;
    button.addEventListener('click', handler);
    return button;
}

function renderSelectedModels() {
    const list = document.getElementById('selectedModelList');
    if (!list) return;
    list.replaceChildren();

    if (AppState.selectedModels.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'model-empty-state';
        empty.textContent = 'Select at least one provider model to activate omway.';
        list.appendChild(empty);
        updateModelPoolSummary();
        return;
    }

    AppState.selectedModels.forEach((modelId, index) => {
        const entry = modelCatalogEntry(modelId);
        const item = document.createElement('div');
        item.className = 'selected-model-item';

        const order = document.createElement('span');
        order.className = 'selected-model-order';
        order.textContent = String(index + 1);

        const details = document.createElement('div');
        details.className = 'selected-model-details';
        const name = document.createElement('strong');
        name.textContent = modelId;
        const providers = document.createElement('div');
        providers.className = 'model-provider-badges';
        appendModelProviderBadges(providers, entry.routable_providers || entry.providers);
        details.append(name, providers);

        const actions = document.createElement('div');
        actions.className = 'model-order-actions';
        actions.append(
            createModelOrderButton('Move model up', '↑', index === 0, () => moveSelectedModel(index, -1)),
            createModelOrderButton('Move model down', '↓', index === AppState.selectedModels.length - 1, () => moveSelectedModel(index, 1)),
            createModelOrderButton('Remove model', '×', false, () => removeSelectedModel(modelId))
        );

        item.append(order, details, actions);
        list.appendChild(item);
    });
    updateModelPoolSummary();
}

function renderModelCatalog() {
    const list = document.getElementById('modelCatalogList');
    if (!list) return;
    const query = document.getElementById('modelCatalogSearch')?.value.trim().toLowerCase() || '';
    const entries = AppState.modelCatalog.filter(entry => {
        if (!query) return true;
        return entry.model_id.toLowerCase().includes(query)
            || entry.providers.some(provider => modelProviderMeta(provider).name.toLowerCase().includes(query));
    });
    list.replaceChildren();

    if (entries.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'model-empty-state';
        empty.textContent = AppState.modelCatalog.length
            ? 'No models match this search.'
            : 'No models are available. Add or enable a provider credential, then refresh the catalog.';
        list.appendChild(empty);
        return;
    }

    entries.forEach(entry => {
        const label = document.createElement('label');
        label.className = `model-catalog-item${entry.available ? '' : ' unavailable'}`;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = AppState.selectedModels.includes(entry.model_id);
        checkbox.disabled = !entry.available && !checkbox.checked;
        checkbox.addEventListener('change', () => toggleModelSelection(entry.model_id, checkbox.checked));

        const details = document.createElement('div');
        details.className = 'model-catalog-details';
        const name = document.createElement('strong');
        name.textContent = entry.model_id;
        const providers = document.createElement('div');
        providers.className = 'model-provider-badges';
        appendModelProviderBadges(providers, entry.routable_providers || entry.providers);
        details.append(name, providers);
        label.append(checkbox, details);
        list.appendChild(label);
    });
}

function toggleModelSelection(modelId, selected) {
    if (selected && !AppState.selectedModels.includes(modelId)) {
        AppState.selectedModels.push(modelId);
    } else if (!selected) {
        AppState.selectedModels = AppState.selectedModels.filter(value => value !== modelId);
    }
    renderSelectedModels();
    renderModelCatalog();
}

function moveSelectedModel(index, offset) {
    const nextIndex = index + offset;
    if (index < 0 || nextIndex < 0 || nextIndex >= AppState.selectedModels.length) return;
    const values = [...AppState.selectedModels];
    [values[index], values[nextIndex]] = [values[nextIndex], values[index]];
    AppState.selectedModels = values;
    renderSelectedModels();
    renderModelCatalog();
}

function removeSelectedModel(modelId) {
    AppState.selectedModels = AppState.selectedModels.filter(value => value !== modelId);
    renderSelectedModels();
    renderModelCatalog();
}

async function loadModelCatalog(forceRefresh = false) {
    const loading = document.getElementById('modelCatalogLoading');
    const workspace = document.getElementById('modelPoolWorkspace');
    const refreshButton = document.getElementById('refreshModelCatalogBtn');
    if (loading) loading.classList.remove('hidden');
    if (workspace) workspace.classList.add('hidden');
    if (refreshButton) refreshButton.disabled = true;
    try {
        const response = await fetch(`./api/model-catalog${forceRefresh ? '?refresh=true' : ''}`, {
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        AppState.modelCatalog = Array.isArray(data.catalog) ? data.catalog : [];
        AppState.modelBlacklist = Array.isArray(data.blacklist) ? data.blacklist : [];
        AppState.selectedModels = Array.isArray(data.pool?.selected_models)
            ? [...data.pool.selected_models]
            : [];
        AppState.modelPoolEnabled = data.pool?.enabled !== false;
        renderSelectedModels();
        renderModelCatalog();
        renderModelBlacklist();
        if (workspace) workspace.classList.remove('hidden');
        if (forceRefresh) showStatus('Provider model catalog refreshed.', 'success');
    } catch (error) {
        showStatus(`Failed to load the provider model catalog: ${error.message}`, 'error');
    } finally {
        if (loading) loading.classList.add('hidden');
        if (refreshButton) refreshButton.disabled = false;
    }
}

async function saveModelPool() {
    const button = document.getElementById('saveModelPoolBtn');
    if (button) button.disabled = true;
    try {
        const response = await fetch('./api/model-pools/omway', {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                selected_models: AppState.selectedModels,
                enabled: AppState.selectedModels.length > 0
            })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        AppState.selectedModels = [...(data.pool?.selected_models || AppState.selectedModels)];
        AppState.modelPoolEnabled = data.pool?.enabled !== false;
        renderSelectedModels();
        renderModelCatalog();
        showStatus(data.message || 'Virtual model updated.', 'success');
    } catch (error) {
        showStatus(`Failed to save omway: ${error.message}`, 'error');
    } finally {
        if (button) button.disabled = false;
    }
}

// =====================================================================

// =====================================================================

async function startAuth() {

    const projectId = document.getElementById('projectId').value.trim();

    AppState.currentProjectId = projectId || null;

    const btn = document.getElementById('getAuthBtn');

    btn.disabled = true;

    btn.textContent = t('fetching_authentication_link');

    try {

        const requestBody = projectId ? { project_id: projectId } : {};

        showStatus(projectId ? t('generating_authentication_link_usin') : t('attempting_to_autodetect_project_id'), 'info');

        const response = await fetch('./api/auth/start', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify(requestBody)

        });

        const data = await response.json();

        if (response.ok) {

            document.getElementById('authUrl').href = data.auth_url;

            document.getElementById('authUrl').textContent = data.auth_url;

            document.getElementById('authUrlSection').classList.remove('hidden');

            const msg = data.auto_project_detection

                ? t('authentication_link_generated_proje_dup_dup')

                : t('authentication_link_generated_proje', {data_detected_project_id: data.detected_project_id});

            showStatus(msg, 'info');

            AppState.authInProgress = true;

        } else {

            showStatus(t('error_dataerror_failed_to_fetch_aut', {data_error: data.detail || data.error || t('failed_to_fetch_authentication_link')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_authentication_link');

    }

}

async function getCredentials() {

    if (!AppState.authInProgress) {

        showStatus(t('please_fetch_the_authentication_lin'), 'error');

        return;

    }

    const btn = document.getElementById('getCredsBtn');

    btn.disabled = true;

    btn.textContent = t('waiting_for_oauth_callback');

    try {

        showStatus(t('waiting_for_oauth_callback_this_may'), 'info');

        const requestBody = AppState.currentProjectId ? { project_id: AppState.currentProjectId } : {};

        const response = await fetch('./api/auth/callback', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify(requestBody)

        });

        const data = await response.json();

        if (response.ok) {

            document.getElementById('credentialsContent').textContent = JSON.stringify(data.credentials, null, 2);

            const msg = data.auto_detected_project

                ? t('authentication_successful_project_i_dup', {data_credentials_project_id: data.credentials.project_id, data_file_path: data.file_path})

                : t('authentication_successful_file_save', {data_file_path: data.file_path});

            showStatus(msg, 'success');

            document.getElementById('credentialsSection').classList.remove('hidden');

            AppState.authInProgress = false;

        } else if (data.requires_project_selection && data.available_projects) {

            let projectOptions = t('please_select_a_projectnn');

            data.available_projects.forEach((project, index) => {

                projectOptions += `${index + 1}. ${project.name} (${project.project_id})\n`;

            });

            projectOptions += t('nplease_enter_index_1dataavailable', {data_available_projects_length: data.available_projects.length});

            const selection = await showPromptModal(projectOptions);

            const projectIndex = parseInt(selection) - 1;

            if (projectIndex >= 0 && projectIndex < data.available_projects.length) {

                AppState.currentProjectId = data.available_projects[projectIndex].project_id;

                btn.textContent = t('retry_fetching_authentication_file');

                showStatus(t('retry_using_the_selected_project'), 'info');

                setTimeout(() => getCredentials(), 1000);

                return;

            } else {

                showStatus(t('invalid_selection_please_restart_th'), 'error');

            }

        } else if (data.requires_manual_project_id) {

            const userProjectId = await showPromptModal(t('unable_to_autodetect_project_id_ple'));

            if (userProjectId && userProjectId.trim()) {

                AppState.currentProjectId = userProjectId.trim();

                btn.textContent = t('retry_fetching_authentication_file');

                showStatus(t('retrying_with_manually_entered_proj'), 'info');

                setTimeout(() => getCredentials(), 1000);

                return;

            } else {

                showStatus(t('project_id_required_to_complete_aut'), 'error');

            }

        } else {

            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: data.detail || data.error || t('failed_to_retrieve_authentication_f_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_authentication_file');

    }

}

// =====================================================================

// =====================================================================

async function startPrimaryAuth() {

    const btn = document.getElementById('getPrimaryAuthBtn');

    btn.disabled = true;

    btn.textContent = t('generating_authentication_link');

    try {

        showStatus(t('generating_primary_authenticati'), 'info');

        const response = await fetch('./api/auth/start', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ mode: 'provider' })

        });

        const data = await response.json();

        if (response.ok) {

            AppState.primaryAuthState = data.state;

            AppState.primaryAuthInProgress = true;

            AppState.primaryCredentialFilename = '';

            const authUrlLink = document.getElementById('primaryAuthUrl');

            authUrlLink.href = data.auth_url;

            authUrlLink.textContent = data.auth_url;

            document.getElementById('primaryAuthUrlSection').classList.remove('hidden');
            document.getElementById('primarySaveResult')?.classList.add('hidden');
            document.getElementById('primaryCredsSection')?.classList.add('hidden');
            const primaryCallbackUrlInput = document.getElementById('primaryCallbackUrlInput');
            if (primaryCallbackUrlInput) primaryCallbackUrlInput.value = '';
            updatePrimaryCallbackUrlPlaceholder(data.callback_url);
            setPrimaryCallbackUrlSectionVisible(true);
            const primaryCredsContent = document.getElementById('primaryCredsContent');
            if (primaryCredsContent) primaryCredsContent.textContent = '';

            showStatus(t('primary_authentication_link_gen'), 'success');

        } else {

            showStatus(t('error_dataerror_failed_to_generate', {data_error: data.detail || data.error || t('failed_to_generate_authentication_l_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('get_primary_authentication_link');

    }

}

function setPrimaryCallbackUrlSectionVisible(visible, focusInput = false) {
    const section = document.getElementById('primaryCallbackUrlSection');
    const input = document.getElementById('primaryCallbackUrlInput');
    if (!section) return;
    section.classList.toggle('hidden', !visible);
    if (visible && focusInput && input) {
        input.focus();
        input.select();
    }
}

function updatePrimaryCallbackUrlPlaceholder(callbackUrl = '') {
    const input = document.getElementById('primaryCallbackUrlInput');
    if (!input) return;

    const callbackBase = callbackUrl || 'http://localhost:4283/callback';
    input.placeholder = `${callbackBase}?state=...&code=...`;
}

function getPrimaryCallbackUrl() {
    return document.getElementById('primaryCallbackUrlInput')?.value.trim() || '';
}

function validateCallbackUrl(callbackUrl) {
    if (!callbackUrl) {
        showStatus(t('please_enter_the_callback_url'), 'error');
        return false;
    }

    if (!callbackUrl.startsWith('http://') && !callbackUrl.startsWith('https://')) {
        showStatus(t('please_enter_a_valid_url_starting_w'), 'error');
        return false;
    }

    if (!callbackUrl.includes('code=') || !callbackUrl.includes('state=')) {
        showStatus(t('this_is_not_a_valid_callback_url_pl'), 'error');
        return false;
    }

    return true;
}

async function completePrimaryCredentialSave(data) {
    const credentialSaved = data.credential_saved !== false;
    const credentialAction = data.credential_action || 'created';
    const resultTitle = credentialAction === 'skipped'
        ? t('provider_credential_skipped_title')
        : credentialAction === 'replaced'
            ? t('provider_credential_replaced_title')
            : t('provider_credential_saved_title');
    const fileSuffix = data.file_path ? ` File: ${data.file_path}.` : '';
    const resultBody = data.message
        ? `${data.message}${data.message.endsWith('.') ? '' : '.'}${fileSuffix}`
        : credentialSaved
            ? t('provider_credential_saved_body', {data_file_path: data.file_path})
            : t('provider_credential_skipped_body', {data_file_path: data.file_path});

    const primaryCredsSection = document.getElementById('primaryCredsSection');
    const primaryCredsContent = document.getElementById('primaryCredsContent');
    const primaryCredsDownloadBtn = document.getElementById('primaryCredsDownloadBtn');

    if (credentialSaved) {
        primaryCredsContent.textContent = JSON.stringify(data.credentials, null, 2);
        primaryCredsSection.classList.remove('hidden');
        primaryCredsDownloadBtn?.classList.remove('hidden');
        AppState.primaryCredentialFilename = getDownloadFilename(data.file_path, `primary-credential-${Date.now()}.json`);
    } else {
        primaryCredsContent.textContent = '';
        primaryCredsSection.classList.add('hidden');
        primaryCredsDownloadBtn?.classList.add('hidden');
        AppState.primaryCredentialFilename = '';
    }

    AppState.primaryAuthInProgress = false;
    setPrimaryCallbackUrlSectionVisible(false);

    const saveResult = document.getElementById('primarySaveResult');
    const saveResultTitle = document.getElementById('primarySaveResultTitle');
    const saveResultText = document.getElementById('primarySaveResultText');
    if (saveResult && saveResultText) {
        if (saveResultTitle) saveResultTitle.textContent = resultTitle;
        saveResultText.textContent = resultBody;
        saveResult.classList.remove('hidden');
    }

    try {
        await AppState.primaryCreds.refresh();
        await refreshUsageStats();
    } catch (refreshError) {
        console.warn('Credential flow completed, but pool refresh failed:', refreshError);
    }

    showStatus(resultBody, credentialSaved ? 'success' : 'info');
}

async function getPrimaryCredentials() {

    if (!AppState.primaryAuthInProgress) {

        showStatus(t('please_obtain_the_primary_authe'), 'error');

        return;

    }

    const btn = document.getElementById('getPrimaryCredsBtn');

    btn.disabled = true;

    btn.textContent = t('checking_provider_authorization');

    try {

        const callbackUrl = getPrimaryCallbackUrl();
        if (callbackUrl) {
            if (!validateCallbackUrl(callbackUrl)) return;
            await savePrimaryCredentialsFromCallbackUrl(callbackUrl, btn);
            return;
        }

        showStatus(t('checking_provider_authorization'), 'info');

        const state = AppState.primaryAuthState;
        const statusResponse = await fetch(`./api/auth/status?state=${encodeURIComponent(state)}`, {
            headers: getAuthHeaders()
        });
        const statusData = await statusResponse.json().catch(() => ({}));

        if (!statusResponse.ok) {
            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: statusData.detail || statusData.error || t('unknown_error')}), 'error');
            return;
        }

        if (statusData.status === 'not_found') {
            AppState.primaryAuthInProgress = false;
            showStatus(t('provider_authorization_expired'), 'error');
            return;
        }

        if (statusData.status !== 'completed') {
            setPrimaryCallbackUrlSectionVisible(true, true);
            showStatus(t('provider_authorization_pending'), 'info');
            return;
        }

        btn.textContent = t('saving_provider_credentials');

        showStatus(t('saving_provider_credentials'), 'info');

        const response = await fetch('./api/auth/callback', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ mode: 'provider' })

        });

        const data = await response.json();

        if (response.ok) {

            await completePrimaryCredentialSave(data);

        } else {

            showStatus(t('error_dataerror_failed_to_get_authe', {data_error: data.detail || data.error || t('failed_to_retrieve_authentication_f_dup')}), 'error');

        }

    } catch (error) {

        showStatus(t('status_net_error', {error: error.message}), 'error');

    } finally {

        btn.disabled = false;

        btn.textContent = t('fetch_primary_credentials');

    }

}

async function savePrimaryCredentialsFromCallbackUrl(callbackUrl, btn = document.getElementById('getPrimaryCredsBtn')) {
    try {
        if (btn) btn.textContent = t('saving_provider_credentials');
        showStatus(t('saving_provider_credentials_from_callback'), 'info');

        const response = await fetch('./api/auth/callback-url', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ callback_url: callbackUrl, mode: 'provider' })
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            await completePrimaryCredentialSave(data);
            const input = document.getElementById('primaryCallbackUrlInput');
            if (input) input.value = '';
        } else {
            showStatus(data.detail || data.error || t('failed_to_fetch_credentials_from_ca'), 'error');
        }
    } catch (error) {
        showStatus(t('failed_to_retrieve_credentials_from_dup', {error_message: error.message}), 'error');
    }
}

function getDownloadFilename(filePath, fallback) {

    const rawName = String(filePath || '').split(/[\\/]/).pop().trim();

    return rawName || fallback;

}

function downloadPrimaryCredentials() {

    const content = document.getElementById('primaryCredsContent').textContent;

    const blob = new Blob([content], { type: 'application/json' });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = getDownloadFilename(AppState.primaryCredentialFilename, `primary-credential-${Date.now()}.json`);

    a.click();

    window.URL.revokeObjectURL(url);

}

// =====================================================================

// =====================================================================

function toggleProjectIdSection() {

    const section = document.getElementById('projectIdSection');

    const icon = document.getElementById('projectIdToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(90deg)';

        icon.textContent = '';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '';

    }

}

function toggleCallbackUrlSection() {

    const section = document.getElementById('callbackUrlSection');

    const icon = document.getElementById('callbackUrlToggleIcon');

    if (section.style.display === 'none') {

        section.style.display = 'block';

        icon.style.transform = 'rotate(180deg)';

        icon.textContent = '';

    } else {

        section.style.display = 'none';

        icon.style.transform = 'rotate(0deg)';

        icon.textContent = '';

    }

}

async function processCallbackUrl() {

    const callbackUrl = document.getElementById('callbackUrlInput').value.trim();

    if (!callbackUrl) {

        showStatus(t('please_enter_the_callback_url'), 'error');

        return;

    }

    if (!callbackUrl.startsWith('http://') && !callbackUrl.startsWith('https://')) {

        showStatus(t('please_enter_a_valid_url_starting_w'), 'error');

        return;

    }

    if (!callbackUrl.includes('code=') || !callbackUrl.includes('state=')) {

        showStatus(t('this_is_not_a_valid_callback_url_pl'), 'error');

        return;

    }

    showStatus(t('retrieving_credentials_from_callbac'), 'info');

    try {

        const projectId = document.getElementById('projectId')?.value.trim() || null;

        const response = await fetch('./api/auth/callback-url', {

            method: 'POST',

            headers: getAuthHeaders(),

            body: JSON.stringify({ callback_url: callbackUrl, project_id: projectId })

        });

        const result = await response.json();

        if (result.credentials) {

            showStatus(result.message || t('credentials_fetched_successfully_fr'), 'success');

            const credentialsContent = document.getElementById('credentialsContent');
            const pre = document.createElement('pre');
            pre.textContent = JSON.stringify(result.credentials, null, 2);
            credentialsContent.replaceChildren(pre);

            document.getElementById('credentialsSection').classList.remove('hidden');

        } else if (result.requires_manual_project_id) {

            showStatus(t('manual_project_id_specification_req'), 'error');

        } else if (result.requires_project_selection) {

            let msg = t('brstrongavailable_projectsstrongbr');

            result.available_projects.forEach(p => {

                msg += `- ${p.name} (ID: ${p.project_id})<br>`;

            });

            showStatus(t('multiple_projects_detected_please_s') + msg, 'error');

        } else {

            showStatus(result.detail || result.error || t('failed_to_fetch_credentials_from_ca'), 'error');

        }

        document.getElementById('callbackUrlInput').value = '';

    } catch (error) {

        showStatus(t('failed_to_retrieve_credentials_from_dup', {error_message: error.message}), 'error');

    }

}

// =====================================================================

// =====================================================================
