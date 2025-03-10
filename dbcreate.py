from flask import Flask, request, jsonify
from app import app, db
from flask_sqlalchemy import SQLAlchemy

with app.app_context():
    db.create_all()
