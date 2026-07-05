"""Internal implementation detail."""
import asyncio
import socket
import threading
import time
import uuid
from datetime import timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse
from config import get_config_value, get_ogw_api_url
from log import log
from .google_oauth_api import Credentials, Flow, enable_required_apis, fetch_project_id_and_tier, get_user_projects, select_default_project
from .storage_adapter import get_storage_adapter
from .utils import OGW_CLIENT_ID, OGW_CLIENT_SECRET, OGW_SCOPES, OGW_USER_AGENT, OGW_CODE_ASSIST_CLIENT_ID, OGW_CODE_ASSIST_CLIENT_SECRET, OGW_CODE_ASSIST_SCOPES, CALLBACK_HOST, TOKEN_URL

async def get_callback_port():
    """Internal implementation detail."""
    return int(await get_config_value('oauth_callback_port', '11451', 'OGW_OAUTH_CALLBACK_PORT'))

def _prepare_credentials_data(credentials: Credentials, project_id: str, mode: str='code_assist', subscription_tier: str=None) -> Dict[str, Any]:
    """Internal implementation detail."""
    if mode == 'omni':
        creds_data = {'client_id': OGW_CLIENT_ID, 'client_secret': OGW_CLIENT_SECRET, 'token': credentials.access_token, 'refresh_token': credentials.refresh_token, 'scopes': OGW_SCOPES, 'token_uri': TOKEN_URL, 'project_id': project_id}
    else:
        creds_data = {'client_id': OGW_CODE_ASSIST_CLIENT_ID, 'client_secret': OGW_CODE_ASSIST_CLIENT_SECRET, 'token': credentials.access_token, 'refresh_token': credentials.refresh_token, 'scopes': OGW_CODE_ASSIST_SCOPES, 'token_uri': TOKEN_URL, 'project_id': project_id}
    if credentials.expires_at:
        if credentials.expires_at.tzinfo is None:
            expiry_utc = credentials.expires_at.replace(tzinfo=timezone.utc)
        else:
            expiry_utc = credentials.expires_at
        creds_data['expiry'] = expiry_utc.isoformat()
    return creds_data

def _cleanup_auth_flow_server(state: str):
    """Internal implementation detail."""
    if state in auth_flows:
        flow_data_to_clean = auth_flows[state]
        try:
            if flow_data_to_clean.get('server'):
                server = flow_data_to_clean['server']
                port = flow_data_to_clean.get('callback_port')
                async_shutdown_server(server, port)
        except Exception as e:
            log.debug('OAuth debug event')
        del auth_flows[state]

class _OAuthLibPatcher:
    """Internal implementation detail."""

    def __init__(self):
        import oauthlib.oauth2.rfc6749.parameters
        self.module = oauthlib.oauth2.rfc6749.parameters
        self.original_validate = None

    def __enter__(self):
        self.original_validate = self.module.validate_token_parameters

        def patched_validate(params):
            try:
                return self.original_validate(params)
            except Warning:
                pass
        self.module.validate_token_parameters = patched_validate
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_validate:
            self.module.validate_token_parameters = self.original_validate
auth_flows = {}
MAX_AUTH_FLOWS = 20
DEFAULT_PROJECT_ID = 'gemini-pro-1751713012-07fc4dfd'

def cleanup_auth_flows_for_memory():
    """Internal implementation detail."""
    global auth_flows
    cleanup_expired_flows()
    if len(auth_flows) > 10:
        sorted_flows = sorted(auth_flows.items(), key=lambda x: x[1].get('created_at', 0), reverse=True)
        new_auth_flows = dict(sorted_flows[:10])
        for state, flow_data in auth_flows.items():
            if state not in new_auth_flows:
                try:
                    if flow_data.get('server'):
                        server = flow_data['server']
                        port = flow_data.get('callback_port')
                        async_shutdown_server(server, port)
                except Exception:
                    pass
                flow_data.clear()
        auth_flows = new_auth_flows
        log.info('OAuth flow event')
    return len(auth_flows)

async def find_available_port(start_port: int=None) -> int:
    """Internal implementation detail."""
    if start_port is None:
        start_port = await get_callback_port()
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                log.info('OAuth flow event')
                return port
        except OSError:
            continue
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 0))
            port = s.getsockname()[1]
            log.info('OAuth flow event')
            return port
    except OSError as e:
        log.error('OAuth operation failed')
        raise RuntimeError('Operation failed')

