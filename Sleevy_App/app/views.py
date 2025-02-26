
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.models import Coach, Player,EMG, PPG,Session
from threading import Thread
import base64
from datetime import datetime
from sqlalchemy import desc
from PIL import Image
from io import BytesIO
import os
import requests


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/portal_coach')
def portal_coach():
    return render_template('portal_coach.html')

@app.route('/portal_joueur')
def portal_joueur():
    return render_template('portal_joueur.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_joueur')
def register_joueur():
    return render_template('register_joueur.html')


@app.route('/login_joueur')
def login_joueur():
    return render_template('login_joueur.html')

@app.route('/login_coach')
def login_coach():
    return render_template('login_coach.html')



@app.route('/add', methods=['POST'])
def add_data():
    type = request.json['type']
    charts64 = request.json['charts64']
    new_data = Session(type=type, charts64=charts64)
    db.session.add(new_data)
    db.session.commit()

  

@app.route('/register_coaches', methods=['POST'])
def register_coaches():
    form = request.form
    new_coach = Coach(
        ndccoach=form['username'],  
    )
    new_coach.set_password(form['password'])  
    db.session.add(new_coach)
    db.session.commit()

    coach = Coach.query.filter_by(ndccoach=form['username']).first()  
    if coach:
        session['coach'] = coach.idcoach  
        return redirect(url_for('coaches'))
    else:
        return redirect(url_for('register'))
    
@app.route('/register_joueurs', methods=['POST'])
def register_joueurs():
    form = request.form
    new_joueur = Player(
        pseudo=form['username'],idcoach=form['idcoach']
    )
    new_joueur.set_password(form['password'])  
    db.session.add(new_joueur)
    db.session.commit()

    joueur = Player.query.filter_by(pseudo=form['username']).first()  
    if joueur:
        session['joueur'] = joueur.idjoueur
        return redirect(url_for('joueurs'))
    else:
        return redirect(url_for('register'))




@app.route('/login_coaches', methods=['POST'])
def login_coaches():
    form = request.form
    coach = Coach.query.filter_by(ndccoach=form['username']).first()
    if not coach:
        return redirect(url_for('login_coach'))
    if coach.check_password(form['password']):
        session['coach'] = coach.idcoach
        return redirect(url_for('coaches'))
    else:
        return redirect(url_for('login_coach'))
    


@app.route('/login_players', methods=['POST'])
def login_players():
    form = request.form
    joueur = Player.query.filter_by(pseudo=form['username']).first()
    if not joueur:
        return redirect(url_for('login_joueur'))
    if joueur.check_password(form['password']):
        session['joueur'] = joueur.idjoueur  
        print(session['joueur'])
        return redirect(url_for('joueurs'))
    else:
        return redirect(url_for('login_joueur'))


@app.route('/coaches', methods=['POST', 'GET'])
def coaches():
    if session.get('coach'):
        coach_id = session.get('coach')
        print(coach_id)
        coach_players = Player.query.filter_by(idcoach=coach_id)
        return render_template('main_coach.html', coach_players=coach_players)
    return render_template('login.html')

@app.route('/joueurs', methods=['POST', 'GET'])
def joueurs():
    if session.get('joueur'): 
        joueur_id = session.get('joueur')
        print(joueur_id)
        joueur = Player.query.filter_by(idjoueur=joueur_id).first()  
        return render_template('main_joueur.html', player=joueur)
    print('error')
    return render_template('login_joueur.html')

@app.route('/historique', methods=['POST', 'GET'])
def historique():
    print("➡️ Route /historique appelée")  # Vérification de l'appel

    joueur_id = session.get('joueur')
    if not joueur_id:
        print("❌ Aucun joueur connecté, redirection vers l'index.")
        return redirect(url_for('index')) 

    player_sessions = Session.query.filter_by(idjoueur=joueur_id).all()
    print("Sessions récupérées :", player_sessions)  # Debugging

    return render_template('historique_joueur.html', sessions=player_sessions)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('coach', None)
    return redirect(url_for('index'))


