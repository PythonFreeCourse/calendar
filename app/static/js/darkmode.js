let root = document.documentElement;
console.log('koree')
const button = document.querySelector('#darkmode');
let isDarkMode = (localStorage.getItem('isDarkMode') == "true");
setThemeMode(isDarkMode, button)

button.addEventListener('click', event => {
    isDarkMode = !isDarkMode
    localStorage.setItem('isDarkMode', isDarkMode);
    setThemeMode(isDarkMode, button)
});


function changeIcon(mode) {
    setTimeout(function() {
        const modeButton = document.querySelector('#darkmode');
        modeButton.name = mode
        }, 100)
}


function setThemeMode(isDarkMode, button) {
    const DARK_BACKGROUND = "#000000";
    const REG_BACKGROUND = "#f7f7f7";
    const DARK_TEXT = "#EEEEEE"
    const REG_TEXT = "#222831"
    const DARK_START_MONTH = "#8c28bf"
    const REG_START_MONTH = "#e9ecef"
    const DARK_NAVBAR_COLOR = "#e9ecef"
    const REG_NAVBAR_COLOR = "rgba(0,0,0,.55)"
    const DARK_NAVBAR_HOVCOLOR = "rgb(255 255 255)"
    const REG_NAVBAR_HOVCOLOR = "rgba(0,0,0,.7)"
    const DARK_CARD_COLOR = "#230a88";
    const REG_CARD_COLOR = "#fff";
    if (isDarkMode) {
        root.style.setProperty('--backgroundcol', DARK_BACKGROUND);
        root.style.setProperty('--textcolor', DARK_TEXT);
        root.style.setProperty('--start-of-month', DARK_START_MONTH);
        root.style.setProperty('--navcolor', DARK_NAVBAR_COLOR);
        root.style.setProperty('--navhovercolor', DARK_NAVBAR_HOVCOLOR);
        root.style.setProperty('--cardcolor', DARK_CARD_COLOR);
        button.name = 'moon';
        changeIcon('moon');
    } else {
        root.style.setProperty('--backgroundcol', REG_BACKGROUND);
        root.style.setProperty('--textcolor', REG_TEXT);
        root.style.setProperty('--start-of-month', REG_START_MONTH);
        root.style.setProperty('--navcolor', REG_NAVBAR_COLOR);
        root.style.setProperty('--navhovercolor', REG_NAVBAR_HOVCOLOR);
        root.style.setProperty('--cardcolor', REG_CARD_COLOR);
        button.name = 'moon-outline';
        changeIcon('moon-outline');
    }
}
