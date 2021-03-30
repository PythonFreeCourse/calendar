document.addEventListener("DOMContentLoaded", () => {
  const tabBtn = document.getElementsByClassName("tab");
  for (let i = 0; i < tabBtn.length; i++) {
    const btn = document.getElementById("tab" + i);
    btn.addEventListener("click", () => {
      tabClick(btn.id, tabBtn);
    });
  }

  const menstrualSubscriptionSwitch = document.getElementById("switch3");
  menstrualSubscriptionSwitch.addEventListener("click", () => {
    const btnState = menstrualSubscriptionSwitch.checked;
    if (btnState) {
    fetch('/menstrual-predictor/')
    .then(response => {
        let subscriptionContainer = document.getElementById('menstrual-prediction-container');
        subscriptionContainer.innerHTML = response;
    })

      console.log(menstrualSubscriptionSwitch.checked);
    }
  });
});
async function loadSubscriptionPage(response){
    const data = await response.text();
    return data;
}
function tabClick(tab_id, tabBtn) {
  let shownTab = document.querySelector(".tab-show");
  let selectedTabContent = document.querySelector(`#${tab_id}-content`);
  shownTab.classList.remove("tab-show");
  shownTab.classList.add("tab-hide");
  for (btn of tabBtn) {
    btn.children[0].classList.remove("active");
  }
  document.getElementById(tab_id).classList.add("active");
  selectedTabContent.classList.remove("tab-hide");
  selectedTabContent.classList.add("tab-show");
}
