// Celebration Confetti & Success Reveal
window.addEventListener('load', () => {
    const canvas = document.getElementById('successCanvas');
    const messageBox = document.getElementById('success-message');

    // 1. Reveal the message immediately
    if (messageBox) {
        setTimeout(() => {
            messageBox.classList.add('visible');
        }, 100);
    }

    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let particles = [];

    class Confetti {
        constructor() {
            this.x = canvas.width / 2;
            this.y = canvas.height / 2;
            const angle = Math.random() * Math.PI * 2;
            const velocity = Math.random() * 15 + 5;
            this.vx = Math.cos(angle) * velocity;
            this.vy = Math.sin(angle) * velocity;
            this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
            this.size = Math.random() * 5 + 2;
            this.alpha = 1;
            this.decay = Math.random() * 0.02 + 0.005;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.vy += 0.2; // Gravity
            this.vx *= 0.96; // Friction
            this.vy *= 0.96;
            this.alpha -= this.decay;
        }

        draw() {
            ctx.globalAlpha = this.alpha;
            ctx.fillStyle = this.color;
            ctx.fillRect(this.x, this.y, this.size, this.size);
            ctx.globalAlpha = 1;
        }
    }

    function init() {
        for (let i = 0; i < 200; i++) {
            particles.push(new Confetti());
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            p.update();
            p.draw();
            if (p.alpha <= 0) particles.splice(i, 1);
        }

        if (particles.length > 0) {
            requestAnimationFrame(animate);
        }
    }

    init();
    animate();
});
