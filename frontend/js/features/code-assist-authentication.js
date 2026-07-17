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
