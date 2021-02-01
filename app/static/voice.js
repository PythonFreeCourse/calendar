window.addEventListener("load",(event) => {
 
  let synth = window.speechSynthesis;
  let voices = [];
  let voiceSelect = document.querySelector("#voice");

  
  function listVoices(){
    voices = synth.getVoices();
    let selectedIndex = voiceSelect.selectedIndex < 0 ? 0 : voiceSelect.selectedIndex;
    
    voiceSelect.innerHTML = '';
    for(let voice of voices) {
      var option = document.createElement('option');
      option.textContent = `${voice.name} (${voice.lang})`;
      if(voice.default) {
        option.textContent += ' -- DEFAULT';
        option.selected = true;
      }
      option.setAttribute('data-lang', voice.lang);
      option.setAttribute('data-name', voice.name);
      voiceSelect.appendChild(option);
    }
    voiceSelect.selectedIndex = selectedIndex;
  }

  listVoices();
  if(synth.onvoiceschanged !== undefined){
    synth.onvoiceschanged = listVoices;
  }
  
  let controls = ["volume","pitch","rate"];
  let actions = ["load","input"];
  function setOutput(ctrl){
    let range = document.querySelector(ctrl);
    range.nextElementSibling.textContent = range.value;
  }
  for(let control of controls){
    for(let action of actions){
      setOutput(`#${control}`);
      document.querySelector(`#${control}`).addEventListener(action, (event) => {
        setOutput(`#${control}`);
      });  
    }
  }
  
  
  document.querySelector("#speak").addEventListener("click", (event) => {
    event.preventDefault();
    let say = document.querySelector("#say").value;
    let sayThis = new SpeechSynthesisUtterance(say);
    
    let vox = voiceSelect.selectedOptions[0].getAttribute('data-name');
    for(voice of voices){
      if(voice.name === vox) {
        sayThis.voice = voice;
        break;
      }
    }
    
    sayThis.pitch = document.querySelector("#pitch").value;
    sayThis.rate = document.querySelector("#rate").value;
    synth.speak(sayThis);
  });
  
});

