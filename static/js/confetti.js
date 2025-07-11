// © 2024–2025 Harnisch LLC. All Rights Reserved.
// Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
// Unauthorized use, distribution, or modification is prohibited.

function triggerConfetti() {
    // Create confetti container
    const confettiContainer = document.createElement('div');
    confettiContainer.className = 'confetti-container';
    document.body.appendChild(confettiContainer);
    
    // Create multiple confetti pieces
    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            createConfettiPiece(confettiContainer);
        }, i * 50); // Stagger the confetti creation
    }
    
    // Clean up after animation
    setTimeout(() => {
        if (document.body.contains(confettiContainer)) {
            document.body.removeChild(confettiContainer);
        }
    }, 4000);
}

function createConfettiPiece(container) {
    const confetti = document.createElement('div');
    confetti.className = `confetti confetti-${Math.floor(Math.random() * 6) + 1}`;
    
    // Random horizontal position
    confetti.style.left = Math.random() * 100 + '%';
    
    // Random size variation
    const size = Math.random() * 6 + 4; // 4-10px
    confetti.style.width = size + 'px';
    confetti.style.height = size + 'px';
    
    // Random animation duration
    confetti.style.animationDuration = (Math.random() * 2 + 2) + 's'; // 2-4 seconds
    
    container.appendChild(confetti);
    
    // Remove individual confetti piece after animation
    setTimeout(() => {
        if (confetti.parentNode) {
            confetti.parentNode.removeChild(confetti);
        }
    }, 4000);
}
