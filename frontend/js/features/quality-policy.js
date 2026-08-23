const QUALITY_POLICY_FIELDS = {
    compatibilityModeEnabled: ['compatibility_mode'],
    returnThoughtsToFrontend: ['return_reasoning'],
    antiTruncationMaxAttempts: ['anti_truncation_max_attempts'],
    tokenCompressionEnabled: ['compression', 'enabled'],
    tokenCompressionThreshold: ['compression', 'threshold_tokens'],
    tokenCompressionTarget: ['compression', 'target_tokens'],
    tokenCompressionMinRecentTurns: ['compression', 'min_recent_turns'],
    qualityGuardrailsEnabled: ['guardrails', 'enabled'],
    qualityPiiMaskingEnabled: ['guardrails', 'pii_masking_enabled'],
    qualityInjectionDetectionEnabled: ['guardrails', 'injection_detection_enabled'],
    qualityBlockedKeywords: ['guardrails', 'blocked_keywords'],
    qualityResponseCacheEnabled: ['response_cache', 'enabled'],
    qualityResponseCacheTtl: ['response_cache', 'ttl_seconds'],
    qualityResponseCacheMaxEntries: ['response_cache', 'max_entries']
};

function cloneQualitySettings(settings) {
    return JSON.parse(JSON.stringify(settings || {}));
}

function qualityFieldValue(settings, path) {
    return path.reduce((value, part) => value?.[part], settings);
}

function setQualityFieldValue(settings, path, value) {
    let target = settings;
    for (const part of path.slice(0, -1)) target = target[part];
    target[path[path.length - 1]] = value;
}

function selectedQualityProfile() {
    return document.querySelector('input[name="qualityProfile"]:checked')?.value || 'balanced';
}

function setSelectedQualityProfile(profile) {
    document.querySelectorAll('input[name="qualityProfile"]').forEach(input => {
        input.checked = input.value === profile;
        input.closest('.quality-profile-card')?.classList.toggle('selected', input.checked);
    });
    AppState.qualityDraftProfile = profile;
}

function populateQualitySettings(settings) {
    for (const [elementId, path] of Object.entries(QUALITY_POLICY_FIELDS)) {
        const element = document.getElementById(elementId);
        if (!element) continue;
        const value = qualityFieldValue(settings, path);
        if (element.type === 'checkbox') {
            element.checked = Boolean(value);
        } else if (elementId === 'qualityBlockedKeywords') {
            element.value = Array.isArray(value) ? value.join('\n') : '';
        } else {
            element.value = value ?? '';
        }
    }
}

function effectiveQualityPresetSettings(profile) {
    const settings = cloneQualitySettings(AppState.qualityProfileDefaults[profile]);
    const effective = AppState.qualityEffectiveSettings;
    if (!settings || !effective) return settings;
    for (const [elementId, path] of Object.entries(QUALITY_POLICY_FIELDS)) {
        const policyField = document.getElementById(elementId)?.dataset.policyField;
        if (policyField && AppState.qualityEnvLockedFields.has(policyField)) {
            setQualityFieldValue(settings, path, qualityFieldValue(effective, path));
        }
    }
    return settings;
}

function getQualityDraftSettings() {
    const baseline = AppState.qualityPolicy?.settings || AppState.qualityProfileDefaults.balanced;
    const settings = cloneQualitySettings(baseline);
    for (const [elementId, path] of Object.entries(QUALITY_POLICY_FIELDS)) {
        const element = document.getElementById(elementId);
        if (!element) continue;
        let value;
        if (element.type === 'checkbox') {
            value = element.checked;
        } else if (elementId === 'qualityBlockedKeywords') {
            value = element.value.split(/[\n,]/).map(item => item.trim()).filter(Boolean);
        } else {
            value = Number.parseInt(element.value, 10);
        }
        setQualityFieldValue(settings, path, value);
    }
    return settings;
}

function qualityErrorMessage(data, fallbackKey) {
    const code = data?.error?.code;
    const keyedErrors = {
        quality_policy_revision_conflict: 'quality.error_conflict',
        quality_policy_environment_locked: 'quality.error_environment_locked',
        quality_policy_unavailable: 'quality.error_unavailable',
        quality_policy_invalid: 'quality.error_invalid'
    };
    return t(keyedErrors[code] || fallbackKey);
}

