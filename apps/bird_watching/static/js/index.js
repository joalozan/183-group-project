new Vue({
    el: '#app',
    data: {
        my_value: 'Welcome to the Bird Watching App!',
        selectedSpecies: '',
        speciesList: [],
        map: null,
        heatmapLayer: null,
        drawnItems: new L.FeatureGroup(),
        circleMarkerLayer: null  // To store the reference to the circleMarker layer
    },
    mounted() {
        console.log('Vue instance mounted');
        this.fetchSpecies();
        this.initMap();
    },
    methods: {
        fetchSpecies() {
            console.log('Fetching species');
            fetch(species_url)
                .then(response => response.json())
                .then(data => {
                    console.log('Species fetched', data);
                    this.speciesList = data.species.map(species => species.name);
                })
                .catch(error => {
                    console.error('Error fetching species:', error);
                });
        },
        initMap() {
            console.log('Initializing map');
            // Default to Santa Cruz, California if geolocation fails
            const defaultLat = 36.9741;
            const defaultLng = -122.0308;

            const initializeMap = (lat, lng) => {
                console.log('Setting map view', lat, lng);
                this.map = L.map('map').setView([lat, lng], 13);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }).addTo(this.map);

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
                        circlemarker: true, // Enable the circleMarker tool
                        marker: false,
                        rectangle: true
                    }
                });
                this.map.addControl(drawControl);

                // Event handler for drawing rectangles
                this.map.on(L.Draw.Event.CREATED, (event) => {
                    var layer = event.layer;
                    if (layer instanceof L.CircleMarker) {
                        // Remove previous circleMarker if it exists
                        if (this.circleMarkerLayer) {
                            this.drawnItems.removeLayer(this.circleMarkerLayer);
                        }
                        this.circleMarkerLayer = layer;
                    }
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
            console.log('Updating map for species:', this.selectedSpecies);
            const species = this.selectedSpecies;  // Default to 'all' if no species selected
            let heatmapData = [];

            fetch(`${sightings_url}?species=${species}`)
                .then(response => response.json())
                .then(data => {
                    console.log('Sightings fetched', data);

                    if (!species || species === 'all' || species === ''){
                        console.log('species is all');
                        heatmapData = data.sightings.map(sighting => [
                            parseFloat(sighting.checklists.latitude),
                            parseFloat(sighting.checklists.longitude),
                            parseInt(sighting.sightings.count),  // Assuming each sighting has the same weight
    
                        ]);
                    } else {
                        heatmapData = data.sightings.filter(sighting => {
                            return sighting.sightings.name == species;
                        }).map(sighting => [
                            parseFloat(sighting.checklists.latitude),
                            parseFloat(sighting.checklists.longitude),
                            parseInt(sighting.sightings.count),  // Assuming each sighting has the same weight
    
                        ]);
                    }
        
                    if (this.heatmapLayer) {
                        this.map.removeLayer(this.heatmapLayer);
                        this.heatmapLayer = null;
                    }
        
                    this.heatmapLayer = L.heatLayer(heatmapData, {
                        radius: 35,
                        blur: 15,
                        maxZoom: 17,
                        opacity: 0.8
                    }).addTo(this.map);

                })
                .catch(error => {
                    console.error('Error fetching sightings:', error);
                });
        },

        navigateToChecklist() {
            if (this.circleMarkerLayer) {
                const center = this.circleMarkerLayer.getLatLng();
                // Redirect to checklist page with circle center as parameters
                window.location.href = `/bird_watching/checklist?lat=${center.lat}&lng=${center.lng}`;
            } else {
                alert("Please draw a circle marker to select a region.");
            }
        },
        navigateToStats() {
            window.location.href = '/bird_watching/user_stats';
        },
        showStatisticsOnRegion() {
            const layers = this.drawnItems.getLayers();
            if (layers.length > 0) {
                const layer = layers[0];
                const bounds = layer.getBounds();
        
                // Extract the coordinates
                const sw = bounds.getSouthWest(); // Southwest corner
                const ne = bounds.getNorthEast(); // Northeast corner
        
                // Convert coordinates to strings
                const swLat = sw.lat;
                const swLng = sw.lng;
                const neLat = ne.lat;
                const neLng = ne.lng;
        
                // Redirect to the location page with bounds as parameters
                window.location.href = `/bird_watching/location?swLat=${swLat}&swLng=${swLng}&neLat=${neLat}&neLng=${neLng}`
            } else {
                alert("Please draw a rectangle to select a region.");
            }
        }
        
    },
    watch: {
        selectedSpecies(newSpecies, oldSpecies) {
            console.log('Selected species changed to', newSpecies, 'from', oldSpecies);
            this.updateMap();
        }
    }
});
