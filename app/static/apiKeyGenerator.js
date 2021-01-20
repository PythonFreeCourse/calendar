async function callAPIKeyRoute(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    body: JSON.stringify(data),
  });
  return response.json();
}

async function buildAPIContent(state) {
  callAPIKeyRoute("/api/generate_key", { user: user_id, refresh: state }).then(
    (data) => {
      let keyText = document.getElementById("apiKeyHolder");
      keyText.textContent = "API Key: " + data.key;
    }
  );
}

async function removeAPIContent() {
  callAPIKeyRoute("/api/delete_key", { user: user_id }).then((data) => {
    if (data.success) {
      let keyText = document.getElementById("apiKeyHolder");
      let refreshButton = document.getElementById("apiKeyRefresh");
      keyText.insertAdjacentHTML(
        "beforebegin",
        '<button id="apiKeyGen" type="button" class="btn btn-primary">Generate API Key</button>'
      );
      keyText.remove();
      refreshButton.remove();
      buildGenButton();
    }
  });
}

function activateGenButton(genButton) {
  genButton.insertAdjacentHTML(
    "afterend",
    '<p id="apiKeyHolder" class="m-0"></p><button id="apiKeyRefresh" type="button" class="btn btn-primary">Refresh API Key</button><button id="apiKeyDelete" type="button" class="btn btn-primary">Delete API Key</button>'
  );
  buildAPIContent(false).then(genButton.remove());
  buildRefreshButton();
  buildDeleteButton();
}

function buildRefreshButton() {
  const refreshButton = document.getElementById("apiKeyRefresh");
  refreshButton.addEventListener("click", function () {
    buildAPIContent(true);
  });
}

function buildDeleteButton() {
  const delButton = document.getElementById("apiKeyDelete");
  delButton.addEventListener("click", function () {
    removeAPIContent();
    delButton.remove();
  });
}

function buildGenButton() {
  const genButton = document.getElementById("apiKeyGen");
  genButton.addEventListener("click", function () {
    activateGenButton(genButton);
  });
}

if (document.getElementById("apiKeyGen")) {
  buildGenButton();
}

if (document.getElementById("apiKeyRefresh")) {
  buildRefreshButton();
}

if (document.getElementById("apiKeyDelete")) {
  buildDeleteButton();
}
