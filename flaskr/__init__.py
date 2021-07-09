from flask import flash, render_template
import logging
from logging import Formatter, FileHandler
from flaskr.forms import *
from flaskr.app import app
from flaskr.db import db
import flaskr.filters
import flaskr.controllers.venues
import flaskr.controllers.artists
import flaskr.controllers.shows
from flaskr.models import Venue, Artist


@app.route('/')
def index():
    recent_venues = []
    recent_artists = []
    try:
        # show latest venues/artists, most recent first
        recent_venues = Venue.query.order_by(
            Venue.created_at.desc()).limit(10).all()
        recent_artists = Artist.query.order_by(
            Artist.created_at.desc()).limit(10).all()
    except Exception as e:
        print(f'Error [GET] / - {e}')
        # still render the page even if the items can't be fetched
        # but flash an error letting the user know
        flash("Couldn't get recent venues or artists. Refresh or try again later.")
    finally:
        db.session.close()
    return render_template('pages/home.html', recent_venues=recent_venues, recent_artists=recent_artists)


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
