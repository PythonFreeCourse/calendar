const ROOT = document.documentElement;

window.addEventListener("DOMContentLoaded", (event) => {
  const button = document.getElementById("darkmode");
  let isDarkMode = localStorage.getItem("isDarkMode") == "true";
  setThemeMode(isDarkMode, button, ROOT);
  button.addEventListener("click", (event) => {
    isDarkMode = !isDarkMode;
    localStorage.setItem("isDarkMode", isDarkMode);
    setThemeMode(isDarkMode, button, ROOT);
  });
});

function changeIcon(mode) {
  const modeButton = document.getElementById("darkmode");
  modeButton.name = mode;
}

function setThemeMode(isDarkMode, button, root) {
  if (isDarkMode) {
    root.dataset['colorMode'] = "dark";
    button.name = "moon";
    changeIcon("moon");
  } else {
    root.dataset['colorMode'] = "regular";
    button.name = "moon-outline";
    changeIcon("moon-outline");
  }
}
