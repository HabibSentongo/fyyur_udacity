#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data = []
  # fetch all venues grouped by their city and state
  db_venues = Venue.query.distinct(Venue.city, Venue.state).all()

  # structure all cities with their states
  for venue in db_venues:
    city = {}
    city["city"] = venue.city
    city["state"] = venue.state
    data.append(city)

  # add vevues list in each city dict
  for city in data:
    city_venues = Venue.query.filter_by(city=city["city"], state=city["state"]).all()
    city["venues"] = [venue for venue in city_venues]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  key = request.form.get('search_term', '')
  matches = Venue.query.order_by(Venue.id).filter(Venue.name.ilike(f'%{key}%'))
  data = [{'name': venue.name, 'id': venue.id} for venue in matches]
  
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', matches=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = {}
  past_shows = []
  upcoming_shows = []

  # fetch all fields of specified venue
  db_venue = Venue.query.get(venue_id)

  past_shows.append(db.session.query(Show).filter_by(venue_id=db_venue.id).filter(Show.start_time < datetime.utcnow().isoformat()).all())
  upcoming_shows.append(db.session.query(Show).filter_by(venue_id=db_venue.id).filter(Show.start_time > datetime.utcnow().isoformat()).all())
  
  data_past = []
  data_upcoming = []

  for shows in upcoming_shows:
    for a_show in shows:
      show_detail = {}
      show_detail["artist_id"] = a_show.Artist.id
      show_detail["artist_name"] = a_show.Artist.id
      show_detail["artist_image_link"] = a_show.Artist.image_link
      show_detail["start_time"] = a_show.start_time.strftime(("%m/%d/%Y, %H:%M:%S"))
      data_upcoming.append(show_detail)

  for shows in past_shows:
    for a_show in shows:
      show_detail = {}
      show_detail["artist_id"] = a_show.Artist.id
      show_detail["artist_name"] = a_show.Artist.id
      show_detail["artist_image_link"] = a_show.Artist.image_link
      show_detail["start_time"] = a_show.start_time.strftime(str("%m/%d/%Y, %H:%M:%S"))
      data_past.append(show_detail)

  data["id"] = db_venue.id
  data["name"] = db_venue.name
  data["genres"] = db_venue.genres
  data["city"] = db_venue.city
  data["state"] = db_venue.state
  data["phone"] = db_venue.phone
  data["website"] = db_venue.website
  data["facebook_link"] = db_venue.facebook_link
  data["seeking_talent"] = db_venue.seek_status
  data["seeking_description"] = db_venue.seek_body
  data["artist_image_link"] = db_venue.image_link
  data["past_shows_count"] = len(past_shows[0])
  data["past_shows"] = data_past
  data["upcoming_shows_count"] = len(upcoming_shows[0])
  data["upcoming_shows"] = data_upcoming
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm

  data = Venue(
    name=request.form.get("name"),
    genres=request.form.get("genres"),
    city=request.form.get("city"),
    state=request.form.get("state"),
    phone=request.form.get("phone"),
    website=request.form.get("website"),
    image_link=request.form.get("image_link"),
    facebook_link=request.form.get("facebook_link"),
    seek_status=request.form.get("seeking_talent"),
    seek_body=request.form.get("seeking_description")
  )

  try:
    db.session.add(data)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # on unsuccessful db insert, flash error
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.close()
    flash('Venue ' + venue.name + ' has been deleted.')
  except:
    flash('Oops, something went wrong! Venue not deleted.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  key = request.form.get('search_term', '')
  matches = Artist.query.order_by(Artist.id).filter(Artist.name.ilike(f'%{key}%'))
  data = [{'name': artist.name, 'id': artist.id} for artist in matches]
  response={
    "count": len(matches),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  data = {}
  db_artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  past_shows.append(db.session.query(Show).filter_by(artist_id=db_artist.id).filter(Show.start_time < datetime.utcnow().isoformat()).all())
  upcoming_shows.append(db.session.query(Show).filter_by(artist_id=db_artist.id).filter(Show.start_time > datetime.utcnow().isoformat()).all())
  
  data_past = []
  data_upcoming = []

  for shows in past_shows:
    for a_show in shows:
      show_detail = {}
      show_detail["venue_id"] = a_show.Venue.id
      show_detail["venue_name"] = a_show.Venue.id
      show_detail["venue_image_link"] = a_show.Venue.image_link
      show_detail["start_time"] = a_show.start_time.strftime(("%m/%d/%Y, %H:%M:%S"))
      data_past.append(show_detail)

  for shows in upcoming_shows:
    for a_show in shows:
      show_detail = {}
      show_detail["venue_id"] = a_show.Venue.id
      show_detail["venue_name"] = a_show.Venue.id
      show_detail["venue_image_link"] = a_show.Venue.image_link
      show_detail["start_time"] = a_show.start_time.strftime(("%m/%d/%Y, %H:%M:%S"))
      data_upcoming.append(show_detail)

  data["id"] = db_artist.id
  data["artist_name"] = db_artist.name
  data["genres"] = db_artist.genres
  data["city"] = db_artist.city
  data["state"] = db_artist.state
  data["phone"] = db_artist.phone
  data["website"] = db_artist.website
  data["facebook_link"] = db_artist.facebook_link
  data["seeking_venue"] = db_artist.seek_status
  data["seeking_description"] = db_artist.seek_body
  data["artist_image_link"] = db_artist.image_link
  data["past_shows"] = db_artist.data_past
  data["past_shows_count"] = len(past_shows[0])
  data["upcoming_shows"] = db_artist.data_upcoming
  data["upcoming_shows_count"] = len(upcoming_shows[0])
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id).__dict__
  form.name.default = artist["name"]
  form.genres.default = artist["genres"]
  form.city.default = artist["city"]
  form.state.default = artist["state"]
  form.phone.default = artist["phone"]
  form.website.default = artist["website"]
  form.image_link.default = artist["image_link"]
  form.facebook_link.default = artist["facebook_link"]
  form.seeking_venue.default = artist["seek_status"]
  form.seeking_description.default = artist["seek_body"]
  form.process()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  try:
    db_artist = Artist.query.get(artist_id)
    db_artist.name = form.name.data
    db_artist.city = form.city.data
    db_artist.state = form.state.data
    db_artist.phone = form.phone.data
    db_artist.genres = form.genres.data
    db_artist.facebook_link = form.facebook_link.data
    db_artist.website = form.website.data
    db_artist.image_link = form.image_link.data
    db_artist.seek_status = form.seeking_venue.data
    db_artist.seek_body = form.seeking_description.data
    
    db.session.commit()
    flash('Artist ' + form.name.data + ' has been updated.')
  except:
    flash('An error occurred. Artist could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id).__dict__
  form.name.default = venue["name"]
  form.genres.default = venue["genres"]
  form.city.default = venue["city"]
  form.state.default = venue["state"]
  form.phone.default = venue["phone"]
  form.webiste.default = venue["website"]
  form.image_link.default = venue["image_link"]
  form.seeking_talent.default = venue["seek_status"]
  form.seeking_description.default = venue["seek_body"]
  form.facebook_link.default = venue["facebook_link"]
  form.process()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)

  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seek_status = form.seeking_talent.data
    venue.seek_body = form.seeking_description.data

    db.session.commit()
    flash('Venue ' + form.name.data + ' has been updated.')
  except:
    flash('An error occurred. Venue could not be updated.')
    db.session.rollback()
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
  form = ArtistForm()

  data = Artist(
    name = request.form.get("name"),
    genres = request.form.get("city"),
    city = request.form.get("city"),
    state = request.form.get("state"),
    phone = request.form.get("phone"),
    website = request.form.get("website"),
    image_link = request.form.get("image_link"),
    facebook_link = request.form.get("facebook_link"),
    seek_status = request.form.get("seeking_venue"),
    seek_body = request.form.get("seeking_description")
  )

  try:
    db.session.add(data)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  db_shows = db.session.query(Show).join(Venue, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).all()

  for a_show in db_shows:
    show_detail = {}
    show_detail["venue_id"] = a_show.venue.id
    show_detail["venue_name"] = a_show.venue.name
    show_detail["artist_id"] = a_show.artist.id
    show_detail["artist_name"] = a_show.artist.name
    show_detail["artist_image_link"] = a_show.artist.image_link
    show_detail["start_time"] = a_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    data.append(a_show)
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  venue_id = db.session.query(Venue).filter_by(id = request.form.get("venue_id")).first()
  artist_id = db.session.query(Artist).filter_by(id = request.form.get("artist_id")).first()
  if (not venue_id) or (not artist_id):
    flash('Venue or Artist does not exist')
  
  data = Show(
    venue_id = request.form.get("venue_id"),
    artist_id = request.form.get("artist_id"),
    start_time = request.form.get("start_time")
  )

  try:
    db.session.add(data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
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
