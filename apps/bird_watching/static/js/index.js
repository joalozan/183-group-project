new Vue({
    el: '#app',
    data: {
        my_value: 'Welcome to the Bird Watching App!',
        selectedSpecies: 'all',
        speciesList: [],
        map: null,
        heatmapLayer: null,
        drawnItems: new L.FeatureGroup()
    },
    mounted() {
        this.fetchSpecies();
        this.initMap();
    },
    methods: {
        fetchSpecies() {
            fetch(species_url)
                .then(response => response.json())
                .then(data => {
                    this.speciesList = data.species.map(species => species.name);
                });
        },
        initMap() {
            // Default to Santa Cruz, California if geolocation fails
            const defaultLat = 36.9741;
            const defaultLng = -122.0308;

            const initializeMap = (lat, lng) => {
                this.map = L.map('map').setView([lat, lng], 13);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }).addTo(this.map);

                this.heatmapLayer = L.heatLayer([], { radius: 25 }).addTo(this.map);
                this.updateMap();

                // Initialize the draw control and pass it the FeatureGroup of editable layers
                this.map.addLayer(this.drawnItems);
                var drawControl = new L.Control.Draw({
                    edit: {
                        featureGroup: this.drawnItems
                    },
                    draw: {
                        polygon: false,
                        polyline: false,
                        circle: false,
                        marker: false,
                        rectangle: true
                    }
                });
                this.map.addControl(drawControl);

                // Event handler for drawing rectangles
                this.map.on(L.Draw.Event.CREATED, (event) => {
                    var layer = event.layer;
                    this.drawnItems.addLayer(layer);
                });
            };

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition((position) => {
                    const userLat = position.coords.latitude;
                    const userLng = position.coords.longitude;
                    initializeMap(userLat, userLng);
                }, () => {
                    // If user denies geolocation or it fails, set to default coordinates
                    initializeMap(defaultLat, defaultLng);
                });
            } else {
                // If browser doesn't support geolocation, set to default coordinates
                initializeMap(defaultLat, defaultLng);
            }
        },
        updateMap() {
            fetch(sightings_url)
                .then(response => response.json())
                .then(data => {
                    const sightings = data.sightings.filter(sighting => this.selectedSpecies === 'all' || sighting.species === this.selectedSpecies);
                    const heatmapData = sightings.map(sighting => [sighting.latitude, sighting.longitude, sighting.count]);
                    this.heatmapLayer.setLatLngs(heatmapData);
                });
        },
        navigateToChecklist() {
            window.location.href = '/bird_watching/checklist';
        },
        navigateToStats() {
            window.location.href = '/bird_watching/user_stats';
        },
        showStatisticsOnRegion() {
            const layers = this.drawnItems.getLayers();
            if (layers.length > 0) {
                const layer = layers[0];
                const bounds = layer.getBounds();
                window.location.href = `/stats?bounds=${bounds.toBBoxString()}`;
            } else {
                alert("Please draw a rectangle to select a region.");
            }
        }
    }
});
