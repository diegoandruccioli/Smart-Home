/*!
 * Gestore Tema Dark/Light per Bootstrap 5.3+
 * Salva la preferenza in localStorage.
 */
(() => {
    'use strict';

    const getStoredTheme = () => localStorage.getItem('theme');
    const setStoredTheme = theme => localStorage.setItem('theme', theme);

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme();
        if (storedTheme) {
            return storedTheme;
        }
        // Fallback: usa le preferenze di sistema
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const setTheme = theme => {
        document.documentElement.setAttribute('data-bs-theme', theme);
    };

    // Imposta il tema al caricamento della pagina
    const initialTheme = getPreferredTheme();
    setTheme(initialTheme);

    // Aggiungi l'evento al pulsante
    window.addEventListener('DOMContentLoaded', () => {
        const themeToggleButton = document.getElementById('theme-toggle-btn');

        if (themeToggleButton) {
            themeToggleButton.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-bs-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                setStoredTheme(newTheme);
                setTheme(newTheme);
            });
        }
    });
})();