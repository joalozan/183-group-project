from datetime import datetime
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.grid import Column

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        my_callback_url=URL('my_callback', signer=url_signer),
        species_url=URL('species', signer=url_signer),
        sightings_url=URL('sightings', signer=url_signer),
        stats_url=URL('stats', signer=url_signer)
    )

@action('checklist')
@action.uses('checklist.html', db, auth, url_signer)
def checklist():
    return dict(
        #placeholder/ experiment
        my_callback_url = URL('my_callback', signer=url_signer),
        get_checklists_URL = URL('get_checklists'),
        get_species_URL= URL('get_species'),
        submit_checklist_URL = URL('submit_checklist'),
        saveTimestamp_URL = URL('saveTimestamp')
    )

@action('manage_checklists')
@action.uses('manage_checklists.html', db, auth, url_signer)
def manage_checklists():
    return dict(
        #placeholder/ experiment
        my_callback_url = URL('my_callback', signer=url_signer),
        get_checklists_URL = URL('get_checklists'),
        get_species_URL= URL('get_species'),
        update_checklist_url = URL('update_checklist'),
        delete_checklist_url = URL('delete_checklist')
    )

@action('get_checklists', method=['GET'])
@action.uses(db, auth.user)
def get_checklists():
    user_email = auth.current_user.get('email') #uncomment this and comment line below and it will be the users checklists
    #user_email = 'obs1644106'
    checklists = db(db.checklists.observer_id == user_email).select().as_list()

    for checklist in checklists:
        checklist_id = checklist['event']
        sightings = db(db.sightings.event == checklist_id).select().as_list()
        checklist['sightings'] = sightings
    #print(checklists)
    return dict(checklists=checklists)

   
@action('submit_checklist', method=['POST'])
@action.uses(db, auth.user)
def submit_checklist():
    #section for checklists database
    event = datetime.now().strftime("%Y%m%d%H%M%S") #generate event string
    latitude = 0 #still need to link this from index
    longitude = 0 #^^^
    observation_date = datetime.now().date()
    observ_time = request.json.get('observ_time')
    #observer_id = don't need as it is set in models
    duration = request.json.get('duration')

    db.checklists.insert(
         event=event,
         latitude=latitude,
         longitude=longitude,
         observation_date=observation_date,
         observ_time=observ_time,
         duration=duration,
         # other fields as necessary

    )
    #section for sightins database
    species_and_count = request.json.get('species_and_count')


    for species_id, details in species_and_count.items():
        #print(details)

        db.sightings.insert(
            event=event,  # Ensure you have the correct foreign key linkage
            name=details['name'],
            count=details['quantity']
        )


    return dict(success=True, redirect_url=URL('index'))
    #return dict(success=True)

@action('update_checklist', method=['POST'])
@action.uses(db, auth.user)  # Ensure the user is authenticated
def update_checklist():
    # Retrieve the JSON data from the request
    data = request.json
    checklist_id = data.get('id')
    event = data.get('event')
    observation_date = data.get('observation_date')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    observ_time = data.get('observ_time')
    duration = data.get('duration')
    sightings = data.get('sightings')

    # Update the checklist
    db(db.checklists.id == checklist_id).update(
        event=event,
        observation_date=observation_date,
        latitude=latitude,
        longitude=longitude,
        observ_time=observ_time,
        duration=duration
    )

    # Update the sightings
    for sighting in sightings:
        sighting_id = sighting.get('id')
        name = sighting.get('name')
        count = sighting.get('count')

        db(db.sightings.id == sighting_id).update(
            event = event,
            name=name,
            count=count
        )

    return dict(success=True, message="Checklist updated successfully")


@action('delete_checklist', method=['POST'])
@action.uses(db, auth.user)  # Ensure the user is authenticated
def delete_checklist():
    checklist_id = request.json.get('id')
    if checklist_id:
        # Delete associated sightings first
        db(db.sightings.event == checklist_id).delete()
        # Then delete the checklist
        db(db.checklists.id == checklist_id).delete()
        return dict(success=True, message="Checklist deleted successfully")
    return dict(success=False, message="Checklist ID not provided")


