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
        empty.textContent = 'No unavailable model routes are recorded.';
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
        if (entry.credential_name) {
            const credential = document.createElement('span');
            credential.textContent = `Credential ${entry.credential_name}`;
            metadata.appendChild(credential);
        }
        details.append(identity, metadata);

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'btn btn-secondary btn-small';
        removeButton.textContent = 'Remove';
        removeButton.title = entry.credential_name
            ? 'Restore this credential-model route'
            : 'Restore this provider-model route';
        removeButton.addEventListener('click', () => removeModelBlacklistEntry(
            entry.provider_id,
            entry.model_id,
            entry.credential_name || '',
            removeButton
        ));
        item.append(details, removeButton);
        list.appendChild(item);
    });
}

async function removeModelBlacklistEntry(providerId, modelId, credentialName, button) {
    if (button) button.disabled = true;
    try {
        const query = credentialName
            ? `?credential_name=${encodeURIComponent(credentialName)}`
            : '';
        const response = await fetch(
            `./api/model-blacklist/${encodeURIComponent(providerId)}/models/${encodeURIComponent(modelId)}${query}`,
            { method: 'DELETE', headers: getAuthHeaders() }
        );
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        await loadModelCatalog(false, { preserveContent: true });
        showStatus(data.message || 'Model route removed from blacklist.', 'success');
    } catch (error) {
        showStatus(`Failed to remove the model route: ${error.message}`, 'error');
        if (button) button.disabled = false;
    }
}

async function clearModelBlacklist() {
    const confirmed = await showConfirmModal(
        'Restore every unavailable model route currently excluded after an upstream 404 response?',
        {
            title: 'Clear Unavailable Routes',
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
        await loadModelCatalog(false, { preserveContent: true });
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

async function loadModelCatalog(forceRefresh = false, options = {}) {
    const loading = document.getElementById('modelCatalogLoading');
    const workspace = document.getElementById('modelPoolWorkspace');
    const refreshButton = document.getElementById('refreshModelCatalogBtn');
    const preserveContent = options.preserveContent ?? AppState.modelCatalogLoaded;
    if (loading && !preserveContent) loading.classList.remove('hidden');
    if (workspace && !preserveContent) workspace.classList.add('hidden');
    if (refreshButton) refreshButton.disabled = true;
    try {
        const response = await fetch(`./api/model-catalog${forceRefresh ? '?refresh=true' : ''}`, {
            headers: getAuthHeaders()
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error || 'Unknown error');
        AppState.modelCatalog = Array.isArray(data.catalog) ? data.catalog : [];
        AppState.modelCatalogLoaded = true;
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
        if (loading && !preserveContent) loading.classList.add('hidden');
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
