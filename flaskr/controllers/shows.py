
from flask import abort, flash, redirect, render_template, request, url_for
from flaskr.db import db
from flaskr.app import app
from flaskr.models import Show
from flaskr.forms import ShowForm

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
    try:
        shows = Show.query.all()
        data = [select_show_details(show) for show in shows]
        return render_template('pages/shows.html', shows=data)
    except Exception as e:
        db.session.close()
        print(f'Error fetching shows: {e}')
        flash('Shows could not be fetched at this time. Refresh or try again later.')
        abort(500)
    finally:
        db.session.close()


#  Create Show
#  ----------------------------------------------------------------


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
        return render_template('pages/home.html')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating a show: {e}')
        flash('An error occurred. Show could not be listed.')
        return redirect(url_for('create_shows'))
    finally:
        db.session.close()
