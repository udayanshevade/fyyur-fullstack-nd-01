from flaskr.app import db, Genre, Venue, Artist, Show

genres_data = [
    {'name': 'Alternative'},
    {'name': 'Blues'},
    {'name': 'Classical'},
    {'name': 'Country'},
    {'name': 'Electronic'},
    {'name': 'Folk'},
    {'name': 'Funk'},
    {'name': 'Hip-Hop'},
    {'name': 'Heavy Metal'},
    {'name': 'Instrumental'},
    {'name': 'Jazz'},
    {'name': 'Musical Theatre'},
    {'name': 'Pop'},
    {'name': 'Punk'},
    {'name': 'R&B'},
    {'name': 'Reggae'},
    {'name': 'Rock n Roll'},
    {'name': 'Soul'},
    {'name': 'Swing'},
    {'name': 'Other'}
]


def seed_genres():
    '''Populate the db with initial genres data'''
    if db.session.query(Genre).count() != 0:
        # Ignore if already populated
        return

    print('Seeding genres')
    try:
        for genre_data in genres_data:
            genre = Genre(name=genre_data['name'])
            db.session.add(genre)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Something went wrong while seeding genre data: {}'.format(e))
    finally:
        db.session.close()


venues_data = [{
    "id": 1,
    "name": "The Musical Hop",
    "genres": [{
        "id": 11,
        "name": "Jazz"
    }, {
        "id": 16,
        "name": "Reggae"
    }, {
        "id": 19,
        "name": "Swing"
    }, {
        "id": 3,
        "name": "Classical"
    }, {
        "id": 6,
        "name": "Folk"
    }],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
}, {
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": [{
        "id": 3,
        "name": "Classical"
    }, {
        "id": 15,
        "name": "R&B"
    }, {
        "id": 8,
        "name": "Hip-Hop"
    }],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
}, {
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": [{
        "id": 17,
        "name": "Rock n Roll"
    }, {
        "id": 11,
        "name": "Jazz"
    }, {
        "id": 3,
        "name": "Classical"
    }, {
        "id": 6,
        "name": "Folk"
    }],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
}]


def seed_venues():
    '''Populate the db with initial venues data'''
    if db.session.query(Venue).count() != 0:
        # Ignore if already populated
        return
    print('Seeding venues')
    try:
        for venue_data in venues_data:
            venue = Venue(
                name=venue_data['name'],
                city=venue_data['city'],
                state=venue_data['state'],
                address=venue_data['address'],
                phone=venue_data['phone'],
                facebook_link=venue_data['facebook_link'],
                image_link=venue_data['image_link'],
                seeking_talent=venue_data['seeking_talent'],
                seeking_description=venue_data.get(
                    'seeking_description', None),
                website=venue_data['website'],
            )

            venue.genres = [Genre.query.get(
                venue_genre_data['id']) for venue_genre_data in venue_data['genres']]

            db.session.add(venue)
        db.session.commit()
    except Exception as e:
        print('Something went wrong while seeding venue data: {}'.format(e))
        db.session.rollback()
    finally:
        db.session.close()


artists_data = [{
    "id": 1,
    "name": "Guns N Petals",
    "genres": [{
        "id": 17,
        "name": "Rock n Roll"
    }],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
}, {
    "id": 2,
    "name": "Matt Quevedo",
    "genres": [{
        "id": 11,
        "name": "Jazz"
    }],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
}, {
    "id": 3,
    "name": "The Wild Sax Band",
    "genres": [{
        "id": 11,
        "name": "Jazz"
    }, {
        "id": 3,
        "name": "Classical"
    }],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
}]


def seed_artists():
    '''Populate the db with initial artists data'''
    if db.session.query(Artist).count() != 0:
        # Ignore if already populated
        return
    print('Seeding artists')
    try:
        for artist_data in artists_data:
            artist = Artist(
                name=artist_data['name'],
                city=artist_data['city'],
                state=artist_data['state'],
                phone=artist_data['phone'],
                facebook_link=artist_data.get('facebook_link', None),
                image_link=artist_data['image_link'],
                seeking_venue=artist_data['seeking_venue'],
                seeking_description=artist_data.get(
                    'seeking_description', None),
                website=artist_data.get('website', None),
            )
            artist.genres = [Genre.query.get(
                artist_genre_data['id']) for artist_genre_data in artist_data['genres']]
            db.session.add(artist)
        db.session.commit()
    except Exception as e:
        print('Something went wrong while seeding artist data: {}'.format(e))
        db.session.rollback()
    finally:
        db.session.close()


shows_data = [{
    "venue_id": 1,
    "artist_id": 1,
    "start_time": "2019-05-21T21:30:00.000Z",
    "end_time": "2019-05-22T02:00:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 2,
    "start_time": "2019-06-15T23:00:00.000Z",
    "end_time": "2019-06-16T03:00:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 3,
    "start_time": "2035-04-01T20:00:00.000Z",
    "end_time": "2035-04-02T00:00:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 3,
    "start_time": "2035-04-08T20:00:00.000Z",
    "end_time": "2035-04-08T23:30:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 3,
    "start_time": "2035-04-15T20:00:00.000Z",
    "end_time": "2035-04-16T00:00:00.000Z"
}]


def seed_shows():
    '''Populate the db with initial shows data'''
    if db.session.query(Show).count() != 0:
        # Ignore if already populated
        return
    print('Seeding shows')

    try:
        for show_data in shows_data:
            artist = Artist.query.get(show_data['artist_id'])
            venue = Venue.query.get(show_data['venue_id'])
            show = Show(
                start_time=show_data['start_time'],
                end_time=show_data['end_time']
            )
            show.artist = artist
            show.venue = venue
            db.session.add(show)
        db.session.commit()
    except Exception as e:
        print('Something went wrong while seeding artist data: {}'.format(e))
        db.session.rollback()
    finally:
        db.session.close()


if __name__ == '__main__':
    print('Seeding db')
    seed_genres()
    seed_venues()
    seed_artists()
    seed_shows()
