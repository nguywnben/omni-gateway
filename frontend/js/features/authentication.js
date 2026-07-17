// Omni Gateway management console: console.

async function refreshSetupStatus() {

    try {

        const response = await fetch('./api/auth/setup/status');

        const data = await response.json();

        AppState.setupRequired = Boolean(data.setup_required);

        AppState.authenticated = Boolean(data.authenticated);

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

    if (AppState.authenticated) {

        navigate(window.location.pathname, false);

        return true;

    }

    navigate('/login', false);

    return false;

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
