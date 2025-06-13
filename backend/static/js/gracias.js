document.addEventListener('DOMContentLoaded', () => {

    // --- Part 1: Matrix Digital Rain ---
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
    const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const nums = '0123456789';
    const alphabet = katakana + latin + nums;

    const fontSize = 16;
    const columns = canvas.width / fontSize;
    const rainDrops = [];

    for (let x = 0; x < columns; x++) {
        rainDrops[x] = 1;
    }

    const drawMatrix = () => {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#39ff14'; // Neon lime green
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < rainDrops.length; i++) {
            const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
            ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);

            if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                rainDrops[i] = 0;
            }
            rainDrops[i]++;
        }
    };

    setInterval(drawMatrix, 33);
    
    // Resize canvas when window is resized
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        // Recalculate columns for the new width
        const newColumns = canvas.width / fontSize;
        // Simple reset, could be more sophisticated
        for (let x = 0; x < newColumns; x++) {
            rainDrops[x] = Math.floor(Math.random() * (canvas.height/fontSize));
        }
    });


    // --- Part 2: Chip Pulse Animation ---
    const chip = document.getElementById('ai-chip');
    const container = document.querySelector('.content-container');

    // Add click event listener to the chip
    if (chip) {
        chip.addEventListener('click', () => {
            window.location.href = '/';
        });
    }

    // Define pin locations on the chip as percentages of its width/height
    // This makes it responsive to the chip's size
    const pins = [
        // Top pins
        { top: '0%', left: '35%', dir: 'up' }, { top: '0%', left: '50%', dir: 'up' }, { top: '0%', left: '65%', dir: 'up' },
        // Bottom pins
        { top: '100%', left: '35%', dir: 'down' }, { top: '100%', left: '50%', dir: 'down' }, { top: '100%', left: '65%', dir: 'down' },
        // Left pins
        { top: '35%', left: '0%', dir: 'left' }, { top: '50%', left: '0%', dir: 'left' }, { top: '65%', left: '0%', dir: 'left' },
        // Right pins
        { top: '35%', left: '100%', dir: 'right' }, { top: '50%', left: '100%', dir: 'right' }, { top: '65%', left: '100%', dir: 'right' },
    ];

    function createPulse() {
        if (!chip) return;

        // Pick a random pin to start the pulse from
        const randomPin = pins[Math.floor(Math.random() * pins.length)];

        const pulse = document.createElement('div');
        pulse.className = 'pulse';

        // Set initial position at the pin
        pulse.style.top = randomPin.top;
        pulse.style.left = randomPin.left;
        
        chip.appendChild(pulse); // Append to chip for relative positioning

        // Define travel distance and direction
        let travelX = 0;
        let travelY = 0;
        const distance = Math.max(window.innerWidth, window.innerHeight) / 2;

        switch (randomPin.dir) {
            case 'up':    travelY = -distance; break;
            case 'down':  travelY = distance;  break;
            case 'left':  travelX = -distance; break;
            case 'right': travelX = distance;  break;
        }

        // Animate using the Web Animations API
        const animation = pulse.animate([
            { transform: 'translate(-50%, -50%) scale(1)', opacity: 1 },
            { transform: `translate(calc(-50% + ${travelX}px), calc(-50% + ${travelY}px)) scale(3)`, opacity: 0 }
        ], {
            duration: 2000 + Math.random() * 1000, // 2-3 seconds
            easing: 'ease-out'
        });

        // Remove the pulse element after the animation completes
        animation.onfinish = () => {
            pulse.remove();
        };
    }

    // Create a new pulse at a random interval
    setInterval(createPulse, 200); // Create a pulse every 200ms
});