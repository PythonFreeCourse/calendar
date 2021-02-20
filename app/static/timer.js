//credit for the countdowntimer: https://gist.github.com/Mak-Pro/0e1194d0f8696489a5c8bac72c8fa300
function countdownTimer() {
  fetch('/timer')
    .then(response => response.json())
    .then(data => {

    let countDownDate = new Date(data.timer).getTime();

    // Update the countdown every 1 second
    const timerInterval = setInterval(function() {
      const now = new Date().getTime();
      const distance = countDownDate - now;
      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      let seconds = Math.floor((distance % (1000 * 60)) / 1000);
      // Output the result to base.html in an element with id="eventtimer"
      document.getElementById("eventtimer").innerText = "Upcoming event in: " + days + "d " + hours + "h "
      + minutes + "m " + seconds + "s ";
      // Countdown had finished
      if (distance < 0) {
        clearInterval(timerInterval);
        document.getElementById("eventtimer").innerText = "Your Event Starts NOW:)";
      }
    }, 1000);
  } );
}

document.addEventListener("DOMContentLoaded", countdownTimer);