def create_callback_server(port: int) -> HTTPServer:
    """Internal implementation detail."""
    try:
        server = HTTPServer(('0.0.0.0', port), AuthCallbackHandler)
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.timeout = 1.0
        log.info('OAuth flow event')
        return server
    except OSError as e:
        log.error('OAuth operation failed')
        raise

class AuthCallbackHandler(BaseHTTPRequestHandler):
    """Internal implementation detail."""

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get('code', [None])[0]
        state = query_components.get('state', [None])[0]
        log.info('OAuth flow event')
        if code and state and (state in auth_flows):
            auth_flows[state]['code'] = code
            auth_flows[state]['completed'] = True
            log.info('OAuth flow event')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>OAuth authentication successful!</h1><p>You can close this window. Please return to the original page and click 'Get Credentials' button.</p>")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Authentication failed.</h1><p>Please try again.</p>')

    def log_message(self, format, *args):
        pass

async def create_auth_url(project_id: Optional[str]=None, user_session: str=None, mode: str='code_assist') -> Dict[str, Any]:
    """Internal implementation detail."""
    try:
        callback_port = await find_available_port()
        callback_url = f'http://{CALLBACK_HOST}:{callback_port}'
        try:
            callback_server = create_callback_server(callback_port)
            server_thread = threading.Thread(target=callback_server.serve_forever, daemon=True, name=f'OAuth-Server-{callback_port}')
            server_thread.start()
            log.info('OAuth flow event')
        except Exception as e:
            log.error('OAuth operation failed')
            return {'success': False, 'error': f'Failed to start OAuth callback server on port {callback_port}: {str(e)}'}
        if mode == 'omni':
            client_id = OGW_CLIENT_ID
            client_secret = OGW_CLIENT_SECRET
            scopes = OGW_SCOPES
        else:
            client_id = OGW_CODE_ASSIST_CLIENT_ID
            client_secret = OGW_CODE_ASSIST_CLIENT_SECRET
            scopes = OGW_CODE_ASSIST_SCOPES
        if not client_id or not client_secret:
            client_prefix = 'OGW_CLIENT' if mode == 'omni' else 'OGW_CODE_ASSIST_CLIENT'
            return {'success': False, 'error': f'Missing OAuth client configuration. Set {client_prefix}_ID and {client_prefix}_SECRET.'}
        flow = Flow(client_id=client_id, client_secret=client_secret, scopes=scopes, redirect_uri=callback_url)
        if user_session:
            state = f'{user_session}_{str(uuid.uuid4())}'
        else:
            state = str(uuid.uuid4())
        auth_url = flow.get_auth_url(state=state)
        if len(auth_flows) >= MAX_AUTH_FLOWS:
            oldest_state = min(auth_flows.keys(), key=lambda k: auth_flows[k].get('created_at', 0))
            try:
                old_flow = auth_flows[oldest_state]
                if old_flow.get('server'):
                    server = old_flow['server']
                    port = old_flow.get('callback_port')
                    async_shutdown_server(server, port)
            except Exception as e:
                log.warning(f'Failed to cleanup old auth flow {oldest_state}: {e}')
            del auth_flows[oldest_state]
            log.debug(f'Removed oldest auth flow: {oldest_state}')
        auth_flows[state] = {'flow': flow, 'project_id': project_id, 'user_session': user_session, 'callback_port': callback_port, 'callback_url': callback_url, 'server': callback_server, 'server_thread': server_thread, 'code': None, 'completed': False, 'created_at': time.time(), 'auto_project_detection': project_id is None, 'mode': mode}
        cleanup_expired_flows()
        log.info('OAuth flow event')
        log.info('OAuth flow event')
        log.info('OAuth flow event')
        return {'auth_url': auth_url, 'state': state, 'callback_port': callback_port, 'success': True, 'auto_project_detection': project_id is None, 'detected_project_id': project_id}
    except Exception as e:
        log.error('OAuth operation failed')
        return {'success': False, 'error': str(e)}

def wait_for_callback_sync(state: str, timeout: int=300) -> Optional[str]:
    """Internal implementation detail."""
    if state not in auth_flows:
        log.error('OAuth operation failed')
        return None
    flow_data = auth_flows[state]
    callback_port = flow_data['callback_port']
    log.info('OAuth flow event')
    start_time = time.time()
    while time.time() - start_time < timeout:
        if flow_data.get('code'):
            log.info('OAuth flow event')
            return flow_data['code']
        time.sleep(0.5)
        if state in auth_flows:
            flow_data = auth_flows[state]
    log.warning('OAuth flow warning')
    return None

