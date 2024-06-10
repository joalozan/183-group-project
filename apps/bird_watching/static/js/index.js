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
            this.map = L.map('map').setView([51.505, -0.09], 13);
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
            // Handle statistics on region logic here
            // This can involve extracting the coordinates of the drawn rectangle and sending a request to get stats for that region
            const layers = this.drawnItems.getLayers();
            if (layers.length > 0) {
                const layer = layers[0];
                const bounds = layer.getBounds();
                // Example: Redirect to a stats page with bounds as parameters
                window.location.href = `/stats?bounds=${bounds.toBBoxString()}`;
            } else {
                alert("Please draw a rectangle to select a region.");
            }
        }
    }
});
