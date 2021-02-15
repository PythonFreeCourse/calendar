function filterByCategory(events) {
    // TODO(issue#67): Allow filter by category name
    const category = document.getElementById("category").value;

    let result = "";
    for (const [key, eventsList] of Object.entries(events)) {
        let filteredValues = eventsList.filter(el => el.category_id == category);
        if (!Number.isInteger(+category) || !category || 0 === category.length) {
            filteredValues = [...eventsList];
        }
        let innerResult = "";
        if (filteredValues.length > 0) {
            innerResult = '<div class="p-3">' + key + '</div>';
            for (event of filteredValues) {
                innerResult += '<div class="event_line" style="background-color:' + event.color + '">';
                let availability = event.availability ? 'Busy' : 'Free';
                innerResult += '<div class=' + availability.toLocaleLowerCase() + ' title=' + availability + '></div>';
                innerResult += '<div><b>' + event.start + ' - <a href="/event/view/' + event.id + '">' + encodeHTML(event.title) + '</a></b><br>';
                innerResult += '<span class="duration">duration:' + event.duration + '</span>';
                innerResult += '</div>';
                innerResult += '</div>';
            }
        }
        result += innerResult;
    }
    document.getElementById("events").innerHTML = result;
}

function encodeHTML(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
}