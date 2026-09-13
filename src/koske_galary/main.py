from flask import Flask, render_template, request, redirect, url_for
from koske_galary.config import Config
from koske_galary.database import db
from koske_galary.models import User, Gallery, Image
from flask_login import LoginManager, login_required, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import update


config = Config()
app = Flask(__name__)
for key in config.config:
    app.config[key] = config.config[key]
    print(f"Set config {key} to value: {app.config[key]}")

login_manager = LoginManager()
login_manager.login_view = 'auth.login' #pyright: ignore
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
        return db.session.scalar(db.select(User).where(User.id == user_id)).first()

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

@login_required
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

@login_required
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
                file.save(f"src/koske_galary/static/{file.filename}")
                relativePath = f"src/koske_galary/static/{file.filename}"

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

@app.route("/login")
def login(method=["GET", "POST"]):
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if password:
            if check_password_hash(db.session.scalar(db.select(User).where(User.username == username)).first().password, password=password):
                login_user(db.session.scalar(db.select(User).where(User.username == username)).first(), remember=True)
    return render_template('login.html')

@login_required
@app.route("/manage")
def manage(method=["GET", "POST"]):
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if password and username:
            if db.session.scalars(db.select(User).where(User.username==username)).first() is not None:
                db.session.execute(
                    db.update(User).where(User.username==username).value(password=generate_password_hash(password=password))
                    )
            else:
                hash = generate_password_hash(password=password)
                newUser = User(username=username, password=hash) #pyright: ignore
                db.session.add(newUser)
                db.session.commit()
    return render_template('manage.html')
    
if __name__ == "__main__":
    app.run(Config().config["HOST"], Config().config["PORT"], debug=Config().config["DEBUG"])