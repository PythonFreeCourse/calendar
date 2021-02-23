const modal_container = document.querySelector('.countries-modal-container');
const open_modal = document.querySelector('.open-countries-modal');
const close_modal = document.querySelector('.close-countries-modal');
const submit_country = document.querySelector('.check-time');
const upper_result = document.querySelector('.upper-result');
const start_result = document.querySelector('.start-result');
const end_result = document.querySelector('.end-result');
const error_msg = document.querySelector('.empty-fields-error');
const error_timeout_duration = 3000;
const time_not_filled = 'Please enter meeting time';
const country_not_filled = 'Please choose country';

const start_date = document.querySelector('#start_date');
const start_time = document.querySelector('#start_time');
const end_date = document.querySelector('#end_date');
const end_time = document.querySelector('#end_time');
const user_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

function showErrorMsg(content) {
    error_msg.classList.remove('empty-fields-error-disappear');
    error_msg.innerText = content;
    setTimeout(() => error_msg.classList.add('empty-fields-error-disappear'), error_timeout_duration);
}

open_modal.addEventListener('click', (event) => {
    event.preventDefault();
    modal_container.classList.add('modal-active');
    let start_date_input = start_date.value;
    let start_time_input = start_time.value;
    let end_date_input = end_date.value;
    let end_time_input = end_time.value;
    if (start_date_input === '' || start_time_input === '') {
        showErrorMsg(time_not_filled)
    }
});

submit_country.addEventListener('click', (event) => {
    event.preventDefault();
    let start_date_input = start_date.value;
    let start_time_input = start_time.value;
    let end_date_input = end_date.value;
    let end_time_input = end_time.value;
    if (start_date_input === '' || start_time_input === '') {
        showErrorMsg(time_not_filled)
        return;
    }
    const start_datetime = new Date(start_date_input + 'T' + start_time_input);
    const end_datetime = new Date(end_date_input + 'T' + end_time_input);
    const chosen_country = document.querySelector('#countries-datalist').value;
    if (chosen_country === '') {
        showErrorMsg(country_not_filled)
        return;
    }
    fetch(`/event/check_country_timezone/${chosen_country}`)
    .then(response => response.json())
    .then(data => {
        let converted_start_time = start_datetime.toLocaleTimeString('en-US', {timeZone: data.timezone});
        upper_result.innerText = 'Meeting Time in ' + chosen_country + ' is:';
        start_result.innerText = converted_start_time;
        if (!(end_date_input === "" || end_time_input === "")) {
            let converted_end_time = end_datetime.toLocaleTimeString('en-US', {timeZone: data.timezone});
            end_result.innerText = ' until ' + converted_end_time;
        }
    })
});

close_modal.addEventListener('click', (event) => {
    event.preventDefault();
    modal_container.classList.remove('modal-active');
});
