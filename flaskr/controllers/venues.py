import pytz
from datetime import datetime
from flask import abort, flash, json, redirect, render_template, request, url_for
from flaskr.db import db
from flaskr.app import app
from flaskr.models import Venue, Genre
from flaskr.forms import VenueForm

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
        flash('Venues could not be fetched at this time.')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view

#  Search
#  ----------------------------------------------------------------


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


#  Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        if not venue:
            abort(404, 'Venue does not exist')

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

        db.session.close()

        return render_template('pages/show_venue.html', venue=data)
    except Exception as e:
        db.session.close()
        print(f'Error fetching venue {venue_id}: {e}')
        err_message = getattr(
            e, 'message', 'Venue could not be fetched at this time')
        err_status = getattr(e, 'code', 500)
        flash(err_message)
        abort(err_status)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    view = ''
    try:
        all_genres = Genre.query.all()
        form = VenueForm()
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
        view = render_template('forms/new_venue.html', form=form)
    except Exception as e:
        print(f'Error creating venue form: {e}')
        view = render_template('errors/500.html')
    finally:
        db.session.close()
        return view


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


#  Update Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        all_genres = Genre.query.all()
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
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
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


#  Delete Venue
#  ----------------------------------------------------------------


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
