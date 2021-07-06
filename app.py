#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import date, datetime
import pytz
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
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

venue_genres = db.Table('venue_genres',
                        db.Column('venue_id', db.Integer, db.ForeignKey(
                            'Venue.id'), nullable=False),
                        db.Column('genre_id', db.Integer, db.ForeignKey(
                            'Genre.id'), nullable=False)
                        )

artist_genres = db.Table('artist_genres',
                         db.Column('artist_id', db.Integer, db.ForeignKey(
                             'Artist.id'), nullable=False),
                         db.Column('genre_id', db.Integer, db.ForeignKey(
                             'Genre.id'), nullable=False)
                         )


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

    seeking_description = db.Column(db.String, nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(500), nullable=True)

    shows = db.relationship('Show', backref='venue')
    genres = db.relationship(
        'Genre', secondary=venue_genres, backref=db.backref('venue'))

    def __repr__(self) -> str:
        return f'<Venue id: {self.id}, name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))

    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    seeking_description = db.Column(db.String, nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(500), nullable=True)

    shows = db.relationship('Show', backref='artist')
    genres = db.relationship(
        'Genre', secondary=artist_genres, backref=db.backref('artist'))

    def __repr__(self) -> str:
        return f'<Artist id: {self.id}, name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    end_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    start_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f'<Show id: {self.id}>'


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self) -> str:
        return f'<Genre id: {self.id}, name: {self.name}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = value if type(
        value) is datetime else dateutil.parser.parse(value)
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
    view = ''

    try:
        all_venues = Venue.query.all()
        places = {}
        now = datetime.now(pytz.utc)
        for venue in all_venues:
            upcoming_shows = [
                show for show in venue.shows if show.start_time >= now]
            num_upcoming_shows = len(upcoming_shows)
            new_venue_data = {
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': num_upcoming_shows
            }
            if places.get(f'{venue.state}{venue.city}', None):
                places[f'{venue.state}{venue.city}']['venues'].append(
                    new_venue_data)
            else:
                places[f'{venue.state}{venue.city}'] = {
                    'city': venue.city,
                    'state': venue.state,
                    'venues': [new_venue_data]
                }
        data = places.values()
        view = render_template('pages/venues.html', areas=data)
    except Exception as e:
        print(f'Error fetching venues: {e}')
        flash('Venues could not be listed at this time. Refresh or try again later.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view


@app.route('/venues/search', methods=['POST'])
def search_venues():
    view = ''
    try:
        search_term = request.form.get('search_term', '')
        data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
        response = {
            "count": data.count(),
            "data": data.all()
        }
        view = render_template('pages/search_venues.html',
                               results=response, search_term=search_term)
    except Exception as e:
        print(f'Error searching venues for {search_term}: {e}')
        flash('Venues could not be searched at this time. Refresh or try again later.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view


def select_venue_show_details(show):
    '''Helper to select pertinent fields from Show object'''
    artist = show.artist
    return {
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time,
    }


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    view = ''
    try:
        venue = Venue.query.get(venue_id)
        shows = venue.shows
        now = datetime.now(pytz.utc)
        past_shows = [select_venue_show_details(show)
                      for show in shows if show.end_time <= now]
        upcoming_shows = [select_venue_show_details(
            show) for show in shows if show.start_time >= now]
        data = {
            'id': venue.id,
            'name': venue.name,
            'genres': [x.name for x in venue.genres],
            'address': venue.address,
            'city': venue.city,
            'state': venue.state,
            'phone': venue.phone,
            'website': venue.website,
            'facebook_link': venue.facebook_link,
            'seeking_talent': venue.seeking_talent,
            'seeking_description': venue.seeking_description,
            'image_link': venue.image_link,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows),
        }

        view = render_template('pages/show_venue.html', venue=data)
    except Exception as e:
        print(f'Error fetching venue {venue_id}: {e}')
        flash('Venue could not be fetched at this time. Refresh or try again later.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    page = None
    try:
        venue_data = request.form
        venue = Venue(
            name=venue_data.get('name'),
            city=venue_data.get('city'),
            state=venue_data.get('state'),
            address=venue_data.get('address'),
            phone=venue_data.get('phone'),
            facebook_link=venue_data.get('facebook_link', None),
            image_link=venue_data.get('image_link', None),
            seeking_talent=venue_data.get('seeking_talent', False),
            seeking_description=venue_data.get(
                'seeking_description', None),
            website=venue_data.get('website', None),
        )

        venue_genre_data = venue_data.getlist('genres')
        genres = [Genre.query.get(id) for id in venue_genre_data]
        venue.genres = genres

        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        page = render_template('pages/home.html')
    except Exception as e:
        print(f'Error creating venue: {e}')
        flash('Venue ' + request.form['name'] + ' could not be created.')
        db.session.rollback()
    finally:
        db.session.close()
        return page


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    page = ''
    try:
        Venue.query.get(venue_id).delete()
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully deleted!')
        page = redirect(url_for('index'))
    except Exception as e:
        print(f'Error deleting venue: {e}')
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' could not be deleted.')
        page = redirect(url_for('show_venue', venue_id=venue_id))
    finally:
        db.session.close()
        return page

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    view = ''
    try:
        data = Artist.query.all()
        view = render_template('pages/artists.html', artists=data)
    except Exception as e:
        print(f'Error fetching artists: {e}')
        flash('Artists could not be fetched right now. Refresh or try again later.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view


@app.route('/artists/search', methods=['POST'])
def search_artists():
    view = ''
    try:
        search_term = request.form.get('search_term', '')
        data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
        response = {
            "count": data.count(),
            "data": data.all()
        }
        view = render_template('pages/search_artists.html',
                               results=response, search_term=search_term)
    except Exception as e:
        print(f'Error fetching artists: {e}')
        flash('Artists could not be searched right now. Try again later.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view


def select_artist_show_details(show):
    '''Helper to select pertinent fields from Show object'''
    venue = show.venue
    return {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.start_time,
    }


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    view = ''
    try:
        artist = Artist.query.get(artist_id)
        shows = artist.shows
        now = datetime.now(pytz.utc)
        past_shows = [select_artist_show_details(show)
                      for show in shows if show.end_time <= now]
        upcoming_shows = [select_artist_show_details(
            show) for show in shows if show.start_time >= now]
        data = {
            'id': artist.id,
            'name': artist.name,
            'genres': [genre.name for genre in artist.genres],
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'website': artist.website,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'image_link': artist.image_link,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows),
        }
        view = render_template('pages/show_artist.html', artist=data)
    except Exception as e:
        print(f'Error fetching artist: {e}')
        flash('Artist could not be fetched right now. Try again later.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
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

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
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

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
