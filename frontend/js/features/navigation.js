let providerCatalogResizeObserver = null;

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

function initStaticUiBindings() {
    const clickHandlers = {
        'toggle-mobile-menu': () => toggleMobileMenu(),
        'switch-tab': (element) => switchTab(element.dataset.tab),
        logout: () => logout(),
        'copy-api-key': () => copyInputValue('apiKey'),
        'toggle-api-key': () => toggleApiKeyVisibility(),
        'regenerate-api-key': () => regenerateApiKey(),
        'copy-url': (element) => cpUrl(element),
        'refresh-pool': () => refreshPrimaryCredsList(),
        'select-pool-archive': () => selectPoolImportArchive(),
        'download-pool': () => downloadAllPrimaryCreds(),
        'batch-primary': (element) => batchPrimaryAction(element.dataset.batchAction),
        'batch-verify-primary': () => batchVerifyProviderCredentials(),
        'change-primary-page': (element) => changePrimaryPage(Number(element.dataset.pageDelta)),
        'refresh-model-catalog': () => loadModelCatalog(true),
        'save-model-pool': () => saveModelPool(),
        'clear-model-blacklist': () => clearModelBlacklist(),
        'select-provider': (element) => selectProviderWorkspace(element.dataset.provider),
        'scroll-provider-catalog': (element) => scrollProviderCatalog(Number(element.dataset.direction)),
        'select-ai-studio-files': () => document.getElementById('googleAiStudioFileInput')?.click(),
        'upload-ai-studio-files': () => uploadGoogleAiStudioFiles(),
        'clear-ai-studio-files': () => clearGoogleAiStudioFiles(),
        'save-ai-studio-settings': () => saveGoogleAIStudioSettings(),
        'reset-ai-studio-settings': () => resetGoogleAIStudioSettings(),
        'start-xai-oauth': () => startXaiOauth(),
        'save-xai-oauth': () => saveXaiOauth(),
        'select-grok-files': () => document.getElementById('grokFileInput')?.click(),
        'upload-grok-files': () => uploadGrokFiles(),
        'clear-grok-files': () => clearGrokFiles(),
        'select-xai-console-files': () => document.getElementById('xaiConsoleFileInput')?.click(),
        'upload-xai-console-files': () => uploadXaiConsoleFiles(),
        'clear-xai-console-files': () => clearXaiConsoleFiles(),
        'save-grok-settings': () => saveXaiSettings('oauth'),
        'reset-grok-settings': () => resetXaiSettings('oauth'),
        'save-xai-console-settings': () => saveXaiSettings('api'),
        'reset-xai-console-settings': () => resetXaiSettings('api'),
        'start-codex-oauth': () => startCodexOauth(),
        'complete-codex-oauth': () => completeCodexOauth(),
        'select-codex-files': () => document.getElementById('codexFileInput')?.click(),
        'upload-codex-files': () => uploadCodexFiles(),
        'clear-codex-files': () => clearCodexFiles(),
        'select-openai-platform-files': () => document.getElementById('openaiPlatformFileInput')?.click(),
        'upload-openai-platform-files': () => uploadOpenAIPlatformFiles(),
        'clear-openai-platform-files': () => clearOpenAIPlatformFiles(),
        'save-openai-settings': (element) => saveOpenAISettings(element.dataset.openaiScope),
        'reset-openai-settings': (element) => resetOpenAISettings(element.dataset.openaiScope),
        'start-claude-oauth': () => startClaudeOauth(),
        'save-claude-oauth': () => saveClaudeOauth(),
        'select-claude-code-files': () => document.getElementById('claudeCodeFileInput')?.click(),
        'upload-claude-code-files': () => uploadClaudeCodeFiles(),
        'clear-claude-code-files': () => clearClaudeCodeFiles(),
        'select-claude-platform-files': () => document.getElementById('claudePlatformFileInput')?.click(),
        'upload-claude-platform-files': () => uploadClaudePlatformFiles(),
        'clear-claude-platform-files': () => clearClaudePlatformFiles(),
        'save-anthropic-settings': (element) => saveAnthropicSettings(element.dataset.anthropicScope),
        'reset-anthropic-settings': (element) => resetAnthropicSettings(element.dataset.anthropicScope),
        'copy-claude-auth-url': () => cpUrl(document.getElementById('claudeAuthorizationUrl')),
        'select-ollama-files': () => document.getElementById('ollamaFileInput')?.click(),
        'upload-ollama-files': () => uploadOllamaFiles(),
        'clear-ollama-files': () => clearOllamaFiles(),
        'copy-codex-device-code': (element) => {
            cpUrl(element);
            element.blur();
        },
        'copy-codex-verification-url': () => cpUrl(document.getElementById('codexVerificationUrl')),
        'copy-xai-auth-url': () => cpUrl(document.getElementById('xaiAuthorizationUrl')),
        'copy-primary-auth-url': () => cpUrl(document.getElementById('primaryAuthUrl')),
        'get-primary-credentials': () => getPrimaryCredentials(),
        'download-primary-credentials': () => downloadPrimaryCredentials(),
        'select-primary-files': () => document.getElementById('primaryFileInput')?.click(),
        'upload-primary-files': () => uploadPrimaryFiles(),
        'clear-primary-files': () => clearPrimaryFiles(),
        'save-antigravity-settings': () => saveAntigravitySettings(),
        'reset-antigravity-settings': () => resetAntigravitySettings(),
        'save-config': () => saveConfig(),
        'reset-config': () => resetConfig(),
        'set-current-keepalive-url': () => autoSetKeepaliveUrl(),
        'download-logs': () => downloadLogs(),
        'clear-logs': () => clearLogs(),
        'check-updates': () => checkForUpdates()
    };
    const changeHandlers = {
        'usage-period': (element) => setUsagePeriod(element.value),
        'pool-archive': (_element, event) => handlePoolImportArchive(event),
        'select-all-primary': () => toggleSelectAllPrimary(),
        'primary-filter': () => applyPrimaryStatusFilter(),
        'primary-page-size': () => changePrimaryPageSize(),
        'ai-studio-files': (_element, event) => handleGoogleAiStudioFileSelect(event),
        'grok-files': (_element, event) => handleGrokFileSelect(event),
        'xai-console-files': (_element, event) => handleXaiConsoleFileSelect(event),
        'codex-files': (_element, event) => handleCodexFileSelect(event),
        'openai-platform-files': (_element, event) => handleOpenAIPlatformFileSelect(event),
        'claude-code-files': (_element, event) => handleClaudeCodeFileSelect(event),
        'claude-platform-files': (_element, event) => handleClaudePlatformFileSelect(event),
        'ollama-files': (_element, event) => handleOllamaFileSelect(event),
        'primary-files': (_element, event) => handlePrimaryFileSelect(event),
        'routing-strategy': () => syncRoutingPolicyControls(),
        'log-level': () => filterLogs()
    };

    document.addEventListener('click', (event) => {
        const element = event.target.closest('[data-ui-action]');
        if (!element) return;
        const handler = clickHandlers[element.dataset.uiAction];
        if (handler) handler(element, event);
    });

    document.addEventListener('change', (event) => {
        const element = event.target.closest('[data-ui-change]');
        if (!element) return;
        const handler = changeHandlers[element.dataset.uiChange];
        if (handler) handler(element, event);
    });

    document.addEventListener('input', (event) => {
        if (event.target.matches('[data-ui-input="model-catalog-search"]')) {
            renderModelCatalog();
        }
        if (event.target.matches('[data-ui-input="provider-catalog-search"]')) {
            filterProviderCatalog(event.target.value);
        }
    });

    document.getElementById('loginForm')?.addEventListener('submit', (event) => {
        event.preventDefault();
        login();
    });
    document.getElementById('setupForm')?.addEventListener('submit', (event) => {
        event.preventDefault();
        completeInitialSetup();
    });
    document.getElementById('googleAiStudioCredentialForm')?.addEventListener('submit', addGoogleAIStudioCredential);
    document.getElementById('xaiCredentialForm')?.addEventListener('submit', addXaiApiKeyCredential);
    document.getElementById('openaiPlatformCredentialForm')?.addEventListener('submit', addOpenAIPlatformCredential);
    document.getElementById('claudePlatformCredentialForm')?.addEventListener('submit', addClaudePlatformCredential);
    document.getElementById('ollamaCredentialForm')?.addEventListener('submit', addOllamaCredential);
    document.getElementById('accessPasswordForm')?.addEventListener('submit', (event) => {
        event.preventDefault();
        saveAccessCredentials();
    });

    document.getElementById('apiKey')?.addEventListener('mousedown', (event) => event.preventDefault());

    for (const [areaId, dropHandler] of [
        ['googleAiStudioUploadArea', handleGoogleAiStudioFileDrop],
        ['grokUploadArea', handleGrokFileDrop],
        ['xaiConsoleUploadArea', handleXaiConsoleFileDrop],
        ['codexUploadArea', handleCodexFileDrop],
        ['openaiPlatformUploadArea', handleOpenAIPlatformFileDrop],
        ['claudeCodeUploadArea', handleClaudeCodeFileDrop],
        ['claudePlatformUploadArea', handleClaudePlatformFileDrop],
        ['ollamaUploadArea', handleOllamaFileDrop],
        ['primaryUploadArea', handlePrimaryFileDrop]
    ]) {
        const area = document.getElementById(areaId);
        area?.addEventListener('dragover', (event) => {
            event.preventDefault();
            area.classList.add('dragover');
        });
        area?.addEventListener('dragleave', () => area.classList.remove('dragover'));
        area?.addEventListener('drop', dropHandler);
    }

    const providerCatalogViewport = document.getElementById('providerCatalogViewport');
    providerCatalogViewport?.addEventListener(
        'scroll',
        updateProviderCatalogNavigation,
        { passive: true }
    );
    if (providerCatalogViewport && typeof ResizeObserver === 'function') {
        providerCatalogResizeObserver = new ResizeObserver(updateProviderCatalogNavigation);
        providerCatalogResizeObserver.observe(providerCatalogViewport);
    }
    updateProviderCatalogNavigation();
}

