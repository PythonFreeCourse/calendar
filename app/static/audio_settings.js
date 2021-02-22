// Event listeners
const set_checked_ids = [
  "music-on",
  "music-off",
  "sound-effects-on",
  "sound-effects-off",
];
const other_ids_and_their_funcs = [
  ["activate", set_default],
  ["on", start_audio],
  ["off", stop_audio],
];

window.addEventListener("load", function () {
  set_checked_ids.forEach((val) => {
    add_set_checked_listener(val);
  });
  other_ids_and_their_funcs.forEach((val) => {
    perform_func_on_click(val[0], val[1]);
  });
});

/**
 * @summary This function gets an element_id and adds eventListener to it.
 * upon activation the set_checked function runs,
 * with the element_id as argument.
 * @param {string} element_id - the id attribute of the html element. One of: Music On/off, Sound Effects On/Off.
 */
function add_set_checked_listener(element_id) {
  const elem = document.getElementById(element_id);
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
function perform_func_on_click(element_id, func) {
  const elem = document.getElementById(element_id);
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
  const is_music = element_id.includes("music");
  const is_off = element_id.includes("off");
  const to_toggle = is_music ? "music" : "sfx";
  set_disabled_or_enabled(to_toggle, is_music, is_off);
}

/**
 * @summary This function sets audio options off by default.
 */
function set_default() {
  set_default_for_audio_type("music-on", "music-off");
  set_default_for_audio_type("sound-effects-on", "sound-effects-off");
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
  document.getElementById("rangeInput-" + name).disabled = to_set;
}

/**
 * @summary This function is an helper function for the set_default function,
 * and we use it to privent code duplication by having one function to handle music as well as sound effects.
 * @param {string} audio_id_on - the id corresponding to the On option of the element, for Music as well as sfx.
 * @param {string} audio_id_off - the id corresponding to the Off option of the element, for Music as well as sfx.
 */
function set_default_for_audio_type(audio_id_on, audio_id_off) {
  const is_on = document.getElementById(audio_id_on).checked;
  const is_off = document.getElementById(audio_id_off).checked;
  if (!is_on && !is_off) {
    document.getElementById(audio_id_off).checked = true;
  }
}

function prepare_audio() {
  let audio_settings = JSON.parse(this.response);
  const music = document.getElementById("my-audio");
  const sfx = document.getElementById("sfx");
  audio_settings = JSON.parse(audio_settings);
  const music_on = audio_settings["music_on"];

  if (music.muted && (music_on || music_on == null)) {
    const choices = audio_settings["playlist"];
    music.src = `/static/tracks/${
      choices[Math.floor(Math.random() * choices.length)]
    }`;
    music.volume = audio_settings["music_vol"];
    music.muted = false;
  }

  if (music.paused) {
    music.play();
  }

  const sfx_on = audio_settings["sfx_on"];
  if (sfx.muted && (sfx_on || sfx_on == null)) {
    const sfx_choice = audio_settings["sfx_choice"];
    sfx.src = "/static/tracks/" + sfx_choice;
    sfx.volume = audio_settings["sfx_vol"];
    sfx.muted = false;
  }

  if (!sfx.muted) {
    document.body.addEventListener("click", play_sfx, true);
  }
}

/**
 * @summary This function loads user choices and starts audio.
 */
function start_audio() {
  const request = new XMLHttpRequest();
  request.open("GET", "/audio/start", true);

  request.onload = prepare_audio;
  request.send();
}

/**
 * @summary This function plays a sound effect.
 */
function play_sfx() {
  const sfx = document.getElementById("sfx");
  sfx.play();
}

/**
 * @summary This function stops the audio.
 */
function stop_audio() {
  const music = document.getElementById("my-audio");
  const sfx = document.getElementById("sfx");

  if (!music.paused) {
    music.pause();
    music.currentTime = 0;
  }

  if (!sfx.muted) {
    sfx.muted = true;
    document.body.removeEventListener("click", play_sfx, false);
  }
}
