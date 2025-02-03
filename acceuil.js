// Animation du texte pour faire bouger le texte de bienvenue
const welcomeText = document.querySelector('.welcome-text');
let direction = 1;

function animateText() {
    let currentPosition = parseFloat(window.getComputedStyle(welcomeText).transform.split(',')[5]);
    if (currentPosition >= 0 || currentPosition <= -50) {
        direction *= -1;
    }
    welcomeText.style.transform = `translateY(${currentPosition + direction}px)`;
    requestAnimationFrame(animateText);
}

animateText();