document.addEventListener('DOMContentLoaded', initStaticUiBindings);

window.addEventListener('resize', () => {

    const activeTab = document.querySelector('.tab.active');

    if (activeTab) updateTabSlider(activeTab, false);

    if (window.innerWidth > 960) setMobileMenuState(false);

    updateProviderCatalogNavigation();

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
    },
    grok: {
        selectorId: 'providerSelectorGrok',
        panelId: 'providerWorkspaceGrok'
    },
    xai_console: {
        selectorId: 'providerSelectorXaiConsole',
        panelId: 'providerWorkspaceXaiConsole'
    },
    codex: {
        selectorId: 'providerSelectorCodex',
        panelId: 'providerWorkspaceCodex'
    },
    openai_platform: {
        selectorId: 'providerSelectorOpenAiPlatform',
        panelId: 'providerWorkspaceOpenAiPlatform'
    },
    claude_code: {
        selectorId: 'providerSelectorClaudeCode',
        panelId: 'providerWorkspaceClaudeCode'
    },
    claude_platform: {
        selectorId: 'providerSelectorClaudePlatform',
        panelId: 'providerWorkspaceClaudePlatform'
    },
    ollama: {
        selectorId: 'providerSelectorOllama',
        panelId: 'providerWorkspaceOllama'
    }
};

