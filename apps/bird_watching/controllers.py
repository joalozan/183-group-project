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
    #user_email = auth.current_user.get('email') #uncomment this and comment line below and it will be the users checklists
    user_email = 'obs1644106'
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
        species_name = request.params.get('species')
        if species_name and species_name != 'all':
            query = (db.sightings.name == species_name) & (db.sightings.event == db.checklists.event) & \
                    (db.sightings.count != 'X') & (db.checklists.latitude != '') & (db.checklists.longitude != '')
        else:
            query = (db.sightings.event == db.checklists.event) & \
                    (db.sightings.count != 'X') & (db.checklists.latitude != '') & (db.checklists.longitude != '')

        sightings_list = db(query).select(db.sightings.name, db.sightings.count, db.checklists.latitude, db.checklists.longitude).as_list()
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
    valid_events = [checklist.event for checklist in db(db.checklists.observer_id == get_user_email()).select()]
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
    histogram = dict()
    for species in db(db.sightings.event.contains(valid_events)).select():
        key = db.checklists(db.checklists.event == species.event).observation_date
        key = str(key)
        histogram[key] = histogram.get(key, 0) + int(species.count)
    dates = list(histogram.keys())
    counts = list(histogram.values())
    return dict(
        grid=grid,
        dates=dates,
        counts=counts
    )

@action('event/<path:path>', method=['POST', 'GET'])
@action('event', method=['POST', 'GET'])
@action.uses('event.html', db, session, auth)
def event(path=None):
    date = db.checklists(db.checklists.event == path).observation_date
    latitude = db.checklists(db.checklists.event == path).latitude
    longitude = db.checklists(db.checklists.event == path).longitude
    print(date, latitude, longitude)
    return dict(
        date = date,
        latitude = latitude,
        longitude = longitude,
    )


@action('location')
@action.uses('location.html', db, auth, url_signer)
def location():
    return dict(
        location_load_url=URL('location_load'),
    )

@action('location_load', method={'GET', 'POST'})
@action.uses(db, auth)
def location_load():
    sw_lat = request.params.get('swLat')
    sw_lng = request.params.get('swLng')
    ne_lat = request.params.get('neLat')
    ne_lng = request.params.get('neLng')

    logger.info(f"Received bounds: swLat={sw_lat}, swLng={sw_lng}, neLat={ne_lat}, neLng={ne_lng}")


    if not (sw_lat and sw_lng and ne_lat and ne_lng):
        abort(400, "Missing bounds parameter")

    # Parse bounds
    try:
        sw_lat = float(sw_lat)
        sw_lng = float(sw_lng)
        ne_lat = float(ne_lat)
        ne_lng = float(ne_lng)
    except ValueError:
        abort(400, "Invalid bounds parameter format")

    logger.info(f"Parsed bounds: swLat={sw_lat}, swLng={sw_lng}, neLat={ne_lat}, neLng={ne_lng}")

    # Fetch checklists within bounds
    checklists_in_bounds = db((db.checklists.latitude.cast('float') >= sw_lat) & 
                              (db.checklists.latitude.cast('float') <= ne_lat) &
                              (db.checklists.longitude.cast('float') >= sw_lng) &
                              (db.checklists.longitude.cast('float') <= ne_lng)).select().as_list()

    logger.info("Checklists in bounds:", checklists_in_bounds)

    if not checklists_in_bounds:
        logger.warning("No checklists found within the specified bounds.")
        return dict(locationDetails={}, topContributors=[])


    # Collect all sampling event identifiers within the bounds
    event_ids = [checklist['event'] for checklist in checklists_in_bounds]

    # Fetch sightings for these event ids
    sightings_in_bounds = db(db.sightings.event.belongs(event_ids)).select()

    # Process sightings to calculate species counts and sightings over time
    species_counts = {}
    species_sightings_over_time = {}
    for sighting in sightings_in_bounds:
        species = sighting['name']
        count_str = sighting['count']
        try:
            count = int(count_str)
        except ValueError:
            logger.warning(f"Non-integer count value encountered: {count_str}")
            continue  # Skip this sighting if count is not an integer
        
        event = sighting['event']
        date = db(db.checklists.event == event).select().first()['observation_date']
        logger.info(f"Sighting: {sighting}, Date: {date}")

        if species in species_counts:
            species_counts[species]['checklistCount'] += 1
            species_counts[species]['sightingsCount'] += count
        else:
            species_counts[species] = {'checklistCount': 1, 'sightingsCount': count}

        if species not in species_sightings_over_time:
            species_sightings_over_time[species] = {}

        if date in species_sightings_over_time[species]:
            species_sightings_over_time[species][date] += count
        else:
            species_sightings_over_time[species][date] = count


    birds = [
        {
            'name': species,
            'checklistCount': data['checklistCount'],
            'sightingsCount': data['sightingsCount'],
            'sightingsOverTime': [{'date': date, 'count': count} for date, count in species_sightings_over_time[species].items()]
        }
        for species, data in species_counts.items()
    ]


    # Calculate top contributors
    contributor_counts = {}
    for checklist in checklists_in_bounds:
        observer = checklist['observer_id']
        if observer in contributor_counts:
            contributor_counts[observer] += 1
        else:
            contributor_counts[observer] = 1

    top_contributors = sorted(contributor_counts.items(), key=lambda item: item[1], reverse=True)

    print("Top contributors:", top_contributors)

    location_details = {
        "name": f"Region ({sw_lat}, {sw_lng}) to ({ne_lat}, {ne_lng})",
        "description": f"Details for region from ({sw_lat}, {sw_lng}) to ({ne_lat}, {ne_lng})",
        "birds": birds
    }

    top_contributors_list = [{"name": contributor, "checklists": count} for contributor, count in top_contributors]

    return dict(
        locationDetails=location_details,
        topContributors=top_contributors_list
    )
