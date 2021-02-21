var items_num = 1;

document.addEventListener('click', function (e)
{
	if (e.target && e.target.id.includes('btnRemoveItem'))
	{
		removeItem(e.target.id);
	}
	else if (e.target && e.target.id.includes("btnRemoveLabel"))
	{
		let parent = document.getElementById(e.target.id).parentElement.id
		removeItem(parent);
	}
	else if (e.target && e.target.id == "btnAddItem")
	{
		addItem();
	}
});


function addItem()
{
	const REMOVE_BUTTON = 7;
	const REMOVE_LABEL = 1;
	let item = document.getElementById("shared_list_item").cloneNode(true);
	item.className = "shared_list_item_on"
	item.childNodes[REMOVE_BUTTON].id += String(items_num);
	item.childNodes[REMOVE_BUTTON].childNodes[REMOVE_LABEL].id += String(items_num);
	items_num++;
	for (child of item.children)
	{
		if (child.tagName == 'INPUT')
		{
			child.setAttribute('required', 'required');
		}
	}
	document.getElementById("Items").appendChild(item);
}

function removeItem(item_id)
{
	document.getElementById(item_id).parentElement.remove();
	items_num--;
}
