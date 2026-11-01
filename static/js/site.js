const menu = document.querySelector('.menu-button');
const navigation = document.querySelector('#navigation');
if (menu && navigation) {
    menu.addEventListener('click', () => {
        const expanded = menu.getAttribute('aria-expanded') !== 'true';
        // Keep the screen-reader state in sync with the visible navigation.
        menu.setAttribute('aria-expanded', String(expanded));
        navigation.classList.toggle('is-open', expanded);
    });
}
