from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

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
