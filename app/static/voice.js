function listVoices(synth, voiceSelect) {
  const voices = synth.getVoices();
  const selectedIndex = Math.max(0, voiceSelect.selectedIndex);
  voicesSetup(voices, voiceSelect, selectedIndex);
}


function voicesSetup(voices, voiceSelect, selectedIndex) {
  voiceSelect.innerText = '';
  for (const voice of voices) {
    const option = document.createElement('option');
    option.textContent = `${voice.name} (${voice.lang})`;
    if (voice.default) {
      option.textContent += ' -- DEFAULT';
      option.selected = true;
    }
    option.setAttribute('data-lang', voice.lang);
    option.setAttribute('data-name', voice.name);
    voiceSelect.appendChild(option);
  }
  voiceSelect.selectedIndex = selectedIndex;
}


function setOutput(ctrl) {
  const range = document.getElementById(ctrl);
  range.nextElementSibling.textContent = range.value;
}


function setListenersToControls(controls, actions) {
  for (const control of controls) {
    for (const action of actions) {
      setOutput(`${control}`);
      document.getElementById(`${control}`).addEventListener(action, (event) => {
        setOutput(`${control}`);
      });
    }
  }
}


function speechText(voiceSelect, voices, synth) {
  document.getElementById('speak').addEventListener("click", (event) => {
    event.preventDefault();
    const say = document.getElementById('say').value;
    const sayThis = new SpeechSynthesisUtterance(say);

    const vox = voiceSelect.selectedOptions[0].dataset.name;
    for (voice of voices) {
      if (voice.name === vox) {
        sayThis.voice = voice;
        break;
      }
    }

    sayThis.pitch = document.getElementById('pitch').value;
    sayThis.rate = document.getElementById('rate').value;
    synth.speak(sayThis);
  });
}


window.addEventListener("load", (event) => {

  const synth = window.speechSynthesis;
  let voices = [];
  const voiceSelect = document.getElementById('voice');

  listVoices(synth, voiceSelect);
  if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = listVoices;
  }

  const controls = ["volume", "pitch", "rate"];
  const actions = ["load", "input"];

  setListenersToControls(controls, actions);
  speechText(voiceSelect, voices, synth);
});

