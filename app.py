#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from sre_parse import State
from termios import VMIN
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://abbiemccallum@localhost:5432/fyyur'
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)    
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue',lazy='joined', cascade="all, delete")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String)    
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all,delete")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
   __tablename__ = 'Show'
   id = db.Column(db.Integer, primary_key=True)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
   start_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

#Please note part of this code was found as an example in knowledge. 
  data = []
  venues = Venue.query.all()
  #Creating places to link city and state
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  #Show each venue in place
  for place in places:
    data.append({
      'city' : place.city,
      'state': place.state,
      'venues': [{'id': venue.id, 'name':venue.name}     
      for venue in venues
        if venue.city == place.city and venue.state == place.state]
    })

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)
  upcoming_shows= []
  past_shows= []

  for show in venue.shows:
    show_data = {
      'artist_image_link': show.artist.image_link,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if show.start_time <= datetime.now():
      past_shows.append(show_data)
    else:
        upcoming_shows.append(show_data)

  data= {
   'id': venue.id,
   'name': venue.name,
   'genres': venue.genres,
   'address': venue.address,
   'city': venue.city,
   'state': venue.state,
   'phone': venue.phone,
   'website_link': venue.website_link,
   'image_link': venue.image_link,
   'facebook_link': venue.facebook_link,
   'seeking_talent': venue.seeking_talent,
   'seeking_description': venue.seeking_description,
   'past_shows': past_shows,
   'upcoming_shows': upcoming_shows,
   'past_shows_count': len(past_shows),
   'upcoming_shows_count': len(upcoming_shows)
  }

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = VenueForm(request.form)  
  try: 
    venue = Venue(name=form.name.data,city=form.city.data,state=form.state.data,
    address=form.address.data,phone=form.phone.data,image_link=form.image_link.data,
    genres=form.genres.data,facebook_link=form.facebook_link.data,website_link=form.website_link.data,
    seeking_talent=form.seeking_talent.data,seeking_description=form.seeking_description.data)
   
    db.session.add(venue)
    db.session.commit()
  
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
   # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # else:
  #   flash('An error occurred. Venue ' + Venue.name + ' could not be listed.')
  except ValueError as e:
   print(e)
   flash('An error occurred. Venue ' + Venue.name + ' could not be listed.')
   db.session.rollback()
  finally: 
    db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try: 
    venue= Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
   db.sesion.rollback()
  finally:
    db.session.close()
  return jsonify({'success':True})

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist= Artist.query.get(artist_id)
  upcoming_shows= []
  past_shows= []

  for show in artist.shows:
    show_data = {
      'venue_image_link': show.venue.image_link,
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if show.start_time <= datetime.now():
      past_shows.append(show_data)
    else:
        upcoming_shows.append(show_data)

  data= {
   'id': artist.id,
   'name': artist.name,
   'genres': artist.genres,
   'city': artist.city,
   'state': artist.state,
   'phone': artist.phone,
   'website_link': artist.website_link,
   'facebook_link': artist.facebook_link,
   'image_link': artist.image_link,
   'seeking_venue': artist.seeking_venue,
   'seeking_description': artist.seeking_description,
   'past_shows': past_shows,
   'upcoming_shows': upcoming_shows,
   'past_shows_count': len(past_shows),
   'upcoming_shows_count': len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist= Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  artist={
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    "state": artist.state,
    'phone': artist.phone,
    'website_link': artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist= Artist.query.get(artist_id)
  form=ArtistForm(request.form)
  try: 
   
    artist.name=form.name.data,
    artist.city=form.city.data,
    artist.state=form.state.data, 
    artist.phone=form.phone.data,
    artist.image_link=form.image_link.data,
    artist.genres=form.genres.data,
    artist.facebook_link=form.facebook_link.data,
    artist.website_link=form.website_link.data,
    artist.seeking_venue=form.seeking_venue.data,
    artist.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + Artist.name + ' could not be updated.')
  finally: 
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  venue={
    'id': venue.id, 
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website_link': venue.website_link, 
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  try:
    venue.name=form.name.data,
    venue.city=form.city.data,
    venue.state=form.state.data,
    venue.address=form.address.data,
    venue.phone=form.phone.data,
    venue.image_link=form.image_link.data,
    venue.genres=form.genres.data,
    venue.facebook_link=form.facebook_link.data,
    venue.website_link=form.website_link.data,
    venue.seeking_talent=form.seeking_talent.data,
    venue.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + Venue.name + ' could not be updated.')
  finally: 
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  body = {}
  form = ArtistForm(request.form)
  try: 
    artist= Artist(name=form.name.data,city=form.city.data,state=form.state.data, 
    phone=form.phone.data,image_link=form.image_link.data,genres=form.genres.data,
    facebook_link=form.facebook_link.data,website_link=form.website_link.data,
    seeking_venue=form.seeking_venue.data,seeking_description=form.seeking_description.data)
    
    db.session.add(artist)
    db.session.commit()

  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + Artist.name + ' could not be listed.')
  finally: 
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  data = []
  shows = Show.query.order_by(Show.start_time.desc()).all()
  for show in shows: 
    data.append({
      'venue_id': show.venue.id,
      'artist_id': show.artist.id,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      'venue_name': show.venue.name,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link 
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form)
  try: 
    show = Show(artist_id=form.artist_id.data,venue_id=form.venue_id.data,start_time=form.start_time.data)

    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except ValueError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Show ' + Show.name + ' could not be listed.')
  finally: 
   db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