function qualitySourceLabel(source) {
    return t(source === 'versioned_policy' ? 'quality.source_versioned' : 'quality.source_legacy');
}

function renderQualityPolicyMetadata(data) {
    const policy = data.policy;
    const formatter = new Intl.NumberFormat(getActiveLocale());
    document.getElementById('qualityRuntimeStatus').textContent = data.runtime_active
        ? t('quality.runtime_active')
        : t('quality.runtime_inactive');
    document.getElementById('qualityRevision').textContent = formatter.format(policy.revision);
    document.getElementById('qualitySource').textContent = qualitySourceLabel(data.runtime_source);
    document.getElementById('qualityEnvironmentOverrides').textContent = data.environment_overrides?.length
        ? formatter.format(data.environment_overrides.length)
        : t('quality.none');
}

function applyQualityPolicyResponse(data) {
    AppState.qualityPolicy = data.policy;
    AppState.qualityEffectiveSettings = cloneQualitySettings(
        data.effective_settings || data.policy.settings
    );
    AppState.qualityProfileDefaults = data.profile_defaults || AppState.qualityProfileDefaults;
    AppState.qualityEnvLockedFields = new Set(data.env_locked || []);
    AppState.qualityPolicyLoaded = true;
    setSelectedQualityProfile(data.policy.profile);
    populateQualitySettings(data.effective_settings || data.policy.settings);
    renderQualityPolicyMetadata(data);
    syncQualityPolicyControls();
}

async function loadQualityPolicy(options = {}) {
    const loading = document.getElementById('qualityLoading');
    const form = document.getElementById('qualityForm');
    const preserveContent = options.preserveContent ?? AppState.qualityPolicyLoaded;
    if (!preserveContent) {
        if (loading) loading.hidden = false;
        form?.classList.add('hidden');
    }
    try {
        const response = await fetch('./api/quality-policy', {headers: getAuthHeaders(false)});
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(qualityErrorMessage(data, 'quality.error_load'));
        applyQualityPolicyResponse(data);
        form?.classList.remove('hidden');
    } catch (error) {
        showStatus(error.message || t('quality.error_load'), 'error');
    } finally {
        if (loading) loading.hidden = true;
    }
}

function selectQualityProfile(profile) {
    const supported = new Set(['quality', 'balanced', 'capacity', 'custom']);
    if (!supported.has(profile)) return;
    if (profile !== 'custom') {
        const defaults = effectiveQualityPresetSettings(profile);
        if (defaults) populateQualitySettings(defaults);
    }
    setSelectedQualityProfile(profile);
    document.getElementById('qualityPreviewResult')?.classList.add('hidden');
    syncQualityPolicyControls();
}

function syncQualityPolicyControls() {
    const custom = selectedQualityProfile() === 'custom';
    document.querySelectorAll('[data-quality-control]').forEach(control => {
        const locked = AppState.qualityEnvLockedFields.has(control.dataset.policyField);
        const dependency = control.closest('[data-quality-dependency]');
        const dependencyEnabled = !dependency
            || Boolean(document.getElementById(dependency.dataset.qualityDependency)?.checked);
        control.disabled = !custom || locked || !dependencyEnabled;
        control.classList.toggle('env-locked', locked);
        control.closest('.switch-row')?.classList.toggle('env-locked', locked);
        control.title = locked ? t('quality.environment_managed') : '';
    });
}

function validateQualityDraft() {
    if (selectedQualityProfile() !== 'custom') return true;
    const controls = [...document.querySelectorAll('[data-quality-control]')];
    const invalid = controls.find(control => !control.disabled && !control.checkValidity());
    if (invalid) {
        invalid.reportValidity();
        return false;
    }
    const settings = getQualityDraftSettings();
    const keywords = settings.guardrails.blocked_keywords;
    if (keywords.length > 100 || keywords.some(keyword => keyword.length > 128)) {
        showStatus(t('quality.error_keywords'), 'error');
        document.getElementById('qualityBlockedKeywords')?.focus();
        return false;
    }
    if (settings.compression.target_tokens >= settings.compression.threshold_tokens) {
        showStatus(t('quality.error_target'), 'error');
        document.getElementById('tokenCompressionTarget')?.focus();
        return false;
    }
    return true;
}

