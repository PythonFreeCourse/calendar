function openPanel(targetID, classToSet) {
    const target = document.getElementById(targetID);
    target.classList.toggle(classToSet);
}

function setFeatureInformation(element) {
    const panel = {
        "feature-description": element.dataset.description,
        "feature-name": element.dataset.name,
        "feature-followers": element.dataset.followers,
        "feature-creator": element.dataset.creator
    };
    for (const key in panel) {
        document.getElementById(key).innerHTML = panel[key];
    }
    console.log('make a call')
    renderTemplate(panel["feature-name"]);
}

function setFeaturesSettings() {
    const allFeatures = document.getElementsByClassName("feature");
    for (let i = 0; i < allFeatures.length; ++i) {
        allFeatures[i].addEventListener('click', function () {
            openPanel("feature-set-panel", "feature-settings-open");
            const target = document.getElementById("feature-set-panel");
            if (target.classList.contains("feature-settings-open")) {
                setFeatureInformation(allFeatures[i]);
            }
        })
    }
}

function appandFeatures(){
    const baseURL = window.location.origin;
    const route = new URL('/features/installed', baseURL);

    fetch(route)
        .then((response) => {
                return response.json();
            }).then((data) => {
                const iconStrip = document.getElementById('icon-strip');
                for (let i = 0; i < data.length; ++i) {
                    const fData = data[i]
                    console.log(fData)
                    let feature = document.createElement('div');
                    feature.classList.add('feature');
                    feature.id = 'feature-' + fData.id;
                    feature.dataset.name = fData.name;
                    feature.dataset.creator = fData.creator;
                    feature.dataset.description = fData.description;
                    feature.dataset.followers = fData.followers;

                    console.log(feature)

                    let icon = document.createElement('ion-icon');
                    icon.setAttribute('name', fData.icon);
                    feature.appendChild(icon);
                    iconStrip.appendChild(feature);
                }
            });
}

function renderTemplate(featureName){
    const baseURL = window.location.origin;
    const route = new URL('/features/settings/' + featureName, baseURL);
    const formData = new FormData();
    formData.append('feature_name', featureName);

    fetch(route,
        {
            body: formData,
            method: "post"
        }
    ).then(function (response) {
        return response.text();
    }).then(function (html) {
        const content = document.getElementById("feature-content")
        content.innerHTML = ''
        content.insertAdjacentHTML('afterbegin', html);
    });
}

document.addEventListener(
    'DOMContentLoaded', function () {
    appandFeatures();
    setTimeout(setFeaturesSettings, 200);
    }
)
