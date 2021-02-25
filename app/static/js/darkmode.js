const ROOT = document.documentElement;
window.addEventListener("DOMContentLoaded", (event) => {
  const button = document.querySelector("#darkmode");
  let isDarkMode = localStorage.getItem("isDarkMode") == "true";
  setThemeMode(isDarkMode, button, ROOT);
  button.addEventListener("click", (event) => {
    isDarkMode = !isDarkMode;
    localStorage.setItem("isDarkMode", isDarkMode);
    setThemeMode(isDarkMode, button, ROOT);
  });
});

function changeIcon(mode) {
  const modeButton = document.querySelector("#darkmode");
  modeButton.name = mode;
}

function setThemeMode(isDarkMode, button, root) {
  if (isDarkMode) {
    console.log(root)
    root.dataset['colorMode'] = "dark";
    button.name = "moon";
    changeIcon("moon");
  } else {
    root.dataset['colorMode'] = "regular";
    button.name = "moon-outline";
    changeIcon("moon-outline");
  }
}
