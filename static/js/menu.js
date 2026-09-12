const menu = document.querySelector('.site-menu');

if (menu) {
    const menuLinks = menu.querySelectorAll('.menu-navigation a');

    menuLinks.forEach((link) => {
        link.addEventListener('click', () => {
            menu.removeAttribute('open');
        });
    });
}
