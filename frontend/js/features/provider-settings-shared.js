function setProviderSettingsLoading(loadingIds, formIds, isLoading, preserveContent = false) {
    loadingIds.forEach((id) => {
        const element = document.getElementById(id);
        if (!element) return;
        element.hidden = !isLoading || preserveContent;
        element.setAttribute('aria-busy', String(isLoading));
    });

    formIds.forEach((id) => {
        document.getElementById(id)?.classList.toggle('hidden', isLoading && !preserveContent);
    });
}
