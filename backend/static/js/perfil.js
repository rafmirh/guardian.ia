// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    // Add event listeners if elements exist
    if (menuBtn && sidebar && overlay) {
        menuBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);
    }

    // Toggle menu function
    function toggleMenu() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }

    // Initialize gauge chart
    initializeGauge();
});

function initializeGauge() {
    const canvas = document.getElementById('riskGauge');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const riskPercentageElement = document.getElementById('riskPercentage');
    const riskValue = parseFloat(riskPercentageElement.textContent) || 0;

    // Create gauge chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [riskValue, 100 - riskValue],
                backgroundColor: [
                    getColorByRisk(riskValue),
                    'rgba(255, 255, 255, 0.1)'
                ],
                borderWidth: 0,
                cutout: '70%',
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            animation: {
                animateRotate: true,
                duration: 2000
            }
        }
    });
}

function getColorByRisk(risk) {
    if (risk < 25) return '#4CAF50';      // Verde - Riesgo Bajo
    if (risk < 50) return '#FF9800';      // Naranja - Riesgo Moderado  
    if (risk < 75) return '#FF5722';      // Rojo Naranja - Riesgo Alto
    return '#F44336';                     // Rojo - Riesgo Muy Alto
}