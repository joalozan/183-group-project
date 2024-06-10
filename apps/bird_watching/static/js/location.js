"use strict";

let app = {};

app.data = {
    data: function() {
        return {
            locationDetails: null,
            topContributors: [],
            errorMessage: '',
            selectedSpecies: null,
            speciesChart: null
        };
    },
    methods: {
        fetchLocationDetails: function() {
            const urlParams = new URLSearchParams(window.location.search);
            const swLat = urlParams.get('swLat');
            const swLng = urlParams.get('swLng');
            const neLat = urlParams.get('neLat');
            const neLng = urlParams.get('neLng');

            if (!(swLat && swLng && neLat && neLng)) {
                this.errorMessage = "No region selected.";
                return;
            }

            const bounds = `${swLat},${swLng},${neLat},${neLng}`;

            axios.get(`/location_details?bounds=${bounds}`)
                .then(response => {
                    this.locationDetails = response.data.locationDetails;
                    this.topContributors = response.data.topContributors;
                    this.errorMessage = '';
                })
                .catch(error => {
                    this.errorMessage = "Failed to fetch location details.";
                    console.error(error);
                });
        },
        selectSpecies: function(speciesName) {
            this.selectedSpecies = this.locationDetails.birds.find(bird => bird.name === speciesName);
            this.drawSpeciesChart();
        },
        drawSpeciesChart: function() {
            if (this.speciesChart) {
                this.speciesChart.destroy();
            }
            const ctx = document.getElementById('speciesChart').getContext('2d');
            const speciesData = this.selectedSpecies.sightingsOverTime;

            this.speciesChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: speciesData.map(entry => entry.date),
                    datasets: [{
                        label: `${this.selectedSpecies.name} Sightings`,
                        data: speciesData.map(entry => entry.count),
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Number of Sightings'
                            }
                        }
                    }
                }
            });
        }
    },
    mounted: function() {
        this.fetchLocationDetails();
    }
};

app.vue = Vue.createApp(app.data).mount("#app");
