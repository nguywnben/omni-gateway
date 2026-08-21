function autoSetKeepaliveUrl() {

    const url = `${window.location.protocol}//${window.location.host}`;

    document.getElementById('keepaliveUrl').value = url;

}



function setMobileMenuState(isOpen) {
    const sidebar = document.querySelector('.dashboard-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const menuButton = document.querySelector('.mobile-menu-btn');
    if (!sidebar || !overlay) return;

    sidebar.classList.toggle('open', isOpen);
    overlay.classList.toggle('open', isOpen);
    document.body.classList.toggle('mobile-menu-open', isOpen);
    overlay.style.display = isOpen ? 'block' : 'none';
    overlay.setAttribute('aria-hidden', String(!isOpen));

    if (menuButton) {
        menuButton.setAttribute('aria-expanded', String(isOpen));
        menuButton.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
    }
}

function toggleMobileMenu() {
    const sidebar = document.querySelector('.dashboard-sidebar');
    setMobileMenuState(!sidebar?.classList.contains('open'));
}

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setMobileMenuState(false);
});
