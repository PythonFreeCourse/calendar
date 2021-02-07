// Event listeners
const set_checked_ids = [
  "Music On",
  "Music Off",
  "Sound Effects On",
  "Sound Effects Off",
];
const other_ids_and_their_funcs = [
  ["activate", set_default],
  ["on", start_audio],
  ["off", stop_audio],
];
set_checked_ids.forEach((val) => {
  add_set_checked_listener(val);
});
other_ids_and_their_funcs.forEach((val) => {
  add_other_listeners(val[0], val[1]);
});

/**
 * @summary This function gets an element_id and adds eventListener to it.
 * upon activation the set_checked function runs,
 * with the element_id as argument.
 * @param {string} element_id - the id attribute of the html element. One of: Music On/off, Sound Effects On/Off.
 */
function add_set_checked_listener(element_id) {
  let elem = document.getElementById(element_id);
  if (elem) {
    elem.addEventListener("click", function () {
      set_checked(element_id);
    });
  }
}

/**
 * @summary This function gets an element_id and a function and
 * adds eventListener to the element with element_id.
 * upon activation the function supplied runs with no arguments.
 * @param {function} func - the function to run.
 * @param {string} element_id - the id attribute of the html element.
 * One of: Music On/off, Sound Effects On/Off.
 */
function add_other_listeners(element_id, func) {
  let elem = document.getElementById(element_id);
  if (elem) {
    elem.addEventListener("click", func);
  }
}

/**
 * @summary This function gets an element_id and set its checked attribute.
 * According to the element_id, we disable or enable track selection and volume change for that audio type.
 * @param {string} element_id - the id attribute of the html element. One of: Music On/off, Sound Effects On/Off.
 */
function set_checked(element_id) {
  document.getElementById(element_id).setAttribute("checked", "checked");
  if (element_id == "Music Off") {
    set_disabled_or_enabled("music", true, true);
  } else if (element_id == "Music On") {
    set_disabled_or_enabled("music", true, false);
  } else if (element_id == "Sound Effects Off") {
    set_disabled_or_enabled("sfx", false, true);
  } else if (element_id == "Sound Effects On") {
    set_disabled_or_enabled("sfx", false, false);
  }
}

/**
 * @summary This function sets audio options off by default.
 */
function set_default() {
  set_default_for_audio_type("Music On", "Music Off");
  set_default_for_audio_type("Sound Effects On", "Sound Effects Off");
}

/**
 * @summary This function gets class or id name, boolean value to tell if class or id, and bolean value to set,
 * And sets the disabled attribute of the corresponding element accordingly.
 * @param {string} name - name of the elements' class or id.
 * @param {Boolean} is_class - class if true, id otherwise.
 * @param {Boolean} to_set - we set the disabled attribute if true, false oterwise.
 */
function set_disabled_or_enabled(name, is_class, to_set) {
  if (is_class) {
    let elements = document.getElementsByClassName(name);
    for (let element of elements) {
      element.disabled = to_set;
    }
  } else {
    document.getElementById(name).disabled = to_set;
  }
  document.getElementById("rangeInput " + name).disabled = to_set;
}

/**
 * @summary This function is an helper function for the set_default function,
 * and we use it to privent code duplication by having one function to handle music as well as sound effects.
 * @param {string} audio_id_on - the id corresponding to the On option of the element, for Music as well as sfx.
 * @param {string} audio_id_off - the id corresponding to the Off option of the element, for Music as well as sfx.
 */
function set_default_for_audio_type(audio_id_on, audio_id_off) {
  let is_on = document.getElementById(audio_id_on).checked;
  let is_off = document.getElementById(audio_id_off).checked;
  if (!is_on && !is_off) {
    document.getElementById(audio_id_off).checked = true;
  }
}

/**
 * @summary This function loads user choices and starts audio.
 */
function start_audio() {
  var request = new XMLHttpRequest();
  request.open("GET", "/audio/start", true);

  request.onload = function () {
    var audio_settings = JSON.parse(this.response);
    music = document.getElementById("my_audio");
    sfx = document.getElementById("sfx");
    var audio_settings = JSON.parse(audio_settings);
    var music_on = audio_settings["music_on"];

    if (music.muted && (music_on || music_on == null)) {
      var choices = audio_settings["playlist"];
      music.src =
        "../static/tracks/" +
        choices[Math.floor(Math.random() * choices.length)];
      music.volume = audio_settings["music_vol"];
      music.muted = false;
    }

    if (music.paused) {
      music.play();
    }

    sfx_on = audio_settings["sfxs_on"];
    if (sfx.muted && (sfx_on || sfx_on == null)) {
      sfx_choice = audio_settings["sfx_choice"];
      sfx.src = "../static/tracks/" + sfx_choice;
      sfx.volume = audio_settings["sfxs_vol"];
      sfx.muted = false;
    }

    if (!sfx.muted) {
      document.body.addEventListener("click", play_sfx, true);
    }
  };
  request.send();
}

/**
 * @summary This function plays a sound effect.
 */
function play_sfx() {
  sfx = document.getElementById("sfx");
  sfx.play();
}

/**
 * @summary This function stops the audio.
 */
function stop_audio() {
  music = document.getElementById("my_audio");
  sfx = document.getElementById("sfx");

  if (!music.paused) {
    music.pause();
    music.currentTime = 0;
  }

  if (!sfx.muted) {
    sfx.muted = true;
    document.body.removeEventListener("click", play_sfx, false);
  }
}