function buildQualityPolicyPayload() {
    const profile = selectedQualityProfile();
    const payload = {
        revision: AppState.qualityPolicy?.revision ?? 0,
        profile
    };
    if (profile === 'custom') payload.settings = getQualityDraftSettings();
    return payload;
}

async function saveQualityPolicy() {
    if (!validateQualityDraft()) return;
    const button = document.getElementById('qualitySaveButton');
    if (button) button.disabled = true;
    try {
        const response = await fetch('./api/quality-policy', {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(buildQualityPolicyPayload())
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            if (response.status === 409) await loadQualityPolicy({preserveContent: true});
            throw new Error(qualityErrorMessage(data, 'quality.error_save'));
        }
        applyQualityPolicyResponse(data);
        showStatus(t('quality.saved'), 'success');
    } catch (error) {
        showStatus(error.message || t('quality.error_save'), 'error');
    } finally {
        if (button) button.disabled = false;
    }
}

async function resetQualityPolicy() {
    const confirmed = await showConfirmModal(t('quality.restore_confirm'), {
        title: t('quality.restore_title'),
        confirmLabel: t('quality.restore_balanced')
    });
    if (!confirmed) return;
    selectQualityProfile('balanced');
    await saveQualityPolicy();
}

function qualityPreviewDescriptor() {
    return {
        estimated_input_tokens: Number.parseInt(document.getElementById('qualityPreviewTokens').value, 10),
        message_count: Number.parseInt(document.getElementById('qualityPreviewMessages').value, 10),
        tool_count: Number.parseInt(document.getElementById('qualityPreviewTools').value, 10),
        has_system_instruction: document.getElementById('qualityPreviewSystem').checked,
        has_tool_pairs: document.getElementById('qualityPreviewToolPairs').checked
    };
}

function renderQualityPreview(data) {
    const decision = data.preview.decision;
    const formatter = new Intl.NumberFormat(getActiveLocale());
    document.getElementById('qualityPreviewBefore').textContent = formatter.format(decision.estimated_tokens_before);
    document.getElementById('qualityPreviewAfter').textContent = formatter.format(decision.estimated_tokens_after);
    document.getElementById('qualityPreviewSaved').textContent = formatter.format(decision.estimated_tokens_saved);
    document.getElementById('qualityPreviewDecision').textContent = t(`quality.decision_${decision.reason}`);
    const protectedLabels = decision.protected_structures.map(item => t(`quality.protected_${item}`));
    document.getElementById('qualityPreviewProtection').textContent = protectedLabels.length
        ? t('quality.protected_summary', {items: protectedLabels.join(', ')})
        : t('quality.protected_none');
    document.getElementById('qualityPreviewResult').classList.remove('hidden');
    if (data.applies_with_environment_overrides || !data.can_apply) {
        showStatus(t('quality.error_environment_locked'), 'warning');
    }
}

async function previewQualityPolicy() {
    if (!validateQualityDraft()) return;
    const descriptorFields = [
        document.getElementById('qualityPreviewTokens'),
        document.getElementById('qualityPreviewMessages'),
        document.getElementById('qualityPreviewTools')
    ];
    const invalid = descriptorFields.find(field => !field.checkValidity());
    if (invalid) {
        invalid.reportValidity();
        return;
    }
    const button = document.getElementById('qualityPreviewButton');
    if (button) button.disabled = true;
    try {
        const response = await fetch('./api/quality-policy/preview', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({...buildQualityPolicyPayload(), ...qualityPreviewDescriptor()})
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            if (response.status === 409) await loadQualityPolicy({preserveContent: true});
            throw new Error(qualityErrorMessage(data, 'quality.error_preview'));
        }
        renderQualityPreview(data);
    } catch (error) {
        showStatus(error.message || t('quality.error_preview'), 'error');
    } finally {
        if (button) button.disabled = false;
    }
}
