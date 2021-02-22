const open_countries_modal = document.getElementById('open_countries_modal');
// const countries_modal_container = document.getElementById(countrie_modal_container);
// const countries_modal = document.getElementById(countries_modal);
// const close_countries_modal = document.getElementById(close_countries_modal);


open_countries_modal.addEventListener('click', (event) => {
    event.preventDefault();
    countries_modal.classList.add('show');
});

// countries_modal_container.classList.add('show');



// close_countries_modal.addEventListener('click', (event) => {
//     event.preventDefault();
//     countries_modal.classList.remove('show');
//     // countries_modal_container.classList.remove('show');
// });
