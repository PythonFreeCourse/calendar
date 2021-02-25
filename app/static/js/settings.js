document.addEventListener('DOMContentLoaded', () => {
    const tabBtn = document.querySelectorAll(".tab");
    for (let i = 0; i < tabBtn.length; i++) {
        const btn = document.getElementById("tab" + i);
        btn.addEventListener('click', () => {
            tabClick(btn.id, tabBtn);
        });
    }
});


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
