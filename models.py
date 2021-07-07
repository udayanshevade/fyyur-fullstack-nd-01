from db import db

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
