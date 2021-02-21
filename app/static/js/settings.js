const tabBtn =
	document.querySelectorAll(".tab");
const tab =
	document.querySelectorAll(".tabShow");

function clearMenu(options)
{
	for (var i = 0, l = options.length; i < l; i++)
	{
		cat = document.getElementById("options").children[i].children[0]
		if (!(cat.classList.contains("active")))
		{
      options[i].classList.remove("tabShow")
			options[i].classList.add("tabHide")
		}
	}
};

function tabClick(tab_id)
{
	tab.forEach(function (node)
	{
    node.classList.remove("tabShow")
    node.classList.add("tabHide")
	});
	tab_elem = document.getElementById(tab_id);
	tab_num = parseInt(tab_id.slice(-1));
  tab[tab_num].classList.remove("tabHide")
	tab[tab_num].classList.add("tabShow")
	tab_elem.classList.add("active");

	let els = document.getElementById("options").children;
	for (var i = 0, l = els.length; i < l; i++)
	{
		if (els[i].childNodes[0].id != tab_id)
		{
			els[i].childNodes[0].classList.remove("active")
		}
	}
};

clearMenu(document.getElementById("settings-main").children)
