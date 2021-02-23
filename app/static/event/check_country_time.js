const modal_container = document.querySelector('.countries_modal_container');
const open_modal = document.querySelector('.open_countries_modal');
const close_modal = document.querySelector('.close_countries_modal');
const submit_country = document.querySelector('.check_time');
const upper_result = document.querySelector('.upper_result')
const start_result = document.querySelector('.start_result')
const end_result = document.querySelector('.end_result')
const error_msg = document.querySelector('.empty_fields_error')

const start_date = document.querySelector('#start_date');
const start_time = document.querySelector('#start_time');
const end_date = document.querySelector('#end_date');
const end_time = document.querySelector('#end_time');
const user_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;



open_modal.addEventListener('click', (event) => {
    event.preventDefault();
    modal_container.classList.add('modal-active');
    let start_date_input = start_date.value
    let start_time_input = start_time.value
    let end_date_input = end_date.value
    let end_time_input = end_time.value
    if(start_date_input === '' || start_time_input === ''){
        error_msg.innerHTML = 'Please enter meeting time'
        setTimeout(() => error_msg.remove(), 10000);
    }
});

submit_country.addEventListener('click', (event) => {
    event.preventDefault();
    let start_date_input = start_date.value
    let start_time_input = start_time.value
    let end_date_input = end_date.value
    let end_time_input = end_time.value
    if(!(start_date_input === '' || start_time_input === '')){
        const start_datetime = new Date(start_date_input + 'T' + start_time_input)
        const end_datetime = new Date(end_date_input + 'T' + end_time_input)
        const chosen_country = document.querySelector('#countries_datalist').value;
        if(chosen_country === ''){
            error_msg.innerHTML = 'Please choose country'
            setTimeout(() => error_msg.remove(), 3000);
        } else {
            fetch(`/event/check_country_timezone/${chosen_country}`)
            .then(response => response.json())
            .then(data => {
                let converted_start_time = start_datetime.toLocaleTimeString('en-US', {timeZone: data.timezone})
                upper_result.innerHTML = 'Meeting Time in ' + chosen_country + ' is:'
                start_result.innerHTML = converted_start_time
                if (!(end_date_input === "" || end_time_input === "")) {
                    let converted_end_time = end_datetime.toLocaleTimeString('en-US', {timeZone: data.timezone})
                    end_result.innerHTML = ' until ' + converted_end_time
                }
            })
        }
    }
});

close_modal.addEventListener('click', (event) => {
    event.preventDefault();
    modal_container.classList.remove('modal-active');
});
