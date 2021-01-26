import './mousetrap.js'

Mousetrap.bind('alt+n', function () {
    var nameModal = document.getElementById("updateNameModal");
    nameModal.style = 'padding-right: 16px; display: block;';
    console.log('hey')
});