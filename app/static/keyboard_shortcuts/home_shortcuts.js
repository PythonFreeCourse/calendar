import './mousetrap.js'
import './mousetrap_bind_dict.js'

let key_shortcuts = {
    'alt+c+i': function() { window.open('invitations/', '_self'); },
    'alt+c+p': function() { window.open('profile/', '_self'); }
};

Mousetrap.bind(key_shortcuts);