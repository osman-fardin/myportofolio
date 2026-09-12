const menu = document.querySelector('.site-menu');

if (menu) {
    const menuLinks = menu.querySelectorAll('.menu-navigation a');

    menuLinks.forEach((link) => {
        link.addEventListener('click', () => {
            const destination = new URL(link.href, window.location.href);
            const staysOnCurrentPage =
                destination.pathname === window.location.pathname &&
                destination.search === window.location.search;

            if (staysOnCurrentPage) {
                menu.removeAttribute('open');
            }
        });
    });
}
