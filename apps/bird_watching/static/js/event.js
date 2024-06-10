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
        this.initMap();
    },
    methods: {

        initMap() {
            this.map = L.map('map').setView([latitude, longitude], 13);
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
    }
});
