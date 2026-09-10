from flask import Flask, render_template #pyright: ignore
from flask_sqlalchemy import SQLAlchemy #pyright: ignore
from koske_galary.config import Config
from koske_galary.database import db
from koske_galary.models import User, Gallery, Image

config = Config()
app = Flask(__name__)
for key in config.config:
    app.config[key] = config.config[key]
    print(f"Set config {key} to value: {app.config[key]}")
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/gallery")
def gallary():
    galleries = db.session.scalars(db.select(Gallery)).all()
    return render_template('gallery.html', galleries=galleries)

@app.route("/gallery/<id>")
def render_gallery(id):
    gallery = db.session.scalars(db.select(Gallery).where(Gallery.id == id)).first()
    images = db.session.scalars(db.select(Image).where(Image.galleryId == id)).all()
    return render_template("gallery_render.html", id=id)

if __name__ == "__main__":
    app.run(Config().config["HOST"], Config().config["PORT"],debug=Config().config["DEBUG"])