@action('saveTimestamp', method=['POST'])
def save_timestamp():
    try:
        data = request.json
        timestamp = data.get('timestamp')
        # Now you can use this timestamp as a variable or save it in the database
        # For instance, storing it in session or a temporary variable (shown as a print here)
        print("Timestamp received:", timestamp)
        return dict(message="Timestamp saved successfully", status=200)
    except Exception as e:
        # Handle exception, e.g., if timestamp is not provided or JSON is malformed
        print(str(e))
        abort(400)

@action('get_species')
@action.uses(db, auth)
def get_species():
    # Ensure only logged-in users can access this data
    species_data = db(db.species).select().as_list()
    return dict(species=species_data)

@action('my_callback')
@action.uses(db, auth)
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=3)

@action('species')
@action.uses(db, auth)
def species():
    try:
        species_list = db(db.species).select().as_list()
        return dict(species=species_list)
    except Exception as e:
        logger.error(f"Error in species: {e}")
        abort(500)

@action('sightings')
@action.uses(db, auth)
def sightings():
    try:
        sightings_list = db(db.sightings).select().as_list()
        return dict(sightings=sightings_list)
    except Exception as e:
        logger.error(f"Error in sightings: {e}")
        abort(500)

@action('stats')
@action.uses(db, auth)
def stats():
    try:
        bounds = request.params.get('bounds')
        if not bounds:
            abort(400, "Missing bounds parameter")
        
        # Parse bounds
        bounds = list(map(float, bounds.split(',')))
        sw_lat, sw_lng, ne_lat, ne_lng = bounds

        # Find sightings within bounds
        query = (db.sightings.latitude >= sw_lat) & (db.sightings.latitude <= ne_lat) & \
                (db.sightings.longitude >= sw_lng) & (db.sightings.longitude <= ne_lng)
        sightings_list = db(query).select().as_list()

        return dict(sightings=sightings_list)
    except Exception as e:
        logger.error(f"Error in stats: {e}")
        abort(500)

@action('user_stats/<path:path>', method=['POST', 'GET'])
@action('user_stats', method=['POST', 'GET'])
@action.uses('user_stats.html', db, session, auth)
def user_stats(path=None):
    valid_events = [checklist.event for checklist in db(db.checklists.observer_id == 'obs1644106').select()]
    grid = Grid(path,
                formstyle=FormStyleBulma,
                grid_class_style=GridClassStyleBulma,
                query=(db.sightings.event.contains(valid_events)),
                editable=False,
                deletable=False,
                details=False,
                columns=[Column("Species", lambda row: A(f"{row.name}", _href=f"/bird_watching/event/{row.event}")), db.sightings.count],
                search_queries=[['Search by Name', lambda val: db.sightings.name.contains(val)]],
                )
    return dict(
        grid=grid,
    )

#user version
#@action('user_stats/<path:path>', method=['POST', 'GET'])
#@action('user_stats', method=['POST', 'GET'])
#@action.uses('user_stats.html', db, session, auth.user)
#def user_stats(path=None):
#    user_email = auth.current_user.get('email')
#    valid_events = [checklist.event for checklist in db(db.checklists.observer_id == user_email).select()]
#    grid = Grid(path,
#                formstyle=FormStyleBulma,
#                grid_class_style=GridClassStyleBulma,
#                query=(db.sightings.event.contains(valid_events)),
#                editable=False,
#                deletable=False,
#                columns=[db.sightings.name, db.sightings.count],
#                search_queries=[['Search by Name', lambda val: db.sightings.name.contains(val)]],
#                )
#    return dict(
#        grid=grid,
#    )

@action('event/<path:path>', method=['POST', 'GET'])
@action('event', method=['POST', 'GET'])
@action.uses('event.html', db, session, auth)
def event(path=None):
    date = db.checklists(db.checklists.event == path).observation_date
    return dict(
        date = date,
    )
