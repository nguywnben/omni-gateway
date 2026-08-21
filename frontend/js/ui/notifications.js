// Omni Gateway management console: ui.

function ensureTerminalPunctuation(message) {

    const value = String(message ?? '');
    const trimmedEnd = value.trimEnd();

    if (!trimmedEnd) return value;

    const visibleText = trimmedEnd
        .replace(/<br\s*\/?>/gi, ' ')
        .replace(/<[^>]+>/g, '')
        .trim();

    if (!visibleText || /[.!?;:…]$/.test(visibleText)) return value;

    return value.slice(0, trimmedEnd.length) + '.' + value.slice(trimmedEnd.length);

}

function mountModal(modal) {

    document.body.appendChild(modal);
    return Promise.resolve();

}

function unmountModal(modal) {

    modal.remove();
    return Promise.resolve();

}

function showStatus(message, type = 'info') {

    const displayMessage = ensureTerminalPunctuation(message);

    const statusSection = document.getElementById('statusSection');

    if (statusSection) {

        if (window._statusTimeout) {

            clearTimeout(window._statusTimeout);

        }

        const statusDiv = document.createElement('div');
        const statusType = ['success', 'error', 'warning', 'info'].includes(type)
            ? type
            : 'info';
        statusDiv.className = `status ${statusType}`;
        statusDiv.textContent = displayMessage;
        statusSection.replaceChildren(statusDiv);

        window._statusTimeout = setTimeout(() => {

            if (statusDiv.parentElement === statusSection) statusDiv.remove();

        }, 3000);

    } else {

        showMessageModal(t('dialog_tip'), displayMessage, 'info');

    }

}
