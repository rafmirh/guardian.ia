document.addEventListener('DOMContentLoaded', function() {
    // Sidebar menu elements (if they exist on this page)
    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    // Form and feed elements for trazabilidad page
    const spamForm = document.getElementById('spamForm');
    const simularBtn = document.getElementById('simularBtn');
    const responseArea = document.getElementById('responseArea'); // Was resultsContainer
    const resultsContent = document.getElementById('resultsContent');
    const messageTextarea = document.getElementById('message'); // Was messageText
    const includePublicCheckbox = document.getElementById('include_public'); // Was includePublicPost

    const botFeedArea = document.getElementById('botFeedArea');
    const botUsernameSpan = document.getElementById('botUsername');

    // Add event listeners for menu (if elements exist)
    if (menuBtn && sidebar && overlay) {
        menuBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);
        function toggleMenu() {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
        }
    }

    async function loadBotFeed() {
        if (!botFeedArea) {
            // console.error('Error: botFeedArea element not found in HTML.');
            if (botUsernameSpan) botUsernameSpan.textContent = 'N/A';
            return;
        }
        botFeedArea.innerHTML = '<p>Cargando feed...</p>';
        try {
            const response = await fetch('/trazabilidad/get_bot_feed?limit=15');
            const data = await response.json();

            if (botUsernameSpan) {
                botUsernameSpan.textContent = data.username || 'bot';
            }

            if (data.success) {
                botFeedArea.innerHTML = '';
                if (data.feed.length === 0) {
                    botFeedArea.innerHTML = '<p>No hay posts en el feed.</p>';
                    return;
                }
                data.feed.forEach(post => {
                    const postElement = document.createElement('div');
                    postElement.classList.add('feed-post');

                    const textElement = document.createElement('p');
                    textElement.classList.add('post-text');
                    textElement.textContent = post.text;

                    const metaElement = document.createElement('p');
                    metaElement.classList.add('post-meta');
                    const postDate = new Date(post.createdAt).toLocaleString();
                    const rkey = post.uri.split('/').pop();
                    const postUrl = `https://bsky.app/profile/${data.username}/post/${rkey}`;
                    
                    metaElement.innerHTML = `Publicado: ${postDate} | <a href="${postUrl}" target="_blank" rel="noopener noreferrer">Ver post</a>`;
                    
                    postElement.appendChild(textElement);
                    postElement.appendChild(metaElement);
                    botFeedArea.appendChild(postElement);
                });
            } else {
                botFeedArea.innerHTML = `<p>Error al cargar el feed: ${data.error || 'Error desconocido'}</p>`;
            }
        } catch (error) {
            console.error('Error fetching bot feed:', error);
            botFeedArea.innerHTML = '<p>Error de conexión al cargar el feed.</p>';
            if (botUsernameSpan && botUsernameSpan.textContent === 'cargando...') {
                 botUsernameSpan.textContent = 'Error';
            }
        }
    }

    function setLoadingState(isLoading) {
        if (!simularBtn || !messageTextarea) return;

        const btnText = simularBtn.querySelector('.btn-text');
        const btnLoading = simularBtn.querySelector('.btn-loading');
        
        simularBtn.disabled = isLoading;
        messageTextarea.disabled = isLoading;
        if (btnText) btnText.style.display = isLoading ? 'none' : 'inline-block';
        if (btnLoading) btnLoading.style.display = isLoading ? 'inline-block' : 'none';
    }

    function showResponse(data, isSuccess) {
        if (!responseArea || !resultsContent) return;

        const results = [];
        if (isSuccess && data.success) {
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
            if (messageTextarea) messageTextarea.value = '';
            if (includePublicCheckbox) includePublicCheckbox.checked = false;
            loadBotFeed(); // Refresh feed on success
        } else {
            results.push({
                type: 'error',
                message: `❌ Error: ${data.error || 'Error desconocido al enviar el mensaje.'}`
            });
        }

        resultsContent.innerHTML = '';
        results.forEach(result => {
            const resultDiv = document.createElement('div');
            resultDiv.className = `result-item result-${result.type}`;
            resultDiv.textContent = result.message;
            resultsContent.appendChild(resultDiv);
        });
        responseArea.style.display = 'block';
        responseArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    if (spamForm) {
        spamForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            if (!messageTextarea || !includePublicCheckbox) return;

            const messageText = messageTextarea.value.trim();
            const includePublic = includePublicCheckbox.checked;

            if (!messageText) {
                showResponse({ error: 'Por favor, ingresa un mensaje antes de enviar.' }, false);
                return;
            }

            setLoadingState(true);
            if (responseArea) responseArea.style.display = 'none';

            try {
                const apiResponse = await fetch('/trazabilidad', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageText, include_public: includePublic })
                });
                const data = await apiResponse.json();
                showResponse(data, apiResponse.ok);
            } catch (error) {
                console.error('Error:', error);
                showResponse({ error: 'Error de conexión. Verifica tu conexión a internet e intenta nuevamente.' }, false);
            } finally {
                setLoadingState(false);
            }
        });
    }

    // Auto-resize textarea (if element exists)
    if (messageTextarea) {
        messageTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 300) + 'px';
        });
    }

    // Character counter (optional, if element exists)
    function addCharacterCounter() {
        if (!messageTextarea) return;

        const maxLength = 280; // Bluesky character limit
        const counterDiv = document.createElement('div');
        counterDiv.className = 'character-counter';
        Object.assign(counterDiv.style, {
            textAlign: 'right', fontSize: '14px', color: '#666', marginTop: '5px'
        });
        
        messageTextarea.parentNode.appendChild(counterDiv);
        
        function updateCounter() {
            const currentLength = messageTextarea.value.length;
            counterDiv.textContent = `${currentLength}/${maxLength}`;
            counterDiv.style.color = currentLength > maxLength ? '#e74c3c' :
                                   currentLength > maxLength * 0.9 ? '#f39c12' : '#666';
        }
        
        messageTextarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial count
    }

    addCharacterCounter();

    // Initial load of the bot feed
    if (botFeedArea) {
        loadBotFeed();
    }
});