function updateProviderCatalogNavigation() {
    const viewport = document.getElementById('providerCatalogViewport');
    const previousButton = document.getElementById('providerCatalogPrevious');
    const nextButton = document.getElementById('providerCatalogNext');
    if (!viewport || !previousButton || !nextButton) return;
    if (viewport.clientWidth <= 1) return;

    const maximumScroll = Math.max(0, viewport.scrollWidth - viewport.clientWidth);
    previousButton.disabled = maximumScroll <= 1 || viewport.scrollLeft <= 1;
    nextButton.disabled = maximumScroll <= 1 || viewport.scrollLeft >= maximumScroll - 1;
}

function scrollProviderCatalog(direction) {
    const viewport = document.getElementById('providerCatalogViewport');
    const catalog = document.getElementById('providerCatalog');
    const firstVisibleCard = catalog?.querySelector('[data-provider]:not(.hidden)');
    if (!viewport || !catalog || !firstVisibleCard || !direction) return;

    const catalogStyles = getComputedStyle(catalog);
    const gap = Number.parseFloat(catalogStyles.columnGap || catalogStyles.gap) || 0;
    const distance = firstVisibleCard.getBoundingClientRect().width + gap;
    viewport.scrollBy({
        left: Math.sign(direction) * distance,
        behavior: 'auto'
    });
    requestAnimationFrame(updateProviderCatalogNavigation);
}

