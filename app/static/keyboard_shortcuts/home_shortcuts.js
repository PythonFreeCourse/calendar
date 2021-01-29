import './mousetrap.js'
import './mousetrap_bind_dict.js'

let key_shortcuts = {
    'alt+c+i': function() { window.open('invitations/', '_self'); },
    'alt+c+p': function() { window.open('profile/', '_self'); },
    'alt+c+s': function() { window.open('search/', '_self'); },
    'alt+c+a': function() { window.open('agenda/', '_self'); },
    'ctrl+.': function() { window.open('keyboard_shortcuts/', '_self'); }
};

Mousetrap.bind(key_shortcuts);