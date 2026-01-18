(() => {
    const launcher = document.getElementById('chatLauncher');
    const backdrop = document.getElementById('chatbotBackdrop');
    const closeBtn = document.getElementById('chatbotClose');
    const sendBtn = document.getElementById('chatbotSend');
    const input = document.getElementById('chatbotInput');
    const responseBox = document.getElementById('chatbotResponse');
    const cityInput = document.getElementById('cityInput');

    const show = () => { backdrop.style.display = 'flex'; input.focus(); };
    const hide = () => { backdrop.style.display = 'none'; };

    launcher?.addEventListener('click', show);
    closeBtn?.addEventListener('click', hide);
    backdrop?.addEventListener('click', (e) => { if (e.target === backdrop) hide(); });

    const setLoading = (state) => {
        if (state) {
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
        } else {
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
        }
    };

    const sendMessage = async () => {
        const message = (input.value || '').trim();
        if (!message) return;
        setLoading(true);
        try {
            const city = (cityInput?.value || 'Managua').trim();
            const res = await fetch('/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, city })
            });
            if (!res.ok) throw new Error('Network error');
            const data = await res.json();
            responseBox.textContent = data.reply || 'No reply received.';
        } catch (err) {
            responseBox.textContent = 'I could not answer now. Try again.';
        } finally {
            setLoading(false);
        }
    };

    sendBtn?.addEventListener('click', sendMessage);
    input?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
            sendMessage();
        }
    });
})();