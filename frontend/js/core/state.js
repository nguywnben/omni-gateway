
// =====================================================================

// =====================================================================

// =====================================================================

// =====================================================================

const AppState = {

    authenticated: false,

    setupRequired: false,

    authInProgress: false,

    currentProjectId: '',

    primaryAuthState: null,

    primaryAuthInProgress: false,

    primaryCredentialFilename: '',

    creds: createCredsManager('normal'),

    primaryCreds: createCredsManager('primary'),

    credentialCardIndex: {},

    uploadFiles: createUploadManager('normal'),

    primaryUploadFiles: createUploadManager('primary'),

    googleAiStudioUploadFiles: createUploadManager('googleAiStudio', {
        endpoint: './api/providers/google-ai-studio/credentials/import',
        elementPrefix: 'googleAiStudio',
        credentialType: 'Google AI Studio',
        timeoutMs: 900000,
        onComplete: () => AppState.primaryCreds.refresh()
    }),

    grokUploadFiles: createUploadManager('grok', {
        endpoint: './api/providers/xai/credentials/import?credential_type=oauth',
        elementPrefix: 'grok',
        credentialType: 'Grok Build OAuth',
        timeoutMs: 900000,
        onComplete: async () => {
            await AppState.primaryCreds.refresh();
            await loadModelCatalog(true);
            await refreshUsageStats();
        }
    }),

    xaiConsoleUploadFiles: createUploadManager('xaiConsole', {
        endpoint: './api/providers/xai/credentials/import?credential_type=api_key',
        elementPrefix: 'xaiConsole',
        credentialType: 'SpaceXAI Console',
        timeoutMs: 900000,
        onComplete: async () => {
            await AppState.primaryCreds.refresh();
            await loadModelCatalog(true);
            await refreshUsageStats();
        }
    }),

    codexUploadFiles: createUploadManager('codex', {
        endpoint: './api/providers/openai/credentials/import?credential_type=oauth',
        elementPrefix: 'codex',
        credentialType: 'Codex',
        timeoutMs: 900000,
        onComplete: async () => {
            await AppState.primaryCreds.refresh();
            await loadModelCatalog(true);
            await refreshUsageStats();
        }
    }),

    openaiPlatformUploadFiles: createUploadManager('openaiPlatform', {
        endpoint: './api/providers/openai/credentials/import?credential_type=api_key',
        elementPrefix: 'openaiPlatform',
        credentialType: 'OpenAI Platform',
        timeoutMs: 900000,
        onComplete: async () => {
            await AppState.primaryCreds.refresh();
            await loadModelCatalog(true);
            await refreshUsageStats();
        }
    }),

    currentConfig: {},

    configLoaded: false,

    envLockedFields: new Set(),

    antigravityConfig: {},

    antigravityConfigLoaded: false,

    antigravityEnvLockedFields: new Set(),

    activeProviderWorkspace: 'google_antigravity',

    modelCatalog: [],

    modelCatalogLoaded: false,

    modelBlacklist: [],

    selectedModels: [],

    modelPoolEnabled: true,

    logWebSocket: null,

    allLogs: [],

    filteredLogs: [],

    currentLogFilter: 'all',

    usageStatsData: {},

    usageStatsLoaded: false,

    usagePeriod: '1d',

    tabLoadTimes: {},

    tabLoadPromises: {},

    quotaPreviewCache: {},

    cooldownTimerInterval: null

};

const STORAGE_KEYS = {
    logAutoScroll: 'omni_gateway_log_auto_scroll',
};

// =====================================================================

// =====================================================================
