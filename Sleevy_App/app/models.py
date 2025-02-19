from app import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash


class Coach(db.Model):
    __tablename__ = 'coach'
    idcoach = db.Column(db.Integer, primary_key=True)
    ndccoach = db.Column(db.String(200), unique=True, nullable=False)
    mdpcoach = db.Column(db.String(200), nullable=False)
    players = db.relationship('Player', backref='coach', lazy=True)

    def set_password(self, password):
        self.mdpcoach = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.mdpcoach, password)


class Player(db.Model):
    __tablename__ = 'joueur'
    idjoueur = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(200), unique=True, nullable=False)
    mdp = db.Column(db.String(200), nullable=False)
    idcoach = db.Column(db.Integer, db.ForeignKey('coach.idcoach'))
    sessions = db.relationship('Session', backref='player', lazy=True)

    def set_password(self, password):
        self.mdp = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.mdp, password)


class Session(db.Model):
    __tablename__ = 'sleevy_session'
    session_id = db.Column(db.Integer, primary_key=True)
    idjoueur = db.Column(db.Integer, db.ForeignKey('joueur.idjoueur'))
    starttime = db.Column(db.DateTime)
    endtime = db.Column(db.DateTime)
    gamenumber = db.Column(db.Integer)


class EMG(db.Model):
    __tablename__ = 'sleevyemg'
    idjoueur = db.Column(db.Integer, db.ForeignKey('joueur.idjoueur'), primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sleevy_session.session_id'), primary_key=True)
    valeuremg = db.Column(db.Integer)
    dateemg = db.Column(db.Date)
    heureemg = db.Column(db.DateTime, default=datetime.utcnow)


class PPG(db.Model):
    __tablename__ = 'sleevyppg'
    idjoueur = db.Column(db.Integer, db.ForeignKey('joueur.idjoueur'), primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sleevy_session.session_id'), primary_key=True)
    valeurppg = db.Column(db.Integer)
    dateppg = db.Column(db.Date)
    heureppg = db.Column(db.DateTime, default=datetime.utcnow)


class Accelerometer(db.Model):
    __tablename__ = 'sleevyaccelerometre'
    idjoueur = db.Column(db.Integer, db.ForeignKey('joueur.idjoueur'), primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sleevy_session.session_id'), primary_key=True)
    valeuraccel = db.Column(db.Integer)
    dateaccel = db.Column(db.Date)
    heureaccel = db.Column(db.DateTime, default=datetime.utcnow)
