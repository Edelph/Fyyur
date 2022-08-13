#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import DateTime, func
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


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
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.JSON, nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_description = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    genres = db.Column(db.JSON, nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime, nullable=True)

    artist = db.relationship(Artist, backref="shows")
    venue = db.relationship(Venue, backref="shows")


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data0 = db.session.query(Venue.city, Venue.state).group_by(
        Venue.city, Venue.state).all()
    bigVenue = []
    for d in data0:
        venues = db.session.query(Venue.id, Venue.name).filter(
            Venue.city == d.city, Venue.state == d.state).all()
        venuesArray = []
        for v in venues:
            venue = {
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": 0,
            }
            venuesArray.append(venue)

        datatmp = {
            "city": d.city,
            "state": d.state,
            "venues": venuesArray
        }
        bigVenue.append(datatmp)
    return render_template('pages/venues.html', areas=bigVenue)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.

    search = request.form.get('search_term')
    dataBase = db.session.query(Venue.id, Venue.name).filter(
        Venue.name.like("%"+search.lower()+"%")).all()
    count = db.session.query(Venue.id).filter(
        Venue.name.like("%"+search.lower()+"%")).count()
    data = []
    for venue in dataBase:
        tmp = {
            "id": venue.id,
            "name": venue.name,
        }
        data.append(tmp)
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    upcoming_shows = []
    past_shows = []
    dataShowed = Show.query.filter(
        Show.start_time < datetime.date(datetime.now()), Show.venue_id == venue_id).all()
    dataShow = Show.query.filter(
        Show.start_time > datetime.date(datetime.now()), Show.venue_id == venue_id).all()

    for sd in dataShowed:
        tmp = {
            "artist_id": sd.artist_id,
            "artist_name": sd.artist.name,
            "artist_image_link": sd.artist.image_link,
            "start_time": sd.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        past_shows.append(tmp)

    for sd in dataShow:
        tmp = {
            "artist_id": sd.artist_id,
            "artist_name": sd.artist.name,
            "artist_image_link": sd.artist.image_link,
            "start_time": sd.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        upcoming_shows.append(tmp)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [] if venue.genres == None else venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

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
    form = VenueForm(request.form)
    print(form.genres.data)
    isAdded = False
    if form.validate():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                genres=form.genres.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )

            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
            isAdded = True
        except:
            db.session.rollback()
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('Venue ' + request.form['name'] + ' was not valid listed!')

    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    if isAdded:
        return render_template('pages/home.html')
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    isDeleted = True
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        isDeleted = False
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    dataBase = db.session.query(Artist.id, Artist.name).all()
    data = []
    for artist in dataBase:
        tmp = {
            "id": artist.id,
            "name": artist.name,
        }
        data.append(tmp)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search = request.form.get('search_term')
    dataBase = db.session.query(Artist.id, Artist.name).filter(
        Artist.name.like("%"+search.lower()+"%")).all()
    count = db.session.query(Artist.id).filter(
        Artist.name.like("%"+search.lower()+"%")).count()

    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    data = []
    for artist in dataBase:
        tmp = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": 0,
        }
        data.append(tmp)
    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    upcoming_shows = []
    past_shows = []
    dataShowed = Show.query.filter(
        Show.start_time < datetime.date(datetime.now()), Show.artist.id == artist_id).all()
    dataShow = Show.query.filter(
        Show.start_time > datetime.date(datetime.now()), Show.artist.id == artist_id).all()

    for sd in dataShowed:
        tmp = {
            "venue_id": sd.venue_id,
            "venue_name": sd.venue.name,
            "venue_image_link": sd.venue.image_link,
            "start_time": sd.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        past_shows.append(tmp)

    for sd in dataShow:
        tmp = {
            "venue_id": sd.venue_id,
            "venue_name": sd.venue.name,
            "venue_image_link": sd.venue.image_link,
            "start_time": sd.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        upcoming_shows.append(tmp)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": [] if artist.genres == None else artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        image_link=artist.image_link,
        genres=[] if artist.genres == None else artist.genres,
        website_link=artist.website_link,
        facebook_link=artist.facebook_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description,
    )
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    isEdited = False
    # TODO: take values from the form submitted, and update existing
    newArtist = ArtistForm(request.form)
    if newArtist.validate():
        artist = Artist.query.get(artist_id)

        artist.name = newArtist.name.data
        artist.city = newArtist.city.data
        artist.state = newArtist.state.data
        artist.phone = newArtist.phone.data
        artist.image_link = newArtist.image_link.data
        artist.genres = newArtist.genres.data
        artist.facebook_link = newArtist.facebook_link.data
        artist.website_link = newArtist.website_link.data
        artist.seeking_venue = newArtist.seeking_venue.data
        artist.seeking_description = newArtist.seeking_description.data
        try:
            db.session.commit()
            isEdited = True
            flash('Artist ' + request.form['name'] +
                  ' was edited successfully !')
        except:
            db.session.rollback()
            flash('Artist ' + request.form['name'] + ' was not edited listed!')
        finally:
            db.session.close()

    else:
        flash('Artist ' + request.form['name'] + ' was not valid listed!')

    # venue record with ID <venue_id> using the new attributes
    if isEdited:
        return redirect(url_for('show_artist', artist_id=artist_id))

    return redirect(url_for("edit_artist", artist_id=artist_id))

    # artist record with ID <artist_id> using the new attributes


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(
        name=venue.name,
        city=venue.city,
        state=venue.state,
        address=venue.address,
        phone=venue.phone,
        image_link=venue.image_link,
        facebook_link=venue.facebook_link,
        genres=[] if venue.genres == None else venue.genres,
        website_link=venue.website_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description
    )
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    isEdited = False
    # TODO: take values from the form submitted, and update existing
    newVenue = VenueForm(request.form)
    print(newVenue.genres.data)
    if newVenue.validate():
        venue = Venue.query.get(venue_id)

        venue.name = newVenue.name.data
        venue.genres = newVenue.genres.data
        venue.address = newVenue.address.data
        venue.city = newVenue.city.data
        venue.state = newVenue.state.data
        venue.phone = newVenue.phone.data
        venue.website_link = newVenue.website_link.data
        venue.facebook_link = newVenue.facebook_link.data
        venue.seeking_talent = newVenue.seeking_talent.data
        venue.seeking_description = newVenue.seeking_description.data
        venue.image_link = newVenue.image_link.data
        try:
            db.session.commit()
            isEdited = True
            flash('Venue ' + request.form['name'] +
                  ' was edited successfully !')
        except:
            db.session.rollback()
            flash('Venue ' + request.form['name'] + ' was not edited listed!')
        finally:
            db.session.close()

    else:
        flash('Venue ' + request.form['name'] + ' was not valid listed!')

    # venue record with ID <venue_id> using the new attributes
    if isEdited:
        return redirect(url_for('show_venue', venue_id=venue_id))

    return redirect(url_for("edit_venue", venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm(request.form)
    isValid = False

    # TODO: insert form data as a new Venue record in the db, instead
    if form.validate():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
            isValid = True
        except:
            db.session.rollback()
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('Artist ' + request.form['name'] + ' ! was not valid !')
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    if isValid:
        return render_template('pages/home.html')
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    dataBase = Show.query.all()
    data = []
    for d in dataBase:
        tmp = {
            "venue_id": d.venue_id,
            "venue_name": d.venue.name,
            "artist_id": d.artist_id,
            "artist_name": d.artist.name,
            "artist_image_link": d.artist.image_link,
            "start_time": d.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        data.append(tmp)
    # TODO: replace with real venues data.
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm(request.form)
    isAdded = False
    if form.validate():
        try:
            venue = Venue.query.get(form.venue_id.data)
            artist = Artist.query.get(form.artist_id.data)
            show = Show(start_time=form.start_time.data)
            show.venue = venue
            show.artist = artist

            db.session.add(show)
            db.session.commit()
            isAdded = True
            flash('Show was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    else:
        flash('Venue not valid!!.')
        # TODO: insert form data as a new Show record in the db, instead

        # on successful db insert, flash success
        # flash('Show was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    if isAdded:
        return render_template('pages/home.html')
    return


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)