async def complete_auth_flow(project_id: Optional[str]=None, user_session: str=None) -> Dict[str, Any]:
    """Internal implementation detail."""
    try:
        state = None
        flow_data = None
        if project_id:
            for s, data in auth_flows.items():
                if data['project_id'] == project_id:
                    if user_session and data.get('user_session') == user_session:
                        state = s
                        flow_data = data
                        break
                    elif not state:
                        state = s
                        flow_data = data
        if not state:
            for s, data in auth_flows.items():
                if data.get('auto_project_detection', False):
                    if user_session and data.get('user_session') == user_session:
                        state = s
                        flow_data = data
                        break
                    elif not state:
                        state = s
                        flow_data = data
        if not state or not flow_data:
            return {'success': False, 'error': 'Authentication flow not found. Please click to get an authentication link first.'}
        if not project_id:
            project_id = flow_data.get('project_id')
            if not project_id:
                project_id = DEFAULT_PROJECT_ID
                log.warning('OAuth flow warning')
        flow = flow_data['flow']
        if not flow_data.get('code'):
            log.info('OAuth flow event')
            auth_code = wait_for_callback_sync(state)
            if not auth_code:
                return {'success': False, 'error': 'Authorization callback not received. Please ensure you completed OAuth authorization in the browser.'}
            auth_flows[state]['code'] = auth_code
            auth_flows[state]['completed'] = True
        else:
            auth_code = flow_data['code']
        with _OAuthLibPatcher():
            try:
                credentials = await flow.exchange_code(auth_code)
                if flow_data.get('auto_project_detection', False) and (not project_id):
                    log.info('OAuth flow event')
                    log.info('OAuth flow event')
                    log.info('OAuth flow event')
                    user_projects = await get_user_projects(credentials)
                    if user_projects:
                        if len(user_projects) == 1:
                            project_id = user_projects[0].get('projectId')
                            if project_id:
                                flow_data['project_id'] = project_id
                                log.info('OAuth flow event')
                        else:
                            project_id = await select_default_project(user_projects)
                            if project_id:
                                flow_data['project_id'] = project_id
                                log.info('OAuth flow event')
                            else:
                                return {'success': False, 'error': 'Please select one of the following projects', 'requires_project_selection': True, 'available_projects': [{'project_id': p.get('projectId'), 'name': p.get('displayName') or p.get('projectId'), 'projectNumber': p.get('projectNumber')} for p in user_projects]}
                    else:
                        project_id = DEFAULT_PROJECT_ID
                        flow_data['project_id'] = project_id
                        log.warning('OAuth flow warning')
                if not project_id:
                    project_id = DEFAULT_PROJECT_ID
                    flow_data['project_id'] = project_id
                    log.warning('OAuth flow warning')
                saved_filename = await save_credentials(credentials, project_id)
                creds_data = _prepare_credentials_data(credentials, project_id, mode='code_assist')
                _cleanup_auth_flow_server(state)
                log.info('OAuth flow event')
                return {'success': True, 'credentials': creds_data, 'file_path': saved_filename, 'auto_detected_project': flow_data.get('auto_project_detection', False)}
            except Exception as e:
                log.error(f'Failed to retrieve credential: {e}')
                return {'success': False, 'error': f'Failed to retrieve credential: {str(e)}'}
    except Exception as e:
        log.error('OAuth operation failed')
        return {'success': False, 'error': str(e)}

