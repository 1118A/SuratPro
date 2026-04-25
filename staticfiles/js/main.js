// FreelanceMarket — Main JavaScript

document.addEventListener('DOMContentLoaded', function () {

    // ---- Auto-dismiss flash alerts after 5 seconds ----
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            } else {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.4s ease';
                setTimeout(function () { alert.remove(); }, 400);
            }
        }, 5000);
    });

    // ---- Active nav link highlighting ----
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link-main').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === currentPath) {
            link.classList.add('active');
        }
    });

    // ---- Bootstrap tooltip init ----
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

});
