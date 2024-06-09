new Vue({
    el: '#app',
    data: {
        my_value: 'Welcome to the Bird Watching App!',
        selectedSpecies: 'all',
        speciesList: ['Sparrow', 'Eagle', 'Hawk', 'Owl'],
        map: null,
        heatmapLayer: null
    },
    mounted() {
        this.initMap();
    },
    methods: {
        initMap() {
            this.map = L.map('map').setView([51.505, -0.09], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(this.map);

            this.heatmapLayer = L.heatLayer([], { radius: 25 }).addTo(this.map);
            this.updateMap();
        },
        updateMap() {
            // Fetch data based on selectedSpecies and update heatmapLayer
            // For now, let's add some dummy data
            const dummyData = [
                [51.505, -0.09, 0.5],
                [51.51, -0.1, 0.5],
                [51.51, -0.12, 0.5]
            ];
            this.heatmapLayer.setLatLngs(dummyData);
        },
        navigateToChecklist() {
            window.location.href = '/checklist';
        },
        navigateToStats() {
            window.location.href = '/stats';
        }
    }
});
