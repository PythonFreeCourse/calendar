function change_max_to_today_date(el) {
  today = new Date();
  today_str = today.toISOString().substring(0, 10);
  el.max = today_str;
}
function validate_date_older_than_today(received_date) {
  return received_date < new Date();
}

document.addEventListener('DOMContentLoaded', () => {
let last_period_date_element = document.getElementById("last-period-date");
change_max_to_today_date(last_period_date_element);
});
