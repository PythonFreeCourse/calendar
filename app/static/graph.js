function busiestDayOfTheWeekGraph(events) {
    events = JSON.parse(events);
    
    const data = Object.values(events);
    const labels = Object.keys(events);
    const ctx = document.getElementById("myChart");
    ctx.style.backgroundColor = "rgba(255, 255, 255, 1)";
    const myChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "# Events",
                data: data,
                backgroundColor: [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(255, 206, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(153, 102, 255, 0.2)",
                    "rgba(255, 159, 64, 0.2)",
                    "rgba(200, 130, 40, 0.2)",
                    "rgba(255, 99, 132, 0.2)"
                ],
                borderColor: [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 206, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)",
                    "rgba(200, 130, 64, 1)",
                    "rgba(255, 99, 132, 1)"
                ],
                borderWidth: 1
            }]
        }
    });
}

function addEventsAfterPageLoaded() {
    const element = document.getElementsByClassName("graph")[0];
    element.addEventListener("click", function() {
        let eventsPerDateData = element.name;
        busiestDayOfTheWeekGraph(eventsPerDateData);
    }, false);
}

document.addEventListener("DOMContentLoaded", addEventsAfterPageLoaded);