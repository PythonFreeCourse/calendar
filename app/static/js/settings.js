const tabBtn =
    document.querySelectorAll(".tab");


function tabClick(tab_id) {
    let shown_tab = document.querySelector(".tabShow")
    let selected_tab_content = document.querySelector("#" + tab_id + "-content")
    shown_tab.classList.remove("tabShow")
    shown_tab.classList.add("tabHide")
    for (btn of tabBtn) {
        btn.children[0].classList.remove("active")
    }
    document.getElementById(tab_id).classList.add("active")
    selected_tab_content.classList.remove("tabHide")
    selected_tab_content.classList.add("tabShow")
};


for (i = 0; i < tabBtn.length; i++) {
    let btn = document.getElementById("tab" + i)
    btn.addEventListener('click', () => {
        tabClick(btn.id)
    })
}
