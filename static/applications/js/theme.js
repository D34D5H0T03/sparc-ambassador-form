document.addEventListener("DOMContentLoaded", () => {
    const STORAGE_KEY = "sparc-theme";
    const rootElement = document.documentElement;
    const toggleButton = document.getElementById("theme-toggle");
    const toggleLabel = document.getElementById("theme-toggle-label");

    function applyTheme(theme) {
        const normalizedTheme = theme === "dark" ? "dark" : "light";
        rootElement.setAttribute("data-theme", normalizedTheme);
        localStorage.setItem(STORAGE_KEY, normalizedTheme);

        if (toggleButton && toggleLabel) {
            const isDark = normalizedTheme === "dark";
            toggleLabel.textContent = isDark ? "Dark" : "Light";
            toggleButton.setAttribute(
                "aria-label",
                isDark ? "Switch to light theme" : "Switch to dark theme"
            );
            toggleButton.setAttribute("aria-pressed", String(isDark));
        }
    }

    const currentTheme = rootElement.getAttribute("data-theme") || "light";
    applyTheme(currentTheme);

    if (toggleButton) {
        toggleButton.addEventListener("click", () => {
            const activeTheme = rootElement.getAttribute("data-theme");
            const nextTheme = activeTheme === "dark" ? "light" : "dark";
            applyTheme(nextTheme);
        });
    }
});