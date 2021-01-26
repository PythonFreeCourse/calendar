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
 * This function sets audio options off by default.
 */
function set_default() {
    set_default_for_audio_type("Music On", "Music Off")
    set_default_for_audio_type("Sound Effects On", "Sound Effects Off")
}


/** 
 * This function gets class or id name, boolean value to tell if class or id, and bolean value to set,
 * And sets the disabled attribute of the corresponding element accordingly. 
 * @param {string} name - name of the elements' class or id.
 * @param {Boolean} is_class - class if true, id otherwise.
 * @param {Boolean} to_set - we set the disabled attribute if true, false oterwise.
 */
function set_disabled_or_enabled(name, is_class, to_set) {
    if (is_class) {
        var elements = document.getElementsByClassName(name);
        for (let element of elements) {
            element.disabled = to_set;
        }
    } else {
        document.getElementById(name).disabled = to_set;
    }
    document.getElementById("rangeInput " + name).disabled = to_set;
}


/** 
 * This function is an helper function for the set_default function, 
 * and we use it to privent code duplication by having one function to handle music as well as sound effects.
 * @param {string} audio_id_on - the id corresponding to the On option of the element, for Music as well as sfx.
 * @param {string} audio_id_off - the id corresponding to the Off option of the element, for Music as well as sfx.
 */
function set_default_for_audio_type(audio_id_on, audio_id_off) {
    var is_on = document.getElementById(audio_id_on).checked;
    var is_off = document.getElementById(audio_id_off).checked;
    if (!is_on && !is_off) {
        document.getElementById(audio_id_off).checked = true;
    }
}