function filterProviderCatalog(value = '') {
    const query = String(value || '').trim().toLowerCase();
    const cards = Array.from(document.querySelectorAll('#providerCatalog [data-provider]'));
    let visibleCount = 0;
    cards.forEach((card) => {
        const searchableText = [
            card.dataset.provider,
            card.dataset.providerName,
            card.textContent
        ].join(' ').toLowerCase();
        const isVisible = !query || searchableText.includes(query);
        card.classList.toggle('hidden', !isVisible);
        card.setAttribute('aria-hidden', String(!isVisible));
        visibleCount += isVisible ? 1 : 0;
    });
    document.getElementById('providerCatalogEmpty')?.classList.toggle('hidden', visibleCount > 0);
    const viewport = document.getElementById('providerCatalogViewport');
    if (viewport) viewport.scrollLeft = 0;
    requestAnimationFrame(updateProviderCatalogNavigation);
}

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
        const selector = document.getElementById(selected.selectorId);
        selector?.focus();
        selector?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
}

function initProviderWorkspaceSelector() {
    const providerIds = Object.keys(PROVIDER_WORKSPACES);

    providerIds.forEach((providerId) => {
        const selector = document.getElementById(PROVIDER_WORKSPACES[providerId].selectorId);
        selector?.addEventListener('keydown', (event) => {
            if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
            event.preventDefault();

            const visibleProviderIds = providerIds.filter((id) => {
                const candidate = document.getElementById(PROVIDER_WORKSPACES[id].selectorId);
                return candidate && !candidate.classList.contains('hidden');
            });
            if (!visibleProviderIds.length) return;

            const currentIndex = Math.max(0, visibleProviderIds.indexOf(providerId));
            let nextIndex = currentIndex;
            if (event.key === 'ArrowLeft') {
                nextIndex = (currentIndex - 1 + visibleProviderIds.length) % visibleProviderIds.length;
            }
            if (event.key === 'ArrowRight') {
                nextIndex = (currentIndex + 1) % visibleProviderIds.length;
            }
            if (event.key === 'Home') nextIndex = 0;
            if (event.key === 'End') nextIndex = visibleProviderIds.length - 1;

            selectProviderWorkspace(visibleProviderIds[nextIndex], true);
        });
    });

    selectProviderWorkspace(AppState.activeProviderWorkspace);
}

document.addEventListener('DOMContentLoaded', initProviderWorkspaceSelector);

const MODEL_PROVIDER_META = {
    google_antigravity: {
        name: 'Google Antigravity',
        logo: '/frontend/assets/providers/google-antigravity-logo.png'
    },
    google_ai_studio: {
        name: 'Google AI Studio',
        logo: '/frontend/assets/providers/google-ai-studio-logo.png'
    },
    grok: {
        name: 'Grok Build',
        logo: '/frontend/assets/providers/grok-build-logo.png'
    },
    xai_console: {
        name: 'SpaceXAI Console',
        logo: '/frontend/assets/providers/spacexai-console-logo.png'
    },
    codex: {
        name: 'Codex',
        logo: '/frontend/assets/providers/codex-logo.png'
    },
    openai_platform: {
        name: 'OpenAI Platform',
        logo: '/frontend/assets/providers/openai-platform-logo.png'
    },
    claude_code: {
        name: 'Claude Code',
        logo: '/frontend/assets/providers/claude-code-logo.png'
    },
    claude_platform: {
        name: 'Claude Platform',
        logo: '/frontend/assets/providers/claude-platform-logo.png'
    },
    anthropic: {
        name: 'Anthropic',
        logo: '/frontend/assets/providers/claude-platform-logo.png'
    },
    ollama: {
        name: 'Ollama',
        logo: '/frontend/assets/providers/ollama-logo.png'
    },
    xai: {
        name: 'Grok Build',
        logo: '/frontend/assets/providers/grok-build-logo.png'
    },
    openai: {
        name: 'OpenAI Platform',
        logo: '/frontend/assets/providers/openai-platform-logo.png'
    }
};
