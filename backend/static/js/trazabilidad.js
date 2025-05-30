// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const messageForm = document.getElementById('messageForm');
    const simularBtn = document.getElementById('simularBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsContent = document.getElementById('resultsContent');

    // Add event listeners for menu (if elements exist)
    if (menuBtn && sidebar && overlay) {
        menuBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);
    }

    // Add event listener for message form
    if (messageForm) {
        messageForm.addEventListener('submit', handleFormSubmit);
    }

    // Toggle menu function
    function toggleMenu() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }

    // Handle form submission
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        const messageText = document.getElementById('messageText').value.trim();
        const includePublicPost = document.getElementById('includePublicPost').checked;
        
        if (!messageText) {
            showResults([{
                type: 'error',
                message: 'Por favor, ingresa un mensaje antes de enviar.'
            }]);
            return;
        }

        // Show loading state
        setLoadingState(true);
        hideResults();

        try {
            const response = await fetch('/trazabilidad', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: messageText,
                    include_public: includePublicPost
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                handleSuccessResponse(data);
            } else {
                handleErrorResponse(data);
            }
            
        } catch (error) {
            console.error('Error:', error);
            showResults([{
                type: 'error',
                message: 'Error de conexión. Verifica tu conexión a internet e intenta nuevamente.'
            }]);
        } finally {
            setLoadingState(false);
        }
    }

    // Set loading state
    function setLoadingState(isLoading) {
        const btnText = simularBtn.querySelector('.btn-text');
        const btnLoading = simularBtn.querySelector('.btn-loading');
        const messageTextarea = document.getElementById('messageText');
        
        if (isLoading) {
            simularBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
            messageTextarea.disabled = true;
        } else {
            simularBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
            messageTextarea.disabled = false;
        }
    }

    // Handle successful response
    function handleSuccessResponse(data) {
        const results = [];
        
        if (data.success) {
            results.push({
                type: 'success',
                message: `✅ Mensaje enviado exitosamente a ${data.results.success} de ${data.results.total} contactos.`
            });
            
            if (data.results.failed > 0) {
                results.push({
                    type: 'error',
                    message: `⚠️ ${data.results.failed} mensajes no pudieron ser enviados.`
                });
            }
            
            if (data.public_post_sent) {
                results.push({
                    type: 'info',
                    message: '📢 Mensaje también publicado en el feed.'
                });
            }
            
            // Clear the form on success
            document.getElementById('messageText').value = '';
            document.getElementById('includePublicPost').checked = false;
            
        } else {
            results.push({
                type: 'error',
                message: `❌ Error: ${data.error || 'Error desconocido al enviar el mensaje.'}`
            });
        }
        
        showResults(results);
    }

    // Handle error response
    function handleErrorResponse(data) {
        showResults([{
            type: 'error',
            message: `❌ Error: ${data.error || 'Error del servidor al procesar la solicitud.'}`
        }]);
    }

    // Show results
    function showResults(results) {
        resultsContent.innerHTML = '';
        
        results.forEach(result => {
            const resultDiv = document.createElement('div');
            resultDiv.className = `result-item result-${result.type}`;
            resultDiv.textContent = result.message;
            resultsContent.appendChild(resultDiv);
        });
        
        resultsContainer.style.display = 'block';
        
        // Scroll to results
        resultsContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    // Hide results
    function hideResults() {
        resultsContainer.style.display = 'none';
    }

    // Auto-resize textarea
    const messageTextarea = document.getElementById('messageText');
    if (messageTextarea) {
        messageTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 300) + 'px';
        });
    }

    // Character counter (optional)
    function addCharacterCounter() {
        const messageTextarea = document.getElementById('messageText');
        const maxLength = 280; // Bluesky character limit
        
        if (messageTextarea) {
            const counterDiv = document.createElement('div');
            counterDiv.className = 'character-counter';
            counterDiv.style.textAlign = 'right';
            counterDiv.style.fontSize = '14px';
            counterDiv.style.color = '#666';
            counterDiv.style.marginTop = '5px';
            
            messageTextarea.parentNode.appendChild(counterDiv);
            
            function updateCounter() {
                const currentLength = messageTextarea.value.length;
                counterDiv.textContent = `${currentLength}/${maxLength}`;
                
                if (currentLength > maxLength) {
                    counterDiv.style.color = '#e74c3c';
                } else if (currentLength > maxLength * 0.9) {
                    counterDiv.style.color = '#f39c12';
                } else {
                    counterDiv.style.color = '#666';
                }
            }
            
            messageTextarea.addEventListener('input', updateCounter);
            updateCounter(); // Initial count
        }
    }
    
    // Initialize character counter
    addCharacterCounter();
});