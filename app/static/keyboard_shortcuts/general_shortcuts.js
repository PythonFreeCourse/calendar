import './mousetrap.js'
import './mousetrap_bind_dict.js'

let key_shortcuts = {
    'alt+c+h': function() { window.open('/', '_self'); },
    'alt+c+p': function() { window.open('/profile/', '_self'); },
    'alt+c+s': function() { window.open('/search/', '_self'); },
    'alt+c+a': function() { window.open('/agenda/', '_self'); },
    'alt+c+u': function() { window.open('/audio/settings/', '_self'); }

};

Mousetrap.bind(key_shortcuts);
