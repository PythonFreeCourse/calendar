const root = document.documentElement
window.addEventListener('DOMContentLoaded', (event) => {
    const button = document.querySelector('#darkmode');
    console.log('loaded')
    let isDarkMode = (localStorage.getItem('isDarkMode') == "true");
    setThemeMode(isDarkMode, button);
    button.addEventListener('click', event => {
    isDarkMode = !isDarkMode;
    localStorage.setItem('isDarkMode', isDarkMode);
    setThemeMode(isDarkMode, button);
    });
});

function changeIcon(mode) {
    const modeButton = document.querySelector('#darkmode');
    modeButton.name = mode;
}

function setThemeMode(isDarkMode, button) {
    if (isDarkMode) {
        root.setAttribute("color-mode", "dark");
        button.name = 'moon';
        changeIcon('moon');
    } else {
        root.setAttribute("color-mode", "regular");
        button.name = 'moon-outline';
        changeIcon('moon-outline');
    }
}
