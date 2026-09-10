const ACTIVITY_VIEWS = Object.freeze({
    traces: {tabId: 'activityTracesTab', panelId: 'activityTracesPanel', loader: 'traces'},
    audit: {tabId: 'activityAuditTab', panelId: 'activityAuditPanel', loader: 'audit'},
    runtime: {tabId: 'activityRuntimeTab', panelId: 'activityRuntimePanel', loader: 'runtime_logs'}
});

function normalizeActivityView(view) {
    return Object.hasOwn(ACTIVITY_VIEWS, view) ? view : 'traces';
}

function activityViewFromLocation(pathname = window.location.pathname, search = window.location.search) {
    if (pathname === '/audit') return 'audit';
    if (pathname === '/logs') return 'traces';
    return normalizeActivityView(new URLSearchParams(search).get('view'));
}

function setActivityView(view, {load = true} = {}) {
    const selectedView = normalizeActivityView(view);
    AppState.activeActivityView = selectedView;

    for (const [name, definition] of Object.entries(ACTIVITY_VIEWS)) {
        const selected = name === selectedView;
        const tab = document.getElementById(definition.tabId);
        const panel = document.getElementById(definition.panelId);
        if (tab) {
            tab.setAttribute('aria-selected', String(selected));
            tab.tabIndex = selected ? 0 : -1;
        }
        if (panel) panel.hidden = !selected;
    }

    if (load) return triggerTabDataLoad(ACTIVITY_VIEWS[selectedView].loader);
}

function activityUrl(view) {
    return view === 'traces' ? '/activity' : `/activity?view=${encodeURIComponent(view)}`;
}

function switchActivityView(view) {
    const selectedView = normalizeActivityView(view);
    const nextUrl = activityUrl(selectedView);
    if (`${window.location.pathname}${window.location.search}` !== nextUrl) {
        history.pushState(null, '', nextUrl);
    }
    return setActivityView(selectedView);
}

function loadActivityConsole() {
    const selectedView = normalizeActivityView(AppState.activeActivityView);
    return triggerTabDataLoad(ACTIVITY_VIEWS[selectedView].loader);
}

function initActivityTabs() {
    for (const [name, definition] of Object.entries(ACTIVITY_VIEWS)) {
        const tab = document.getElementById(definition.tabId);
        tab?.addEventListener('keydown', (event) => {
            if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
            event.preventDefault();
            const names = Object.keys(ACTIVITY_VIEWS);
            const currentIndex = names.indexOf(name);
            let nextIndex = currentIndex;
            if (event.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + names.length) % names.length;
            if (event.key === 'ArrowRight') nextIndex = (currentIndex + 1) % names.length;
            if (event.key === 'Home') nextIndex = 0;
            if (event.key === 'End') nextIndex = names.length - 1;
            const nextView = names[nextIndex];
            switchActivityView(nextView);
            document.getElementById(ACTIVITY_VIEWS[nextView].tabId)?.focus();
        });
    }
    setActivityView(activityViewFromLocation(), {load: false});
}

document.addEventListener('DOMContentLoaded', initActivityTabs);
