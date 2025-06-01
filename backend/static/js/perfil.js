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

    // Privacy Modal Logic
    const privacyModal = document.getElementById('privacy-modal');
    const acceptBtn = document.getElementById('accept-btn');
    const scrollBox = document.getElementById('modal-scrollbox');

    if (privacyModal && acceptBtn && scrollBox) {
        // Check if the modal has already been accepted in this session
        if (sessionStorage.getItem('privacyModalAccepted') === 'true') {
            privacyModal.style.display = 'none';
        } else {
            // Show the modal if it hasn't been accepted
            privacyModal.style.display = 'block';

            // Enable accept button on scroll to bottom
            scrollBox.addEventListener('scroll', function () {
                // Check if scrolled to near the bottom (within 5px)
                if (scrollBox.scrollTop + scrollBox.clientHeight >= scrollBox.scrollHeight - 5) {
                    acceptBtn.disabled = false;
                    acceptBtn.classList.add('enabled'); // Assuming 'enabled' class provides styling
                }
            });

            // Handle modal close and set session storage
            acceptBtn.addEventListener('click', function() {
                privacyModal.style.display = 'none';
                sessionStorage.setItem('privacyModalAccepted', 'true');
            });
        }
    } else {
        console.warn('Privacy modal elements not found. Ensure IDs (privacy-modal, accept-btn, modal-scrollbox) are correct.');
    }

    // Form Persistence Logic
    const riskForm = document.getElementById('risk-form');
    const sexoSelect = document.getElementById('sexo');
    const edadInput = document.getElementById('edad');
    const alcaldiaSelect = document.getElementById('alcaldia');

    if (riskForm && sexoSelect && edadInput && alcaldiaSelect) {
        // Load saved form data from sessionStorage on page load
        if (sessionStorage.getItem('perfilFormSexo')) {
            sexoSelect.value = sessionStorage.getItem('perfilFormSexo');
        }
        if (sessionStorage.getItem('perfilFormEdad')) {
            edadInput.value = sessionStorage.getItem('perfilFormEdad');
        }
        if (sessionStorage.getItem('perfilFormAlcaldia')) {
            alcaldiaSelect.value = sessionStorage.getItem('perfilFormAlcaldia');
        }

        // Save form data to sessionStorage on submit
        riskForm.addEventListener('submit', function() {
            sessionStorage.setItem('perfilFormSexo', sexoSelect.value);
            sessionStorage.setItem('perfilFormEdad', edadInput.value);
            sessionStorage.setItem('perfilFormAlcaldia', alcaldiaSelect.value);
        });
    }
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