(function () {
    const root = document.documentElement;

    let saved = null;
    try { saved = localStorage.getItem('theme'); } catch (e) { }
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.setAttribute('data-theme', saved || (prefersDark ? 'dark' : 'light'));

    document.addEventListener('DOMContentLoaded', function () {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'theme-toggle';
        btn.setAttribute('aria-label', 'Toggle dark mode');

        function render() {
            btn.textContent = root.getAttribute('data-theme') === 'dark' ? '☀ Light' : '🌙 Dark';
        }

        btn.addEventListener('click', function () {
            const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            try { localStorage.setItem('theme', next); } catch (e) { }
            render();
        });

        render();
        document.body.appendChild(btn);
    });
})();