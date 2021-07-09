
from flask import abort, flash, redirect, render_template, request, url_for
from flaskr.db import db
from flaskr.app import app
from flaskr.models import Show, Artist, Venue
from flaskr.forms import ShowForm

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows', methods=['GET'])
def shows():
    try:
        shows = db.session.query(
            Show.id,
            Show.start_time,
            Show.end_time,
            Artist.id.label('artist_id'),
            Artist.name.label('artist_name'),
            Artist.image_link.label('artist_image_link'),
            Venue.id.label('venue_id'),
            Venue.name.label('venue_name')
        ).select_from(Show).join(Artist, Venue).all()

        return render_template('pages/shows.html', shows=shows)
    except Exception as e:
        db.session.close()
        print(f'Error - [GET] /shows - {e}')
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
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
        db.session.rollback()
        print(f'Error - GET /shows/create - {e}')
        flash('An error occurred. Show could not be listed.')
        return redirect(url_for('create_shows'))
    finally:
        db.session.close()
