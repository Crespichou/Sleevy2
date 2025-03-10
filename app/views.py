
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.models import Coach, Player,EMG, PPG,Session, Accelerometer, PPGReference
from threading import Thread
import base64
from datetime import datetime, timedelta
from Projet.Session_BDDConnected import main
from sqlalchemy import desc
from PIL import Image
from io import BytesIO
import os
import requests
from threading import Event
from Projet.ping import test
import threading

stop_event = Event()

@app.route('/')
def index():
    return render_template('main.html')


@app.route('/portal_coach')
def portal_coach():
    return render_template('portal_coach.html')

@app.route('/portal_joueur')
def portal_joueur():
    return render_template('portal_joueur.html')

@app.route('/register_coach')
def register():
    return render_template('register_coach.html')

@app.route('/register_joueur')
def register_joueur():
    return render_template('register_joueur.html')


@app.route('/login_joueur')
def login_joueur():
    return render_template('login_joueur.html')

@app.route('/login_coach')
def login_coach():
    return render_template('login_coach.html')

@app.route('/analyse_performance')
def analyse_performance():
    return render_template('analyse_performances.html')


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
        flash("Pseudo incorrect", "danger")
        return redirect(url_for('login_joueur'))

    if joueur.check_password(form['password']):
        session['joueur'] = joueur.idjoueur  # ✅ Stocker l'ID du joueur dans la session
        session['pseudo'] = joueur.pseudo  # ✅ Stocker son pseudo (facultatif)
        return redirect(url_for('joueurs'))
    else:
        flash("Mot de passe incorrect", "danger")
        return redirect(url_for('login_joueur'))


@app.route('/coaches', methods=['POST', 'GET'])
def coaches():
    if session.get('coach'):
        coach_id = session.get('coach')
        coach_players = Player.query.filter_by(idcoach=coach_id) 
        coach = Coach.query.filter_by(idcoach=coach_id).first()
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        sessions_last_7_days = (
            db.session.query(Session.idjoueur, db.func.count(Session.session_id).label('game_count'))
            .filter(Session.starttime >= seven_days_ago)
            .group_by(Session.idjoueur)
            .all()
        )
        last_7_days_games = {session.idjoueur: session.game_count for session in sessions_last_7_days}

        return render_template('main_coach.html', coach_players=coach_players, coach=coach, last_7_days_games=last_7_days_games)
    return render_template('login_coach.html')

@app.route('/joueurs', methods=['POST', 'GET'])
def joueurs():
    if 'joueur' in session:  # ✅ Vérifier si 'joueur' est dans la session
        joueur_id = session['joueur']
        joueur = Player.query.filter_by(idjoueur=joueur_id).first()
        player_sessions = Session.query.filter_by(idjoueur=joueur_id).all()

        return render_template('main_joueur.html', player=joueur, sessions=player_sessions)

    flash("Vous devez être connecté pour accéder à cette page.", "warning")
    return redirect(url_for('login_joueur'))



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
    session.pop('joueur', None) 
    return redirect(url_for('index'))

#Sélection des données PPG, EMG et Accel correspondant à la dernière session
@app.route('/graphique_ppg_emg', methods=['GET'])
def graphique_ppg_emg():
    joueur_id = session.get('joueur')
    print(joueur_id)
    if not joueur_id:
        return jsonify({"error": "Aucun joueur connecté."}), 400

    max_session = db.session.query(Session.session_id).filter_by(idjoueur=joueur_id).order_by(Session.session_id.desc()).first()
    if not max_session:
        return jsonify({"error": "Aucune session trouvée pour ce joueur."}), 404

    ppg_data = db.session.query(PPG.valeurppg, PPG.heureppg).filter_by(session_id=max_session[0], idjoueur=joueur_id).all()
    if not ppg_data:
        return jsonify({"error": "Aucune donnée PPG trouvée pour cette session."}), 404
    ppg_values = [{"valeur": ppg[0], "heure": ppg[1]} for ppg in ppg_data]

    emg_data = db.session.query(EMG.valeuremg, EMG.heureemg).filter_by(session_id=max_session[0], idjoueur=joueur_id).all()
    if not emg_data:
        return jsonify({"error": "Aucune donnée EMG trouvée pour cette session."}), 404
    emg_values = [{"valeur": emg[0], "heure": emg[1]} for emg in emg_data]

    accel_data = db.session.query(Accelerometer.valeuraccel, Accelerometer.heureaccel).filter_by(session_id=max_session[0], idjoueur=joueur_id).all()
    if not accel_data:
        return jsonify({"error": "Aucune donnée Accel trouvée pour cette session."}), 404
    accel_values = [{"valeur": accel[0], "heure": accel[1]} for accel in accel_data]

    return jsonify({
        "ppg_values": ppg_values,
        "emg_values": emg_values,
        "accel_values": accel_values
    })



