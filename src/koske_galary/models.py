from koske_galary.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(120), unique=True, nullable=False)
    longDescription = db.Column(db.String(10000), unique=True, nullable=False)
    thumbnailFilename = db.Column(db.String(120), unique=True, default=None)
    private = db.Column(db.Boolean())

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(1000), unique=True, nullable=False)
    filename = db.Column(db.String(120), unique=True, nullable=False)
    galleryId = db.Column(db.Integer(), db.ForeignKey('gallery.id'), nullable=False)
    imageOrder = db.Column(db.Integer())
    
