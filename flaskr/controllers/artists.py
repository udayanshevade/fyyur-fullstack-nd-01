import pytz
from datetime import datetime
from flask import abort, flash, json, redirect, render_template, request, url_for
from flaskr.app import app
from flaskr.db import db
from flaskr.models import Artist, Genre
from flaskr.forms import ArtistForm

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists', methods={'GET'})
def artists():
    try:
        artists = Artist.query.all()
        return render_template('pages/artists.html', artists=artists)
    except Exception as e:
        print(f'Error fetching artists: {e}')
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
        print(f'Error fetching artists: {e}')
        flash('Artists could not be searched at this time. Refresh or try again later.')
        abort(500)
    finally:
        db.session.close()


def select_artist_show_details(show):
    '''Helper to select pertinent fields from Show object'''
    venue = show.venue
    return {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.start_time,
    }


#  Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        if not artist:
            abort(404, 'Artist does not exist')

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
        return render_template('pages/show_artist.html', artist=data)
    except Exception as e:
        print(f'Error fetching artist {artist_id}: {e}')
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
        form.genres.choices = [(genre.id, genre.name) for genre in all_genres]
        return render_template('forms/edit_artist.html',
                               form=form, artist=artist)
    except Exception as e:
        print(f'Error getting artist {artist_id} to edit: {e}')
        flash('Error getting artist to edit. Refresh or try again later.')
        return redirect(url_for('show_artist', artist_id=artist_id))
    finally:
        db.session.close()


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
        return redirect(url_for('show_artist', artist_id=artist_id))
    except Exception as e:
        db.session.rollback()
        err_message = getattr(
            e, 'message', 'Could not edit venue at this time. Try again later.')
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
        print(f'Error setting form for creating an artist: {e}')
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
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash(f'Artist {artist.name} was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
        db.session.rollback()
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
        print(f'Error deleting artist: {e}')
    finally:
        db.session.close()
        return json.dumps(success), status
