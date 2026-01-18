// Map picker with Leaflet + Esri World Imagery (satellite) + Nominatim reverse geocoding
(function() {
    const modal = document.getElementById('mapModal');
    const openBtn = document.getElementById('pickOnMapBtn');
    const closeBtn = document.getElementById('closeMapModal');
    const cityInput = document.getElementById('cityInput');
    const mapContainerId = 'mapPicker';
    let mapInstance = null;
    let marker = null;

    const showModal = () => { modal.style.display = 'flex'; };
    const hideModal = () => { modal.style.display = 'none'; };

    const ensureMap = () => {
        if (mapInstance) {
            mapInstance.invalidateSize();
            return;
        }
        mapInstance = L.map(mapContainerId).setView([12.114, -86.236], 3); // Default view (Managua-ish / global)
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 18,
            attribution: 'Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community'
        }).addTo(mapInstance);

        mapInstance.on('click', async (e) => {
            const { lat, lng } = e.latlng;
            if (marker) marker.remove();
            marker = L.marker([lat, lng]).addTo(mapInstance);

            // Reverse geocode with Nominatim (free)
            try {
                const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;
                const resp = await fetch(url, { headers: { 'Accept-Language': 'en' } });
                if (resp.ok) {
                    const data = await resp.json();
                    const city = data.address?.city || data.address?.town || data.address?.village || data.address?.state || '';
                    if (city) {
                        cityInput.value = city;
                    }
                }
            } catch (err) {
                console.warn('Reverse geocoding failed', err);
            }
        });
    };

    openBtn?.addEventListener('click', () => {
        showModal();
        setTimeout(() => ensureMap(), 50);
    });

    closeBtn?.addEventListener('click', hideModal);
    modal?.addEventListener('click', (e) => { if (e.target === modal) hideModal(); });

    // Optional: center on user geolocation if allowed
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                if (!mapInstance) return;
                const { latitude, longitude } = pos.coords;
                mapInstance.setView([latitude, longitude], 10);
            },
            () => {/* ignore errors */}
        );
    }
})();