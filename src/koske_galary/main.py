import os
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from koske_galary.config import Config
from koske_galary.database import db
from koske_galary.models import User, Gallery, Image

config = Config()
app = Flask(__name__)
for key in config.config:
    app.config[key] = config.config[key]
    print(f"Set config {key} to value: {app.config[key]}")

uploadFolder = Path(app.root_path) / "static" / "uploads"
uploadFolder.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(uploadFolder)

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/gallery")
def gallary():
    galleries = db.session.scalars(db.select(Gallery).where(Gallery.private==False)).all()
    return render_template('gallery.html', galleries=galleries)

@app.route("/gallery/<int:id>")
def render_gallery(id):
    gallery = db.session.scalars(db.select(Gallery).where(Gallery.id == id)).first()
    images = db.session.scalars(db.select(Image).where(Image.galleryId == id)).all()
    return render_template("gallery_render.html", galery=gallery, images=images)

@app.route("/build", methods=["GET", "POST"])
def build():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        longDescription = request.form.get("longDescription")
        is_private = bool(request.form.get("private"))

        if name:
            new_gallery = Gallery(
                name=name, #pyright: ignore
                description=description, #pyright: ignore
                longDescription=longDescription, #pyright: ignore
                private=is_private #pyright: ignore
            )
            db.session.add(new_gallery)
            db.session.commit()
            return redirect(url_for("build"))  

    galleries = db.session.scalars(db.select(Gallery)).all()
    return render_template("galleryBuilder.html", galleries=galleries)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def editGallery(id):
    gallery = db.get_or_404(Gallery, id)
    images = db.session.scalars(db.select(Image).where(Image.galleryId == id)).all()

    if request.method == "POST":
        if "upload_photo" in request.form:
            photoName = request.form.get("name")
            photoDescription = request.form.get("description")
            file = request.files.get("file")

            if file and photoName:
                filename = secure_filename(file.filename) #pyright: ignore
                filePath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filePath)
                relativePath = f"uploads/{filename}"

                newImage = Image(
                    name=photoName, #pyright: ignore
                    description=photoDescription, #pyright: ignore
                    filename=relativePath, #pyright: ignore
                    galleryId=gallery.id #pyright: ignore
                )
                db.session.add(newImage)
                
                if not gallery.thumbnailFilename:
                    gallery.thumbnailFilename = relativePath

                db.session.commit()
                return redirect(url_for("editGallery", id=id))

        if "save_changes" in request.form:
            selectedThumbnail = request.form.get("thumbnail")
            if selectedThumbnail:
                thumbImage = db.get_or_404(Image, int(selectedThumbnail))
                gallery.thumbnailFilename = thumbImage.filename

            for img in images:
                if f"delete_{img.id}" in request.form:
                    db.session.delete(img)
                    continue

                updatedName = request.form.get(f"name_{img.id}")
                updatedDesc = request.form.get(f"description_{img.id}")
                if updatedName:
                    img.name = updatedName
                if updatedDesc is not None:
                    img.description = updatedDesc

            db.session.commit()
            return redirect(url_for("editGallery", id=id))

    return render_template('galleryEditor.html', gallery=gallery, images=images)

if __name__ == "__main__":
    app.run(Config().config["HOST"], Config().config["PORT"], debug=Config().config["DEBUG"])