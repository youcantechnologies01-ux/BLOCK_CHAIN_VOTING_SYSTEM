// FINAL INTRO: Tech Runner Logo + Circuitry + Particle Text
window.addEventListener('load', () => {

    // CHECK IF INTRO ALREADY PLAYED
    // if (sessionStorage.getItem('introShown')) {
    //     const intro = document.getElementById('intro-overlay');
    //     if (intro) intro.style.display = 'none';
    //     return;
    // }

    const canvas = document.getElementById('introCanvas');
    if (!canvas) {
        // Fallback if canvas missing
        const intro = document.getElementById('intro-overlay');
        const content = document.getElementById('main-content');
        if (intro) intro.style.display = 'none';
        if (content) content.classList.add('content-enter');
        return;
    }

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Load Logo Image
    const logoImg = new Image();
    logoImg.src = '/static/logo.svg';

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        init();
    });

    const TEXT = "YOU CAN TECHNOLOGIES";
    let particles = [];
    let circuits = [];
    let state = 'WARP'; // WARP, REVEAL, HOLD, INTERACTIVE
    let timer = 0;

    // Config
    const LOGO_SIZE = 250;

    // --- CIRCUIT CLASS ---
    class Circuit {
        constructor() { this.reset(); }
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.history = [];
            this.dir = Math.floor(Math.random() * 4);
            this.len = 0;
            this.maxLen = Math.random() * 50 + 20;
            this.life = 100;
            this.speed = 2 + Math.random();
        }
        update() {
            this.life--;
            if (this.len > this.maxLen || this.life <= 0 || Math.random() < 0.01) {
                this.reset();
            } else {
                this.len++;
                this.history.push({ x: this.x, y: this.y });
                if (this.history.length > 10) this.history.shift();

                if (this.dir === 0) this.x += this.speed;
                else if (this.dir === 1) this.y += this.speed;
                else if (this.dir === 2) this.x -= this.speed;
                else if (this.dir === 3) this.y -= this.speed;

                if (Math.random() < 0.05) this.dir = Math.floor(Math.random() * 4);
            }
        }
        draw() {
            if (state === 'INTERACTIVE') return;
            ctx.strokeStyle = `rgba(0, 242, 96, ${this.life / 200})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            if (this.history.length) {
                ctx.moveTo(this.history[0].x, this.history[0].y);
                for (let p of this.history) ctx.lineTo(p.x, p.y);
            }
            ctx.lineTo(this.x, this.y);
            ctx.stroke();
        }
    }

    // --- PARTICLE CLASS (For Text) ---
    class WarpStar {
        constructor(destX, destY, color) {
            this.x = (Math.random() - 0.5) * canvas.width * 4;
            this.y = (Math.random() - 0.5) * canvas.height * 4;
            this.z = Math.random() * 2000;
            this.destX = destX;
            this.destY = destY;
            this.screenX = 0;
            this.screenY = 0;
            this.color = color || '#00f260';
            this.arrived = false;
        }

        update() {
            if (state === 'WARP') {
                this.z -= 40;
                if (this.z < 1) {
                    this.z = 2000;
                    this.x = (Math.random() - 0.5) * canvas.width * 4;
                    this.y = (Math.random() - 0.5) * canvas.height * 4;
                }
            } else if (state === 'REVEAL' || state === 'HOLD') {
                const fov = 300;
                const scale = fov / (fov + this.z);
                const currentScreenX = (this.x * scale) + canvas.width / 2;
                const currentScreenY = (this.y * scale) + canvas.height / 2;

                const dx = this.destX - currentScreenX;
                const dy = this.destY - currentScreenY;

                this.screenX = currentScreenX + dx * 0.1;
                this.screenY = currentScreenY + dy * 0.1;

                this.z *= 0.9;
                this.x += (this.destX - canvas.width / 2 - this.x) * 0.1;
                this.y += (this.destY - canvas.height / 2 - this.y) * 0.1;

                if (Math.abs(dx) < 1 && Math.abs(dy) < 1) this.arrived = true;
            }
        }

        draw() {
            if (state === 'WARP') {
                const fov = 300;
                const scale = fov / (fov + this.z);
                const x2d = (this.x * scale) + canvas.width / 2;
                const y2d = (this.y * scale) + canvas.height / 2;
                const s = Math.max(0, (2000 - this.z) / 500);
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(x2d, y2d, s, 0, Math.PI * 2);
                ctx.fill();
            } else {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.screenX, this.screenY, 2, 2);
            }
        }
    }

    function init() {
        particles = [];
        circuits = [];
        for (let i = 0; i < 15; i++) circuits.push(new Circuit());

        // Scan Text Particles
        const fontSize = Math.min(canvas.width / 15, 50);
        ctx.font = `900 ${fontSize}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Position text BELOW the logo
        const textY = canvas.height / 2 + 120;

        ctx.fillStyle = 'white';
        ctx.fillText(TEXT, canvas.width / 2, textY);
        const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let y = 0; y < canvas.height; y += 4) {
            for (let x = 0; x < canvas.width; x += 4) {
                if (data[((x + y * canvas.width) * 4) + 3] > 128) {
                    particles.push(new WarpStar(x, y, '#00f260'));
                }
            }
        }

        // Add some random stars
        for (let i = 0; i < 150; i++) {
            particles.push(new WarpStar(Math.random() * canvas.width, Math.random() * canvas.height, '#ffffff'));
        }

        state = 'WARP';
        timer = 0;
    }

    function animate() {
        if (state === 'INTERACTIVE') {
            ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear
            return; // Stop intro loop, let CSS overlay removal take over visualization
        }

        // Background Fade
        ctx.fillStyle = 'rgba(15, 12, 41, 0.3)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw Circuits
        circuits.forEach(c => { c.update(); c.draw(); });

        // Update Particles
        particles.forEach(p => { p.update(); p.draw(); });

        // State Machine
        if (state === 'WARP') {
            timer++;
            if (timer > 80) {
                state = 'REVEAL';
                timer = 0;
                // Flash white?
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
        } else if (state === 'REVEAL' || state === 'HOLD') {
            // Draw LOGO Image Centered
            try {
                // Pulse effect
                const scale = 1 + Math.sin(Date.now() / 300) * 0.02;
                const w = LOGO_SIZE * scale;
                const h = LOGO_SIZE * scale;
                const lx = (canvas.width - w) / 2;
                const ly = (canvas.height - h) / 2 - 50; // Move up slightly

                // Glow behind logo
                ctx.save();
                ctx.shadowBlur = 40;
                ctx.shadowColor = '#00f260';
                ctx.globalAlpha = Math.min(timer / 30, 1); // Fade in
                ctx.drawImage(logoImg, lx, ly, w, h);
                ctx.restore();
            } catch (e) { }

            timer++;
            if (state === 'REVEAL' && timer > 60) state = 'HOLD';
            if (state === 'HOLD' && timer > 150) finishIntro();
        }

        requestAnimationFrame(animate);
    }

    function finishIntro() {
        if (state === 'INTERACTIVE') return;
        state = 'INTERACTIVE'; /* Mark handled */
        sessionStorage.setItem('introShown', 'true');

        const intro = document.getElementById('intro-overlay');
        if (intro) {
            intro.style.transition = 'opacity 1.5s ease-out';
            intro.style.opacity = '0';
            setTimeout(() => { intro.style.display = 'none'; }, 1500);
        }
    }

    init();
    animate();
});
