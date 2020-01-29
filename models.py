from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
import os
from flask_migrate import Migrate
from sqlalchemy.dialects import postgresql

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__='venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    genres = db.Column(postgresql.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seek_status = db.Column(db.Boolean)
    seek_body = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref = db.backref('venue', lazy = True, cascade = "all"))

    def __repr__(self):
        return f'<Venue:{self.name}>'

class Artist(db.Model):
    __tablename__='artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    genres = db.Column(postgresql.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seek_status = db.Column(db.Boolean)
    seek_body = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref = db.backref('artist', lazy = True, cascade = "all"))

    def __repr__(self):
        return f'<Artist:{self.name}>'

class Show(db.Model):
    __tablename__='shows'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable = False)

    def __repr__(self):
        return f'<Show:{self.id}, Date:{self.date}>'