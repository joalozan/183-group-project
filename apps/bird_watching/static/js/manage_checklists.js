"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

app.data = {
    data: function() {
        return {
            checklists: [],  // This will store the checklist data fetched from the server
        };
    },
    methods: {
        findChecklistIdx: function(id) {
            for (let i = 0; i < this.checklists.length; i++) {
                if (this.checklists[i].id === id) {
                    return i;
                }
            }
            return null;
        },
        deleteChecklist: function(id) {
            let self = this;
            axios.post(delete_checklist_url, { id: id }).then(function (response) {
                if (response.data.success) {
                    self.load_data();  // Reload the data after deletion
                } else {
                    console.error(response.data.message);
                }
            }).catch(function (error) {
                console.error("Error in deleting checklist:", error);
            });
        },
        toggleEdit: function(checklist) {
            checklist.isEditable = !checklist.isEditable;
        },
        saveChecklist: function(checklist) {
            let self = this;
            checklist.isEditable = false;
            axios.post(update_checklist_url, {
                id: checklist.id,
                event: checklist.event,
                observation_date: checklist.observation_date,
                latitude: checklist.latitude,
                longitude: checklist.longitude,
                observ_time: checklist.observ_time,
                duration: checklist.duration,
                sightings: checklist.sightings.map(sighting => ({
                    id: sighting.id,
                    name: sighting.name,
                    count: sighting.count
                }))
            }).then(function(response) {
                console.log('Checklist saved:', response.data);
            }).catch(function(error) {
                console.error('Error saving checklist:', error);
                checklist.isEditable = true; // Re-enable editing if save fails
            });
        },
        load_data: function () {
            let self = this;
            axios.get(get_checklists_URL).then(function (response) {
                self.checklists = response.data.checklists.map(checklist => ({
                    id: checklist.id,
                    event: checklist.event,
                    latitude: checklist.latitude,
                    longitude: checklist.longitude,
                    observation_date: checklist.observation_date,
                    observ_time: checklist.observ_time,
                    duration: checklist.duration,
                    sightings: checklist.sightings,
                    isEditable: false // Ensure the initial state is not editable
                }));
            }).catch(function (error) {
                console.error("There was an error fetching the checklists:", error);
                alert("Failed to fetch checklists due to an error.");
            });
        }
    },
    mounted: function() {
        this.load_data();
    }
};

app.vue = Vue.createApp(app.data).mount("#app");
