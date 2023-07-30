from app import db, User, Post, app  # make sure to import app

with app.app_context():
    db.create_all()