async def asyncio_complete_auth_flow(project_id: Optional[str]=None, user_session: str=None, mode: str='code_assist') -> Dict[str, Any]:
    """Internal implementation detail."""
    try:
        log.info('OAuth flow event')
        state = None
        flow_data = None
        log.debug('OAuth debug event')
        if project_id:
            log.info('OAuth flow event')
            for s, data in auth_flows.items():
                if data['project_id'] == project_id:
                    if user_session and data.get('user_session') == user_session:
                        state = s
                        flow_data = data
                        log.info('OAuth flow event')
                        break
                    elif not state:
                        state = s
                        flow_data = data
                        log.info('OAuth flow event')
        if not state:
            log.info('OAuth flow event')
            completed_flows = []
            for s, data in auth_flows.items():
                if data.get('auto_project_detection', False):
                    if user_session and data.get('user_session') == user_session:
                        if data.get('code'):
                            completed_flows.append((s, data, data.get('created_at', 0)))
            if completed_flows:
                completed_flows.sort(key=lambda x: x[2], reverse=True)
                state, flow_data, _ = completed_flows[0]
                log.info('OAuth flow event')
            else:
                pending_flows = []
                for s, data in auth_flows.items():
                    if data.get('auto_project_detection', False):
                        if user_session and data.get('user_session') == user_session:
                            pending_flows.append((s, data, data.get('created_at', 0)))
                        elif not user_session:
                            pending_flows.append((s, data, data.get('created_at', 0)))
                if pending_flows:
                    pending_flows.sort(key=lambda x: x[2], reverse=True)
                    state, flow_data, _ = pending_flows[0]
                    log.info('OAuth flow event')
        if not state or not flow_data:
            log.error('OAuth operation failed')
            log.debug('OAuth debug event')
            return {'success': False, 'error': 'Authentication flow not found. Please click to get an authentication link first.'}
        log.info('OAuth flow event')
        log.info('OAuth flow event')
        log.info('OAuth flow event')
        log.info('OAuth flow event')
        if flow_data.get('auto_project_detection', False) and (not project_id):
            log.info('OAuth flow event')
        elif not project_id:
            log.info('OAuth flow event')
            project_id = flow_data.get('project_id')
            if not project_id:
                project_id = DEFAULT_PROJECT_ID
                flow_data['project_id'] = project_id
                log.warning('OAuth flow warning')
        else:
            log.info('OAuth flow event')
        log.info('OAuth flow event')
        log.info('OAuth flow event')
        log.info('OAuth flow event')
        max_wait_time = 60
        wait_interval = 1
        waited = 0
        while waited < max_wait_time:
            if flow_data.get('code'):
                log.info('OAuth flow event')
                break
            if waited % 5 == 0 and waited > 0:
                log.info('OAuth flow event')
                log.debug('OAuth debug event')
            await asyncio.sleep(wait_interval)
            waited += wait_interval
            if state in auth_flows:
                flow_data = auth_flows[state]
        if not flow_data.get('code'):
            log.error('OAuth operation failed')
            return {'success': False, 'error': 'OAuth callback timed out. Please ensure you completed authorization in your browser and saw the success page.'}
        flow = flow_data['flow']
        auth_code = flow_data['code']
        log.info('OAuth flow event')
        with _OAuthLibPatcher():
            try:
                log.info('OAuth flow event')
                credentials = await flow.exchange_code(auth_code)
                log.info('OAuth flow event')
                log.info('OAuth flow event')
                cred_mode = flow_data.get('mode', 'code_assist') if flow_data.get('mode') else mode
                if cred_mode == 'omni':
                    log.info('OAuth flow event')
                    omni_url = await get_ogw_api_url()
                    project_id, subscription_tier = await fetch_project_id_and_tier(credentials.access_token, OGW_USER_AGENT, omni_url)
                    if project_id:
                        log.info(f'Successfully fetched project_id from API: {project_id}, tier: {subscription_tier}')
                    else:
                        project_id = DEFAULT_PROJECT_ID
                        log.warning(f'Unable to fetch project_id from API, using default project_id: {project_id}')
                    saved_filename = await save_credentials(credentials, project_id, mode='omni', subscription_tier=subscription_tier)
                    creds_data = _prepare_credentials_data(credentials, project_id, mode='omni', subscription_tier=subscription_tier)
                    _cleanup_auth_flow_server(state)
                    log.info('OAuth flow event')
                    return {'success': True, 'credentials': creds_data, 'file_path': saved_filename, 'auto_detected_project': False, 'mode': 'omni'}
                if flow_data.get('auto_project_detection', False) and (not project_id):
                    log.info('Standard mode: Fetching project_id from project list...')
                    user_projects = await get_user_projects(credentials)
                    if user_projects:
                        if len(user_projects) == 1:
                            project_id = user_projects[0].get('projectId')
                            if project_id:
                                flow_data['project_id'] = project_id
                                log.info('OAuth flow event')
                                log.info('OAuth flow event')
                                await enable_required_apis(credentials, project_id)
                        else:
                            project_id = await select_default_project(user_projects)
                            if project_id:
                                flow_data['project_id'] = project_id
                                log.info('OAuth flow event')
                                log.info('OAuth flow event')
                                await enable_required_apis(credentials, project_id)
                            else:
                                return {'success': False, 'error': 'Please select one of the following projects', 'requires_project_selection': True, 'available_projects': [{'project_id': p.get('projectId'), 'name': p.get('displayName') or p.get('projectId'), 'projectNumber': p.get('projectNumber')} for p in user_projects]}
                    else:
                        project_id = DEFAULT_PROJECT_ID
                        flow_data['project_id'] = project_id
                        log.warning('OAuth flow warning')
                elif project_id:
                    log.info('OAuth flow event')
                    await enable_required_apis(credentials, project_id)
                if not project_id:
                    project_id = DEFAULT_PROJECT_ID
                    flow_data['project_id'] = project_id
                    log.warning('OAuth flow warning')
                saved_filename = await save_credentials(credentials, project_id)
                creds_data = _prepare_credentials_data(credentials, project_id, mode='code_assist')
                _cleanup_auth_flow_server(state)
                log.info('OAuth flow event')
                return {'success': True, 'credentials': creds_data, 'file_path': saved_filename, 'auto_detected_project': flow_data.get('auto_project_detection', False)}
            except Exception as e:
                log.error(f'Failed to retrieve credential: {e}')
                return {'success': False, 'error': f'Failed to retrieve credential: {str(e)}'}
    except Exception as e:
        log.error(f'Failed to complete asynchronous auth flow: {e}')
        return {'success': False, 'error': str(e)}

