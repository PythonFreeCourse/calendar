//credit for the countdowntimer: https://gist.github.com/Mak-Pro/0e1194d0f8696489a5c8bac72c8fa300
fetch('/timer')
  .then(response => response.json())
  .then(data => {

var countDownDate = new Date(data.timer).getTime();

// Update the countdown every 1 second
var x = setInterval(function() {
  var now = new Date().getTime();
  var distance = countDownDate - now;
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);
  // Output the result to base.html in an element with id="eventtimer"
  document.getElementById("eventtimer").innerHTML = "Next Event will be in: " + days + "d " + hours + "h "
  + minutes + "m " + seconds + "s ";
  // Countdown had finished
  if (distance < 0) {
    clearInterval(x);
    document.getElementById("eventtimer").innerHTML = "Your Event Starts NOW:)";
  }
}, 1000);
 } );