#Sélection de toutes les données PPG pour un joueur donné 
@app.route('/graphique_ppg_toutes_sessions', methods=['GET'])
def graphique_ppg_toutes_sessions():
    joueur_id = session.get('joueur')
    if not joueur_id:
        return jsonify({"error": "Aucun joueur connecté."}), 400

    # Récupérer tous les session_id associés à ce joueur
    sessions = db.session.query(Session.session_id).filter_by(idjoueur=joueur_id).order_by(Session.session_id.asc()).all()
    if not sessions:
        return jsonify({"error": "Aucune session trouvée pour ce joueur."}), 404

    ppg_sessions = {}

    for session_row in sessions:
        session_id = session_row[0]
        ppg_data = db.session.query(PPG.valeurppg).filter_by(session_id=session_id, idjoueur=joueur_id).all()
        if ppg_data:
            ppg_sessions[session_id] = [ppg[0] for ppg in ppg_data]

    if not ppg_sessions:
        return jsonify({"error": "Aucune donnée PPG trouvée pour ce joueur."}), 404

    ppg_data_repos = db.session.query(PPGReference.valeurppgrepos).filter_by(idjoueur=joueur_id).all()
    if not ppg_data_repos:
        return jsonify({"error": "Aucune donnée PPG trouvée pour cette session."}), 404
    ppg_values = [ppg[0] for ppg in ppg_data_repos]  # Simplification pour obtenir une liste de valeurs

    # Inclure les valeurs de référence dans la réponse
    return jsonify({
        "ppg_sessions": ppg_sessions,
        "referenceValues": ppg_values
    })

@app.route("/historique_coach/<int:idjoueur>", methods=['GET'])
def historique_coach(idjoueur):
    # Vérifier que le joueur existe
    player = Player.query.filter_by(idjoueur=idjoueur).first()
    
    if not player:
        return "Joueur non trouvé", 404

    # Récupérer les sessions associées à ce joueur
    games = Session.query.filter_by(idjoueur=idjoueur).order_by(Session.starttime.desc()).all()

    return render_template("historique_coach.html", player=player, games=games)


@app.route('/detail_coach/<int:session_id>', methods=['GET'])
def detail_coach(session_id):
    # Vérification que le coach est bien connecté
    if not session.get('coach'):
        return jsonify({"error": "Accès refusé. Connectez-vous en tant que coach."}), 403
    
    # Récupération des données de la session sélectionnée
    ppg_data = db.session.query(PPG.valeurppg, PPG.heureppg).filter_by(session_id=session_id).all()
    emg_data = db.session.query(EMG.valeuremg, EMG.heureemg).filter_by(session_id=session_id).all()
    accel_data = db.session.query(Accelerometer.valeuraccel, Accelerometer.heureaccel).filter_by(session_id=session_id).all()

    if not ppg_data or not emg_data or not accel_data:
        return jsonify({"error": "Aucune donnée trouvée pour cette session."}), 404

    ppg_values = [{"valeur": ppg[0], "heure": ppg[1]} for ppg in ppg_data]
    emg_values = [{"valeur": emg[0], "heure": emg[1]} for emg in emg_data]
    accel_values = [{"valeur": accel[0], "heure": accel[1]} for accel in accel_data]

    return render_template("detail_coach.html", session_id=session_id, ppg_values=ppg_values, emg_values=emg_values, accel_values=accel_values)

@app.route('/detail_joueur/<int:session_id>', methods=['GET'])
def detail_joueur(session_id):
    # Vérification si le joueur est connecté
    if 'joueur' not in session:
        return jsonify({"error": "Accès refusé. Connectez-vous en tant que joueur."}), 403
    print(session_id)
    print('ping')
    

    # Récupération des données de la session sélectionnée
    ppg_data = db.session.query(PPG.valeurppg, PPG.heureppg).filter_by(session_id=session_id).all()
    emg_data = db.session.query(EMG.valeuremg, EMG.heureemg).filter_by(session_id=session_id).all()
    accel_data = db.session.query(Accelerometer.valeuraccel, Accelerometer.heureaccel).filter_by(session_id=session_id).all()
    print(ppg_data)
    if not ppg_data or not emg_data or not accel_data:
        return jsonify({"error": "Aucune donnée trouvée pour cette session."}), 404

    ppg_values = [{"valeur": ppg[0], "heure": ppg[1]} for ppg in ppg_data]
    emg_values = [{"valeur": emg[0], "heure": emg[1]} for emg in emg_data]
    accel_values = [{"valeur": accel[0], "heure": accel[1]} for accel in accel_data]

    return render_template("detail_joueur.html", session_id=session_id, ppg_values=ppg_values, emg_values=emg_values, accel_values=accel_values)

@app.route('/start/<int:idjoueur>', methods=['GET'])
def start(idjoueur):
    main(idjoueur)
    return redirect(url_for('joueurs'))


