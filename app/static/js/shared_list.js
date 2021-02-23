window.addEventListener('load', () => {
    document.getElementById("btn-add-item").addEventListener('click', addItem)
});


function addItem() {
    const LIST_ITEMS_NUM = document.querySelectorAll("#Items > div").length
    const list_items = document.getElementById("Items")
    let shared_list_item = document.getElementById("shared-list-item").cloneNode(true);

    shared_list_item.className = "shared-list-item-on"
    shared_list_item.id = shared_list_item.id + LIST_ITEMS_NUM
    for (child of shared_list_item.children) {
        if (child.tagName == 'INPUT') {
            child.setAttribute('required', 'required');
        }
    }
    list_items.appendChild(shared_list_item);
    document.querySelector("#" + shared_list_item.id + " > .remove-btn").addEventListener('click', () => {
        removeItem(shared_list_item, list_items)
    })
}


function removeItem(shared_list_item, list_items) {
    shared_list_item.remove()
	for (const [index, child] of list_items.childNodes.entries())
	{
		child.id = "shared-list-item" + String(index)
	}
}
