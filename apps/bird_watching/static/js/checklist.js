"use strict";

let app = {};

app.data = {
    data: function() {
        return {
            checklists: [],
            species: [],
            searchQuery: '',
            selectedSpecies: {},  // Object to store selected species and their quantities
            initialTimestamp: null,
        };
    },
    methods: {
        fetchSpecies: function() {
            axios.get(get_species_URL)
                .then(response => {
                    this.species = response.data.species;
                })
                .catch(error => {
                    console.error("There was an error fetching the species:", error);
                    alert("Failed to fetch species due to an error.");
                });
        },
        handleSpeciesClick: function(speciesItem) {
            // Check if the species is already in the selectedSpecies object
            if (!this.selectedSpecies[speciesItem.id]) {
                // If not, add it with initial quantity of 1
                this.selectedSpecies[speciesItem.id] = {
                    name: speciesItem.name,
                    quantity: 1
                };
            } else {
                // If it exists, just increment the quantity
                this.selectedSpecies[speciesItem.id].quantity++;
            }
            // Ensure updates are reactive
            this.selectedSpecies = {...this.selectedSpecies};
        },
        incrementQuantity: function(speciesId) {
            // Increment the quantity of the given species
            if (this.selectedSpecies[speciesId]) {
                this.selectedSpecies[speciesId].quantity += 1;
            }
        },
        submitSpecies: function(){
            const currentTimestamp = new Date();
            const timeDiff = (currentTimestamp - this.initialTimestamp) / 60000; // Time difference in seconds

            axios.post(submit_checklist_URL, {
                observ_time: this.initialTimestamp.toISOString(),
                duration: timeDiff,
                species_and_count: this.selectedSpecies,
                //need also longitude and latitude
            })
            .then(response => {
                console.log('Data submitted successfully:', response);
                if (response.data.success) {
                    // Redirect to the URL returned by the server
                    window.location.href = response.data.redirect_url; //only disabled temp
                } else {
                    // Handle error, maybe show user feedback
                    alert("Error: " + response.data.message);
                }
            }).catch(error => {
                console.error("Submission failed", error);
            });
        },
        saveTimestamp: function(timestamp) {
            axios.post(saveTimestamp_URL, { timestamp: timestamp })
                .then(response => console.log('Timestamp saved successfully'))
                .catch(error => console.error('Failed to save timestamp', error));
        },
        manageSpecies: function() {
            window.location.href = '/bird_watching/manage_checklists';
        }
    },
    computed: {
        filteredSpecies() {
            return this.species.filter(speciesItem => {
                return speciesItem.name.toLowerCase().includes(this.searchQuery.toLowerCase());
            });
        }
    },
    mounted: function() {
        this.fetchSpecies();
        this.initialTimestamp = new Date();
        // Call saveTimestamp here if you want to save it as soon as the app is loaded
        this.saveTimestamp(this.initialTimestamp.toISOString());
    }
};

app.vue = Vue.createApp(app.data).mount("#app");
