document.addEventListener('DOMContentLoaded', () => {
    // Cargamos el audio desde la carpeta static
    const audio = new Audio('/static/MC-S.mp3');
    audio.loop = true; // Para que la música nunca pare (bucle)
    audio.volume = 0.4; // Volumen al 40% para no asustar

    const musicBtn = document.getElementById('musicBtn');
    let isPlaying = false;

    // Función para alternar Play/Pause
    musicBtn.addEventListener('click', () => {
        if (isPlaying) {
            audio.pause();
            // Cambiamos el estilo a "apagado"
            musicBtn.innerHTML = '🎵 Play Zen Music';
            musicBtn.style.background = 'transparent';
            musicBtn.style.color = '#2c3e50';
            musicBtn.style.borderColor = '#2c3e50';
        } else {
            // Intentamos reproducir (los navegadores requieren interacción primero)
            audio.play().then(() => {
                // Cambiamos el estilo a "encendido/activo"
                musicBtn.innerHTML = '⏸️ Pause Zen Music';
                musicBtn.style.background = '#2d6a4f';
                musicBtn.style.color = 'white';
                musicBtn.style.borderColor = '#2d6a4f';
            }).catch(error => {
                console.log("Error de Autoplay (El usuario debe interactuar primero):", error);
            });
        }
        isPlaying = !isPlaying;
    });
});