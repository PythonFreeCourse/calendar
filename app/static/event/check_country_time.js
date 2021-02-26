function checkCountryTime() {
    const ERROR_TIME_DURATION = 3000;
    const TIME_NOT_FILLED = 'Please enter the meeting date and time';
    const COUNTRY_NOT_FILLED = 'Please choose country';
    const modal_container = document.querySelector('.countries-modal-container');
    const open_modal = document.querySelector('.open-countries-modal');
    const close_modal = document.querySelector('.close-countries-modal');
    const submit_country = document.querySelector('.check-time');
    const upper_result = document.querySelector('.upper-result');
    const start_result = document.querySelector('.start-result');
    const end_result = document.querySelector('.end-result');
    const error_msg = document.querySelector('.empty-fields-error');
    const user_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    function getStartDate() {
        const start_date = document.getElementById('start_date').value;
        return start_date;
    }

    function getStartTime() {
        const start_time = document.getElementById('start_time').value;
        return start_time;
    }

    function getEndDate() {
        const end_date = document.getElementById('end_date').value;
        return end_date;
    }

    function getEndTime() {
        const end_time = document.getElementById('end_time').value;
        return end_time;
    }

    function displayErrorMsg(content) {
        error_msg.classList.remove('empty-fields-error-disappear');
        error_msg.innerText = content;
        setTimeout(() => error_msg.classList.add('empty-fields-error-disappear'), ERROR_TIME_DURATION);
    }

    function convertTimes(data, chosen_country) {
        const start_datetime = new Date(getStartDate() + 'T' + getStartTime());
        let converted_start_time = start_datetime.toLocaleTimeString('en-US', {timeZone: data.timezone});
        upper_result.innerText = 'Meeting Time in ' + chosen_country + ' is:';
        start_result.innerText = converted_start_time;
        if (!(getEndDate() === "" || getEndTime() === "")) {
            const end_datetime = new Date(getEndDate() + 'T' + getEndTime());
            let converted_end_time = end_datetime.toLocaleTimeString('en-US', {timeZone: data.timezone});
            end_result.innerText = ' until ' + converted_end_time;
        }
    }

    open_modal.addEventListener('click', (event) => {
        event.preventDefault();
        modal_container.classList.add('modal-active');
        if (getStartDate() === '' || getStartTime() === '') {
            displayErrorMsg(TIME_NOT_FILLED);
        }
    });

    submit_country.addEventListener('click', (event) => {
        event.preventDefault();
        if (getStartDate() === '' || getStartTime() === '') {
            displayErrorMsg(TIME_NOT_FILLED);
            return;
        }
        const chosen_country = document.getElementById('countries-datalist').value;
        if (chosen_country === '') {
            displayErrorMsg(COUNTRY_NOT_FILLED);
            return;
        }
        fetch(`/event/timezone/country/${chosen_country}`)
        .then(response => response.json())
        .then(data => convertTimes(data, chosen_country))
    });

    close_modal.addEventListener('click', (event) => {
        event.preventDefault();
        modal_container.classList.remove('modal-active');
    });
}


document.addEventListener("DOMContentLoaded", checkCountryTime);
