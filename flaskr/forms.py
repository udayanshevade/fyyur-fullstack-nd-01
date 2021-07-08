from datetime import datetime, timedelta
import pytz
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, URL, ValidationError
import re
from flaskr.enums import State


#  Validators
#  ----------------------------------------------------------------

def state_validator(field):
    '''Ensure state is in provided choices'''
    state = field.data
    return (state, state) in State.choices()


def phone_validator(field):
    '''
      Validate phone numbers like:
      1234567890 - no space
      123.456.7890 - dot separator
      123-456-7890 - dash separator
      123 456 7890 - space separator
      Patterns:
      000 = [0-9]{3}
      0000 = [0-9]{4}
      -.  = ?[-. ]
      Note: (? = optional) - Learn more: https://regex101.com/
    '''
    number = field.data
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    print(f'number {number}')
    return regex.match(number)

#  Forms
#  ----------------------------------------------------------------


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.now(pytz.utc)
    )
    end_time = DateTimeField(
        'end_time',
        validators=[DataRequired()],
        default=datetime.now(pytz.utc) + timedelta(hours=2)
    )


class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        coerce=int
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )

    def validate_phone(self, field):
        print('validating phone')
        if not phone_validator(field):
            raise ValidationError('Invalid phone')

    def validate_state(self, field):
        print('validating state')
        if not state_validator(field):
            raise ValidationError('Invalid state')


class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), state_validator],
        choices=State.choices()
    )
    phone = StringField(
        'phone',
        validators=[phone_validator]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        coerce=int
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

    website_link = StringField(
        'website_link'
    )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
        'seeking_description'
    )

    def validate_phone(self, field):
        if not phone_validator(field):
            raise ValidationError('Invalid phone')

    def validate_state(self, field):
        if not state_validator(field):
            raise ValidationError('Invalid state')
