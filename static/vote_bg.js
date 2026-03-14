// 3D Honeycomb Tech Hive Background
const canvasBg = document.getElementById('bgCanvas');
const ctxBg = canvasBg.getContext('2d');

let width, height;
let hexGrid = [];

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvasBg.width = width;
    canvasBg.height = height;
    initHexGrid();
}

class Hexagon {
    constructor(q, r) {
        this.q = q; // Axial coords
        this.r = r;
        this.size = 30;
        // Calculate screen pos
        const x = this.size * (3 / 2 * q);
        const y = this.size * (Math.sqrt(3) / 2 * q + Math.sqrt(3) * r);
        this.baseX = x;
        this.baseY = y;
        this.z = Math.random() * 50; // Height/Depth
        this.phase = Math.random() * Math.PI * 2;
    }

    draw(time) {
        // Pulse Z (height) based on time
        const pulse = Math.sin(time * 0.002 + this.phase) * 20;
        const currentZ = this.z + pulse;

        // 3D Projection
        // Simple perspective: center is vanishing point
        const cx = width / 2;
        const cy = height / 2;

        // Flyover effect: move everything down continuously
        let flyY = (this.baseY + time * 0.5) % (height + 200);
        if (flyY < -100) flyY += height + 200;

        // Perspective logic
        const fov = 300;
        const scale = fov / (fov + currentZ); // Scale based on height

        const screenX = cx + (this.baseX - cx) * scale;
        const screenY = cy + (flyY - cy) * scale;

        const s = this.size * scale;

        // Draw Hexagon
        ctxBg.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = 2 * Math.PI / 6 * i;
            const x_i = screenX + s * Math.cos(angle);
            const y_i = screenY + s * Math.sin(angle);
            if (i === 0) ctxBg.moveTo(x_i, y_i);
            else ctxBg.lineTo(x_i, y_i);
        }
        ctxBg.closePath();

        // Style based on depth
        // Dark metallic with green glow edges
        const depthAlpha = Math.max(0.1, 1 - (flyY / height)); // Fade at bottom

        ctxBg.fillStyle = `rgba(15, 20, 35, ${depthAlpha * 0.8})`;
        ctxBg.strokeStyle = `rgba(0, 242, 96, ${depthAlpha * 0.5})`; // Green edges

        if (currentZ > 40) { // Active/High cells glow brighter
            ctxBg.strokeStyle = `rgba(0, 255, 255, ${depthAlpha})`; // Cyan highlight
            ctxBg.shadowBlur = 10;
            ctxBg.shadowColor = '#00f260';
        } else {
            ctxBg.shadowBlur = 0;
        }

        ctxBg.fill();
        ctxBg.stroke();
    }
}

function initHexGrid() {
    hexGrid = [];
    // Create grid covering screen + buffer
    // Roughly calculate columns and rows
    const cols = Math.ceil(width / 45) + 2;
    const rows = Math.ceil(height / 50) + 2;

    for (let q = -cols / 2; q < cols / 2; q++) {
        for (let r = -rows / 2; r < rows / 2; r++) {
            hexGrid.push(new Hexagon(q, r));
        }
    }
}

let time = 0;
function animateBg() {
    ctxBg.clearRect(0, 0, width, height);
    time++;

    // Deep Tech Background
    const grad = ctxBg.createRadialGradient(width / 2, height / 2, 0, width / 2, height / 2, width);
    grad.addColorStop(0, '#0f0c29');
    grad.addColorStop(1, '#000000');
    ctxBg.fillStyle = grad;
    ctxBg.fillRect(0, 0, width, height);

    hexGrid.forEach(h => h.draw(time));

    requestAnimationFrame(animateBg);
}

window.addEventListener('resize', resize);
resize();
animateBg();