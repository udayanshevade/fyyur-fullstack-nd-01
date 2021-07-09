import pytz
from datetime import datetime
from flask import abort, flash, json, redirect, render_template, request, url_for
from flaskr.db import db
from flaskr.app import app
from flaskr.models import Venue, Genre, Show, Artist
from flaskr.forms import VenueForm

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues', methods=['GET'])
def venues():
    try:
        all_venues = Venue.query.all()
        places = {}
        now = datetime.now(pytz.utc)

        # massage data for expected format
        for venue in all_venues:
            num_upcoming_shows = len([
                show for show in venue.shows if show.start_time >= now])
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
        return render_template('pages/venues.html', areas=data)
    except Exception as e:
        print(f'Error - [GET] /venues - {e}')
        flash('Venues could not be fetched at this time.')
        abort(500)
    finally:
        db.session.close()

#  Search
#  ----------------------------------------------------------------


@app.route('/venues/search', methods=['POST'])
def search_venues():
    try:
        search_term = request.form.get('search_term', '')
        data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
        response = {
            "count": data.count(),
            "data": data.all()
        }
        return render_template('pages/search_venues.html',
                               results=response, search_term=search_term)
    except Exception as e:
        print(f'Error - [POST] /venues/search - {e}')
        flash('Venues could not be searched at this time. Refresh or try again later.')
        abort(500)
    finally:
        db.session.close()


def select_show_details_for_venue(show):
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

        now = datetime.now(pytz.utc)

        past_shows = [select_show_details_for_venue(
            show) for show in venue.shows if show.end_time <= now]
        upcoming_shows = [select_show_details_for_venue(
            show) for show in venue.shows if show.start_time >= now]
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

        return render_template('pages/show_venue.html', venue=data)
    except Exception as e:
        print(f'Error - [GET] venues/{venue_id} - {e}')
        err_message = getattr(
            e, 'message', 'Venue could not be fetched at this time')
        err_status = getattr(e, 'code', 500)
        flash(err_message)
        abort(err_status)
    finally:
        db.session.close()


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    view = ''
    try:
        all_genres = Genre.query.all()
        form = VenueForm()
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
        return render_template('forms/new_venue.html', form=form)
    except Exception as e:
        print(f'Error - [GET] venues/create - {e}')
        abort(500)
    finally:
        db.session.close()


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
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

        # validate form inputs
        form = VenueForm(data=venue_data)
        form.genres.choices = [(genre.id, genre.name)
                               for genre in Genre.query.all()]
        if form.validate_on_submit():
            db.session.add(venue)
            db.session.commit()
            flash(f'Venue {venue.name} was successfully listed!')
            return render_template('pages/home.html')
        else:
            db.session.rollback()
            flash(f'Invalid venue details. Fix errors before resubmitting.')
            return render_template('forms/new_venue.html', form=form)
    except Exception as e:
        db.session.rollback()
        venue_name = venue_data.get('name')
        print(f'Error - [POST] venues/create - {e}')
        flash(f'Venue {venue_name} could not be created.')
        abort(500)
    finally:
        db.session.close()


#  Update Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        data = Venue.query.get(venue_id)
        if not data:
            abort(404, 'Venue does not exist')

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
        all_genres = Genre.query.all()
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    except Exception as e:
        db.session.rollback()
        print(f'Error - [GET] venues/{venue_id}/edit - {e}')
        err_message = getattr(
            e, 'message', 'Venue could not be fetched at this time')
        err_status = getattr(e, 'code', 500)
        flash(err_message)
        abort(err_status)
    finally:
        db.session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get(venue_id)

        if not venue:
            abort(404, 'Venue does not exist')

        form_data = request.form

        venue.name = form_data.get('name')
        venue.facebook_link = form_data.get('facebook_link')
        venue.image_link = form_data.get('image_link')
        venue.genres = [Genre.query.get(id)
                        for id in form_data.getlist('genres')]
        venue.city = form_data.get('city')
        venue.state = form_data.get('state')
        venue.phone = form_data.get('phone')
        venue.seeking_talent = form_data.get('seeking_venue') == 'y'
        venue.seeking_description = form_data.get('seeking_description')
        venue.website = form_data.get('website')

        # validate form inputs
        form = VenueForm(data=form_data)
        all_genres = Genre.query.all()
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
        if form.validate_on_submit():
            db.session.commit()
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            print(form.errors)
            db.session.rollback()
            flash(f'Invalid venue details. Fix errors before resubmitting.')
            return render_template('forms/edit_venue.html', form=form, venue=venue)
    except Exception as e:
        db.session.rollback()
        print(f'Error - [POST] venues/{venue_id}/edit - {e}')
        err_message = getattr(
            e, 'message', 'Could not edit venue at this time. Try again later.')
        err_status = getattr(e, 'code', 500)
        flash(err_message)
        abort(err_status)
    finally:
        db.session.close()


#  Delete Venue
#  ----------------------------------------------------------------


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    success = False
    status = 500
    try:
        venue = Venue.query.get(venue_id)
        if not venue:
            abort(404, 'Venue does not exist')
        db.session.delete(venue)
        db.session.commit()
        success = True
        status = 200
    except Exception as e:
        db.session.rollback()
        print(f'Error - [DELETE] venues/{venue_id} - {e}')
    finally:
        db.session.close()
        return json.dumps(success), status
