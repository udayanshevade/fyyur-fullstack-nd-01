import pytz
from datetime import datetime
from flask import abort, flash, json, redirect, render_template, request, url_for
from flaskr.app import app
from flaskr.db import db
from flaskr.models import Artist, Genre, Show, Venue
from flaskr.forms import ArtistForm

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists', methods={'GET'})
def artists():
    try:
        artists = Artist.query.all()
        return render_template('pages/artists.html', artists=artists)
    except Exception as e:
        print(f'Error - [GET] /artists - {e}')
        flash('Artists could not be fetched right now. Refresh or try again later.')
        abort(500)
    finally:
        db.session.close()


#  Search
#  ----------------------------------------------------------------


@app.route('/artists/search', methods=['POST'])
def search_artists():
    try:
        search_term = request.form.get('search_term', '')
        data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
        response = {
            "count": data.count(),
            "data": data.all()
        }
        return render_template('pages/search_artists.html',
                               results=response, search_term=search_term)
    except Exception as e:
        print(f'Error - [POST] /artists/search - {e}')
        flash('Artists could not be searched at this time. Refresh or try again later.')
        abort(500)
    finally:
        db.session.close()


#  Artist
#  ----------------------------------------------------------------

def select_show_details_for_artist(show):
    venue = show.venue
    return {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.start_time,
    }


@app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        if not artist:
            abort(404, 'Artist does not exist')

        now = datetime.now(pytz.utc)

        past_shows = [select_show_details_for_artist(
            show) for show in artist.shows if show.end_time <= now]
        upcoming_shows = [select_show_details_for_artist(
            show) for show in artist.shows if show.start_time >= now]

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
        return render_template('pages/show_artist.html', artist=data)
    except Exception as e:
        print(f'Error - [GET] - /artists/{artist_id} - {e}')
        err_message = getattr(
            e, 'message', 'Artist could not be fetched at this time')
        err_status = getattr(e, 'code', 500)
        flash(err_message)
        abort(err_status)
    finally:
        db.session.close()


#  Update Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        all_genres = Genre.query.all()
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
        # dynamically populate genre choices
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
        return render_template('forms/edit_artist.html',
                               form=form, artist=artist)
    except Exception as e:
        print(f'Error - [GET] /artists/{artist_id}/edit - {e}')
        flash('Error getting artist to edit. Refresh or try again later.')
        return redirect(url_for('show_artist', artist_id=artist_id))
    finally:
        db.session.close()


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.get(artist_id)

        if not artist:
            abort(404, 'Artist does not exist')

        form_data = request.form

        artist.name = form_data.get('name')
        artist.facebook_link = form_data.get('facebook_link')
        artist.image_link = form_data.get('image_link')
        artist.genres = [Genre.query.get(id)
                         for id in form_data.getlist('genres')]
        artist.city = form_data.get('city')
        artist.state = form_data.get('state')
        artist.phone = form_data.get('phone')
        artist.seeking_venue = form_data.get('seeking_venue') == 'y'
        artist.seeking_description = form_data.get('seeking_description')
        artist.website = form_data.get('website')

        # validate the form inputs
        form = ArtistForm(data=form_data)
        all_genres = Genre.query.all()
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
        if form.validate_on_submit():
            db.session.commit()
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            print(form.errors)
            db.session.rollback()
            flash(f'Invalid artist details. Fix errors before resubmitting.')
            return render_template('forms/edit_artist.html', form=form, artist=artist)
    except Exception as e:
        db.session.rollback()
        print(f'Error - [POST] /artists/{artist_id}/edit - {e}')
        err_message = getattr(
            e, 'message', 'Could not edit artist at this time. Try again later.')
        err_status = getattr(e, 'code', 500)
        flash(err_message)
        abort(err_status)
    finally:
        db.session.close()


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    try:
        genres = [(genre.id, genre.name) for genre in Genre.query.all()]
        form = ArtistForm()
        form.genres.choices = genres
        return render_template('forms/new_artist.html', form=form)
    except Exception as e:
        print(f'Error - [GET] /artists/create - {e}')
        abort(500)
    finally:
        db.session.close()


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

        # validate the form inputs
        form = ArtistForm(data=artist_data)
        form.genres.choices = [(genre.id, genre.name)
                               for genre in Genre.query.all()]
        if form.validate_on_submit():
            db.session.add(artist)
            db.session.commit()
            flash(f'Artist {artist.name} was successfully listed!')
            return render_template('pages/home.html')
        else:
            db.session.rollback()
            flash(f'Invalid artist details. Fix errors before resubmitting.')
            return render_template('forms/new_artist.html', form=form)
    except Exception as e:
        db.session.rollback()
        print(f'Error - [POST] /artists/create - {e}')
        artist_name = artist_data.get('name')
        print(f'Artist {artist_name}: {e}')
        flash(f'Artist {artist_name} could not be created.')
        abort(500)
    finally:
        db.session.close()


#  Delete Artist
#  ----------------------------------------------------------------


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    success = False
    status = 500
    try:
        artist = Artist.query.get(artist_id)
        if not artist:
            abort(404, 'Artist does not exist')
        db.session.delete(artist)
        db.session.commit()
        success = True
        status = 200
    except Exception as e:
        db.session.rollback()
        print(f'Error - [DELETE] /artist/{artist_id} - {e}')
    finally:
        db.session.close()
        return json.dumps(success), status
