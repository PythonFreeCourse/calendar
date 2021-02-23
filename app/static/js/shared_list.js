window.addEventListener('load', () =>
{
	document.getElementById("btn-add-item").addEventListener('click', addItem)
});


function addItem()
{
	const SHARED_LIST_ITEMS_NUM = document.querySelectorAll("#Items > div").length
	const shared_list_items = document.getElementById("Items")
	let shared_list_item = document.getElementById("shared-list-item").cloneNode(true);

	shared_list_item.className = "shared-list-item-on"
	shared_list_item.id = shared_list_item.id + SHARED_LIST_ITEMS_NUM
	for (child of shared_list_item.children)
	{
		if (child.tagName == 'INPUT')
		{
			child.setAttribute('required', 'required');
		}
	}
	shared_list_items.appendChild(shared_list_item);
	document.querySelector("#" + shared_list_item.id + " > .remove-btn").addEventListener('click', () =>
	{
		shared_list_item.remove()
		for (i = 3; i < shared_list_items.childNodes.length; i++)
		{
			shared_list_items.childNodes[i].id = "shared-list-item" + String(i - 2);
		}
	})
}
