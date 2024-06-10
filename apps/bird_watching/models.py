"""
This file defines the database models
"""

import csv
import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later\

def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Adjust this format to match your date format
        return True
    except ValueError:
        return False


#had to change all types in database to string due to csv weirdness


db.define_table(
    'species',
    Field('name', 'string')
)

if db(db.species).isempty():
    with open('species.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            db.species.insert(name=row[0])


db.define_table(
    'checklists',
    Field('event', 'string'),
    Field('latitude', 'string'),
    Field('longitude', 'string'),
    Field('observation_date', 'date'),
    Field('observ_time', 'string'),
    Field('observer_id', 'string', default=get_user_email),
    Field('duration', 'string')
)


if db(db.checklists).isempty():
    with open('checklists.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            valid_date = row[3] if is_valid_date(row[3]) else None  # Use None for invalid dates
            db.checklists.insert(
                event=row[0],
                latitude=row[1],
                longitude=row[2],
                observation_date=valid_date,  # Use the validated or None date
                observ_time=row[4],
                observer_id=row[5],
                duration=row[6]
            )
            if valid_date is None:
                print(f"Invalid date skipped and left empty: {row[3]}")



db.define_table(
    'sightings',
    Field('event', 'string'),
    Field('name', 'string'),
    Field('count', 'string')#some values are X becasue there is no count which causes an error if set to integer
)

if db(db.sightings).isempty():
    with open('sightings.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            db.sightings.insert(
                event=row[0],
                name=row[1],
                count=row[2]
            )

db.commit()