async def complete_auth_flow_from_callback_url(callback_url: str, project_id: Optional[str]=None, mode: str='code_assist') -> Dict[str, Any]:
    """Internal implementation detail."""
    try:
        log.info(f'Starting authentication from callback URL: {callback_url}')
        parsed_url = urlparse(callback_url)
        query_params = parse_qs(parsed_url.query)
        if 'state' not in query_params or 'code' not in query_params:
            return {'success': False, 'error': 'Callback URL is missing required parameters (state or code)'}
        state = query_params['state'][0]
        code = query_params['code'][0]
        log.info(f'Parsed from URL: state={state}, code=xxx...')
        if state not in auth_flows:
            return {'success': False, 'error': f'Authentication flow not found. Please start authentication first (state: {state})'}
        flow_data = auth_flows[state]
        flow = flow_data['flow']
        redirect_uri = flow.redirect_uri
        log.info(f'Using redirect_uri: {redirect_uri}')
        try:
            credentials = await flow.exchange_code(code)
            log.info('Access token retrieved successfully')
            cred_mode = flow_data.get('mode', 'code_assist') if flow_data.get('mode') else mode
            if cred_mode == 'omni':
                log.info('Omni mode (from callback URL): Fetching project_id from API...')
                omni_url = await get_ogw_api_url()
                project_id, subscription_tier = await fetch_project_id_and_tier(credentials.access_token, OGW_USER_AGENT, omni_url)
                if project_id:
                    log.info(f'Successfully fetched project_id from API: {project_id}, tier: {subscription_tier}')
                else:
                    project_id = DEFAULT_PROJECT_ID
                    log.warning(f'Unable to fetch project_id from API, using default project_id: {project_id}')
                saved_filename = await save_credentials(credentials, project_id, mode='omni', subscription_tier=subscription_tier)
                creds_data = _prepare_credentials_data(credentials, project_id, mode='omni', subscription_tier=subscription_tier)
                _cleanup_auth_flow_server(state)
                log.info('Completed Omni OAuth auth from callback URL successfully, credentials saved')
                return {'success': True, 'credentials': creds_data, 'file_path': saved_filename, 'auto_detected_project': False, 'mode': 'omni'}
            detected_project_id = None
            auto_detected = False
            subscription_tier = None
            if not project_id:
                try:
                    log.info('Standard mode: Fetching project_id from project list...')
                    projects = await get_user_projects(credentials)
                    if projects:
                        if len(projects) == 1:
                            detected_project_id = projects[0]['projectId']
                            auto_detected = True
                            log.info(f'Automatically detected unique project ID: {detected_project_id}')
                        else:
                            detected_project_id = projects[0]['projectId']
                            auto_detected = True
                            log.info(f'Detected {len(projects)} projects, automatically selected first: {detected_project_id}')
                            log.debug(f"Other available projects: {[p['projectId'] for p in projects[1:]]}")
                    else:
                        detected_project_id = DEFAULT_PROJECT_ID
                        auto_detected = False
                        log.warning(f'No accessible projects detected, using default project_id: {detected_project_id}')
                except Exception as e:
                    log.warning(f'Failed to retrieve project list: {e}, using default project_id')
                    detected_project_id = DEFAULT_PROJECT_ID
                    auto_detected = False
            else:
                detected_project_id = project_id
            if detected_project_id:
                try:
                    log.info(f'Enabling required API services for project {detected_project_id}...')
                    await enable_required_apis(credentials, detected_project_id)
                except Exception as e:
                    log.warning(f'Failed to enable API services: {e}')
            saved_filename = await save_credentials(credentials, detected_project_id, subscription_tier=subscription_tier)
            creds_data = _prepare_credentials_data(credentials, detected_project_id, mode='code_assist', subscription_tier=subscription_tier)
            _cleanup_auth_flow_server(state)
            log.info('Completed OAuth auth from callback URL successfully, credentials saved')
            return {'success': True, 'credentials': creds_data, 'file_path': saved_filename, 'auto_detected_project': auto_detected}
        except Exception as e:
            log.error(f'Failed to retrieve credential from callback URL: {e}')
            return {'success': False, 'error': f'Failed to retrieve credential: {str(e)}'}
    except Exception as e:
        log.error(f'Failed to complete auth flow from callback URL: {e}')
        return {'success': False, 'error': str(e)}

