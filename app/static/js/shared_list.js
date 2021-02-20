var items_num = 1;

document.addEventListener('click', function(e) {
    if (e.target && e.target.id.includes('btnRemoveItem')){
        removeItem(e.target.id);
    }
    else if (e.target && e.target.id.includes("btnRemoveLabel")) {
        let parent = document.getElementById(e.target.id).parentElement.id
        removeItem(parent);
    }
    else if (e.target && e.target.id == "btnAddItem"){
        addItem();
    }
});


function addItem() {
    let remove_button = 7;
    let remove_label = 1;
    let item = document.getElementById("shared_list_item").cloneNode(true);
    item.style.display = "flex";
    item.childNodes[remove_button].id += String(items_num);
    item.childNodes[remove_button].childNodes[remove_label].id +=
    item.id = item.id + String(items_num);
        items_num++;
        for (i = 0; i < item.children.length; i++ ) {
        if (item.children[i].tagName == 'INPUT') {
            item.children[i].setAttribute('required', 'required');
        }
        }
        document.getElementById("Items").appendChild(item);
}

function removeItem(item_id) {
    document.getElementById(item_id).parentElement.remove();
    items_num--;
}
