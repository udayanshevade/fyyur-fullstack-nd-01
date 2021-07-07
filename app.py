#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import date, datetime
import pytz
import babel
from flask import Flask, render_template, request, json, flash, redirect, url_for
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

@app.route('/venues', methods=['GET'])
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


@app.route('/venues/<int:venue_id>', methods=['GET'])
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
            seeking_talent=venue_data.get('seeking_talent', False) == 'y',
            seeking_description=venue_data.get(
                'seeking_description', None),
            website=venue_data.get('website', None),
        )

        venue_genre_data = venue_data.getlist('genres')
        genres = [Genre.query.get(id) for id in venue_genre_data]
        venue.genres = genres

        db.session.add(venue)
        db.session.commit()
        flash(f'Venue {venue.name} was successfully listed!')
        page = render_template('pages/home.html')
    except Exception as e:
        print(f'Error creating venue: {e}')
        venue_name = venue_data.get('name')
        flash(f'Venue {venue_name} could not be created.')
        db.session.rollback()
    finally:
        db.session.close()
        return page


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    success = False
    status = 500
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        success = True
        status = 200
    except Exception as e:
        db.session.rollback()
        print(f'Error deleting venue: {e}')
    finally:
        db.session.close()
        return json.dumps(success), status

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists', methods={'GET'})
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


@app.route('/artists/<int:artist_id>', methods=['GET'])
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
    view = ''
    try:
        data = Artist.query.get(artist_id)
        artist = {
            'id': data.id,
            'name': data.name,
            'facebook_link': data.facebook_link,
            'image_link': data.image_link,
            'genres': [genre.id for genre in data.genres],
            'city': data.city,
            'state': data.state,
            'phone': data.phone,
            'seeking_venue': data.seeking_venue,
            'seeking_description': data.seeking_description,
            'website': data.website,
        }

        # prepopulate form with existing values from artist data
        form = ArtistForm(data=artist)
        view = render_template('forms/edit_artist.html',
                               form=form, artist=artist)
    except Exception as e:
        print(f'Error getting artist {artist_id} to edit: {e}')
        flash('Error getting artist to edit. Refresh or try again later.')
        view = redirect(url_for('show_artist', artist_id=artist_id))
    finally:
        db.session.close()
        return view


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.facebook_link = request.form.get('facebook_link')
        artist.image_link = request.form.get('image_link')
        artist.genres = [Genre.query.get(id)
                         for id in request.form.getlist('genres')]
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.seeking_venue = request.form.get('seeking_venue') == 'y'
        artist.seeking_description = request.form.get('seeking_description')
        artist.website = request.form.get('website')
        db.session.commit()
    except Exception as e:
        print(f'Error editing artist {artist_id}: {e}')
        flash('Could not edit artist. Please try again later.')
        db.session.rollback()
    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        data = Venue.query.get(venue_id)
        venue = {
            'id': data.id,
            'name': data.name,
            'facebook_link': data.facebook_link,
            'image_link': data.image_link,
            'genres': [genre.id for genre in data.genres],
            'address': data.address,
            'city': data.city,
            'state': data.state,
            'phone': data.phone,
            'seeking_talent': data.seeking_talent,
            'seeking_description': data.seeking_description,
            'website': data.website,
        }

        # prepopulate form with existing values from artist data
        form = VenueForm(data=venue)
        view = render_template('forms/edit_venue.html', form=form, venue=venue)
    except Exception as e:
        print(f'Error editing venue: {e}')
        flash('Could not edit venue. Please try again later.')
        db.session.rollback()
    finally:
        db.session.close()
        return view


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.genres = [Genre.query.get(id)
                        for id in request.form.getlist('genres')]
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.phone = request.form.get('phone')
        venue.seeking_talent = request.form.get('seeking_venue') == 'y'
        venue.seeking_description = request.form.get('seeking_description')
        venue.website = request.form.get('website')
        db.session.commit()
    except Exception as e:
        print(f'Error editing venue: {e}')
        flash('Could not edit venue. Please try again later.')
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
    try:
        artist_data = request.form
        artist = Artist(
            name=artist_data.get('name'),
            facebook_link=artist_data.get('facebook_link'),
            image_link=artist_data.get('image_link'),
            city=artist_data.get('city'),
            state=artist_data.get('state'),
            phone=artist_data.get('phone'),
            seeking_venue=artist_data.get('seeking_venue') == 'y',
            seeking_description=artist_data.get('seeking_description'),
            website=artist_data.get('website'),
        )
        artist.genres = [Genre.query.get(id)
                         for id in request.form.getlist('genres')]
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash(f'Artist {artist.name} was successfully listed!')
        view = render_template('pages/home.html')
    except Exception as e:
        print(f'Error creating an artist: {e}')
        flash('An error occurred. Artist could not be listed.')
        view = redirect(url_for('create_artist_form'))
        db.session.rollback()
    finally:
        db.session.close()
        return view


#  Shows
#  ----------------------------------------------------------------

def select_show_details(show):
    '''Helper to select show details'''
    venue = show.venue
    artist = show.artist
    return {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time,
        'end_time': show.end_time,
    }


@app.route('/shows', methods=['GET'])
def shows():
    view = ''
    try:
        shows = Show.query.all()
        data = [select_show_details(show) for show in shows]
        view = render_template('pages/shows.html', shows=data)
    except Exception as e:
        print(f'Error fetching shows: {e}')
        flash('Shows could not be fetched at this time. Refresh or try again later.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view


@app.route('/shows/create', methods=['GET'])
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show(
            artist_id=request.form.get('artist_id'),
            venue_id=request.form.get('venue_id'),
            start_time=request.form.get('start_time'),
            end_time=request.form.get('end_time'),
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        view = render_template('pages/home.html')
    except Exception as e:
        print(f'Error creating a show: {e}')
        flash('An error occurred. Show could not be listed.')
        view = redirect(url_for('create_shows'))
        db.session.rollback()
    finally:
        db.session.close()
        return view


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