async def save_credentials(creds: Credentials, project_id: str, mode: str='code_assist', subscription_tier: str=None) -> str:
    """Internal implementation detail."""
    timestamp = int(time.time())
    if mode == 'omni':
        filename = f'ag_{project_id}-{timestamp}.json'
    else:
        filename = f'{project_id}-{timestamp}.json'
    creds_data = _prepare_credentials_data(creds, project_id, mode, subscription_tier)
    storage_adapter = await get_storage_adapter()
    success = await storage_adapter.store_credential(filename, creds_data, mode=mode)
    if success:
        try:
            default_state = {'error_codes': [], 'disabled': False, 'last_success': time.time(), 'user_email': None, 'tier': subscription_tier}
            await storage_adapter.update_credential_state(filename, default_state, mode=mode)
            log.info('OAuth flow event')
        except Exception as e:
            log.warning('OAuth flow warning')
        return filename
    else:
        raise Exception('Operation failed')

def async_shutdown_server(server, port):
    """Internal implementation detail."""

    def shutdown_server_async():
        try:
            shutdown_completed = threading.Event()

            def do_shutdown():
                try:
                    server.shutdown()
                    server.server_close()
                    shutdown_completed.set()
                    log.info('OAuth flow event')
                except Exception as e:
                    shutdown_completed.set()
                    log.debug('OAuth debug event')
            shutdown_worker = threading.Thread(target=do_shutdown, daemon=True)
            shutdown_worker.start()
            if shutdown_completed.wait(timeout=5):
                log.debug('OAuth debug event')
            else:
                log.warning('OAuth flow warning')
        except Exception as e:
            log.debug('OAuth debug event')
    shutdown_thread = threading.Thread(target=shutdown_server_async, daemon=True)
    shutdown_thread.start()
    log.debug('OAuth debug event')

def cleanup_expired_flows():
    """Internal implementation detail."""
    current_time = time.time()
    EXPIRY_TIME = 600
    states_to_remove = [state for state, flow_data in auth_flows.items() if current_time - flow_data['created_at'] > EXPIRY_TIME]
    cleaned_count = 0
    for state in states_to_remove:
        flow_data = auth_flows.get(state)
        if flow_data:
            try:
                if flow_data.get('server'):
                    server = flow_data['server']
                    port = flow_data.get('callback_port')
                    async_shutdown_server(server, port)
            except Exception as e:
                log.debug('OAuth debug event')
            flow_data.clear()
            del auth_flows[state]
            cleaned_count += 1
    if cleaned_count > 0:
        log.info('OAuth flow event')
    if len(auth_flows) > 20:
        import gc
        gc.collect()
        log.debug('OAuth debug event')

def get_auth_status(project_id: str) -> Dict[str, Any]:
    """Internal implementation detail."""
    for state, flow_data in auth_flows.items():
        if flow_data['project_id'] == project_id:
            return {'status': 'completed' if flow_data['completed'] else 'pending', 'state': state, 'created_at': flow_data['created_at']}
    return {'status': 'not_found'}
auth_tokens = {}
TOKEN_EXPIRY = 3600

async def verify_password(password: str) -> bool:
    """Internal implementation detail."""
    from config import get_panel_password, has_password_configured
    if not await has_password_configured():
        return False
    correct_password = await get_panel_password()
    if not correct_password:
        return False
    return password == correct_password
